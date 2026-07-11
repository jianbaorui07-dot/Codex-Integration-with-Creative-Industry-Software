from __future__ import annotations

import argparse
import json
import mimetypes
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
from uuid import uuid4

from starbridge_mcp.core.security import sanitize
from starbridge_mcp.mcp_server import SERVER_INFO, handle_request

JsonObject = dict[str, Any]
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATIC_ROOT = REPO_ROOT / "examples" / "starbridge_frontend" / "dist"
DEFAULT_HISTORY_PATH = REPO_ROOT / "examples" / "output" / "app_history" / "history.json"

CATALOG_BRIDGE_TIERS: dict[str, dict[str, str]] = {
    "photoshop": {
        "tier": "Pro",
        "price_signal": "Paid recipe pack",
        "buyer": "E-commerce retouching and brand design teams",
    },
    "comfyui": {
        "tier": "Compute",
        "price_signal": "Credits or GPU minutes",
        "buyer": "AI image generation studios",
    },
    "autocad_dxf": {
        "tier": "Studio",
        "price_signal": "Per-seat or project pack",
        "buyer": "CAD drafting and manufacturing teams",
    },
    "illustrator": {
        "tier": "Pro",
        "price_signal": "Vector workflow pack",
        "buyer": "Packaging and illustration teams",
    },
    "blender": {
        "tier": "Studio",
        "price_signal": "Scene automation pack",
        "buyer": "3D product visualization teams",
    },
}

PRODUCT_TIERS: list[JsonObject] = [
    {
        "id": "free",
        "name": "Free",
        "audience": "Developers and integration testers",
        "included": [
            "Local backend",
            "safe capability discovery",
            "dry-run recipe plan",
            "Evidence preview",
        ],
        "limits": ["No cloud queue", "No shared team history", "Sandbox output only"],
    },
    {
        "id": "pro",
        "name": "Pro",
        "audience": "Individual creators",
        "included": [
            "Photoshop and Illustrator recipe packs",
            "local audit history",
            "confirmed sandbox runs",
        ],
        "limits": ["Single local workstation", "Cloud compute billed separately"],
    },
    {
        "id": "team",
        "name": "Team",
        "audience": "Studios and company teams",
        "included": [
            "Studio recipe packs",
            "shared approval workflow",
            "cloud GPU lane",
            "admin policy",
        ],
        "limits": ["Requires organization policy and billing setup"],
    },
]

HYBRID_EXECUTION: JsonObject = {
    "architecture_version": "starbridge.hybrid.v1",
    "policy": "Desktop software stays local; GPU generation may use a metered cloud lane after explicit confirmation.",
    "lanes": [
        {
            "id": "local_desktop",
            "label": "Local desktop lane",
            "bridges": ["photoshop", "illustrator", "blender", "autocad_dxf", "jianying_capcut"],
            "execution_target": "local",
            "billing_unit": "seat",
            "safety": "Never uploads PSD, AI, DWG, blend, video drafts, or local project files.",
        },
        {
            "id": "cloud_gpu",
            "label": "Cloud GPU lane",
            "bridges": ["comfyui"],
            "execution_target": "cloud",
            "billing_unit": "credits_or_gpu_minutes",
            "safety": "Only public prompts, reviewed workflow JSON, and redacted asset manifests may be queued.",
        },
    ],
}


@dataclass(frozen=True)
class BackendResponse:
    status: int
    body: JsonObject | bytes
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str = "application/json; charset=utf-8"


class StarBridgeBackend:
    """Small REST facade over the existing StarBridge MCP handlers."""

    def __init__(self, static_root: Path | None = None, history_path: Path | None = None) -> None:
        self._next_id = 1
        self.static_root = static_root or DEFAULT_STATIC_ROOT
        self.history_path = history_path or DEFAULT_HISTORY_PATH

    def _request_id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def _mcp(self, method: str, params: JsonObject | None = None) -> BackendResponse:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": self._request_id(),
                "method": method,
                "params": params or {},
            }
        )
        if response is None:
            return BackendResponse(204, {"ok": True})
        if "error" in response:
            code = int(response["error"].get("code") or -32603)
            status = 404 if code == -32601 else 400
            return BackendResponse(status, sanitize({"ok": False, "error": response["error"]}))
        return BackendResponse(200, sanitize({"ok": True, "data": response.get("result", {})}))

    def _tool(self, name: str, arguments: JsonObject | None = None) -> BackendResponse:
        response = self._mcp("tools/call", {"name": name, "arguments": arguments or {}})
        if response.status != 200:
            return response
        result = response.body.get("data", {})
        if not isinstance(result, dict):
            return BackendResponse(500, {"ok": False, "error": "invalid tool result"})
        payload = result.get("structuredContent", result)
        is_error = bool(result.get("isError", False))
        status = 400 if is_error else 200
        return BackendResponse(status, sanitize({"ok": not is_error, "data": payload}))

    @staticmethod
    def _one(query: dict[str, list[str]], key: str, default: str | None = None) -> str | None:
        values = query.get(key)
        return values[0] if values else default

    @staticmethod
    def _bool(query: dict[str, list[str]], key: str, default: bool = False) -> bool:
        value = StarBridgeBackend._one(query, key)
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "y", "on"}

    @staticmethod
    def _json_body(raw_body: bytes) -> JsonObject:
        if not raw_body:
            return {}
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _static(self, path: str) -> BackendResponse:
        static_root = self.static_root.resolve()
        if not static_root.exists():
            return BackendResponse(
                404,
                {
                    "ok": False,
                    "error": "frontend build not found",
                    "next_steps": [
                        "Run `npm.cmd --prefix examples\\starbridge_frontend run build`."
                    ],
                },
            )

        relative = unquote(path.lstrip("/")) or "index.html"
        target = (static_root / relative).resolve()
        if target == static_root or target.is_dir():
            target = target / "index.html"
        if static_root not in (target, *target.parents):
            return BackendResponse(403, {"ok": False, "error": "static path escapes frontend root"})
        if not target.exists():
            target = static_root / "index.html"
        if not target.exists():
            return BackendResponse(404, {"ok": False, "error": "frontend index.html not found"})

        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or target.suffix in {".js", ".css", ".svg"}:
            content_type = f"{content_type}; charset=utf-8"
        return BackendResponse(200, target.read_bytes(), content_type=content_type)

    def _load_history(self) -> list[JsonObject]:
        if not self.history_path.exists():
            return []
        try:
            payload = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        return [item for item in payload if isinstance(item, dict)]

    def _save_history(self, events: list[JsonObject]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(
            json.dumps(sanitize(events[-100:]), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _record_recipe_event(
        self, *, recipe_id: str, action: str, result: JsonObject
    ) -> JsonObject:
        quality_gates = (
            result.get("plan", {}).get("quality_gates", [])
            if isinstance(result.get("plan"), dict)
            else result.get("manifest", {}).get("quality_gates", [])
            if isinstance(result.get("manifest"), dict)
            else result.get("quality_gates", [])
            if isinstance(result.get("quality_gates"), list)
            else []
        )
        event = sanitize(
            {
                "event_id": f"evt_{uuid4().hex[:12]}",
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "kind": "recipe_action",
                "recipe_id": recipe_id,
                "bridge": result.get("bridge"),
                "action": action,
                "ok": bool(result.get("ok", False)),
                "status": "completed" if result.get("ok") else "failed",
                "evidence_ready": action in {"evidence", "run"} or "manifest" in result,
                "quality_gate_count": len(quality_gates),
                "execution_target": result.get("execution_target"),
                "summary": result.get("result_summary"),
            }
        )
        events = self._load_history()
        events.append(event)
        self._save_history(events)
        return event

    @staticmethod
    def _catalog_card(recipe: JsonObject) -> JsonObject:
        bridge = str(recipe.get("bridge") or "unknown")
        tier = CATALOG_BRIDGE_TIERS.get(
            bridge,
            {
                "tier": "Core",
                "price_signal": "Included workflow",
                "buyer": "Creative operators",
            },
        )
        gates = recipe.get("quality_gates", [])
        return sanitize(
            {
                "sku": f"starbridge.recipe.{recipe.get('recipe_id')}",
                "recipe_id": recipe.get("recipe_id"),
                "bridge": bridge,
                "title": str(recipe.get("recipe_id") or "recipe").replace("_", " ").title(),
                "goal": recipe.get("goal"),
                "tier": tier["tier"],
                "price_signal": tier["price_signal"],
                "buyer": tier["buyer"],
                "safe_default": bool(recipe.get("safe_default", True)),
                "writes": bool(recipe.get("writes", False)),
                "quality_gates": gates if isinstance(gates, list) else [],
                "install_state": "bundled",
            }
        )

    def _catalog(self) -> BackendResponse:
        response = self._tool("starbridge.recipe_list", {"bridge": "all"})
        if response.status != 200:
            return response
        data = response.body.get("data", {})
        recipes = data.get("recipes", []) if isinstance(data, dict) else []
        cards = [self._catalog_card(recipe) for recipe in recipes if isinstance(recipe, dict)]
        return BackendResponse(
            200,
            {
                "ok": True,
                "data": {
                    "catalog_version": "starbridge.catalog.v1",
                    "item_count": len(cards),
                    "items": cards,
                    "monetization_model": [
                        "Core recipes stay bundled for discovery.",
                        "Pro and Studio recipe packs can be licensed per user or per team.",
                        "Compute recipes can later attach credit or GPU-minute billing.",
                    ],
                },
            },
        )

    @staticmethod
    def _tiers() -> BackendResponse:
        return BackendResponse(
            200,
            {
                "ok": True,
                "data": {
                    "tiers_version": "starbridge.tiers.v1",
                    "tiers": PRODUCT_TIERS,
                },
            },
        )

    @staticmethod
    def _hybrid() -> BackendResponse:
        return BackendResponse(
            200,
            {
                "ok": True,
                "data": HYBRID_EXECUTION,
            },
        )

    @staticmethod
    def _lane_for_bridge(bridge: str, execution_target: str) -> JsonObject | None:
        for lane in HYBRID_EXECUTION["lanes"]:
            if execution_target == lane["execution_target"] and bridge in lane["bridges"]:
                return lane
        return None

    def _run_recipe(self, recipe_id: str, body: JsonObject) -> BackendResponse:
        if not bool(body.get("confirm_run", False)):
            return BackendResponse(
                400,
                {
                    "ok": False,
                    "error": "confirm_run=true is required before a recipe run can be recorded",
                    "required_sequence": ["plan", "evidence", "confirm_run", "run"],
                },
            )

        plan_response = self._tool(
            "starbridge.recipe_plan", {"recipe_id": recipe_id, "dry_run": True}
        )
        if plan_response.status != 200:
            return plan_response
        plan_data = plan_response.body.get("data", {})
        if not isinstance(plan_data, dict) or not plan_data.get("ok"):
            return BackendResponse(404, {"ok": False, "error": "unknown recipe_id"})

        bridge = str(plan_data.get("bridge") or "unknown")
        requested_target = str(
            body.get("execution_target") or ("cloud" if bridge == "comfyui" else "local")
        )
        lane = self._lane_for_bridge(bridge, requested_target)
        if lane is None:
            return BackendResponse(
                400,
                {
                    "ok": False,
                    "error": f"{bridge} does not support execution_target={requested_target}",
                    "hybrid": HYBRID_EXECUTION,
                },
            )

        plan = plan_data.get("plan", {}) if isinstance(plan_data.get("plan"), dict) else {}
        quality_gates = (
            plan.get("quality_gates", []) if isinstance(plan.get("quality_gates"), list) else []
        )
        result = sanitize(
            {
                "ok": True,
                "bridge": bridge,
                "action": "recipe_run",
                "recipe_id": recipe_id,
                "status": "completed",
                "dry_run": True,
                "confirm_run": True,
                "execution_target": requested_target,
                "execution_lane": lane["id"],
                "result_summary": "Confirmed run recorded as a safe dry-run execution request.",
                "tool_sequence": plan.get("action_plan", {}).get("tool_sequence", []),
                "quality_gates": quality_gates,
                "outputs": [
                    {
                        "label": "execution_report",
                        "materialized": False,
                        "reason": "Backend does not launch desktop software from this product UI.",
                    }
                ],
                "billing_preview": {
                    "unit": lane["billing_unit"],
                    "billable": requested_target == "cloud",
                    "metered_quantity": 0,
                },
                "next_steps": [
                    "Review the recorded event in Audit.",
                    "Use bridge-specific confirmed tools for real sandbox output.",
                ],
            }
        )
        event = self._record_recipe_event(recipe_id=recipe_id, action="run", result=result)
        return BackendResponse(200, {"ok": True, "data": result, "event": event})

    def route(self, method: str, target: str, raw_body: bytes = b"") -> BackendResponse:
        parsed = urlparse(target)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        method = method.upper()

        try:
            body = self._json_body(raw_body)
        except ValueError as exc:
            return BackendResponse(400, {"ok": False, "error": str(exc)})

        if method == "OPTIONS":
            return BackendResponse(204, {"ok": True})

        if method == "GET" and path == "/api/health":
            return BackendResponse(
                200,
                {
                    "ok": True,
                    "service": "starbridge-backend",
                    "server": SERVER_INFO,
                },
            )

        if method == "GET" and path == "/api/status":
            arguments: JsonObject = {
                "bridge": self._one(query, "bridge", "all"),
                "probe_executables": self._bool(query, "probe_executables", False),
            }
            if timeout := self._one(query, "timeout"):
                try:
                    arguments["timeout"] = int(timeout)
                except ValueError:
                    return BackendResponse(
                        400, {"ok": False, "error": "timeout must be an integer"}
                    )
            return self._tool("starbridge.status", arguments)

        if method == "GET" and path == "/api/capabilities":
            return self._tool(
                "starbridge.tools",
                {
                    "bridge": self._one(query, "bridge", "all"),
                    "safe_only": self._bool(query, "safe_only", False),
                },
            )

        if method == "GET" and path == "/api/tools":
            return self._mcp("tools/list")

        if method == "GET" and path == "/api/resources":
            return self._mcp("resources/list")

        if method == "GET" and path == "/api/resource":
            uri = self._one(query, "uri")
            if not uri:
                return BackendResponse(
                    400, {"ok": False, "error": "query parameter uri is required"}
                )
            return self._mcp("resources/read", {"uri": uri})

        if method == "GET" and path == "/api/recipes":
            return self._tool(
                "starbridge.recipe_list", {"bridge": self._one(query, "bridge", "all")}
            )

        if method == "GET" and path == "/api/catalog":
            return self._catalog()

        if method == "GET" and path == "/api/tiers":
            return self._tiers()

        if method == "GET" and path == "/api/hybrid":
            return self._hybrid()

        if method == "GET" and path == "/api/audit/history":
            events = list(reversed(self._load_history()))
            limit = self._one(query, "limit")
            if limit:
                try:
                    events = events[: max(0, int(limit))]
                except ValueError:
                    return BackendResponse(400, {"ok": False, "error": "limit must be an integer"})
            return BackendResponse(
                200,
                {
                    "ok": True,
                    "data": {
                        "history_version": "starbridge.audit.v1",
                        "event_count": len(events),
                        "events": events,
                    },
                },
            )

        if method == "DELETE" and path == "/api/audit/history":
            self._save_history([])
            return BackendResponse(
                200,
                {
                    "ok": True,
                    "data": {
                        "history_version": "starbridge.audit.v1",
                        "event_count": 0,
                        "events": [],
                    },
                },
            )

        if method == "GET" and path == "/api/bootstrap":
            capabilities = self._tool("starbridge.tools", {"safe_only": True})
            recipes = self._tool("starbridge.recipe_list", {"bridge": "all"})
            catalog = self._catalog()
            tiers = self._tiers()
            hybrid = self._hybrid()
            safe_roots = self._tool("starbridge.safe_roots", {"bridge": "all"})
            resources = self._mcp("resources/list")
            responses = [capabilities, recipes, catalog, tiers, hybrid, safe_roots, resources]
            if any(response.status != 200 for response in responses):
                return BackendResponse(
                    500,
                    {
                        "ok": False,
                        "error": "bootstrap failed",
                        "responses": [response.body for response in responses],
                    },
                )
            history = self._load_history()
            return BackendResponse(
                200,
                {
                    "ok": True,
                    "data": {
                        "server": SERVER_INFO,
                        "capabilities": capabilities.body["data"],
                        "recipes": recipes.body["data"],
                        "catalog": catalog.body["data"],
                        "tiers": tiers.body["data"],
                        "hybrid": hybrid.body["data"],
                        "history": {
                            "history_version": "starbridge.audit.v1",
                            "event_count": len(history),
                            "events": list(reversed(history)),
                        },
                        "safe_roots": safe_roots.body["data"],
                        "resources": resources.body["data"],
                    },
                },
            )

        if path.startswith("/api/recipes/"):
            parts = [unquote(part) for part in path.split("/") if part]
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "recipes":
                recipe_id, action = parts[2], parts[3]
                arguments = dict(body)
                arguments["recipe_id"] = recipe_id
                if action == "plan" and method in {"GET", "POST"}:
                    response = self._tool("starbridge.recipe_plan", arguments)
                    if response.status == 200 and isinstance(response.body.get("data"), dict):
                        event = self._record_recipe_event(
                            recipe_id=recipe_id, action="plan", result=response.body["data"]
                        )
                        response.body["event"] = event
                    return response
                if action == "evidence" and method in {"GET", "POST"}:
                    response = self._tool("starbridge.recipe_evidence", arguments)
                    if response.status == 200 and isinstance(response.body.get("data"), dict):
                        event = self._record_recipe_event(
                            recipe_id=recipe_id, action="evidence", result=response.body["data"]
                        )
                        response.body["event"] = event
                    return response
                if action == "run" and method == "POST":
                    return self._run_recipe(recipe_id, body)

        if method == "POST" and path == "/api/tools/call":
            name = body.get("name")
            arguments = body.get("arguments") or {}
            if not isinstance(name, str):
                return BackendResponse(400, {"ok": False, "error": "body.name must be a string"})
            if not isinstance(arguments, dict):
                return BackendResponse(
                    400, {"ok": False, "error": "body.arguments must be an object"}
                )
            return self._tool(name, arguments)

        if method == "GET" and not path.startswith("/api/"):
            return self._static(path)

        return BackendResponse(404, {"ok": False, "error": f"unknown route: {method} {path}"})


def _send(
    handler: BaseHTTPRequestHandler, response: BackendResponse, *, write_body: bool = True
) -> None:
    body = (
        b""
        if response.status == 204
        else response.body
        if isinstance(response.body, bytes)
        else json.dumps(sanitize(response.body), ensure_ascii=False, indent=2).encode("utf-8")
    )
    handler.send_response(response.status)
    handler.send_header("Content-Type", response.content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    for name, value in response.headers.items():
        handler.send_header(name, value)
    handler.end_headers()
    if write_body and response.status != 204:
        handler.wfile.write(body)


def make_handler(backend: StarBridgeBackend) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self) -> None:  # noqa: N802
            _send(self, backend.route("OPTIONS", self.path))

        def do_GET(self) -> None:  # noqa: N802
            _send(self, backend.route("GET", self.path))

        def do_HEAD(self) -> None:  # noqa: N802
            _send(self, backend.route("GET", self.path), write_body=False)

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            _send(self, backend.route("POST", self.path, self.rfile.read(length)))

        def do_DELETE(self) -> None:  # noqa: N802
            _send(self, backend.route("DELETE", self.path))

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    backend = StarBridgeBackend()
    server = ThreadingHTTPServer((host, port), make_handler(backend))
    print(f"StarBridge backend listening on http://{host}:{port}", flush=True)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the StarBridge local HTTP backend.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
