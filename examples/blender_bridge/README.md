# Blender 三维场景桥

这个目录是 Blender bridge 的技术占位。当前 maturity 是 `planned`，只提供本机只读 probe，不生成模型、不渲染、不写 `.blend`。

## probe 做什么

- 检查 `STARBRIDGE_BLENDER_EXE` 或 `BLENDER_EXE` 是否存在。
- 检查 PATH 中是否能找到 `blender`。
- 可选读取命令线索，但不启动复杂渲染任务。
- 输出统一安全 JSON report。

## probe 不做什么

- 不创建真实模型。
- 不打开或保存 `.blend`。
- 不读取贴图、资产库或渲染缓存。

## 命令

```powershell
python examples\blender_bridge\probe.py
python examples\blender_bridge\probe.py --json
```
