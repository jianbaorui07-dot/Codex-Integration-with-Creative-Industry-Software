# CAD / AutoCAD 工程制图桥

这个目录保存 AutoCAD 本地桥的最小安全结构。当前只做本机环境 probe，不打开真实 DWG，不写入 DWG，不读取客户图纸。

## probe 做什么

- 检查当前系统是否 Windows。
- 检查是否设置 `STARBRIDGE_CAD_MODE`。
- 检查 `AUTOCAD_EXE` 或 PATH 中是否能找到 `acad`。
- 在 Windows 上检查 `AutoCAD.Application` COM 注册线索。
- 输出统一安全 JSON report。

## probe 不做什么

- 不打开真实 DWG。
- 不创建或保存 CAD 文件。
- 不读取客户图纸、授权文件或真实项目输出。
- 不把真实安装路径写进 report。

## 命令

```powershell
python examples\cad_bridge\probe.py
python examples\cad_bridge\probe.py --json
```

report 默认写入 `examples/cad_bridge/reports/cad_autocad_probe_report.json`，`reports/` 已被 `.gitignore` 忽略。
