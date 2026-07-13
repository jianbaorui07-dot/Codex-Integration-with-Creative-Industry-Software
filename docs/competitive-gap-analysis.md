# 同类创意软件 MCP 项目差距分析

更新时间：2026-07-13。

这份分析只比较公开仓库已经展示的架构与接口，不复制第三方源码，也不把外部项目的能力写成 StarBridge 已验证能力。

## 参考项目与先进点

| 一手来源 | 值得吸收的能力 | StarBridge 当前差距 |
| --- | --- | --- |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | Blender addon 与 MCP server 双向 socket；场景检查、对象/材质控制、viewport screenshot | 目前只有环境探针、scene plan 和 reference reconstruction plan，没有受控的 live sandbox adapter 或视觉回看闭环 |
| [sandraschi/blender-mcp](https://github.com/sandraschi/blender-mcp) | 按 scene/object/render 等域组织高层工具，并提供 dashboard/telemetry | 已有统一 registry 和前端原型，但缺少跨 bridge 的实时 operation telemetry 与状态差异展示 |
| [artokun/comfyui-mcp](https://github.com/artokun/comfyui-mcp) | workflow 可视化/组合、WebSocket 进度、完成通知、持久化生成历史、debug hooks | 已有 compose/validate/repair/lifecycle，但此前缺少 workflow 图、实时进度与可恢复历史 |
| [IO-AtelierTech/comfyui-mcp](https://github.com/IO-AtelierTech/comfyui-mcp) | queue/history/interrupt/object_info 等完整作业控制面 | `agent_run` 已有安全门，但还没有只读 queue snapshot、受控 cancel 与 history 摘要 |
| [alisaitteke/photoshop-mcp](https://github.com/alisaitteke/photoshop-mcp) | 每次操作后返回 document/layer context，降低模型失去软件状态的概率 | 已有 `ps.get_state` / `ps.get_preview`，但没有给所有 recipe 统一附加 before/after state delta |
| [MCP 官方 TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md) | sampling、elicitation 与实验性 tasks 支持长任务、补充输入和异步恢复 | 当前 stdio server 只支持同步 `tools/call`；JobStatus 是统一数据模型，还不是 MCP Tasks 协议实现 |
| [MCP 官方规范仓库](https://github.com/modelcontextprotocol/modelcontextprotocol) | 协议 schema、能力协商与持续演进的扩展机制 | 已声明 tools/resources/prompts，但尚未实现任务、进度和 UI extension 能力协商 |

## 优先级

| 优先级 | 增强项 | 原因 | 当前状态 |
| --- | --- | --- | --- |
| P0 | ComfyUI workflow → Mermaid + 脱敏结构摘要 | 纯内存、跨平台、立刻提升 Codex 对复杂 graph 的理解 | 本轮已实现 `comfy.workflow_visualize` |
| P1 | 统一 operation context envelope | 每次 recipe 返回 before/after state、warnings、evidence 引用 | 待实现 |
| P1 | 只读 queue snapshot + 结构化进度 | 支撑长任务监控，不需要先开放生成或写入 | 待实现 |
| P2 | MCP Tasks / progress capability | 支持 call-now/fetch-later 和断线恢复 | 待客户端兼容矩阵与协议测试 |
| P2 | Blender/Adobe live sandbox adapter | 才能形成真实软件控制闭环 | 需要本机授权软件、显式确认与独立安全审查 |
| P3 | MCP App dashboard | 让状态、graph、证据和确认门可交互 | 需先稳定 P1/P2 数据协议 |

## 本轮采用的设计

`comfy.workflow_visualize` 只接受内联 API-format workflow：

- 输出 Mermaid、节点类别、节点数和连线数；
- 不输出 prompt、模型名或任何 input value；
- 不接收文件路径，不读取本机 workflow；
- 不访问 ComfyUI API，不提交队列；
- 复用现有 workflow validator，并保留结构化 validation errors；
- 作为 safe-only MCP tool 暴露，供 Codex 在 compose/repair 后立即审阅 graph。

下一轮优先实现统一 operation context envelope，然后再评估只读任务进度；不会直接照搬第三方项目中的任意 Python/JSX 执行能力。
