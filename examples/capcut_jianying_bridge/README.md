# 剪映 / CapCut 草稿桥

这个目录是剪映 / CapCut bridge 的研究占位。当前 maturity 是 `research`，不提供自动控制桌面版的代码，也不声称已经接入。现阶段只允许做本机草稿目录和公开 API 情况的安全调研。

## probe 做什么

- 检查是否配置 `JIANYING_EXE` / `CAPCUT_EXE`。
- 检查是否配置 `JIANYING_DRAFTS_DIR` / `CAPCUT_DRAFTS_DIR`。
- 只返回布尔状态，不输出真实路径。
- 输出统一安全 JSON report。

## probe 不做什么

- 不控制桌面版剪映或 CapCut。
- 不打开真实草稿。
- 不读取素材、字幕原稿、账号、会员状态或导出视频。
- 不写入草稿文件。

## 命令

```powershell
python examples\capcut_jianying_bridge\probe.py
python examples\capcut_jianying_bridge\probe.py --json
```
