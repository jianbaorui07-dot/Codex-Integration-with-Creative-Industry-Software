# WorldForge run history

This is the public, sanitized history of the `codex接入UE` / WorldForge work. Status labels describe verified evidence, not intended outcomes.

| Phase | What ran | Result | Public location |
| --- | --- | --- | --- |
| Legacy pre-audit | UE/Codex API probes, starter-scene creation and viewport adjustment | Baseline established | `legacy_pre_audit/` |
| Safety and enhanced copy | Read-only inventory, backup/copy reports, sandbox boundary | Completed | `evidence/audit_baseline`, `evidence/audit_logs` |
| Offline control layer | JSON tasks, schemas, offline runner and execution receipts | Completed prototype | `control_layer/` |
| WorldForge framework v0.1-v0.3 | Command router, safety controller, control desk, checkpoints and handoff reports | Completed evidence bundle; Remote Control stopped at safety gate | `ue_project/Content/WorldForge`, `evidence/handoff_docs` |
| First blockout sandbox | WorldForge lab/blockout maps and roughly 42 managed actors | Map/content evidence present; full behavior not claimed | `ue_project/Content/WorldForge/Maps`, checkpoints |
| WF0009 SnowTemple | Lightweight scene build, validation, preview and recovery probes | Build/validation evidence present; preview defect truthfully recorded | `ue_project/.../Scenes/WF0009_SnowTemple`, `evidence/receipts` |
| WF0010 DNA Bonsai Workshop | Recipe build, 25-actor validation, camera/light/fog and non-black preview metrics | PASS for recorded scene validation | `ue_project/.../Scenes/WF0010_DNABonsaiWorkshop`, receipts |
| WF0011 Low-rise future-tech city | Concept recipe and universe registry | Planning only; no finished map claimed at that stage | `evidence/universe_registry` |
| Disk-first canonical project | Project identity reconciliation, safe D-drive working copy and first boot | PASS locally; raw path registry excluded | summarized here and in handoff evidence |
| Low-rise tech-hub prototype | Basic roads, buildings, technology core, lights/cameras and placeholder NPC visuals | PARTIAL behavior proof | existing WorldForge assets and receipts |
| P1X color pass | Material hierarchy, light/color adjustments and viewport evidence | PARTIAL; main light remained too bright | superseded by P1Y summary |
| P1Y color stability | Fixed exposure, reduced Bloom, restrained main/sky/accent lights, independent materials | PASS | `p1y_color_stability/` |
| P1Y complete humanoids | Three complete Manny/Quinn NPCs with animation classes, ground contact, save/reopen and compile | PASS | `p1y_color_stability/evidence` |
| P2-Lite navigation | RecastNavMesh static-to-dynamic fix and reopen check | PASS for navigation data | `p1y_color_stability/scripts/p2lite_nav_fix.py` |
| P2-Lite patrol test | 65-second Python-driven PIE move/wait/move test for three NPCs | Patrol metrics PASS; overall P2-Lite PARTIAL | `p1y_color_stability/scripts/p2lite_external_patrol_pie.py` |
| Autonomous Behavior Tree | Blackboard/Behavior Tree asset shells and older Blueprint inspection | Not complete; no safe graph wiring evidence | recorded as a remaining boundary |
| GitHub system packaging | Sanitized scripts, receipts, status model and lifecycle documentation | This package | repository current branch |

## Local diagnostic work accounted for but not uploaded raw

The following categories were executed during P1X/P1Y/P2-Lite and remain local because they contain machine paths, transient editor state or oversized diagnostics:

- project/process/window/log identity probes;
- API, Character, CDO and Blueprint capability probes;
- camera position probes and temporary viewport scripts;
- map duplicate/source-switch/reopen phase receipts;
- raw precheck and working-state JSON with absolute paths;
- pause/resume and crash-reporter receipts;
- raw PIE snapshots sampled every second;
- raw UE logs, crash dumps and dialog captures;
- installed Third Person template content and Manny/Quinn `.uasset` files;
- screenshots from the private working project;
- DerivedDataCache, `Saved`, `Intermediate`, shader cache and pycache.

Their conclusions are consolidated in `p1y_color_stability/evidence/p1y_validation.public.json` and `P1Y_REPORT.md`.

## Next honest milestone

Wire the AIController and `BT_WF_NPC_Patrol` for autonomous random patrol-point selection, `Move To`, and 2-5 second waits; then repeat save/reopen and a driver-free 60-second PIE test before changing P2-Lite from `PARTIAL` to `PASS`.
