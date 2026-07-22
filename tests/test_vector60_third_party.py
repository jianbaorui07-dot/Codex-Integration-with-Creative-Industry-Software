from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility.
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


class Vector60ThirdPartyTests(unittest.TestCase):
    def test_vector60_dependencies_are_exactly_pinned(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        vector60 = project["project"]["optional-dependencies"]["vector60"]
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertIn("vtracer==0.6.15", vector60)
        self.assertIn("skia-pathops==0.9.2", vector60)
        self.assertIn("svgpathtools==1.7.2", vector60)
        self.assertEqual(package["devDependencies"]["svgo"], "4.0.2")

    def test_notices_record_license_version_commit_and_scope(self) -> None:
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        expected = {
            "VTracer": ("MIT", "0.6.15", "fd9cdb08e622f237eb05be553a020ddc9e4c47a1"),
            "skia-pathops": (
                "BSD-3-Clause",
                "0.9.2",
                "c11e91f442462d1efc1a45d76c76ae9e74aa0de4",
            ),
            "svgpathtools": (
                "MIT",
                "1.7.2",
                "284fc2c591d852ef51b6168e8d842065f3e41cc2",
            ),
            "SVGO": ("MIT", "4.0.2", "b2309cf541aee11634eb653157b0ff86ab326e98"),
        }
        for component, values in expected.items():
            with self.subTest(component=component):
                self.assertIn(f"## {component}", notices)
                for value in values:
                    self.assertIn(value, notices)
        self.assertIn("diffvg and LIVE remain research references", notices)
        self.assertIn("No complete third-party repository is vendored", notices)


if __name__ == "__main__":
    unittest.main()
