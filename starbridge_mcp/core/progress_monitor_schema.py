from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "starbridge.progress-monitor.v1"
SNAPSHOT_ID_PATTERN = r"^progress_[0-9a-f]{12}$"
LOGICAL_JOB_ID_PATTERN = r"^job_[0-9a-f]{12}$"
LOGICAL_NODE_ID_PATTERN = r"^node_[0-9a-f]{12}$"
MAX_PROGRESS_VALUE = 1_000_000

DECISIONS = (
    "planned",
    "unavailable",
    "observing",
    "idle",
    "queued",
    "running",
    "stalled",
    "completed",
    "failed",
    "interrupted",
)

PROGRESS_MONITOR_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "connect": {
            "type": "boolean",
            "default": False,
            "description": "显式允许只读连接 loopback ComfyUI /ws；默认只返回计划。",
        },
        "comfy_url": {
            "type": "string",
            "maxLength": 128,
            "default": "http://127.0.0.1:8188",
            "description": "只允许无账号、query、fragment 或额外路径的 loopback HTTP URL。",
        },
        "listen_seconds": {
            "type": "integer",
            "minimum": 1,
            "maximum": 30,
            "default": 5,
        },
        "stall_after_seconds": {
            "type": "integer",
            "minimum": 1,
            "maximum": 300,
            "default": 5,
        },
        "max_events": {
            "type": "integer",
            "minimum": 1,
            "maximum": 500,
            "default": 100,
        },
        "target_job_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 512,
            "description": "可选原始 prompt_id；仅用于内存匹配，不会回显。",
        },
    },
    "additionalProperties": False,
}

PROGRESS_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "available": {"type": "boolean"},
        "source": {"type": "string", "enum": ["not_available", "websocket"]},
        "scope": {"type": "string", "const": "current_node"},
        "current": {"type": ["integer", "null"], "minimum": 0},
        "total": {"type": ["integer", "null"], "minimum": 1},
        "percent": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
        "monotonic": {"type": "boolean"},
    },
    "required": [
        "available",
        "source",
        "scope",
        "current",
        "total",
        "percent",
        "monotonic",
    ],
    "additionalProperties": False,
}

MONITOR_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "received_events": {"type": "integer", "minimum": 0},
        "accepted_events": {"type": "integer", "minimum": 0},
        "ignored_events": {"type": "integer", "minimum": 0},
        "binary_events_ignored": {"type": "integer", "minimum": 0},
        "duplicate_progress_events": {"type": "integer", "minimum": 0},
        "progress_regressions": {"type": "integer", "minimum": 0},
        "elapsed_ms": {"type": "integer", "minimum": 0},
        "stalled": {"type": "boolean"},
        "stalled_for_ms": {"type": ["integer", "null"], "minimum": 0},
        "terminal": {"type": "boolean"},
    },
    "required": [
        "received_events",
        "accepted_events",
        "ignored_events",
        "binary_events_ignored",
        "duplicate_progress_events",
        "progress_regressions",
        "elapsed_ms",
        "stalled",
        "stalled_for_ms",
        "terminal",
    ],
    "additionalProperties": False,
}

SAFETY_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        field: {"type": "boolean"}
        for field in (
            "network_access",
            "loopback_only",
            "proxy_used",
            "redirects_followed",
            "binary_payloads_ignored",
            "workflow_payloads_returned",
            "raw_job_ids_returned",
            "raw_node_ids_returned",
            "history_read",
            "queue_mutation",
            "local_file_reads",
            "local_file_writes",
            "desktop_software_started",
        )
    },
    "required": [
        "network_access",
        "loopback_only",
        "proxy_used",
        "redirects_followed",
        "binary_payloads_ignored",
        "workflow_payloads_returned",
        "raw_job_ids_returned",
        "raw_node_ids_returned",
        "history_read",
        "queue_mutation",
        "local_file_reads",
        "local_file_writes",
        "desktop_software_started",
    ],
    "additionalProperties": False,
}

PROGRESS_MONITOR_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "schema_version": {"type": "string", "const": SCHEMA_VERSION},
        "snapshot_id": {"type": "string", "pattern": SNAPSHOT_ID_PATTERN},
        "bridge": {"type": "string", "const": "comfyui"},
        "action": {"type": "string", "const": "progress_monitor"},
        "endpoint": {"type": "string", "const": "/ws"},
        "mode": {"type": "string", "enum": ["planned", "live"]},
        "connected": {"type": "boolean"},
        "decision": {"type": "string", "enum": list(DECISIONS)},
        "logical_job_id": {
            "type": ["string", "null"],
            "pattern": LOGICAL_JOB_ID_PATTERN,
        },
        "logical_node_id": {
            "type": ["string", "null"],
            "pattern": LOGICAL_NODE_ID_PATTERN,
        },
        "queue_remaining": {
            "type": ["integer", "null"],
            "minimum": 0,
            "maximum": MAX_PROGRESS_VALUE,
        },
        "progress": PROGRESS_OUTPUT_SCHEMA,
        "monitor": MONITOR_OUTPUT_SCHEMA,
        "error_code": {
            "type": ["string", "null"],
            "enum": [
                None,
                "websocket_dependency_unavailable",
                "websocket_endpoint_unavailable",
                "progress_event_payload_invalid",
            ],
        },
        "warnings": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "live_progress_not_connected",
                    "websocket_dependency_missing",
                    "loopback_websocket_unavailable",
                    "progress_event_payload_rejected",
                    "progress_regression_ignored",
                    "legacy_completion_event",
                    "binary_preview_ignored",
                    "unknown_events_ignored",
                ],
            },
            "uniqueItems": True,
        },
        "redactions_applied": {"type": "boolean"},
        "safety": SAFETY_OUTPUT_SCHEMA,
        "next_steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "ok",
        "schema_version",
        "snapshot_id",
        "bridge",
        "action",
        "endpoint",
        "mode",
        "connected",
        "decision",
        "logical_job_id",
        "logical_node_id",
        "queue_remaining",
        "progress",
        "monitor",
        "error_code",
        "warnings",
        "redactions_applied",
        "safety",
        "next_steps",
    ],
    "additionalProperties": False,
}
