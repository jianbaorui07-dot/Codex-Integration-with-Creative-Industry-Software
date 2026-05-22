# Illustrator 本地桥示例

这个目录只保存可公开的 Illustrator 接入示例。脚本不包含个人路径、素材路径、账号信息或授权信息；运行时请通过环境变量或参数传入本机配置。

## 前置条件

- Windows。
- 已授权可用的 Adobe Illustrator。
- PowerShell 可以创建 `Illustrator.Application` COM 对象。
- 运行前建议先手动打开 Illustrator，避免脚本触发不受控的登录或授权流程。

## 本地配置

真实安装路径只放本机环境变量，不写进仓库：

```powershell
$env:ILLUSTRATOR_EXE="<path-to-Illustrator.exe>"
```

## COM 探针

创建一个测试画板并导出 PNG：

```powershell
powershell -ExecutionPolicy Bypass -File examples\illustrator_bridge\scripts\com_probe.ps1 -OutputPath "$env:TEMP\codex_illustrator_probe.png"
```

返回结果为 JSON，包含 Illustrator 版本、输出路径、文档名称和页面对象数量。

## 图片转矢量

调用 Illustrator Image Trace，把输入图片追踪成矢量路径，并导出 SVG / AI / PNG 预览：

```powershell
powershell -ExecutionPolicy Bypass -File examples\illustrator_bridge\scripts\trace_image_to_vector.ps1 -InputPath "<source-image>" -OutputSvgPath "$env:TEMP\vector.svg"
```

`InputPath`、`OutputSvgPath`、`OutputAiPath`、`PreviewPngPath` 都通过参数传入。默认使用黑白追踪，适合线稿、手绘稿和高对比度草图；复杂灰度图可能需要调整 `-Threshold`。

## 安全边界

- 不提交 Illustrator 安装路径、Creative Cloud 缓存、账号、许可证、Cookie、token。
- 不提交 AI 私有工程、商业字体、商业笔刷、购买素材、客户图稿。
- 不提交源图路径、桌面路径、输出结果。
- 示例脚本只创建公开安全的程序化测试图形，并输出新文件。
