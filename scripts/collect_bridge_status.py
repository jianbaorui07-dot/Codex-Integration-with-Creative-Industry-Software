from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
FIELDS = [
    "bridge_id",
    "display_name",
    "maturity",
    "platforms",
    "probe_supported",
    "write_supported",
    "safe_report_supported",
    "next_steps",
]


def load_bridge_statuses() -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for status_path in sorted(EXAMPLES_DIR.glob("*_bridge/bridge_status.json")):
        data = json.loads(status_path.read_text(encoding="utf-8"))
        data["_path"] = str(status_path.relative_to(REPO_ROOT)).replace("\\", "/")
        statuses.append(data)
    return statuses


def compact_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def to_markdown(statuses: list[dict[str, Any]]) -> str:
    headers = FIELDS
    rows = []
    for status in statuses:
        rows.append([compact_value(status.get(field, "")) for field in headers])

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="汇总 examples/*_bridge/bridge_status.json。")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="输出 JSON。")
    output.add_argument("--markdown", action="store_true", help="输出 Markdown 表格。")
    args = parser.parse_args()

    statuses = load_bridge_statuses()
    if args.json:
        print(json.dumps({"bridges": statuses}, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(statuses), end="")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit("建议使用 Python 3.10 或更新版本运行本脚本。")
    main()
