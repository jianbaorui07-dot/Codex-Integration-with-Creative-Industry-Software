from __future__ import annotations

import json
import sys
import types
import unittest
from unittest.mock import patch

from starbridge_mcp.core.control_planner import build_control_plan
from starbridge_mcp.core.progress_monitor import (
    ObservedFrame,
    ProgressDependencyUnavailable,
    ProgressRead,
    _read_live_events,
    build_progress_monitor,
)
from starbridge_mcp.core.progress_monitor_schema import SCHEMA_VERSION
from starbridge_mcp.core.tool_registry import list_capabilities
from starbridge_mcp.mcp_server import TOOL_DEFINITIONS, handle_request

RAW_JOB_ID = "9f5f84f8-private-prompt-id"
RAW_NODE_ID = "private-node-17"


def frame(elapsed_ms: int, event_type: str, data: dict) -> ObservedFrame:
    return ObservedFrame(elapsed_ms=elapsed_ms, payload={"type": event_type, "data": data})


def read(*frames: ObservedFrame, elapsed_ms: int, binary: int = 0) -> ProgressRead:
    return ProgressRead(
        frames=list(frames),
        elapsed_ms=elapsed_ms,
        binary_events_ignored=binary,
    )


class ProgressMonitorTests(unittest.TestCase):
    def test_default_is_plan_only_without_loading_live_reader(self) -> None:
        def fail_if_called(
            _url: str, _seconds: int, _events: int, _job: str | None
        ) -> ProgressRead:
            raise AssertionError("live event reader must not run")

        result = build_progress_monitor(event_reader=fail_if_called)

        self.assertTrue(result["ok"])
        self.assertEqual("planned", result["mode"])
        self.assertEqual("planned", result["decision"])
        self.assertFalse(result["connected"])
        self.assertFalse(result["safety"]["network_access"])
        self.assertFalse(result["progress"]["available"])

    def test_live_events_are_monotonic_and_private_payloads_are_omitted(self) -> None:
        private_path = "C:\\Users\\private\\Desktop\\result.png"
        observed = read(
            frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
            frame(100, "executing", {"prompt_id": RAW_JOB_ID, "node": RAW_NODE_ID}),
            frame(
                200,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": RAW_NODE_ID, "value": 2, "max": 10},
            ),
            frame(
                300,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": RAW_NODE_ID, "value": 2, "max": 10},
            ),
            frame(
                400,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": RAW_NODE_ID, "value": 1, "max": 10},
            ),
            frame(
                500,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": RAW_NODE_ID, "value": 5, "max": 10},
            ),
            frame(
                600,
                "executed",
                {
                    "prompt_id": RAW_JOB_ID,
                    "node": RAW_NODE_ID,
                    "output": {"images": [{"filename": private_path}]},
                },
            ),
            elapsed_ms=1_000,
            binary=2,
        )

        result = build_progress_monitor(
            connect=True,
            target_job_id=RAW_JOB_ID,
            stall_after_seconds=5,
            event_reader=lambda *_args: observed,
        )
        serialized = json.dumps(result, ensure_ascii=False)

        self.assertTrue(result["ok"])
        self.assertEqual("running", result["decision"])
        self.assertEqual(5, result["progress"]["current"])
        self.assertEqual(10, result["progress"]["total"])
        self.assertEqual(50.0, result["progress"]["percent"])
        self.assertEqual("current_node", result["progress"]["scope"])
        self.assertTrue(result["progress"]["monotonic"])
        self.assertEqual(1, result["monitor"]["duplicate_progress_events"])
        self.assertEqual(1, result["monitor"]["progress_regressions"])
        self.assertEqual(2, result["monitor"]["binary_events_ignored"])
        self.assertIn("progress_regression_ignored", result["warnings"])
        self.assertIn("binary_preview_ignored", result["warnings"])
        self.assertNotIn(RAW_JOB_ID, serialized)
        self.assertNotIn(RAW_NODE_ID, serialized)
        self.assertNotIn(private_path, serialized)
        self.assertNotIn("filename", serialized)

    def test_progress_can_reset_when_the_current_node_changes(self) -> None:
        observed = read(
            frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
            frame(100, "executing", {"prompt_id": RAW_JOB_ID, "node": "node-a"}),
            frame(
                200,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": "node-a", "value": 9, "max": 10},
            ),
            frame(300, "executing", {"prompt_id": RAW_JOB_ID, "node": "node-b"}),
            frame(
                400,
                "progress",
                {"prompt_id": RAW_JOB_ID, "node": "node-b", "value": 1, "max": 5},
            ),
            elapsed_ms=500,
        )

        result = build_progress_monitor(connect=True, event_reader=lambda *_args: observed)

        self.assertEqual("running", result["decision"])
        self.assertEqual(1, result["progress"]["current"])
        self.assertEqual(5, result["progress"]["total"])
        self.assertEqual(0, result["monitor"]["progress_regressions"])

    def test_duplicate_messages_do_not_hide_a_stalled_job(self) -> None:
        observed = read(
            frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
            frame(100, "progress", {"prompt_id": RAW_JOB_ID, "value": 1, "max": 10}),
            frame(5_200, "progress", {"prompt_id": RAW_JOB_ID, "value": 1, "max": 10}),
            frame(
                5_300,
                "status",
                {"status": {"exec_info": {"queue_remaining": 1}}},
            ),
            elapsed_ms=5_500,
        )

        result = build_progress_monitor(
            connect=True,
            stall_after_seconds=5,
            event_reader=lambda *_args: observed,
        )

        self.assertEqual("stalled", result["decision"])
        self.assertTrue(result["monitor"]["stalled"])
        self.assertEqual(5_400, result["monitor"]["stalled_for_ms"])
        self.assertEqual(1, result["queue_remaining"])

    def test_terminal_events_return_only_safe_status(self) -> None:
        cases = (
            ("execution_success", "completed"),
            ("execution_error", "failed"),
            ("execution_interrupted", "interrupted"),
        )
        for event_type, decision in cases:
            with self.subTest(event_type=event_type):
                observed = read(
                    frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
                    frame(
                        200,
                        event_type,
                        {
                            "prompt_id": RAW_JOB_ID,
                            "exception_message": "private model failed",
                            "traceback": "private traceback",
                        },
                    ),
                    elapsed_ms=200,
                )
                result = build_progress_monitor(
                    connect=True,
                    event_reader=lambda *_args, observed=observed: observed,
                )
                serialized = json.dumps(result, ensure_ascii=False)

                self.assertEqual(decision, result["decision"])
                self.assertTrue(result["monitor"]["terminal"])
                self.assertNotIn("private model failed", serialized)
                self.assertNotIn("private traceback", serialized)

    def test_legacy_executing_null_is_a_compatible_completion_signal(self) -> None:
        observed = read(
            frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
            frame(300, "executing", {"prompt_id": RAW_JOB_ID, "node": None}),
            elapsed_ms=300,
        )

        result = build_progress_monitor(connect=True, event_reader=lambda *_args: observed)

        self.assertEqual("completed", result["decision"])
        self.assertTrue(result["monitor"]["terminal"])
        self.assertIn("legacy_completion_event", result["warnings"])

    def test_status_and_unknown_events_have_conservative_decisions(self) -> None:
        idle = read(
            frame(10, "status", {"status": {"exec_info": {"queue_remaining": 0}}}),
            elapsed_ms=20,
        )
        queued = read(
            frame(10, "status", {"status": {"exec_info": {"queue_remaining": 2}}}),
            elapsed_ms=20,
        )
        observing = read(
            frame(10, "progress_state", {"nodes": {"private": "omitted"}}),
            elapsed_ms=20,
        )

        self.assertEqual(
            "idle",
            build_progress_monitor(connect=True, event_reader=lambda *_args: idle)["decision"],
        )
        self.assertEqual(
            "queued",
            build_progress_monitor(connect=True, event_reader=lambda *_args: queued)["decision"],
        )
        result = build_progress_monitor(connect=True, event_reader=lambda *_args: observing)
        self.assertEqual("observing", result["decision"])
        self.assertIn("unknown_events_ignored", result["warnings"])
        self.assertNotIn("private", json.dumps(result))

    def test_dependency_endpoint_and_payload_failures_are_structured(self) -> None:
        failures = (
            (
                ProgressDependencyUnavailable("do not echo"),
                "websocket_dependency_unavailable",
                "websocket_dependency_missing",
            ),
            (
                OSError("C:\\Users\\private\\socket.log"),
                "websocket_endpoint_unavailable",
                "loopback_websocket_unavailable",
            ),
        )
        for error, error_code, warning in failures:
            with self.subTest(error_code=error_code):

                def fail(*_args: object, error: Exception = error) -> ProgressRead:
                    raise error

                result = build_progress_monitor(connect=True, event_reader=fail)
                serialized = json.dumps(result, ensure_ascii=False)
                self.assertFalse(result["ok"])
                self.assertEqual("unavailable", result["decision"])
                self.assertEqual(error_code, result["error_code"])
                self.assertIn(warning, result["warnings"])
                self.assertNotIn("private", serialized)

        malformed = ProgressRead(
            frames=[ObservedFrame(elapsed_ms=-1, payload={})],
            elapsed_ms=10,
            binary_events_ignored=0,
        )
        result = build_progress_monitor(connect=True, event_reader=lambda *_args: malformed)
        self.assertEqual("progress_event_payload_invalid", result["error_code"])

    def test_live_reader_disables_proxy_redirects_and_drops_binary_frames(self) -> None:
        captured: dict = {}

        class FakeTimeout(Exception):
            pass

        class FakeClosed(Exception):
            pass

        class FakeWebSocketError(Exception):
            pass

        class FakeConnection:
            def __init__(self) -> None:
                self.messages = [
                    b"private-preview-bytes",
                    json.dumps(
                        {
                            "type": "execution_success",
                            "data": {"prompt_id": RAW_JOB_ID},
                        }
                    ),
                ]
                self.closed = False

            def settimeout(self, _timeout: float) -> None:
                return

            def recv(self) -> object:
                if not self.messages:
                    raise FakeClosed
                return self.messages.pop(0)

            def close(self) -> None:
                self.closed = True

        connection = FakeConnection()

        def create_connection(url: str, **kwargs: object) -> FakeConnection:
            captured["url"] = url
            captured.update(kwargs)
            return connection

        fake_module = types.ModuleType("websocket")
        fake_module.create_connection = create_connection
        fake_module.WebSocketTimeoutException = FakeTimeout
        fake_module.WebSocketConnectionClosedException = FakeClosed
        fake_module.WebSocketException = FakeWebSocketError
        direct_socket = object()

        with (
            patch.dict(sys.modules, {"websocket": fake_module}),
            patch(
                "starbridge_mcp.core.progress_monitor._direct_loopback_socket",
                return_value=direct_socket,
            ),
        ):
            observation = _read_live_events(
                "http://127.0.0.1:8188",
                listen_seconds=1,
                max_events=10,
                target_job_id=RAW_JOB_ID,
            )

        self.assertTrue(str(captured["url"]).startswith("ws://127.0.0.1:8188/ws?clientId="))
        self.assertIs(direct_socket, captured["socket"])
        self.assertEqual(0, captured["redirect_limit"])
        self.assertEqual(["127.0.0.1", "localhost", "::1"], captured["http_no_proxy"])
        self.assertTrue(captured["suppress_origin"])
        self.assertEqual(1, observation.binary_events_ignored)
        self.assertEqual(1, len(observation.frames))
        self.assertTrue(connection.closed)

    def test_only_plain_loopback_http_urls_and_bounded_inputs_are_allowed(self) -> None:
        for url in (
            "http://example.invalid:8188",
            "https://127.0.0.1:8188",
            "http://user@127.0.0.1:8188",
            "http://127.0.0.1:8188/api",
        ):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "loopback") as caught:
                build_progress_monitor(connect=True, comfy_url=url)
            self.assertNotIn(url, str(caught.exception))

        for kwargs in (
            {"connect": 1},
            {"listen_seconds": 31},
            {"stall_after_seconds": 0},
            {"max_events": 501},
            {"target_job_id": ""},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_progress_monitor(**kwargs)

    def test_tool_schema_registry_control_plan_and_mcp_are_wired(self) -> None:
        definitions = {item["name"]: item for item in TOOL_DEFINITIONS}
        tool = definitions["comfyui.progress_monitor"]
        self.assertTrue(tool["annotations"]["readOnlyHint"])
        self.assertTrue(tool["annotations"]["safeDefault"])
        self.assertTrue(tool["annotations"]["requiresLocalSoftware"])
        self.assertFalse(tool["inputSchema"]["properties"]["connect"]["default"])
        self.assertEqual(
            SCHEMA_VERSION,
            tool["outputSchema"]["properties"]["schema_version"]["const"],
        )

        capabilities = {item["name"]: item for item in list_capabilities(include_guarded=False)}
        self.assertIn("comfyui.progress_monitor", capabilities)

        plan = build_control_plan(goal="搭建 ComfyUI 文生图 workflow")
        observe = next(phase for phase in plan["phases"] if phase["phase"] == "observe")
        self.assertIn("comfyui.progress_monitor", observe["tools"])
        self.assertFalse(observe["tool_arguments"]["comfyui.progress_monitor"]["connect"])
        self.assertIn("live_progress_reviewed", plan["quality_gates"])

        recipe = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "tools/call",
                "params": {
                    "name": "starbridge.recipe_plan",
                    "arguments": {"recipe_id": "comfyui_txt2img_lifecycle"},
                },
            }
        )
        assert recipe is not None
        recipe_plan = recipe["result"]["structuredContent"]["plan"]
        self.assertEqual(SCHEMA_VERSION, recipe_plan["progress_monitor"]["schema_version"])
        self.assertIn(
            "comfyui.progress_monitor",
            recipe_plan["action_plan"]["tool_sequence"],
        )

        planned = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "comfyui.progress_monitor", "arguments": {}},
            }
        )
        assert planned is not None
        self.assertFalse(planned["result"]["isError"])
        self.assertEqual(
            SCHEMA_VERSION,
            planned["result"]["structuredContent"]["schema_version"],
        )

        observed = read(
            frame(0, "execution_start", {"prompt_id": RAW_JOB_ID}),
            frame(100, "progress", {"prompt_id": RAW_JOB_ID, "value": 4, "max": 8}),
            elapsed_ms=200,
        )
        with patch(
            "starbridge_mcp.core.progress_monitor._read_live_events",
            return_value=observed,
        ):
            live = handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "comfyui.progress_monitor",
                        "arguments": {"connect": True},
                    },
                }
            )
        assert live is not None
        serialized = json.dumps(live, ensure_ascii=False)
        self.assertFalse(live["result"]["isError"])
        self.assertEqual("running", live["result"]["structuredContent"]["decision"])
        self.assertNotIn(RAW_JOB_ID, serialized)


if __name__ == "__main__":
    unittest.main()
