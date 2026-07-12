from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "illustrator_bridge" / "scripts" / "wgc_window_stream.py"


class IllustratorWgcStreamTests(unittest.TestCase):
    def test_stream_is_window_only_and_does_not_write_files(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("WindowCapture", source)
        self.assertIn("illustrator-window", source)
        self.assertNotIn("ImageGrab", source)
        self.assertNotIn("save(", source)
        self.assertNotIn("write_bytes", source)

    def test_stream_has_bounded_fps_and_frame_size(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("args.fps <= 5.0", source)
        self.assertIn("MAX", source.upper())
        self.assertIn("jpeg-quality", source)


if __name__ == "__main__":
    unittest.main()
