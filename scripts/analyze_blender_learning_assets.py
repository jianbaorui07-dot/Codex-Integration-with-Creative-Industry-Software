"""Build a redacted learning index from a local Blender asset library.

This script is intended for public repository use. It never copies source
assets and it only writes relative labels, file types, size buckets, and
study-oriented tags.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


MODEL_EXTS = {".blend", ".blend1", ".fbx", ".obj", ".gltf", ".glb"}
MATERIAL_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
LIGHTING_EXTS = {".hdr", ".exr"}
ARCHIVE_EXTS = {".zip", ".rar", ".7z"}
TEXT_EXTS = {".txt", ".md", ".pdf", ".doc", ".docx"}


def classify_asset(path: Path) -> str:
    ext = path.suffix.lower()
    label = str(path).lower()
    if ext in MODEL_EXTS:
        return "modeling_case"
    if ext in LIGHTING_EXTS or "hdr" in label:
        return "lighting_environment"
    if ext in MATERIAL_EXTS or "tex" in label or "贴图" in label or "材质" in label:
        return "material_texture"
    if ext in ARCHIVE_EXTS:
        return "archived_asset_pack"
    if ext in TEXT_EXTS:
        return "license_or_note"
    return "other"


def study_signal(path: Path) -> str:
    text = str(path).lower()
    ext = path.suffix.lower()
    if ext == ".blend":
        return "open in Blender to study composition, object hierarchy, materials, lights, and cameras"
    if ext in {".fbx", ".obj", ".gltf", ".glb"}:
        return "import to compare topology, scale, UVs, and material slots"
    if ext in LIGHTING_EXTS:
        return "use as world lighting reference for reflective and cinematic renders"
    if ext in MATERIAL_EXTS:
        return "study texture role: base color, roughness, normal, bump, opacity, or decals"
    if ext in ARCHIVE_EXTS:
        return "unpack selectively before study; do not publish raw archive content"
    if "练习" in text:
        return "practice case suitable for rebuilding step by step"
    return "catalog for later manual review"


def size_bucket(size: int) -> str:
    mib = size / (1024 * 1024)
    if mib < 1:
        return "tiny"
    if mib < 25:
        return "small"
    if mib < 250:
        return "medium"
    if mib < 1024:
        return "large"
    return "very_large"


def build_inventory(root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    by_extension: Counter[str] = Counter()
    by_top_folder: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    size_by_category: defaultdict[str, int] = defaultdict(int)

    files = [p for p in root.rglob("*") if p.is_file()]
    folders = [p for p in root.rglob("*") if p.is_dir()]

    for path in sorted(files, key=lambda p: p.as_posix().lower()):
        rel = path.relative_to(root)
        parts = rel.parts
        top_folder = parts[0] if parts else "."
        ext = path.suffix.lower() or "[no extension]"
        category = classify_asset(rel)
        size = path.stat().st_size

        by_extension[ext] += 1
        by_top_folder[top_folder] += 1
        by_category[category] += 1
        size_by_category[category] += size

        rows.append(
            {
                "relative_label": rel.as_posix(),
                "top_folder": top_folder,
                "extension": ext,
                "category": category,
                "size_mb": round(size / (1024 * 1024), 3),
                "size_bucket": size_bucket(size),
                "study_signal": study_signal(rel),
            }
        )

    summary = {
        "source_redaction": "Local absolute paths and raw assets are intentionally omitted.",
        "file_count": len(files),
        "folder_count": len(folders),
        "total_gb": round(sum(p.stat().st_size for p in files) / (1024**3), 3),
        "by_extension": dict(by_extension.most_common()),
        "by_top_folder": dict(by_top_folder.most_common()),
        "by_category": dict(by_category.most_common()),
        "size_gb_by_category": {
            key: round(value / (1024**3), 3)
            for key, value in sorted(size_by_category.items())
        },
    }
    return rows, summary


def write_outputs(rows: list[dict[str, object]], summary: dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = out_dir / "asset_inventory_redacted.csv"
    summary_path = out_dir / "asset_summary_redacted.json"

    with inventory_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Local Blender asset root to inspect.")
    parser.add_argument("--out-dir", required=True, help="Output directory for redacted data.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Asset root does not exist: {root}")

    rows, summary = build_inventory(root)
    write_outputs(rows, summary, Path(args.out_dir))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
