# 5. Codex 接入 Illustrator

这份文档说明 Codex 如何接入 Adobe Illustrator。公开仓库只保存通用协议、脚本和安全边界，不保存 Illustrator 安装路径、账号、授权信息、AI 私有工程、素材路径、源图文件名或桌面输出路径。

## 接入目标

- 让 Codex 连接已授权可用的本地 Illustrator。
- 通过 Windows COM + Illustrator JavaScript 做最小自动化。
- 支持创建测试画板、读取版本、绘制基础矢量对象并导出 PNG。
- 后续评估 UXP/CEP 面板和 MCP 工具层。

## 当前入口

| 文件或目录 | 用途 |
| --- | --- |
| `examples/illustrator_bridge/README.md` | Illustrator 示例说明 |
| `examples/illustrator_bridge/scripts/com_probe.ps1` | COM 探针，创建测试画板并导出 PNG |
| `examples/illustrator_bridge/scripts/trace_image_to_vector.ps1` | 调用 Image Trace，把输入图片转成 SVG / AI 矢量输出 |
| `examples/bridge_status.py` | 增加 Illustrator 状态检查，只读取通用环境和 COM 可用性 |

## 本地配置

真实路径只放本机环境变量或本地 `.env`：

```powershell
$env:ILLUSTRATOR_EXE="<path-to-Illustrator.exe>"
```

运行前建议手动打开 Illustrator，避免脚本触发不受控启动、登录或授权流程。

## 验证命令

```powershell
python examples\bridge_status.py --probe-executables
powershell -ExecutionPolicy Bypass -File examples\illustrator_bridge\scripts\com_probe.ps1 -OutputPath "$env:TEMP\codex_illustrator_probe.png"
```

COM 探针会创建一个公开安全的程序化测试画板，写入连接状态文字和基础矢量图形，并导出 PNG 到参数指定路径。

图片转矢量：

```powershell
powershell -ExecutionPolicy Bypass -File examples\illustrator_bridge\scripts\trace_image_to_vector.ps1 -InputPath "<source-image>" -OutputSvgPath "$env:TEMP\vector.svg"
```

脚本会调用 Illustrator Image Trace，展开为路径后输出 SVG、AI 和 PNG 预览。线稿适合先用黑白追踪；如果线条过粗或过细，可以调整 `-Threshold`。

## 安全边界

- 不提交 Illustrator 安装路径、Creative Cloud 缓存、账号、许可证、Cookie、token。
- 不提交 AI 私有工程、商业字体、商业笔刷、购买素材、客户图稿。
- 不提交源图路径、桌面路径、输出结果。
- 所有会导出的脚本默认输出新文件，不覆盖原图或已有工程。

## 后续优化

- 增加读取当前文档名称、画板数量、选中对象数量的只读探针。
- 增加 PDF 导出示例，输出路径继续由参数传入。
- 把稳定动作封装成 MCP：`get_document_info`、`create_vector_probe`、`export_png`。
