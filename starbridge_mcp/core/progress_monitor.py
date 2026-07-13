from __future__ import annotations

import hashlib
import ipaddress
import json
import socket
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from starbridge_mcp.core.progress_monitor_schema import MAX_PROGRESS_VALUE, SCHEMA_VERSION
from starbridge_mcp.core.queue_snapshot import DEFAULT_COMFY_URL, _validate_loopback_url
from starbridge_mcp.core.security import sanitize

MAX_EVENT_BYTES = 1_048_576


class ProgressDependencyUnavailable(RuntimeError):
    """Raised when the optional live WebSocket dependency is not installed."""


class ProgressPayloadInvalid(ValueError):
    """Raised when an event reader returns data outside the bounded contract."""


@dataclass(frozen=True)
class ObservedFrame:
    elapsed_ms: int
    payload: Any


@dataclass(frozen=True)
class ProgressRead:
    frames: list[ObservedFrame]
    elapsed_ms: int
    binary_events_ignored: int = 0


EventReader = Callable[[str, int, int, str | None], ProgressRead]


def _logical_id(prefix: str, raw_value: str) -> str:
    digest = hashlib.sha256(raw_value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _empty_progress() -> dict[str, Any]:
    return {
        "available": False,
        "source": "not_available",
        "scope": "current_node",
        "current": None,
        "total": None,
        "percent": None,
        "monotonic": False,
    }


def _empty_monitor() -> dict[str, Any]:
    return {
        "received_events": 0,
        "accepted_events": 0,
        "ignored_events": 0,
        "binary_events_ignored": 0,
        "duplicate_progress_events": 0,
        "progress_regressions": 0,
        "elapsed_ms": 0,
        "stalled": False,
        "stalled_for_ms": None,
        "terminal": False,
    }


def _safety(*, network_access: bool) -> dict[str, Any]:
    return {
        "network_access": network_access,
        "loopback_only": True,
        "proxy_used": False,
        "redirects_followed": False,
        "binary_payloads_ignored": True,
        "workflow_payloads_returned": False,
        "raw_job_ids_returned": False,
        "raw_node_ids_returned": False,
        "history_read": False,
        "queue_mutation": False,
        "local_file_reads": False,
        "local_file_writes": False,
        "desktop_software_started": False,
    }


def _snapshot_id(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"progress_{hashlib.sha256(canonical).hexdigest()[:12]}"


def _finalize(payload: dict[str, Any]) -> dict[str, Any]:
    payload["snapshot_id"] = _snapshot_id(payload)
    return sanitize(payload)


def _direct_loopback_socket(base_url: str, timeout: int) -> socket.socket:
    parsed = urlsplit(base_url)
    hostname = parsed.hostname
    if hostname is None:
        raise OSError("loopback endpoint unavailable")
    port = parsed.port or 80
    addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    for family, socktype, proto, _canonical_name, address in addresses:
        try:
            if not ipaddress.ip_address(address[0]).is_loopback:
                continue
        except ValueError:
            continue
        candidate = socket.socket(family, socktype, proto)
        candidate.settimeout(timeout)
        try:
            candidate.connect(address)
            peer = candidate.getpeername()[0]
            if not ipaddress.ip_address(peer).is_loopback:
                candidate.close()
                continue
            return candidate
        except OSError:
            candidate.close()
    raise OSError("loopback endpoint unavailable")


def _matches_terminal_event(payload: Any, target_job_id: str | None) -> bool:
    if not isinstance(payload, dict):
        return False
    event_type = payload.get("type")
    data = payload.get("data")
    if not isinstance(data, dict):
        return False
    raw_job_id = data.get("prompt_id")
    if _valid_identifier(raw_job_id) is None:
        return False
    if target_job_id is not None and raw_job_id != target_job_id:
        return False
    if event_type in {"execution_success", "execution_error", "execution_interrupted"}:
        return True
    return event_type == "executing" and data.get("node") is None


def _read_live_events(
    base_url: str,
    listen_seconds: int,
    max_events: int,
    target_job_id: str | None,
) -> ProgressRead:
    try:
        import websocket
    except ImportError as exc:
        raise ProgressDependencyUnavailable("websocket-client is not installed") from exc

    parsed = urlsplit(base_url)
    client_id = f"starbridge-progress-{uuid.uuid4().hex}"
    ws_url = urlunsplit(("ws", parsed.netloc, "/ws", urlencode({"clientId": client_id}), ""))
    connect_timeout = min(5, listen_seconds)
    direct_socket: socket.socket | None = _direct_loopback_socket(base_url, connect_timeout)
    ws: Any = None
    frames: list[ObservedFrame] = []
    binary_events_ignored = 0
    start = time.monotonic()
    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=connect_timeout,
            socket=direct_socket,
            redirect_limit=0,
            suppress_origin=True,
            http_no_proxy=["127.0.0.1", "localhost", "::1"],
        )
        direct_socket = None
        deadline = start + listen_seconds
        while len(frames) + binary_events_ignored < max_events:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            ws.settimeout(min(0.5, remaining))
            try:
                message = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            except websocket.WebSocketConnectionClosedException:
                break

            elapsed_ms = max(0, int((time.monotonic() - start) * 1_000))
            if isinstance(message, bytes):
                binary_events_ignored += 1
                continue
            if not isinstance(message, str):
                frames.append(ObservedFrame(elapsed_ms=elapsed_ms, payload=None))
                continue
            if len(message.encode("utf-8")) > MAX_EVENT_BYTES:
                raise ProgressPayloadInvalid("WebSocket text frame exceeds the safe limit")
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                payload = None
            safe_payload = payload if isinstance(payload, dict) else None
            frames.append(ObservedFrame(elapsed_ms=elapsed_ms, payload=safe_payload))
            if _matches_terminal_event(safe_payload, target_job_id):
                break
    except ProgressPayloadInvalid:
        raise
    except websocket.WebSocketException as exc:
        raise OSError("loopback WebSocket unavailable") from exc
    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass
        if direct_socket is not None:
            direct_socket.close()

    elapsed_ms = max(0, int((time.monotonic() - start) * 1_000))
    return ProgressRead(
        frames=frames,
        elapsed_ms=elapsed_ms,
        binary_events_ignored=binary_events_ignored,
    )


def _validate_read(observation: ProgressRead, *, max_events: int) -> None:
    if not isinstance(observation, ProgressRead):
        raise ProgressPayloadInvalid("event reader must return ProgressRead")
    if type(observation.elapsed_ms) is not int or observation.elapsed_ms < 0:
        raise ProgressPayloadInvalid("elapsed_ms must be a non-negative integer")
    if type(observation.binary_events_ignored) is not int or observation.binary_events_ignored < 0:
        raise ProgressPayloadInvalid("binary event count must be a non-negative integer")
    if not isinstance(observation.frames, list) or len(observation.frames) > max_events:
        raise ProgressPayloadInvalid("event list exceeds the requested bound")
    previous_elapsed = -1
    for item in observation.frames:
        if not isinstance(item, ObservedFrame):
            raise ProgressPayloadInvalid("event list contains an invalid frame")
        if (
            type(item.elapsed_ms) is not int
            or item.elapsed_ms < 0
            or item.elapsed_ms < previous_elapsed
            or item.elapsed_ms > observation.elapsed_ms
        ):
            raise ProgressPayloadInvalid("event timing is invalid")
        previous_elapsed = item.elapsed_ms


def _valid_identifier(value: Any) -> str | None:
    if isinstance(value, str) and value and len(value) <= 512:
        return value
    return None


def _valid_progress_value(value: Any, *, minimum: int) -> int | None:
    if type(value) is int and minimum <= value <= MAX_PROGRESS_VALUE:
        return value
    return None


def _queue_remaining(data: dict[str, Any]) -> int | None:
    status = data.get("status")
    if not isinstance(status, dict):
        return None
    exec_info = status.get("exec_info")
    if not isinstance(exec_info, dict):
        return None
    return _valid_progress_value(exec_info.get("queue_remaining"), minimum=0)


def _next_steps(decision: str) -> list[str]:
    return {
        "observing": ["Retry a bounded live observation or pair it with a queue snapshot."],
        "idle": ["The observed queue is idle; a real submit still needs explicit confirmation."],
        "queued": ["Wait for queue capacity before considering another guarded submit."],
        "running": ["Continue bounded observation; do not infer completion from queue depth."],
        "stalled": ["Review the local ComfyUI session before any separately confirmed cancel."],
        "completed": ["Record the terminal status without reading private outputs or history."],
        "failed": [
            "Inspect ComfyUI manually; this safe summary omits exception and traceback text."
        ],
        "interrupted": ["Confirm the interruption was expected before retrying the workflow."],
    }[decision]


def _process_observation(
    observation: ProgressRead,
    *,
    target_job_id: str | None,
    stall_after_seconds: int,
) -> dict[str, Any]:
    active_job_id = target_job_id
    active_node_id: str | None = None
    progress_node_id: str | None = None
    queue_remaining: int | None = None
    current: int | None = None
    total: int | None = None
    accepted_events = 0
    ignored_events = 0
    duplicate_progress_events = 0
    progress_regressions = 0
    last_advance_ms: int | None = None
    running_seen = False
    terminal = False
    terminal_decision: str | None = None
    unknown_events_ignored = False
    legacy_completion = False

    known_job_events = {
        "execution_start",
        "executing",
        "progress",
        "executed",
        "execution_cached",
        "execution_success",
        "execution_error",
        "execution_interrupted",
    }

    for observed in observation.frames:
        payload = observed.payload
        if not isinstance(payload, dict):
            ignored_events += 1
            unknown_events_ignored = True
            continue
        event_type = payload.get("type")
        data = payload.get("data")
        if event_type == "status" and isinstance(data, dict):
            safe_queue_remaining = _queue_remaining(data)
            if safe_queue_remaining is None:
                ignored_events += 1
                unknown_events_ignored = True
            else:
                queue_remaining = safe_queue_remaining
                accepted_events += 1
            continue
        if event_type not in known_job_events or not isinstance(data, dict):
            ignored_events += 1
            unknown_events_ignored = True
            continue

        event_job_id = _valid_identifier(data.get("prompt_id"))
        if event_job_id is None:
            ignored_events += 1
            unknown_events_ignored = True
            continue
        if active_job_id is None:
            active_job_id = event_job_id
        elif event_job_id != active_job_id:
            ignored_events += 1
            continue
        if terminal:
            ignored_events += 1
            continue

        if event_type == "execution_start":
            accepted_events += 1
            running_seen = True
            last_advance_ms = observed.elapsed_ms
            continue

        if event_type == "executing":
            node = data.get("node")
            if node is None:
                accepted_events += 1
                terminal = True
                terminal_decision = "completed"
                last_advance_ms = observed.elapsed_ms
                legacy_completion = True
                continue
            safe_node_id = _valid_identifier(node)
            if safe_node_id is None:
                ignored_events += 1
                unknown_events_ignored = True
                continue
            accepted_events += 1
            running_seen = True
            if safe_node_id != active_node_id:
                active_node_id = safe_node_id
                progress_node_id = safe_node_id
                current = None
                total = None
                last_advance_ms = observed.elapsed_ms
            continue

        if event_type == "progress":
            safe_current = _valid_progress_value(data.get("value"), minimum=0)
            safe_total = _valid_progress_value(data.get("max"), minimum=1)
            if safe_current is None or safe_total is None or safe_current > safe_total:
                ignored_events += 1
                unknown_events_ignored = True
                continue
            accepted_events += 1
            running_seen = True
            safe_node_id = _valid_identifier(data.get("node"))
            if safe_node_id is not None and safe_node_id != active_node_id:
                active_node_id = safe_node_id
                progress_node_id = safe_node_id
                current = None
                total = None
                last_advance_ms = observed.elapsed_ms
            elif safe_node_id is not None and progress_node_id != safe_node_id:
                progress_node_id = safe_node_id
                current = None
                total = None
            if current is not None and safe_current < current:
                progress_regressions += 1
                continue
            if current == safe_current and total == safe_total:
                duplicate_progress_events += 1
                continue
            current = safe_current
            total = safe_total
            last_advance_ms = observed.elapsed_ms
            continue

        if event_type in {"executed", "execution_cached"}:
            accepted_events += 1
            running_seen = True
            safe_node_id = _valid_identifier(data.get("node"))
            if safe_node_id is not None:
                active_node_id = safe_node_id
            last_advance_ms = observed.elapsed_ms
            continue

        accepted_events += 1
        terminal = True
        last_advance_ms = observed.elapsed_ms
        terminal_decision = {
            "execution_success": "completed",
            "execution_error": "failed",
            "execution_interrupted": "interrupted",
        }[event_type]

    decision = terminal_decision
    if decision is None:
        if running_seen:
            decision = "running"
        elif queue_remaining is None:
            decision = "observing"
        elif queue_remaining > 0:
            decision = "queued"
        else:
            decision = "idle"

    stalled = False
    stalled_for_ms: int | None = None
    if decision == "running" and last_advance_ms is not None:
        inactive_ms = max(0, observation.elapsed_ms - last_advance_ms)
        if inactive_ms >= stall_after_seconds * 1_000:
            decision = "stalled"
            stalled = True
            stalled_for_ms = inactive_ms

    warnings: list[str] = []
    if progress_regressions:
        warnings.append("progress_regression_ignored")
    if legacy_completion:
        warnings.append("legacy_completion_event")
    if observation.binary_events_ignored:
        warnings.append("binary_preview_ignored")
    if unknown_events_ignored:
        warnings.append("unknown_events_ignored")

    progress = _empty_progress()
    if current is not None and total is not None:
        progress = {
            "available": True,
            "source": "websocket",
            "scope": "current_node",
            "current": current,
            "total": total,
            "percent": round(current * 100 / total, 2),
            "monotonic": True,
        }

    logical_job_id = _logical_id("job", active_job_id) if active_job_id is not None else None
    logical_node_id = _logical_id("node", active_node_id) if active_node_id is not None else None
    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "bridge": "comfyui",
        "action": "progress_monitor",
        "endpoint": "/ws",
        "mode": "live",
        "connected": True,
        "decision": decision,
        "logical_job_id": logical_job_id,
        "logical_node_id": logical_node_id,
        "queue_remaining": queue_remaining,
        "progress": progress,
        "monitor": {
            "received_events": len(observation.frames) + observation.binary_events_ignored,
            "accepted_events": accepted_events,
            "ignored_events": ignored_events,
            "binary_events_ignored": observation.binary_events_ignored,
            "duplicate_progress_events": duplicate_progress_events,
            "progress_regressions": progress_regressions,
            "elapsed_ms": observation.elapsed_ms,
            "stalled": stalled,
            "stalled_for_ms": stalled_for_ms,
            "terminal": terminal,
        },
        "error_code": None,
        "warnings": warnings,
        "redactions_applied": active_job_id is not None or active_node_id is not None,
        "safety": _safety(network_access=True),
        "next_steps": _next_steps(decision),
    }


def progress_monitor_contract() -> dict[str, Any]:
    return {
        "tool": "comfyui.progress_monitor",
        "schema_version": SCHEMA_VERSION,
        "endpoint": "/ws",
        "default_connect": False,
        "live_scope": "direct_loopback_websocket_only",
        "proxy_used": False,
        "redirects_followed": False,
        "binary_payloads_ignored": True,
        "raw_identifiers_returned": False,
        "workflow_payloads_returned": False,
        "history_read": False,
        "queue_mutation": False,
    }


def _unavailable_result(
    *,
    error_code: str,
    warning: str,
    target_job_id: str | None,
    network_access: bool,
) -> dict[str, Any]:
    return {
        "ok": False,
        "schema_version": SCHEMA_VERSION,
        "bridge": "comfyui",
        "action": "progress_monitor",
        "endpoint": "/ws",
        "mode": "live",
        "connected": False,
        "decision": "unavailable",
        "logical_job_id": (
            _logical_id("job", target_job_id) if target_job_id is not None else None
        ),
        "logical_node_id": None,
        "queue_remaining": None,
        "progress": _empty_progress(),
        "monitor": _empty_monitor(),
        "error_code": error_code,
        "warnings": [warning],
        "redactions_applied": target_job_id is not None,
        "safety": _safety(network_access=network_access),
        "next_steps": [
            "Check the local ComfyUI session and retry without widening the loopback boundary."
        ],
    }


def build_progress_monitor(
    *,
    connect: bool = False,
    comfy_url: str = DEFAULT_COMFY_URL,
    listen_seconds: int = 5,
    stall_after_seconds: int = 5,
    max_events: int = 100,
    target_job_id: str | None = None,
    event_reader: EventReader | None = None,
) -> dict[str, Any]:
    if type(connect) is not bool:
        raise ValueError("connect must be boolean")
    if type(listen_seconds) is not int or not 1 <= listen_seconds <= 30:
        raise ValueError("listen_seconds must be an integer between 1 and 30")
    if type(stall_after_seconds) is not int or not 1 <= stall_after_seconds <= 300:
        raise ValueError("stall_after_seconds must be an integer between 1 and 300")
    if type(max_events) is not int or not 1 <= max_events <= 500:
        raise ValueError("max_events must be an integer between 1 and 500")
    if target_job_id is not None and _valid_identifier(target_job_id) is None:
        raise ValueError("target_job_id must be a non-empty string of at most 512 characters")
    base_url = _validate_loopback_url(comfy_url)

    if not connect:
        return _finalize(
            {
                "ok": True,
                "schema_version": SCHEMA_VERSION,
                "bridge": "comfyui",
                "action": "progress_monitor",
                "endpoint": "/ws",
                "mode": "planned",
                "connected": False,
                "decision": "planned",
                "logical_job_id": (
                    _logical_id("job", target_job_id) if target_job_id is not None else None
                ),
                "logical_node_id": None,
                "queue_remaining": None,
                "progress": _empty_progress(),
                "monitor": _empty_monitor(),
                "error_code": None,
                "warnings": ["live_progress_not_connected"],
                "redactions_applied": target_job_id is not None,
                "safety": _safety(network_access=False),
                "next_steps": [
                    "Call again with connect=true for one bounded loopback observation window."
                ],
            }
        )

    reader = event_reader or _read_live_events
    try:
        observation = reader(base_url, listen_seconds, max_events, target_job_id)
        _validate_read(observation, max_events=max_events)
        result = _process_observation(
            observation,
            target_job_id=target_job_id,
            stall_after_seconds=stall_after_seconds,
        )
    except ProgressDependencyUnavailable:
        result = _unavailable_result(
            error_code="websocket_dependency_unavailable",
            warning="websocket_dependency_missing",
            target_job_id=target_job_id,
            network_access=False,
        )
    except (ProgressPayloadInvalid, TypeError, ValueError, json.JSONDecodeError):
        result = _unavailable_result(
            error_code="progress_event_payload_invalid",
            warning="progress_event_payload_rejected",
            target_job_id=target_job_id,
            network_access=True,
        )
    except (OSError, TimeoutError):
        result = _unavailable_result(
            error_code="websocket_endpoint_unavailable",
            warning="loopback_websocket_unavailable",
            target_job_id=target_job_id,
            network_access=True,
        )
    return _finalize(result)
