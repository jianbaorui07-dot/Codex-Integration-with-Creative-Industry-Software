"""Make the current map's RecastNavMesh runtime-safe and save the map."""

import json
from pathlib import Path

import unreal

saved = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())) / "WorldForge"
saved.mkdir(parents=True, exist_ok=True)
result = {"status": "PARTIAL", "old_runtime_generation": None, "new_runtime_generation": None, "saved": False, "errors": []}

try:
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    navmesh = next((actor for actor in actors if actor.get_class().get_name() == "RecastNavMesh"), None)
    if navmesh is None:
        raise RuntimeError("RecastNavMesh was not found in the current level")
    old = navmesh.get_editor_property("runtime_generation")
    result["old_runtime_generation"] = str(old)
    if old != unreal.RuntimeGenerationType.DYNAMIC:
        navmesh.set_editor_property("runtime_generation", unreal.RuntimeGenerationType.DYNAMIC)
        navmesh.modify()
    result["new_runtime_generation"] = str(navmesh.get_editor_property("runtime_generation"))
    world = unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    result["saved"] = bool(unreal.EditorLevelLibrary.save_current_level())
    result["status"] = "PASS" if result["saved"] else "PARTIAL"
except Exception as exc:
    result["errors"].append(str(exc))

(saved / "p2lite_nav_fix.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
