"""Apply the verified P1Y exposure/light pass to the current UE 5.2 level.

Run inside Unreal Editor Python after backing up and opening the intended map.
Actor labels can be overridden with environment variables.
"""

import json
import os
from pathlib import Path

import unreal


def evidence_path(name):
    root = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()))
    target = root / "WorldForge"
    target.mkdir(parents=True, exist_ok=True)
    return target / name


def actors_by_label():
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    return {actor.get_actor_label(): actor for actor in subsystem.get_all_level_actors()}


def set_if_present(obj, name, value, applied, skipped):
    try:
        old = obj.get_editor_property(name)
        obj.set_editor_property(name, value)
        applied.append({"object": obj.get_name(), "property": name, "old": str(old), "new": str(value)})
        return True
    except Exception as exc:
        skipped.append({"object": obj.get_name(), "property": name, "reason": str(exc)})
        return False


result = {"applied": [], "skipped": [], "errors": [], "saved": False}
labels = actors_by_label()

try:
    directional = labels.get(os.getenv("WF_DIRECTIONAL_LABEL", "WF_Template_DirectionalLight_01"))
    skylight = labels.get(os.getenv("WF_SKYLIGHT_LABEL", "WF_Template_SkyLight_01"))
    accent = labels.get(os.getenv("WF_ACCENT_LABEL", "WF_Color_CoreAccentLight"))

    if directional:
        set_if_present(directional.get_component_by_class(unreal.DirectionalLightComponent), "intensity", 2.4, result["applied"], result["skipped"])
    if skylight:
        set_if_present(skylight.get_component_by_class(unreal.SkyLightComponent), "intensity", 0.58, result["applied"], result["skipped"])
    if accent:
        set_if_present(accent.get_component_by_class(unreal.PointLightComponent), "intensity", 170.0, result["applied"], result["skipped"])

    post_process = next((actor for actor in labels.values() if isinstance(actor, unreal.PostProcessVolume)), None)
    if post_process:
        set_if_present(post_process, "unbound", True, result["applied"], result["skipped"])
        settings = post_process.get_editor_property("settings")
        values = {
            "override_auto_exposure_method": True,
            "auto_exposure_method": unreal.AutoExposureMethod.AEM_MANUAL,
            "override_auto_exposure_min_brightness": True,
            "auto_exposure_min_brightness": 1.0,
            "override_auto_exposure_max_brightness": True,
            "auto_exposure_max_brightness": 1.0,
            "override_auto_exposure_bias": True,
            "auto_exposure_bias": 1.75,
            "override_bloom_intensity": True,
            "bloom_intensity": 0.12,
            "override_bloom_threshold": True,
            "bloom_threshold": 1.2,
        }
        for name, value in values.items():
            set_if_present(settings, name, value, result["applied"], result["skipped"])
        post_process.set_editor_property("settings", settings)

    result["saved"] = bool(unreal.EditorLevelLibrary.save_current_level())
except Exception as exc:
    result["errors"].append(str(exc))

evidence_path("p1y_stability_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
