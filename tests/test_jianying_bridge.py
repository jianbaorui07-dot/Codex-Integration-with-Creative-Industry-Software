from __future__ import annotations

import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from starbridge_mcp.bridges import jianying


TIMELINE_SPEC = {
    "clips": [{"clip_id": "scene_001", "asset": "PLACEHOLDER_VIDEO_001.mp4", "start": 0, "duration": 3}],
    "texts": [{"scene_id": "scene_001", "start": 0, "duration": 3, "text": "Demo title"}],
    "audio": [{"scene_id": "scene_001", "asset": "PLACEHOLDER_AUDIO_001.wav", "start": 0, "duration": 3}],
    "subtitles": [{"scene_id": "scene_001", "start": 0, "duration": 3, "text": "Safe subtitle"}],
}


class JianyingBridgeTests(unittest.TestCase):
    def assert_schema(self, result: dict) -> None:
        self.assertEqual({"ok", "bridge", "action", "message", "details", "warnings", "next_steps"}, set(result))
        self.assertEqual("jianying_capcut", result["bridge"])

    def test_status_requires_draft_dir_env(self) -> None:
        old_value = os.environ.pop("STARBRIDGE_JIANYING_DRAFT_DIR", None)
        try:
            result = jianying.status()
            self.assert_schema(result)
            self.assertFalse(result["ok"])
        finally:
            if old_value is not None:
                os.environ["STARBRIDGE_JIANYING_DRAFT_DIR"] = old_value

    def test_validate_timeline_spec_warns_for_missing_optional_fields(self) -> None:
        result = jianying.validate_timeline_spec({"clips": []})
        self.assert_schema(result)
        self.assertTrue(result["ok"])
        self.assertTrue(result["warnings"])

    def test_create_and_validate_draft_plan(self) -> None:
        created = jianying.create_draft_plan(TIMELINE_SPEC)
        self.assert_schema(created)
        self.assertTrue(created["ok"])
        plan = created["details"]["draft_plan"]
        self.assertFalse(plan["write_real_draft"])
        validated = jianying.validate_draft_plan(plan)
        self.assert_schema(validated)
        self.assertTrue(validated["ok"])

    def test_validate_draft_plan_warns_on_absolute_path(self) -> None:
        plan = {
            "schema": "starbridge.draft_plan.v1",
            "write_real_draft": False,
            "tracks": {"video": [{"asset": "C:\\Users\\alice\\Desktop\\clip.mov"}]},
        }
        result = jianying.validate_draft_plan(plan)
        self.assert_schema(result)
        self.assertTrue(result["warnings"])
        self.assertNotIn("C:\\Users\\alice", str(result))

    def test_export_refuses_real_draft_directory(self) -> None:
        plan = jianying.create_draft_plan(TIMELINE_SPEC)["details"]["draft_plan"]
        result = jianying.export_draft_plan(plan, "C:\\Users\\alice\\Documents\\JianyingPro\\draft.json")
        self.assert_schema(result)
        self.assertFalse(result["ok"])

    def test_export_allows_examples_output_without_touching_real_draft(self) -> None:
        plan = jianying.create_draft_plan(TIMELINE_SPEC)["details"]["draft_plan"]
        output = jianying.ALLOWED_OUTPUT_DIR / "draft_plan.example.json"
        with patch.object(Path, "mkdir"), patch.object(Path, "write_text", return_value=None), patch.object(
            Path, "stat", return_value=SimpleNamespace(st_size=123)
        ):
            result = jianying.export_draft_plan(plan, output)
        self.assert_schema(result)
        self.assertTrue(result["ok"])

    def test_storyboard_import_to_timeline(self) -> None:
        storyboard = {
            "scenes": [
                {
                    "scene_id": "intro",
                    "duration": 2,
                    "subtitle": "Hello",
                    "voiceover": "Narration",
                    "visual_note": "Opening shot",
                    "image": "PLACEHOLDER_IMAGE_001.png",
                }
            ]
        }
        result = jianying.import_storyboard_to_timeline(storyboard)
        self.assert_schema(result)
        self.assertTrue(result["ok"])
        timeline = result["details"]["timeline_spec"]
        self.assertEqual(1, len(timeline["clips"]))
        self.assertEqual(1, len(timeline["subtitles"]))


if __name__ == "__main__":
    unittest.main()
