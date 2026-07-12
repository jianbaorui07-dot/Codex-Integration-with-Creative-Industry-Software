# 造境WorldForge：虚幻引擎 3D 世界开发 Agent Example

This folder packages the local `codex接入UE` work as a repository-safe Unreal Engine evidence bundle.

当前宗旨：**先让 Codex 稳定接入 UE，能够打开工程、制作和优化基础场景、创建基础 NPC、自动保存与测试，再逐步扩展到角色动画、交互逻辑和可玩的游戏内容。**

The current checked-in bundle is the honest first stage of that direction. It preserves what was actually run and reviewed locally, while keeping unsafe/private runtime state out of Git.

Start with [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for the complete architecture and [RUN_HISTORY.md](RUN_HISTORY.md) for the phase-by-phase truth record.

## Folder Map

| Path | Purpose |
| --- | --- |
| `ue_project/Content/WorldForge/` | UE maps, blueprints, materials, UI, and editor utility assets created for the WorldForge sandbox. |
| `ue_project/Content/WorldForge/Scenes/` | Sanitized scene-specific WF0009 and WF0010 UE assets from the later WorldForge result project. |
| `ue_project/Content/Python/worldforge/` | UE Python build, validation, preview, recovery, and recipe-launch scripts from the current WorldForge workflow. |
| `ue_project/Config/WorldForge/` | Recipe and quality-policy configuration used by the reusable WorldForge execution layer. |
| `ue_project/Project8_WorldForge.uproject` | Minimal sanitized project descriptor copied from the enhanced UE project. |
| `control_layer/` | Offline control scripts, task schemas, task JSON, and sanitized execution evidence. |
| `tasks_and_checkpoints/` | Plans and checkpoint JSON used by the WorldForge offline workflow. |
| `evidence/` | Sanitized reports, performance baselines, stop reports, screenshots, and handoff docs. |
| `legacy_pre_audit/` | Earlier UE/Codex pre-audit scripts and evidence from the same local project line. |
| `p1y_color_stability/` | Sanitized P1Y/P2-Lite scripts, validation data, and the current honest capability boundary. |
| `manifest.json` | Generated package inventory and exclusion policy. |

## What Is Included

- WorldForge UE assets under `Content/WorldForge`.
- WF0009 SnowTemple micro-scene assets, receipts, black-frame preview defect evidence, and validation records.
- WF0010 DNABonsaiWorkshop R1 assets, receipts, preview metrics, and visual-pass evidence.
- WF0011 LowRiseFutureTechCity planning and universe-registry records only; no completed UE scene is claimed for WF0011.
- WorldForge v1.1 Python core, launchers, recipes, checkpoints, framework baseline, and command-center state files.
- Offline Agent Bridge scripts and task files.
- Checkpoint JSON evidence.
- v0.1, v0.2, and v0.3 handoff reports.
- Performance and safety reports.
- Screenshots from the early UE audit.
- P1Y color/exposure stability and complete humanoid-NPC validation summary.
- A repeatable 65-second Python-driven PIE patrol harness and dynamic NavMesh fix.

## What Is Excluded

- The private original UE project backup.
- Full enhanced project `Saved/` and `Intermediate/` folders.
- Raw UE logs with full telemetry URLs.
- UE crash dumps, private `Saved/Config` state, and raw editor recovery folders.
- pycache files.
- Global Codex config.
- Any software installer or downloaded external asset.

## Current Status

This package is an evidence bundle and prototype seed, not a finished Unreal plugin.

Verified or documented from the source run:

- UE 5.2.1 local project copy.
- `M_WorldForgeLab` and `M_WorldForgeBlockoutSandbox`.
- roughly 42 WorldForge-managed actors after the city upgrade task.
- offline task runner, city mood controller, explorer pawn, control desk, materials, and checkpoint evidence.
- WF0009 R1 has reproducible scene/build evidence but its preview record documents a true black-frame defect.
- WF0010 R1 has a validated map, 25 generated actors, a readable camera, lights/fog, and non-black preview metrics marked `PASS`.
- v1.1 separates recipes, state, receipts, quality policy, and command-center state so future runs can resume without treating screenshots or logs as success.
- no Remote Control or MCP enablement in the uploaded package.
- P1Y passed save/reopen, fixed-exposure, Blueprint compile, and three-complete-humanoid checks.
- P2-Lite moved, stopped, and resumed all three NPCs with a dynamic NavMesh during a 65-second external patrol test.

Still gated:

- UE GUI patch for the `ToggleCityMood` keyboard/UI path.
- Remote Control loopback-only command gate.
- stdio MCP bridge.
- autonomous Behavior Tree patrol; the current verified patrol is driven by a Python PIE test harness.
- large-scale dynamic generation and full playable game logic.
