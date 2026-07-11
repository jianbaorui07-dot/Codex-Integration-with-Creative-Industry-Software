# StarBridge Backend

StarBridge now has a small local HTTP backend for building a real software UI on
top of the existing MCP tools. It uses only the Python standard library and
reuses `starbridge_mcp.mcp_server.handle_request`, so REST calls and MCP calls
share the same safety rules, tool registry, recipes, resources, and evidence
contracts.

## Start

Run the backend and frontend together:

```powershell
npm.cmd run app:dev
```

Run only the backend:

```powershell
npm.cmd run starbridge:backend
```

After building the frontend, the backend also serves the UI from `/`:

```powershell
npm.cmd --prefix examples\starbridge_frontend run build
npm.cmd run starbridge:backend
```

Default URL:

```text
http://127.0.0.1:8765
```

Custom host or port:

```powershell
python -m starbridge_mcp.backend --host 127.0.0.1 --port 8787
```

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Backend health and StarBridge server info. |
| `GET` | `/api/status?bridge=all` | Safe bridge status summary. |
| `GET` | `/api/capabilities?safe_only=true` | `starbridge.capabilities.v2` registry for UI routing. |
| `GET` | `/api/tools` | MCP tool definitions for form generation. |
| `GET` | `/api/resources` | MCP resource list. |
| `GET` | `/api/resource?uri=starbridge://capabilities` | Read one MCP resource. |
| `GET` | `/api/recipes?bridge=all` | Reviewed cross-bridge recipes. |
| `GET` | `/api/bootstrap` | One-call startup payload for the UI. |
| `GET` | `/api/catalog` | Monetizable recipe catalog cards for the UI. |
| `GET` | `/api/tiers` | Free / Pro / Team product packaging model. |
| `GET` | `/api/hybrid` | Local desktop lane and cloud GPU lane policy. |
| `GET` | `/api/audit/history` | Local recipe plan/evidence audit events. |
| `DELETE` | `/api/audit/history` | Clear local audit events. |
| `GET` / `POST` | `/api/recipes/{recipe_id}/plan` | Dry-run action plan and quality gates. |
| `GET` / `POST` | `/api/recipes/{recipe_id}/evidence` | Standard `EvidenceManifest` preview. |
| `POST` | `/api/recipes/{recipe_id}/run` | Confirmed safe execution request record. Requires `confirm_run=true`. |
| `POST` | `/api/tools/call` | Generic MCP tool call wrapper. |

## Example

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
Invoke-RestMethod "http://127.0.0.1:8765/api/capabilities?safe_only=true"
Invoke-RestMethod http://127.0.0.1:8765/api/catalog
Invoke-RestMethod http://127.0.0.1:8765/api/tiers
Invoke-RestMethod http://127.0.0.1:8765/api/hybrid
Invoke-RestMethod http://127.0.0.1:8765/api/recipes/comfyui_txt2img_lifecycle/plan
Invoke-RestMethod http://127.0.0.1:8765/api/recipes/comfyui_txt2img_lifecycle/run `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"confirm_run":true,"execution_target":"cloud"}'
```

## Safety

- The backend does not add new write powers.
- Guarded tools still require their existing `confirm_write`, `confirm_export`,
  or `confirm_run` flags.
- `/api/recipes/{recipe_id}/run` records a confirmed safe request and audit event;
  it does not launch desktop software from the product UI.
- CORS is enabled for local frontend development.
- Outputs are sanitized by the existing StarBridge sanitizer before returning JSON.
