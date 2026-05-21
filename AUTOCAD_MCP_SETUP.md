# AutoCAD MCP Setup

## GitHub Project

Selected project: https://github.com/daobataotie/CAD-MCP

Reason: it targets Windows CAD through COM and supports AutoCAD, GstarCAD, and ZWCAD. This matches the local AutoCAD 2026 install at:

```text
D:\AIGC\cad2026\CAD2026\AutoCAD 2026\acad.exe
```

## Local Paths

```text
C:\Users\jian\Documents\New project\cad-mcp-autocad
C:\Users\jian\Documents\New project\scripts\test_autocad_mcp.py
C:\Users\jian\Documents\New project\output\codex_autocad_mcp_test.dwg
C:\Users\jian\Documents\New project\output\codex_autocad_mcp_protocol_test.dwg
```

## Installed Python Packages

```powershell
python -m pip install --user pywin32 mcp pydantic
```

## Codex MCP Config

Added to `C:\Users\jian\.codex\config.toml`:

```toml
[mcp_servers.autocad]
command = "C:\\Users\\jian\\AppData\\Local\\Programs\\Python\\Python314\\python.exe"
args = ["C:\\Users\\jian\\Documents\\New project\\cad-mcp-autocad\\src\\server.py"]
startup_timeout_sec = 60
tool_timeout_sec = 120
```

Restart or reload Codex after editing the config so the new MCP tool namespace is available in the app.

## Verification

Run:

```powershell
python "C:\Users\jian\Documents\New project\scripts\test_autocad_mcp.py"
```

Expected result: the script lists 11 MCP tools, draws a rectangle and text in AutoCAD, then saves `codex_autocad_mcp_protocol_test.dwg` under the workspace `output` folder.
