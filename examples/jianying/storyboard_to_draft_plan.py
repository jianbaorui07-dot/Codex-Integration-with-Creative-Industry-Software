from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from starbridge_mcp.bridges import jianying


def main() -> None:
    storyboard = json.loads((Path(__file__).parent / "sample_storyboard.json").read_text(encoding="utf-8"))
    timeline_result = jianying.import_storyboard_to_timeline(storyboard)
    if not timeline_result["ok"]:
        print(json.dumps(timeline_result, ensure_ascii=False, indent=2))
        return
    result = jianying.create_draft_plan(timeline_result["details"]["timeline_spec"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
