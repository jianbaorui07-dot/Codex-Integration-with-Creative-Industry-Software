from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image, ImageDraw

from starbridge_mcp.vectorization import (
    RunConfig,
    VectorizationError,
    cli,
    engine,
    run_vectorization,
)

HAS_DESIGN_RUNTIME = all(importlib.util.find_spec(name) is not None for name in ("cv2", "numpy"))


class VectorizationModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_dir.name)
        self.output_root = self.root / "examples" / "output" / "vectorization"
        self.repo_patch = mock.patch.object(engine, "REPO_ROOT", self.root)
        self.output_patch = mock.patch.object(engine, "OUTPUT_ROOT", self.output_root)
        self.repo_patch.start()
        self.output_patch.start()

    def tearDown(self) -> None:
        self.output_patch.stop()
        self.repo_patch.stop()
        self.temporary_dir.cleanup()

    def make_exact_source(self) -> Path:
        source = self.root / "private-customer-name.png"
        image = Image.new("RGBA", (5, 4), (0, 0, 0, 0))
        image.putdata(
            [
                (255, 0, 0, 255),
                (255, 0, 0, 255),
                (0, 0, 255, 128),
                (0, 0, 255, 128),
                (0, 0, 0, 0),
            ]
            * 3
            + [(255, 255, 255, 255)] * 5
        )
        image.save(source)
        return source

    def test_exact_mode_vertically_merges_runs_and_proves_pixel_match(self) -> None:
        source = self.make_exact_source()

        result = run_vectorization(
            RunConfig(input_path=str(source), mode="exact", reference_id="exact-case")
        )

        output = self.output_root / "exact-case" / "exact"
        svg_text = (output / "vector.svg").read_text(encoding="utf-8")
        report_text = (output / "vector_report.json").read_text(encoding="utf-8")
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"]["key"], "exact")
        self.assertTrue(result["exact_validation"]["pixel_match"])
        self.assertEqual(result["exact_validation"]["different_pixel_count"], 0)
        self.assertEqual(result["exact_validation"]["maximum_channel_difference"], 0)
        self.assertEqual(result["vector"]["subpaths"], 4)
        self.assertNotIn("<image", svg_text)
        self.assertNotIn("data:image", svg_text)
        self.assertNotIn(source.name, report_text)
        with Image.open(output / "preview.png") as preview, Image.open(source) as original:
            self.assertEqual(preview.convert("RGBA").tobytes(), original.convert("RGBA").tobytes())

    def test_default_cli_mode_is_smart_and_balanced_is_an_alias(self) -> None:
        parsed = cli.parse_args(["--input", "placeholder.png"])
        self.assertEqual(parsed.mode, "smart")
        self.assertEqual(
            engine._configured(RunConfig("placeholder.png", mode="balanced")).mode, "smart"
        )

    def test_rejects_outside_output_without_creating_artifacts(self) -> None:
        source = self.make_exact_source()
        outside = self.root / "outside"

        with self.assertRaises(VectorizationError) as raised:
            run_vectorization(
                RunConfig(
                    input_path=str(source),
                    mode="exact",
                    reference_id="outside-case",
                    output_dir=str(outside),
                )
            )

        self.assertEqual(raised.exception.code, "output_outside_sandbox")
        self.assertFalse(outside.exists())

    def test_cli_failure_is_structured_and_does_not_echo_private_input(self) -> None:
        private_path = self.root / "do-not-echo-this-name.png"
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = cli.main(["--input", str(private_path), "--mode", "smart"])

        response = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(response["error"]["code"], "unsupported_input")
        self.assertNotIn(private_path.name, stdout.getvalue())


@unittest.skipUnless(HAS_DESIGN_RUNTIME, "smart-vector optional dependencies not installed")
class DesignVectorizationModeTests(VectorizationModeTests):
    def make_design_source(self) -> Path:
        source = self.root / "private-design-source.png"
        image = Image.new("RGBA", (160, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((8, 8, 151, 111), radius=18, fill=(245, 238, 220, 255))
        draw.ellipse((24, 18, 136, 108), fill=(218, 58, 45, 255))
        draw.ellipse((48, 34, 112, 96), fill=(25, 92, 210, 220))
        draw.ellipse((68, 53, 92, 77), fill=(245, 238, 220, 255))
        for index in range(24):
            x = 12 + (index * 23) % 135
            y = 12 + (index * 37) % 95
            color = ((index * 47) % 255, (index * 79) % 255, (index * 31) % 255, 255)
            draw.rectangle((x, y, x + 2, y + 2), fill=color)
        image.save(source)
        return source

    def test_smart_and_lightweight_generate_distinct_verified_outputs(self) -> None:
        source = self.make_design_source()

        smart = run_vectorization(
            RunConfig(input_path=str(source), mode="smart", reference_id="smart-case")
        )
        lightweight = run_vectorization(
            RunConfig(input_path=str(source), mode="lightweight", reference_id="light-case")
        )

        self.assertTrue(smart["mode"]["default"])
        self.assertFalse(lightweight["mode"]["default"])
        self.assertEqual(smart["mode"]["label_zh"], "智能矢量")
        self.assertEqual(lightweight["mode"]["label_zh"], "轻量矢量")
        self.assertLessEqual(lightweight["vector"]["color_count"], 8)
        self.assertLessEqual(lightweight["vector"]["subpaths"], smart["vector"]["subpaths"])
        self.assertLessEqual(lightweight["vector"]["points"], smart["vector"]["points"])
        for reference, mode in (("smart-case", "smart"), ("light-case", "lightweight")):
            output = self.output_root / reference / mode
            svg = (output / "vector.svg").read_text(encoding="utf-8")
            self.assertNotIn("<image", svg)
            self.assertNotIn("base64", svg)
            self.assertTrue((output / "preview.png").is_file())
            self.assertTrue((output / "parameters.json").is_file())
            self.assertTrue((output / "vector_report.md").is_file())

    def test_path_limit_stops_before_target_artifacts_are_published(self) -> None:
        source = self.make_design_source()
        target = self.output_root / "limited" / "smart"

        with self.assertRaises(VectorizationError) as raised:
            run_vectorization(
                RunConfig(
                    input_path=str(source),
                    mode="smart",
                    reference_id="limited",
                    max_subpaths=1,
                )
            )

        self.assertEqual(raised.exception.code, "vector_too_complex")
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
