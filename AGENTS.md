# Agent Instructions

This repository is a mixed local workspace, not a single production app. Prefer small, scoped changes and explain assumptions before editing.

## Important Directories

- `src/`: static frontend demo.
- `virtual-pet/`: standalone static frontend demo.
- `cad-mcp-autocad/`: AutoCAD MCP server subproject. Follow its local README and `requirements.txt`.
- `scripts/`: Python utility scripts for documents, GitHub reports, and AutoCAD automation.
- `output/`, `scratch/`, `docx_render_check/`, `.codex_video_frames/`, `.codex_video_deps/`, `node_modules/`, `__pycache__/`: generated artifacts, caches, dependencies, or temporary outputs.

## Change Rules

- Do not edit generated artifacts, caches, dependency folders, or render outputs unless the task explicitly asks for that exact file.
- Do not delete files or perform broad restructures without explicit approval.
- For frontend changes, keep edits inside the relevant app directory (`src/` or `virtual-pet/`) unless shared configuration is clearly required.
- For Python scripts, inspect imports and expected input/output paths before changing behavior.
- For `cad-mcp-autocad/`, keep changes within that subproject unless root documentation needs an update.
- Avoid committing secrets, tokens, cookies, browser data, payment data, or private credentials.
- If a task requires login, subscription, CAPTCHA, GitHub authorization, or account approval, stop and ask the human to complete it manually.

## Validation Guidance

- Static frontend demos can usually be checked by opening their `index.html` files in a browser.
- Python scripts may require optional packages such as `python-docx`, `pandas`, `opencv-python`, `numpy`, `pywin32`, or `mcp`.
- AutoCAD automation requires Windows and a local AutoCAD installation.
- The root `package.json` currently has no npm scripts, so do not assume `npm test` or `npm run build` exists.

## First-Pass Jules Behavior

For the first task in Jules, operate read-only:

- Summarize repository structure.
- Identify entry points and run commands.
- Identify dependency gaps and generated directories.
- Suggest small, safe next tasks.
- Do not modify files until the human approves a follow-up implementation task.
