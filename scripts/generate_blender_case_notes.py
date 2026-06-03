"""Generate per-case Blender learning notes from redacted scene profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def slugify(label: str, index: int) -> str:
    return f"case-{index:03d}"


def infer_case_type(profile: dict[str, object]) -> str:
    label = str(profile["relative_label"])
    counts = profile.get("object_type_counts", {})
    modifiers = profile.get("modifier_counts", {})
    if "HDR" in label or "环境" in label:
        return "环境光与世界节点"
    if "车" in label or "直升机" in label or "机器人" in label:
        return "硬表面/机械"
    if "人" in label or "女" in label or "Mask" in label or "kama" in label or "Wasp" in label:
        return "角色/人体"
    if "咖啡机" in label or "保龄球" in label or "耳朵" in label or "西瓜" in label:
        return "道具/产品"
    if int(counts.get("ARMATURE", 0)) > 0 or int(modifiers.get("ARMATURE", 0)) > 0:
        return "角色/绑定"
    return "综合场景"


def top_items(values: dict[str, object], limit: int = 8) -> str:
    if not values:
        return "无"
    rows = sorted(values.items(), key=lambda item: int(item[1]), reverse=True)[:limit]
    return "、".join(f"`{key}` {value}" for key, value in rows)


def light_table(profile: dict[str, object]) -> str:
    lights = profile.get("lights", [])
    if not lights:
        return "本案例没有记录到灯光对象。学习时应重点检查 World、材质自发光或手动补灯。"
    lines = ["| 灯光 | 类型 | 能量 | 颜色 |", "| --- | --- | ---: | --- |"]
    for light in lights:
        color = ", ".join(str(v) for v in light.get("color", []))
        lines.append(
            f"| `{light.get('name')}` | `{light.get('type')}` | {light.get('energy')} | [{color}] |"
        )
    return "\n".join(lines)


def camera_text(profile: dict[str, object]) -> str:
    cameras = profile.get("cameras", [])
    if not cameras:
        return "未记录到相机。这个案例更适合作为建模/材质研究，需要自己补相机做出图实验。"
    parts = []
    for camera in cameras:
        parts.append(
            f"`{camera.get('name')}`：{camera.get('lens')}mm，{camera.get('type')}，sensor {camera.get('sensor_width')}"
        )
    return "\n".join(f"- {part}" for part in parts)


def learning_focus(profile: dict[str, object]) -> list[str]:
    case_type = infer_case_type(profile)
    modifiers = profile.get("modifier_counts", {})
    focus: list[str] = []
    if "角色" in case_type:
        focus.append("先观察身体比例、衣物分层、头发/装饰拆分，再研究骨骼和姿势。")
    if "硬表面" in case_type:
        focus.append("重点观察镜像、倒角、细分和边缘高光如何服务机械/车辆轮廓。")
    if "环境" in case_type:
        focus.append("重点研究 World 节点、HDR/EXR 环境光和反射氛围。")
    if "道具" in case_type:
        focus.append("适合临摹基础体块、材质粗糙度和产品视角构图。")
    if int(modifiers.get("SUBSURF", 0)) > 0:
        focus.append("存在 `SUBSURF`：对照低模控制线和最终平滑轮廓。")
    if int(modifiers.get("MIRROR", 0)) > 0:
        focus.append("存在 `MIRROR`：学习只建一半再对称的结构拆分。")
    if int(modifiers.get("BEVEL", 0)) > 0:
        focus.append("存在 `BEVEL`：观察倒角宽度如何制造高光。")
    if int(modifiers.get("SOLIDIFY", 0)) > 0:
        focus.append("存在 `SOLIDIFY`：观察衣物、壳体或薄片如何获得厚度。")
    if int(profile.get("material_count", 0)) > 0:
        focus.append("材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。")
    if int(profile.get("light_count", 0)) > 0:
        focus.append("有灯光：先判断主光、补光、轮廓光，再改材质。")
    if int(profile.get("camera_count", 0)) > 0:
        focus.append("有相机：记录焦段和构图，按这个镜头复建一张图。")
    return focus or ["把它作为综合拆解案例，先分离模型、材质、灯光、相机四层。"]


def render_case(profile: dict[str, object], index: int) -> str:
    label = profile["relative_label"]
    case_type = infer_case_type(profile)
    notes = "\n".join(f"- {item}" for item in learning_focus(profile))
    source_notes = "\n".join(f"- {item}" for item in profile.get("drawing_learning_notes", [])) or "- 无"
    return f"""# 案例 {index:03d}：{Path(str(label)).stem}

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `{label}` |
| 案例类型 | {case_type} |
| 渲染引擎 | `{profile.get("render_engine")}` |
| 分辨率 | {profile.get("resolution")} |
| 帧范围 | {profile.get("frame_range")} |
| 对象数 | {profile.get("object_count")} |
| Mesh | {profile.get("mesh_count")} |
| 材质 | {profile.get("material_count")} |
| 灯光 | {profile.get("light_count")} |
| 相机 | {profile.get("camera_count")} |

## 结构观察

- 对象类型：{top_items(profile.get("object_type_counts", {}))}
- 修改器：{top_items(profile.get("modifier_counts", {}))}
- Mesh 材质槽数量分布：{top_items(profile.get("mesh_material_slot_counts", {}))}

## 灯光

{light_table(profile)}

## 相机

{camera_text(profile)}

## 学习重点

{notes}

## 自动观察备注

{source_notes}

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.profiles).read_text(encoding="utf-8"))
    profiles = data.get("profiles", [])
    out_dir = Path(args.out_dir)
    cases_dir = out_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    index_lines = [
        "# Blender 全量案例学习索引",
        "",
        f"本索引由 `{Path(args.profiles).as_posix()}` 生成，共 {len(profiles)} 个 `.blend` profile。",
        "",
        "| 编号 | 案例 | 类型 | 对象 | 材质 | 灯光 | 相机 |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]

    for index, profile in enumerate(profiles, 1):
        slug = slugify(str(profile["relative_label"]), index)
        filename = f"{slug}.md"
        (cases_dir / filename).write_text(render_case(profile, index), encoding="utf-8")
        index_lines.append(
            f"| {index:03d} | [{Path(str(profile['relative_label'])).stem}](cases/{filename}) | "
            f"{infer_case_type(profile)} | {profile.get('object_count')} | "
            f"{profile.get('material_count')} | {profile.get('light_count')} | {profile.get('camera_count')} |"
        )

    (out_dir / "all-blend-cases.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"generated {len(profiles)} case notes in {cases_dir}")


if __name__ == "__main__":
    main()
