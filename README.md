# Codex 软件接入实验仓库

这个仓库只发布和 **Codex 接入各类本地软件** 有关的协议、示例脚本、状态检查工具和配置说明。当前重点是三条已经实践过的本地创作桥：ComfyUI、Blender、CAD。

不属于这个范围的网页 demo、报告生成脚本、图片素材、PPT 工作区、临时输出和缓存，只保留在本机，不再作为 GitHub 发布内容。

## 项目目标

- 让 Codex 能通过脚本或 MCP 调用本机创作软件。
- 把可公开协作的说明、示例和检查脚本沉淀到 GitHub。
- 保持账号、模型、素材、生成结果、客户图纸和授权信息不进入仓库。
- 为后续接入 Photoshop、Figma、Penpot、Krita 等工具保留清晰路线。

## 当前发布范围

| 目录或文件 | 用途 |
| --- | --- |
| `docs/starbridge-link-protocol.md` | 星桥三联主说明：Codex 接入 ComfyUI、Blender、CAD 的整体方案 |
| `docs/codex-drawing-tool-integrations.md` | 绘画、图像、设计、三维、制图工具的接入路线图 |
| `docs/中文用途索引.md` | 仓库文件中文用途索引 |
| `examples/bridge_status.py` | 一次检查 ComfyUI、Blender、CAD 三条桥的本机状态 |
| `examples/comfy_bridge/` | ComfyUI API 探针、文生图脚本和 workflow 示例 |
| `cad-mcp-autocad/` | AutoCAD MCP 子项目 |
| `AUTOCAD_MCP_SETUP.md` | AutoCAD MCP 本地配置记录 |
| `scripts/test_autocad_mcp.py` | AutoCAD MCP 连接测试脚本 |
| `scripts/draw_*.py`、`scripts/trace_*.py` | AutoCAD 自动绘图示例 |
| `package.json` | 本地桥接检查快捷命令 |

## 快速开始

检查 ComfyUI、Blender、CAD 三条桥：

```powershell
python examples\bridge_status.py
python examples\bridge_status.py --json
python examples\bridge_status.py --probe-executables
```

也可以使用 npm 快捷命令：

```powershell
npm.cmd run bridge:status:json
```

如果 PowerShell 拦截 `npm.ps1`，请使用 `npm.cmd`。

## ComfyUI 接入

先启动本机 ComfyUI：

```powershell
D:\AIGC\Start_ComfyUI_Codex.cmd
```

然后运行探针：

```powershell
python examples\comfy_bridge\comfy_probe.py
```

提交基础文生图任务：

```powershell
python examples\comfy_bridge\run_txt2img.py --prompt "a quiet futuristic tea house in a garden"
```

## Blender 接入

当前本机路径：

```text
D:\AIGC\CAD\blender.exe
D:\AIGC\blender-mcp
```

状态脚本会自动识别 Blender 可执行文件和 Blender MCP 桥目录。需要确认版本时运行：

```powershell
python examples\bridge_status.py --probe-executables
```

## CAD 接入

AutoCAD MCP 子项目位于：

```text
cad-mcp-autocad/
```

安装依赖并启动服务：

```powershell
cd cad-mcp-autocad
python -m pip install -r requirements.txt
python src\server.py
```

测试 AutoCAD MCP：

```powershell
python scripts\test_autocad_mcp.py
```

## 本机路径约定

| 项目 | 路径 |
| --- | --- |
| ComfyUI 启动脚本 | `D:\AIGC\Start_ComfyUI_Codex.cmd` |
| ComfyUI 根目录 | `D:\AIGC\comfyui安装包\ComfyUI` |
| Blender 可执行文件 | `D:\AIGC\CAD\blender.exe` |
| Blender MCP 桥目录 | `D:\AIGC\blender-mcp` |
| AutoCAD 可执行文件 | `D:\AIGC\cad2026\CAD2026\AutoCAD 2026\acad.exe` |
| 新下载源码和安装包 | `E:\00_待整理收件箱\下载` |

新下载的源码、安装包和调研资料先放到 `E:\00_待整理收件箱\下载`。不要把模型、生成图、渲染输出、DWG 成品、浏览器资料或授权文件放进 Git 工作区。

## 不发布内容

以下内容只保留本机，不进入 GitHub：

- 网页 demo、虚拟宠物 demo、PPT 工作区。
- 报告生成脚本、样式参考图片、临时研究文档。
- `output/`、`scratch/`、`docx_render_check/`、缓存和日志。
- ComfyUI 模型、LoRA、VAE、ControlNet、生成图片。
- Blender 私有 `.blend`、贴图、资产库和渲染缓存。
- CAD 客户图纸、商业 DWG、授权文件。
- 密码、token、Cookie、OAuth 缓存、浏览器数据、支付信息。

## 后续方向

- 增加 ComfyUI 的 `img2img`、upscale、inpaint、批量 prompt 示例。
- 增加 Blender 公开安全场景生成脚本。
- 增加 CAD 标准零件参数化绘图脚本。
- 评估 Photoshop、Penpot、Figma、Krita 的 MCP 或脚本接入方式。
- 将稳定脚本逐步包装成 Codex 可调用的 MCP 工具。
