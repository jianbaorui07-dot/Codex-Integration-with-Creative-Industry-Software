# P1Y Color Stability + Humanoid NPC

This package is the repository-safe record of the `WF-P1Y-ColorStability-HumanoidNPC` run.

## Mission

先让 Codex 稳定接入 UE，能够打开工程、制作和优化基础场景、创建基础 NPC、自动保存与测试，再逐步扩展到角色动画、交互逻辑和可玩的游戏内容。

## Verified locally

- Unreal Engine 5.2.1 opened the existing project and a safe duplicated result map.
- Manual exposure was fixed, Bloom was reduced, and the main/sky/accent lights were restrained.
- Three complete Manny/Quinn humanoids were visible with head, torso, arms, hands, legs and feet.
- The result map saved, reopened and recompiled four related Blueprints without a new compile error.
- RecastNavMesh was changed from static to dynamic and survived reopen.
- A 65-second PIE test moved, stopped and resumed all three NPCs. Peak sampled speed was 165 cm/s.

## Honest boundary

P1Y is `PASS`. P2-Lite is `PARTIAL`: the navigation and animation test passed through the repeatable Python PIE driver in `scripts/`, but the Behavior Tree asset itself is not wired for autonomous random patrol. The package does not claim a finished game or a finished Unreal MCP bridge.

## Files

- `scripts/p1y_stability_pass.py` applies the verified exposure/light settings idempotently to an already-open level.
- `scripts/p1y_validate.py` validates exposure, humanoid meshes, animation classes, ground contact and dynamic NavMesh.
- `scripts/p2lite_nav_fix.py` switches the current map's RecastNavMesh to dynamic generation and saves it.
- `scripts/p2lite_external_patrol_pie.py` is the external 65-second movement/idle verification harness.
- `evidence/` contains sanitized status and validation summaries without local paths, usernames, process IDs or raw logs.

These scripts are editor-side examples. Back up the target map and confirm the active project before running them.
