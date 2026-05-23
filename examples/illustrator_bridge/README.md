# Illustrator / AI 矢量文件桥

这个目录是 Illustrator bridge 的技术占位。当前 maturity 是 `planned`，只提供 Windows-first 安全 probe，不写复杂 JSX，不打开用户 `.ai` 文件，不导出 SVG/PDF/PNG。

## probe 做什么

- 检查当前系统是否 Windows。
- 检查 `ILLUSTRATOR_EXE` 是否配置并存在。
- 检查 `Illustrator.Application` COM 类型是否可用。
- 输出统一安全 JSON report。

## probe 不做什么

- 不打开客户 `.ai`。
- 不读取源图、字体、商业画笔或购买素材。
- 不保存导出结果。

## 命令

```powershell
powershell -ExecutionPolicy Bypass -File examples\illustrator_bridge\probe.ps1
```
