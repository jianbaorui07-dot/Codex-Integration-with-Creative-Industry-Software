from __future__ import annotations

import os
import unittest

from starbridge_mcp.bridges import comfyui


MINIMAL_WORKFLOW = {
    "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "a safe demo prompt"}},
    "2": {"class_type": "KSampler", "inputs": {"seed": 1, "steps": 1}},
    "3": {"class_type": "SaveImage", "inputs": {"filename_prefix": "starbridge_demo"}},
}


class ComfyUIBridgeTests(unittest.TestCase):
    def assert_schema(self, result: dict) -> None:
        self.assertEqual({"ok", "bridge", "action", "message", "details", "warnings", "next_steps"}, set(result))
        self.assertEqual("comfyui", result["bridge"])

    def test_status_handles_missing_service(self) -> None:
        result = comfyui.status(base_url="http://127.0.0.1:9", timeout=0.1)
        self.assert_schema(result)
        self.assertFalse(result["ok"])
        self.assertTrue(result["warnings"])

    def test_validate_workflow_rejects_bad_shapes(self) -> None:
        for payload in (None, [], "not json", {}):
            result = comfyui.validate_workflow(payload)
            self.assert_schema(result)
            self.assertFalse(result["ok"])

    def test_validate_workflow_detects_missing_fields(self) -> None:
        result = comfyui.validate_workflow({"1": {"class_type": "KSampler"}, "2": {"inputs": {}}})
        self.assert_schema(result)
        self.assertFalse(result["ok"])
        self.assertIn("errors", result["details"])

    def test_validate_and_summarize_minimal_workflow(self) -> None:
        validation = comfyui.validate_workflow(MINIMAL_WORKFLOW)
        summary = comfyui.summarize_workflow(MINIMAL_WORKFLOW)
        self.assert_schema(validation)
        self.assert_schema(summary)
        self.assertTrue(validation["ok"])
        self.assertTrue(summary["ok"])
        self.assertEqual(3, summary["details"]["node_count"])
        self.assertEqual(["2"], summary["details"]["sampler_nodes"])
        self.assertEqual(["3"], summary["details"]["save_nodes"])

    def test_summary_warns_and_sanitizes_absolute_paths(self) -> None:
        workflow = {"1": {"class_type": "LoadImage", "inputs": {"image": "C:\\Users\\alice\\Desktop\\secret.png"}}}
        result = comfyui.summarize_workflow(workflow)
        self.assert_schema(result)
        text = str(result)
        self.assertIn("absolute path", " ".join(result["warnings"]).lower())
        self.assertNotIn("C:\\Users\\alice", text)

    def test_queue_workflow_is_dry_run_by_default(self) -> None:
        result = comfyui.queue_workflow(MINIMAL_WORKFLOW)
        self.assert_schema(result)
        self.assertTrue(result["ok"])
        self.assertFalse(result["details"]["queued"])
        self.assertTrue(result["details"]["dry_run"])

    def test_real_queue_requires_two_gates(self) -> None:
        old_value = os.environ.pop("STARBRIDGE_COMFYUI_ALLOW_QUEUE", None)
        try:
            result = comfyui.queue_workflow(MINIMAL_WORKFLOW, dry_run=False, allow_queue=False)
            self.assert_schema(result)
            self.assertFalse(result["ok"])
            self.assertFalse(result["details"]["queued"])
        finally:
            if old_value is not None:
                os.environ["STARBRIDGE_COMFYUI_ALLOW_QUEUE"] = old_value


if __name__ == "__main__":
    unittest.main()
