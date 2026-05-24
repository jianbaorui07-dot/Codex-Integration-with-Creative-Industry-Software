from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from starbridge_mcp.bridges import jianying


def main() -> None:
    timeline = json.loads((Path(__file__).parent / "sample_timeline_spec.json").read_text(encoding="utf-8"))
    result = jianying.create_draft_plan(timeline)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
