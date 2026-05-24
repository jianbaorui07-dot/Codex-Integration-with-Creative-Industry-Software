from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from starbridge_mcp.core.result_schema import make_result, validate_result
from starbridge_mcp.core.security import sanitize


BRIDGE = "comfyui"
DEFAULT_URL = "http://127.0.0.1:8188"
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:[\\/][^\s\"'<>]+"),
    re.compile(r"/Users/[^/\s\"'<>]+"),
    re.compile(r"/home/[^/\s\"'<>]+"),
)


def _base_url(base_url: str | None = None) -> str:
    return (base_url or os.environ.get("STARBRIDGE_COMFYUI_URL") or DEFAULT_URL).rstrip("/")


def _result(
    *,
    ok: bool,
    action: str,
    message: str,
    details: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    result = make_result(
        ok=ok,
        bridge=BRIDGE,
        action=action,
        message=message,
        details=sanitize(details or {}),
        warnings=sanitize(warnings or []),
        next_steps=sanitize(next_steps or []),
    )
    validate_result(result)
    return result


def _request_json(
    path: str,
    *,
    base_url: str | None = None,
    timeout: float = 3.0,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[bool, Any, str | None]:
    url = f"{_base_url(base_url)}{path}"
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return True, json.loads(raw) if raw else {}, None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return False, None, str(exc)


def _workflow_nodes(workflow_json: Any) -> list[tuple[str, dict[str, Any]]]:
    if not isinstance(workflow_json, dict):
        return []
    if isinstance(workflow_json.get("nodes"), list):
        nodes = []
        for index, node in enumerate(workflow_json["nodes"]):
            if isinstance(node, dict):
                node_id = str(node.get("id", index))
                class_type = node.get("class_type") or node.get("type") or node.get("name")
                inputs = node.get("inputs", {})
                nodes.append((node_id, {"class_type": class_type, "inputs": inputs}))
        return nodes
    return [(str(node_id), node) for node_id, node in workflow_json.items() if isinstance(node, dict)]


def _walk_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_walk_values(item))
        return values
    return []


def _contains_absolute_path(value: str) -> bool:
    return any(pattern.search(value) for pattern in ABSOLUTE_PATH_PATTERNS)


def status(*, base_url: str | None = None, timeout: float = 2.0) -> dict[str, Any]:
    url = _base_url(base_url)
    probe_result = probe(base_url=url, timeout=timeout)
    if probe_result["ok"]:
        return _result(
            ok=True,
            action="status",
            message="ComfyUI API is reachable.",
            details={"base_url": url, "system_stats": probe_result["details"].get("system_stats", {})},
            next_steps=["Use validate_workflow() and dry-run queue checks before any real queue attempt."],
        )
    return _result(
        ok=False,
        action="status",
        message="ComfyUI API is not reachable.",
        details={"base_url": url, "probe": probe_result["details"]},
        warnings=probe_result["warnings"],
        next_steps=[
            "Start local ComfyUI if you want live probing.",
            "Set STARBRIDGE_COMFYUI_URL when ComfyUI is not running on http://127.0.0.1:8188.",
            "Dry-run workflow validation is still available without ComfyUI.",
        ],
    )


def probe(*, base_url: str | None = None, timeout: float = 3.0) -> dict[str, Any]:
    ok, data, error = _request_json("/system_stats", base_url=base_url, timeout=timeout)
    if ok:
        return _result(
            ok=True,
            action="probe",
            message="ComfyUI /system_stats responded.",
            details={"base_url": _base_url(base_url), "system_stats": data},
        )
    return _result(
        ok=False,
        action="probe",
        message="ComfyUI /system_stats is unavailable.",
        details={"base_url": _base_url(base_url), "error": error},
        warnings=["ComfyUI service is not running or did not return valid JSON."],
        next_steps=["Start ComfyUI locally, or keep using offline validation and dry-run helpers."],
    )


def list_models(*, base_url: str | None = None, timeout: float = 5.0) -> dict[str, Any]:
    ok, data, error = _request_json("/object_info", base_url=base_url, timeout=timeout)
    if not ok or not isinstance(data, dict):
        return _result(
            ok=False,
            action="list_models",
            message="ComfyUI object_info is unavailable.",
            details={"base_url": _base_url(base_url), "unavailable": True, "error": error},
            warnings=["Model metadata could not be read; no live model list is available."],
            next_steps=["Start ComfyUI and retry, or validate workflow structure offline."],
        )

    model_fields = ("ckpt_name", "model_name", "vae_name", "lora_name", "control_net_name")
    discovered: dict[str, list[str]] = {}
    for class_name, class_info in data.items():
        if not isinstance(class_info, dict):
            continue
        inputs = class_info.get("input", {})
        if not isinstance(inputs, dict):
            continue
        sections = []
        for section_name in ("required", "optional"):
            section = inputs.get(section_name, {})
            if isinstance(section, dict):
                sections.append(section)
        for section in sections:
            for field_name, field_info in section.items():
                if field_name not in model_fields or not isinstance(field_info, list) or not field_info:
                    continue
                values = field_info[0]
                if isinstance(values, list):
                    discovered.setdefault(field_name, [])
                    for value in values[:20]:
                        if isinstance(value, str):
                            discovered[field_name].append(value)

    return _result(
        ok=True,
        action="list_models",
        message="ComfyUI object_info was read.",
        details={"base_url": _base_url(base_url), "model_fields": discovered, "class_count": len(data)},
        warnings=[] if discovered else ["object_info responded, but no common model fields were discovered."],
    )


def validate_workflow(workflow_json: Any) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    if not isinstance(workflow_json, dict):
        return _result(
            ok=False,
            action="validate_workflow",
            message="Workflow must be a JSON object.",
            details={"node_count": 0, "errors": ["workflow is not a dict"]},
            warnings=["Nothing was executed."],
            next_steps=["Pass a ComfyUI API-format workflow object."],
        )
    if not workflow_json:
        return _result(
            ok=False,
            action="validate_workflow",
            message="Workflow is empty.",
            details={"node_count": 0, "errors": ["workflow is empty"]},
            warnings=["Nothing was executed."],
            next_steps=["Add at least one node with class_type and inputs."],
        )

    nodes = _workflow_nodes(workflow_json)
    if not nodes:
        errors.append("no valid node objects found")
    for node_id, node in nodes:
        if not node.get("class_type"):
            errors.append(f"node {node_id} missing class_type")
        if "inputs" not in node:
            errors.append(f"node {node_id} missing inputs")
        elif not isinstance(node.get("inputs"), dict):
            errors.append(f"node {node_id} inputs must be an object")
    if isinstance(workflow_json.get("nodes"), list):
        warnings.append("Detected UI-style nodes array; ComfyUI queue usually requires API-format workflow JSON.")

    return _result(
        ok=not errors,
        action="validate_workflow",
        message="Workflow structure is valid." if not errors else "Workflow structure has problems.",
        details={"node_count": len(nodes), "errors": errors},
        warnings=warnings,
        next_steps=[] if not errors else ["Fix missing class_type/inputs before queueing."],
    )


def summarize_workflow(workflow_json: Any) -> dict[str, Any]:
    validation = validate_workflow(workflow_json)
    nodes = _workflow_nodes(workflow_json)
    input_nodes: list[str] = []
    sampler_nodes: list[str] = []
    save_nodes: list[str] = []
    path_hits: list[str] = []

    for node_id, node in nodes:
        class_type = str(node.get("class_type") or "")
        lower = class_type.lower()
        if any(marker in lower for marker in ("load", "input", "cliptextencode")):
            input_nodes.append(node_id)
        if "ksampler" in lower or "sampler" in lower:
            sampler_nodes.append(node_id)
        if "save" in lower or "output" in lower:
            save_nodes.append(node_id)
        for text in _walk_values(node.get("inputs", {})):
            if _contains_absolute_path(text):
                path_hits.append(text)

    warnings = list(validation["warnings"])
    if path_hits:
        warnings.append("Workflow contains absolute path-like values; details were sanitized.")

    return _result(
        ok=validation["ok"],
        action="summarize_workflow",
        message="Workflow summary generated." if validation["ok"] else "Workflow summary generated with validation issues.",
        details={
            "node_count": len(nodes),
            "input_nodes": input_nodes,
            "sampler_nodes": sampler_nodes,
            "save_nodes": save_nodes,
            "validation": validation["details"],
            "absolute_path_hits": sanitize(path_hits),
        },
        warnings=warnings,
        next_steps=validation["next_steps"],
    )


def queue_workflow(
    workflow_json: Any,
    *,
    dry_run: bool = True,
    allow_queue: bool = False,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    validation = validate_workflow(workflow_json)
    if not validation["ok"]:
        return _result(
            ok=False,
            action="queue_workflow",
            message="Workflow was not queued because validation failed.",
            details={"validation": validation["details"], "dry_run": dry_run, "queued": False},
            warnings=validation["warnings"],
            next_steps=validation["next_steps"],
        )
    if dry_run:
        return _result(
            ok=True,
            action="queue_workflow",
            message="Dry-run only; workflow was not queued.",
            details={"base_url": _base_url(base_url), "dry_run": True, "queued": False},
            warnings=["No request was sent to ComfyUI."],
            next_steps=["Set dry_run=False, allow_queue=True, and STARBRIDGE_COMFYUI_ALLOW_QUEUE=1 only when intentional."],
        )
    if not allow_queue or os.environ.get("STARBRIDGE_COMFYUI_ALLOW_QUEUE") != "1":
        return _result(
            ok=False,
            action="queue_workflow",
            message="Real ComfyUI queue refused by safety gate.",
            details={"dry_run": dry_run, "allow_queue": allow_queue, "queued": False},
            warnings=["Real queue requires allow_queue=True and STARBRIDGE_COMFYUI_ALLOW_QUEUE=1."],
            next_steps=["Use dry_run=True for demos, or explicitly enable both queue gates for local experiments."],
        )

    ok, data, error = _request_json(
        "/prompt",
        base_url=base_url,
        timeout=timeout,
        method="POST",
        payload={"prompt": workflow_json},
    )
    return _result(
        ok=ok,
        action="queue_workflow",
        message="Workflow queued." if ok else "ComfyUI queue request failed.",
        details={"base_url": _base_url(base_url), "dry_run": False, "queued": ok, "response": data, "error": error},
        warnings=[] if ok else ["ComfyUI did not accept the queue request."],
        next_steps=[] if ok else ["Check ComfyUI server logs and workflow compatibility."],
    )
