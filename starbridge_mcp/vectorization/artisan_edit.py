from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

MAX_EDIT_INDEX_BYTES = 2 * 1024 * 1024
SHAPE_ID = re.compile(r"^shape-[0-9]{4,}$")
INTENT_SELECTOR = re.compile(r"^intent:[a-z][a-z-]{0,31}$")


class EditIndexError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _load_index(path_value: str) -> dict[str, Any]:
    path = Path(path_value).expanduser()
    if not path.is_file() or path.suffix.lower() != ".json":
        raise EditIndexError("invalid_edit_index", "Edit index must be one explicit JSON file.")
    if path.stat().st_size > MAX_EDIT_INDEX_BYTES:
        raise EditIndexError("edit_index_too_large", "Edit index exceeds the local size limit.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EditIndexError("invalid_edit_index", "Edit index is not valid UTF-8 JSON.") from exc
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise EditIndexError("unsupported_edit_index", "Edit index schema is not supported.")
    objects = value.get("objects")
    selectors = value.get("selectors")
    if not isinstance(value.get("edit_ref"), str) or not isinstance(objects, list):
        raise EditIndexError("invalid_edit_index", "Edit index is missing required records.")
    if not isinstance(selectors, list) or not all(
        isinstance(item, list)
        and len(item) == 4
        and INTENT_SELECTOR.fullmatch(str(item[0]))
        and all(isinstance(number, int) and number >= 0 for number in item[1:])
        for item in selectors
    ):
        raise EditIndexError("invalid_edit_index", "Edit index selectors are invalid.")
    if not all(
        isinstance(item, list)
        and len(item) == 5
        and SHAPE_ID.fullmatch(str(item[0]))
        and isinstance(item[1], str)
        and isinstance(item[2], list)
        and len(item[2]) == 4
        and all(isinstance(number, int) and number >= 0 for number in item[2])
        and isinstance(item[3], int)
        and item[3] >= 0
        and isinstance(item[4], int)
        and item[4] >= 0
        for item in objects
    ):
        raise EditIndexError("invalid_edit_index", "Edit index object records are invalid.")
    if len({item[0] for item in objects}) != len(objects):
        raise EditIndexError("invalid_edit_index", "Edit index shape IDs must be unique.")
    core_keys = (
        "schema_version",
        "structure_ref",
        "strategy",
        "selectors",
        "objects",
        "edit_reference_format",
    )
    if any(key not in value for key in core_keys):
        raise EditIndexError("invalid_edit_index", "Edit index is missing canonical fields.")
    canonical = json.dumps(
        {key: value[key] for key in core_keys},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    if value.get("edit_index_sha256") != digest or value["edit_ref"] != f"edit:{digest[:12]}":
        raise EditIndexError("edit_index_integrity_failed", "Edit index digest does not match.")
    return value


def _bbox_union(objects: list[list[Any]]) -> list[int]:
    boxes = [item[2] for item in objects]
    minimum_x = min(int(box[0]) for box in boxes)
    minimum_y = min(int(box[1]) for box in boxes)
    maximum_x = max(int(box[0]) + int(box[2]) for box in boxes)
    maximum_y = max(int(box[1]) + int(box[3]) for box in boxes)
    return [minimum_x, minimum_y, maximum_x - minimum_x, maximum_y - minimum_y]


def inspect_edit_index(
    path_value: str,
    selector: str,
    *,
    object_limit: int = 24,
) -> dict[str, Any]:
    index = _load_index(path_value)
    if INTENT_SELECTOR.fullmatch(selector):
        intent = selector.removeprefix("intent:")
        objects = [item for item in index["objects"] if item[1] == intent]
    elif SHAPE_ID.fullmatch(selector):
        objects = [item for item in index["objects"] if item[0] == selector]
    else:
        raise EditIndexError(
            "invalid_selector", "Selector must be intent:<name> or one stable shape ID."
        )
    if not objects:
        raise EditIndexError("selector_not_found", "Selector did not match an indexed object.")
    limit = max(1, min(100, object_limit))
    object_ids = [str(item[0]) for item in objects]
    return {
        "ok": True,
        "edit_ref": index["edit_ref"],
        "selector": selector,
        "object_count": len(objects),
        "anchors": sum(int(item[3]) for item in objects),
        "subpaths": sum(int(item[4]) for item in objects),
        "bbox": _bbox_union(objects),
        "object_ids": object_ids[:limit],
        "object_ids_truncated": len(object_ids) > limit,
        "edit_prompt": f"{index['edit_ref']} {selector} <change>",
        "external_ai_calls": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect one local Artisan compact edit scope.")
    parser.add_argument("--index", required=True)
    parser.add_argument("--selector", required=True)
    parser.add_argument("--object-limit", type=int, default=24)
    try:
        args = parser.parse_args(argv)
        result = inspect_edit_index(
            args.index,
            args.selector,
            object_limit=args.object_limit,
        )
    except EditIndexError as exc:
        result = {"ok": False, "error": {"code": exc.code, "message": str(exc)}}
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
