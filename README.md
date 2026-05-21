# New Project Workspace

This repository is a mixed local workspace for small frontend demos, Python document/CAD scripts, and an AutoCAD MCP subproject. It is not a single packaged application yet.

## Main Areas

- `src/` - static browser demo with `index.html`, `styles.css`, and `app.js`.
- `virtual-pet/` - standalone static browser demo. Open `virtual-pet/index.html` in a browser.
- `cad-mcp-autocad/` - AutoCAD MCP server project with its own README files and `requirements.txt`.
- `scripts/` - Python utility scripts for report generation and AutoCAD drawing automation.
- `overtime-analysis-deck/` - slide deck generation workspace.
- `output/`, `scratch/`, `docx_render_check/`, `.codex_video_frames/`, `.codex_video_deps/` - generated artifacts, caches, or render outputs.

## Current Runtime Notes

- Root `package.json` exists but only declares `"private": true` and `"type": "module"`; it does not define npm scripts.
- Root `requirements.txt` does not exist. Python dependencies vary by script.
- `cad-mcp-autocad/requirements.txt` lists the Python dependencies for the AutoCAD MCP server.
- This workspace currently does not use a ComfyUI `custom_nodes/` layout.

## Running Locally

Static browser demos:

```powershell
# Open either file directly in a browser
src\index.html
virtual-pet\index.html
```

AutoCAD MCP subproject:

```powershell
cd cad-mcp-autocad
python -m pip install -r requirements.txt
python src\server.py
```

Python utility scripts:

```powershell
python scripts\<script-name>.py
```

Some scripts require Windows-only automation packages such as `pywin32`, local AutoCAD, or document-generation packages such as `python-docx`, `pandas`, `opencv-python`, and `numpy`. Check imports before running an individual script.

## GitHub / Jules Readiness

Before using Jules, push only source files and useful documentation. Avoid committing dependency folders, render outputs, caches, and generated binary artifacts unless they are intentionally part of the project.

Recommended first Jules task: ask Jules to read the repository and report structure, entry points, run methods, risks, and candidate next tasks without changing files.
