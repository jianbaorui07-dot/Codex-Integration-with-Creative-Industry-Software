# 造境WorldForge：虚幻引擎 3D 世界开发 Agent

造境WorldForge is an Unreal Engine experiment for a local-first 3D world-development agent workflow.

当前宗旨：**先让 Codex 稳定接入 UE，能够打开工程、制作和优化基础场景、创建基础 NPC、自动保存与测试，再逐步扩展到角色动画、交互逻辑和可玩的游戏内容。**

This repository does not present that full vision as finished. The current package preserves the first local UE 5.2.1 evidence from the `codex接入UE` project: a WorldForge-prefixed sandbox, UE assets, offline task runner scripts, checkpoints, safety reports, performance evidence, and the stopped Remote Control/MCP handoff plan.

## Repository Package

The packaged artifact is here:

- `examples/unreal_worldforge_agent/`

It contains:

- `ue_project/Content/WorldForge/` - Unreal `.uasset` and `.umap` assets for the WorldForge sandbox content.
- `control_layer/` - offline Python control scripts, task schemas, task queue files, and sanitized execution evidence.
- `tasks_and_checkpoints/` - checkpoint and task plan JSON/Markdown evidence.
- `evidence/` - sanitized audit reports, performance reports, handoff reports, stop reports, and screenshots.
- `legacy_pre_audit/` - earlier UE pre-audit scripts and evidence used before the WorldForge package was created.
- `p1y_color_stability/` - repository-safe P1Y/P2-Lite scripts, validation summary, and honest completion boundary.
- `manifest.json` - generated inventory and package policy.

The package intentionally excludes the private original UE project backup, UE `Saved/` logs, UE `Intermediate/` caches, pycache files, and raw telemetry URLs.

## Current Proven State

- UE version verified in the source run: UE 5.2.1.
- WorldForge is a project prefix, not an external program.
- The editable WorldForge copy produced two maps: `M_WorldForgeLab` and `M_WorldForgeBlockoutSandbox`.
- The sandbox reached roughly 42 WorldForge-managed actors while staying below the 60 actor limit used in the safety gate.
- Existing WorldForge resources include offline task runner, city mood controller, explorer pawn, control desk, materials, maps, checkpoints, and handoff reports.
- Offline JSON-driven work and checkpoint evidence were created.
- Remote Control and MCP were deliberately not enabled because the local loopback and messaging safety checks were not ready.
- P1Y fixed exposure and restrained Bloom, preserved a neutral material hierarchy, created three complete Manny/Quinn-based humanoid NPCs, saved and reopened the result map, and compiled the related Blueprints without new errors.
- A dynamic RecastNavMesh and a repeatable Python PIE driver moved, stopped, and resumed all three NPCs during a 65-second test.

## Not Yet Claimed

The following remain roadmap items in this package:

- Fully verified keyboard/UI day-night toggle in PIE.
- Remote Control command gate bound only to loopback.
- stdio MCP bridge that talks to Unreal through the approved command gate.
- Autonomous Behavior Tree patrol; the verified P2-Lite patrol still uses a Python test driver.
- Playable game loops, full weather, and large-scale interactive object graphs.

## Safety Model

The WorldForge package follows the same local-first boundary as StarBridge:

- no software installation is required by the evidence package;
- no global Codex configuration is included;
- no firewall, registry, or environment variable changes are included;
- no public network service is started by the repository package;
- Remote Control and MCP remain documented as planned, gated work rather than silently enabled capabilities.
