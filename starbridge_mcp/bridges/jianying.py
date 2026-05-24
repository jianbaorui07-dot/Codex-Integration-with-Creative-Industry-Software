from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from starbridge_mcp.core.result_schema import make_result, validate_result
from starbridge_mcp.core.security import sanitize


BRIDGE = "jianying_capcut"
REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_OUTPUT_DIR = REPO_ROOT / "examples" / "jianying" / "output"
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:[\\/][^\s\"'<>]+"),
    re.compile(r"/Users/[^/\s\"'<>]+"),
    re.compile(r"/home/[^/\s\"'<>]+"),
)


def _result(
    *,
    ok: bool,
    action: str,
    message: str,
    details: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    next_steps: list[str] | None = None,
) -> dict[str, Any]:
    result = make_result(
        ok=ok,
        bridge=BRIDGE,
        action=action,
        message=message,
        details=sanitize(details or {}),
        warnings=sanitize(warnings or []),
        next_steps=sanitize(next_steps or []),
    )
    validate_result(result)
    return result


def _is_placeholder(value: str) -> bool:
    return Path(value).name.startswith("PLACEHOLDER_")


def _contains_absolute_path(value: str) -> bool:
    return any(pattern.search(value) for pattern in ABSOLUTE_PATH_PATTERNS)


def _walk_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_walk_values(item))
        return values
    return []


def _path_warnings(value: Any) -> list[str]:
    warnings = []
    for text in _walk_values(value):
        if _is_placeholder(text):
            continue
        if _contains_absolute_path(text):
            warnings.append(f"Possible absolute path detected and sanitized: {sanitize(text)}")
    return warnings


def status() -> dict[str, Any]:
    draft_dir = os.environ.get("STARBRIDGE_JIANYING_DRAFT_DIR")
    if not draft_dir:
        return _result(
            ok=False,
            action="status",
            message="STARBRIDGE_JIANYING_DRAFT_DIR is not configured.",
            details={"draft_dir_configured": False},
            warnings=["Jianying/CapCut bridge will only generate offline draft_plan objects."],
            next_steps=["Set STARBRIDGE_JIANYING_DRAFT_DIR only for local manual checks; never commit real draft paths."],
        )
    path = Path(draft_dir)
    exists = path.exists()
    return _result(
        ok=exists,
        action="status",
        message="Draft directory is configured." if exists else "Draft directory is configured but does not exist.",
        details={"draft_dir_configured": True, "draft_dir_exists": exists, "draft_dir": sanitize(str(path))},
        warnings=[] if exists else ["Configured draft directory was not found."],
        next_steps=["Use draft_plan export under examples/jianying/output only; do not write to real draft directories."],
    )


def validate_timeline_spec(timeline_spec: Any) -> dict[str, Any]:
    if not isinstance(timeline_spec, dict):
        return _result(
            ok=False,
            action="validate_timeline_spec",
            message="Timeline spec must be a JSON object.",
            details={"errors": ["timeline_spec is not a dict"]},
            warnings=["No draft plan was created."],
        )
    warnings = []
    for field in ("clips", "texts", "audio", "subtitles"):
        if field not in timeline_spec:
            warnings.append(f"Missing optional field: {field}")
        elif not isinstance(timeline_spec[field], list):
            warnings.append(f"Field should be a list: {field}")
    warnings.extend(_path_warnings(timeline_spec))
    clips = timeline_spec.get("clips", [])
    ok = isinstance(clips, list)
    return _result(
        ok=ok,
        action="validate_timeline_spec",
        message="Timeline spec checked.",
        details={
            "clip_count": len(clips) if isinstance(clips, list) else 0,
            "text_count": len(timeline_spec.get("texts", [])) if isinstance(timeline_spec.get("texts", []), list) else 0,
            "audio_count": len(timeline_spec.get("audio", [])) if isinstance(timeline_spec.get("audio", []), list) else 0,
            "subtitle_count": len(timeline_spec.get("subtitles", [])) if isinstance(timeline_spec.get("subtitles", []), list) else 0,
        },
        warnings=warnings,
        next_steps=[] if ok else ["Make clips a list before creating a draft_plan."],
    )


def create_draft_plan(timeline_spec: Any) -> dict[str, Any]:
    validation = validate_timeline_spec(timeline_spec)
    if not validation["ok"] or not isinstance(timeline_spec, dict):
        return _result(
            ok=False,
            action="create_draft_plan",
            message="Draft plan was not created because timeline spec is invalid.",
            details={"validation": validation["details"]},
            warnings=validation["warnings"],
            next_steps=validation["next_steps"],
        )

    clips = list(timeline_spec.get("clips") or [])
    texts = list(timeline_spec.get("texts") or [])
    audio = list(timeline_spec.get("audio") or [])
    subtitles = list(timeline_spec.get("subtitles") or [])
    duration = timeline_spec.get("duration")
    if duration is None:
        duration = sum(float(clip.get("duration", 0)) for clip in clips if isinstance(clip, dict))

    plan = {
        "schema": "starbridge.draft_plan.v1",
        "target": "jianying_capcut",
        "write_real_draft": False,
        "duration": duration,
        "tracks": {
            "video": clips,
            "text": texts,
            "audio": audio,
            "subtitles": subtitles,
        },
        "safety": {
            "real_draft_write": "forbidden",
            "allowed_export_dir": "examples/jianying/output",
            "asset_policy": "placeholders only in public examples",
        },
    }
    warnings = list(validation["warnings"])
    warnings.append("Draft plan only; no Jianying/CapCut draft directory was written.")
    return _result(
        ok=True,
        action="create_draft_plan",
        message="Safe draft_plan generated.",
        details={"draft_plan": sanitize(plan)},
        warnings=warnings,
        next_steps=["Review the plan manually before any future real draft writer is implemented."],
    )


def validate_draft_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return _result(
            ok=False,
            action="validate_draft_plan",
            message="Draft plan must be a JSON object.",
            details={"errors": ["plan is not a dict"]},
            warnings=["Nothing was written."],
        )
    errors = []
    if plan.get("schema") != "starbridge.draft_plan.v1":
        errors.append("schema must be starbridge.draft_plan.v1")
    if plan.get("write_real_draft") is not False:
        errors.append("write_real_draft must be false")
    if not isinstance(plan.get("tracks"), dict):
        errors.append("tracks must be an object")
    warnings = _path_warnings(plan)
    return _result(
        ok=not errors,
        action="validate_draft_plan",
        message="Draft plan is valid." if not errors else "Draft plan has structural problems.",
        details={"errors": errors},
        warnings=warnings,
        next_steps=[] if not errors else ["Regenerate the draft_plan from a valid timeline spec."],
    )


def export_draft_plan(plan: Any, output_path: str | Path) -> dict[str, Any]:
    validation = validate_draft_plan(plan)
    output = Path(output_path)
    resolved_output = output.resolve()
    allowed_root = ALLOWED_OUTPUT_DIR.resolve()
    try:
        resolved_output.relative_to(allowed_root)
        in_allowed_dir = True
    except ValueError:
        in_allowed_dir = False

    if not in_allowed_dir:
        return _result(
            ok=False,
            action="export_draft_plan",
            message="Refused to write outside examples/jianying/output.",
            details={"output_path": sanitize(str(output)), "allowed_dir": "examples/jianying/output"},
            warnings=["Real Jianying/CapCut draft directories are never valid export targets."],
            next_steps=["Choose a path under examples/jianying/output for public demo output."],
        )
    if not validation["ok"]:
        return _result(
            ok=False,
            action="export_draft_plan",
            message="Refused to export invalid draft_plan.",
            details={"validation": validation["details"], "output_path": sanitize(str(output))},
            warnings=validation["warnings"],
            next_steps=validation["next_steps"],
        )

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(json.dumps(sanitize(plan), ensure_ascii=False, indent=2), encoding="utf-8")
    return _result(
        ok=True,
        action="export_draft_plan",
        message="Draft plan exported to safe demo directory.",
        details={"output_path": sanitize(str(resolved_output)), "bytes_written": resolved_output.stat().st_size},
        warnings=["This is a draft_plan JSON only, not a real Jianying/CapCut draft."],
    )


def import_storyboard_to_timeline(storyboard_json: Any) -> dict[str, Any]:
    if isinstance(storyboard_json, dict):
        scenes = storyboard_json.get("scenes", [])
    elif isinstance(storyboard_json, list):
        scenes = storyboard_json
    else:
        return _result(
            ok=False,
            action="import_storyboard_to_timeline",
            message="Storyboard must be a list or an object with scenes.",
            details={"errors": ["storyboard is not a supported shape"]},
        )
    if not isinstance(scenes, list):
        return _result(
            ok=False,
            action="import_storyboard_to_timeline",
            message="storyboard.scenes must be a list.",
            details={"errors": ["scenes is not a list"]},
        )

    clips = []
    texts = []
    audio = []
    subtitles = []
    cursor = 0.0
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            continue
        scene_id = str(scene.get("scene_id", f"scene_{index + 1:03d}"))
        duration = float(scene.get("duration", 3.0))
        image = scene.get("image") or f"PLACEHOLDER_IMAGE_{index + 1:03d}.png"
        clips.append(
            {
                "clip_id": scene_id,
                "asset": image,
                "start": cursor,
                "duration": duration,
                "visual_note": scene.get("visual_note", ""),
            }
        )
        if scene.get("subtitle"):
            subtitles.append({"scene_id": scene_id, "start": cursor, "duration": duration, "text": scene["subtitle"]})
        if scene.get("voiceover"):
            audio.append(
                {
                    "scene_id": scene_id,
                    "asset": f"PLACEHOLDER_AUDIO_{index + 1:03d}.wav",
                    "start": cursor,
                    "duration": duration,
                    "voiceover": scene["voiceover"],
                }
            )
        texts.append({"scene_id": scene_id, "start": cursor, "duration": duration, "text": scene.get("visual_note", "")})
        cursor += duration

    timeline_spec = {"duration": cursor, "clips": clips, "texts": texts, "audio": audio, "subtitles": subtitles}
    return _result(
        ok=True,
        action="import_storyboard_to_timeline",
        message="Storyboard converted to safe timeline_spec.",
        details={"timeline_spec": sanitize(timeline_spec), "scene_count": len(clips)},
        warnings=_path_warnings(timeline_spec),
        next_steps=["Pass timeline_spec to create_draft_plan(); do not write a real draft directory."],
    )
