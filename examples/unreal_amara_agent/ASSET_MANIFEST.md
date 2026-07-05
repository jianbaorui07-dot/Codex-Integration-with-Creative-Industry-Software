# Asset Manifest

The Amara package includes a compact UE content subset and the evidence needed to understand how it was produced.

## UE Content

The UE assets live in `ue_project/Content/Amara/`.

Top-level content groups:

- `Blueprints`
- `EditorTools`
- `Maps`
- `Materials`
- `RemoteControl`
- `UI`

Known important assets from the source run:

- `Maps/M_AmaraLab.umap`
- `Maps/M_AmaraBlockoutSandbox.umap`
- `Blueprints/BP_AmaraOfflineTaskRunner.uasset`
- `Blueprints/BP_AmaraCityMoodController.uasset`
- `Blueprints/BP_AmaraExplorerPawn.uasset`
- `EditorTools/EUW_AmaraControlDesk.uasset`
- `UI/WBP_AmaraStatus.uasset`

## Evidence

Evidence is intentionally text-first and sanitized:

- `evidence/audit_baseline`
- `evidence/audit_logs`
- `evidence/handoff_docs`
- `evidence/legacy_summary`
- `evidence/performance`
- `evidence/screenshots`

## Exclusion Policy

The package excludes full UE runtime folders and the original project backup. This keeps the GitHub repository focused on the Amara agent framework evidence rather than private machine state.
