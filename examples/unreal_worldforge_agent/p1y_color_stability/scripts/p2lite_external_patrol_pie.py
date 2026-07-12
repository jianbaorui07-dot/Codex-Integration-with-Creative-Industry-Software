"""External 65-second PIE patrol verifier used while Behavior Tree wiring is pending.

This is a validation harness, not autonomous gameplay logic.
"""

import json
import math
import os
import time
import traceback
from pathlib import Path

import unreal

NPC_LABELS = tuple(filter(None, os.getenv("WF_NPC_LABELS", "WF_NPC_01_Humanoid,WF_NPC_02_Humanoid,WF_NPC_03_Humanoid").split(",")))
ROUTES = {
    NPC_LABELS[0]: [(-380.0, -760.0, 98.0), (120.0, -720.0, 98.0), (-120.0, -420.0, 98.0)],
    NPC_LABELS[1]: [(-1050.0, 560.0, 98.0), (-620.0, 520.0, 98.0), (-820.0, 260.0, 98.0)],
    NPC_LABELS[2]: [(900.0, 420.0, 98.0), (560.0, 500.0, 98.0), (720.0, 180.0, 98.0)],
}
PHASES = [(3.0, "move_1", 1), (15.0, "wait_1", None), (20.0, "move_2", 2), (34.0, "wait_2", None), (39.0, "move_3", 0), (53.0, "wait_3", None), (58.0, "move_4", 1)]

output = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())) / "WorldForge" / "p2lite_pie_state.json"
output.parent.mkdir(parents=True, exist_ok=True)
state = {
    "status": "STARTING",
    "elapsed_seconds": 0.0,
    "phase": "starting",
    "events": [],
    "metrics": {label: {"initial": None, "latest": None, "max_displacement": 0.0, "max_speed": 0.0, "moving_samples": 0, "idle_samples": 0} for label in NPC_LABELS},
    "error": "",
}
start = time.monotonic()
next_phase = 0
last_sample = 0.0
handle = None


def write_state():
    output.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def game_world():
    try:
        return unreal.EditorLevelLibrary.get_game_world()
    except Exception:
        return None


def npcs(world):
    actors = unreal.GameplayStatics.get_all_actors_with_tag(world, "HumanoidNPC") if world else []
    return {actor.get_actor_label(): actor for actor in actors if actor.get_actor_label() in NPC_LABELS}


def issue(name, route_index, found, elapsed):
    event = {"elapsed": round(elapsed, 3), "phase": name, "requests": []}
    for label, actor in found.items():
        controller = actor.get_controller()
        if controller is None:
            actor.spawn_default_controller()
            controller = actor.get_controller()
        if route_index is None:
            controller.stop_movement()
            result = "STOPPED"
        else:
            request = controller.move_to_location(unreal.Vector(*ROUTES[label][route_index]), 45.0, True, True, True, False, None, True)
            result = str(request)
        event["requests"].append({"label": label, "result": result})
    state["events"].append(event)
    state["phase"] = name


def sample(found):
    waiting = state["phase"].startswith("wait")
    for label, actor in found.items():
        metrics = state["metrics"][label]
        loc = actor.get_actor_location()
        current = [loc.x, loc.y, loc.z]
        speed = actor.get_velocity().length()
        if metrics["initial"] is None:
            metrics["initial"] = current
        metrics["latest"] = current
        displacement = math.dist(metrics["initial"], current)
        metrics["max_displacement"] = max(metrics["max_displacement"], displacement)
        metrics["max_speed"] = max(metrics["max_speed"], speed)
        if speed >= 15.0:
            metrics["moving_samples"] += 1
        if waiting and speed <= 5.0:
            metrics["idle_samples"] += 1


def finish(elapsed):
    global handle
    values = list(state["metrics"].values())
    patrol = all(item["max_displacement"] >= 80.0 for item in values)
    walk = all(item["max_speed"] >= 15.0 and item["moving_samples"] >= 3 for item in values)
    idle = all(item["idle_samples"] >= 2 for item in values)
    state.update({"elapsed_seconds": round(elapsed, 3), "patrol_verified": patrol, "walk_verified": walk, "idle_verified": idle, "status": "PASS_EXTERNAL_PATROL" if patrol and walk and idle else "PARTIAL"})
    write_state()
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None


def tick(delta_seconds):
    global next_phase, last_sample
    elapsed = time.monotonic() - start
    state["elapsed_seconds"] = round(elapsed, 3)
    try:
        world = game_world()
        found = npcs(world)
        if len(found) != 3:
            if elapsed > 12.0:
                raise RuntimeError(f"Expected three tagged humanoid NPCs, found {sorted(found)}")
            return
        if next_phase < len(PHASES) and elapsed >= PHASES[next_phase][0]:
            _, name, route_index = PHASES[next_phase]
            issue(name, route_index, found, elapsed)
            next_phase += 1
        if elapsed - last_sample >= 1.0:
            last_sample = elapsed
            sample(found)
            write_state()
        if elapsed >= 65.0:
            finish(elapsed)
    except Exception:
        state["status"] = "FAILED"
        state["error"] = traceback.format_exc()
        finish(elapsed)


level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if level.is_in_play_in_editor():
    level.editor_request_end_play()
level.editor_play_simulate()
state["status"] = "RUNNING"
write_state()
handle = unreal.register_slate_post_tick_callback(tick)
