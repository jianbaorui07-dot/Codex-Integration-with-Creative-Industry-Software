"""Validate the current P1Y level without treating planned assets as proof."""

import json
import os
from pathlib import Path

import unreal

labels = tuple(filter(None, os.getenv("WF_NPC_LABELS", "WF_NPC_01_Humanoid,WF_NPC_02_Humanoid,WF_NPC_03_Humanoid").split(",")))
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by_label = {actor.get_actor_label(): actor for actor in actors}
result = {"npc_records": [], "fixed_exposure": False, "dynamic_navmesh": False, "errors": []}

for label in labels:
    actor = by_label.get(label)
    record = {"label": label, "exists": actor is not None, "mesh": None, "anim_class": None, "bounds_bottom_z": None}
    if actor:
        mesh = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        if mesh:
            skeletal_mesh = mesh.get_editor_property("skeletal_mesh")
            anim_class = mesh.get_editor_property("anim_class")
            origin, extent = actor.get_actor_bounds(False)
            record.update({"mesh": skeletal_mesh.get_path_name() if skeletal_mesh else None, "anim_class": anim_class.get_path_name() if anim_class else None, "bounds_bottom_z": origin.z - extent.z})
    result["npc_records"].append(record)

post_process = next((actor for actor in actors if isinstance(actor, unreal.PostProcessVolume)), None)
if post_process:
    settings = post_process.get_editor_property("settings")
    result["fixed_exposure"] = (
        settings.get_editor_property("auto_exposure_method") == unreal.AutoExposureMethod.AEM_MANUAL
        and settings.get_editor_property("auto_exposure_min_brightness") == settings.get_editor_property("auto_exposure_max_brightness")
    )

navmesh = next((actor for actor in actors if actor.get_class().get_name() == "RecastNavMesh"), None)
if navmesh:
    result["dynamic_navmesh"] = navmesh.get_editor_property("runtime_generation") == unreal.RuntimeGenerationType.DYNAMIC

result["complete_humanoids"] = len(result["npc_records"]) == 3 and all(item["exists"] and item["mesh"] and item["anim_class"] for item in result["npc_records"])
result["feet_near_ground"] = all(item["bounds_bottom_z"] is not None and abs(item["bounds_bottom_z"]) <= 5.0 for item in result["npc_records"])
result["status"] = "PASS" if result["complete_humanoids"] and result["feet_near_ground"] and result["fixed_exposure"] and result["dynamic_navmesh"] else "PARTIAL"

output = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())) / "WorldForge" / "p1y_validation.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
