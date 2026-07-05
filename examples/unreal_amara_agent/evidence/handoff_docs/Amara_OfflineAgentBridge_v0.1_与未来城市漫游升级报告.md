# Amara OfflineAgentBridge v0.1 与未来城市漫游升级报告

生成时间：2026-07-05 15:05:46 +08:00
总体状态：完成离线桥接与未来城市可漫游夜景升级；停止在离线流程，未进入 Remote Control、MCP、角色、骨骼、NPC、天气、地形或完整游戏阶段。

## 安全边界

- 原项目8是否修改：否。最终复核：原项目与只读备份哈希差异数 0。
- 是否安装软件：否。
- 是否升级 UE：否，仍为 UE 5.2.1。
- 是否启用 UDP Messaging：否；启动使用一次性 -UDPMESSAGING_TRANSPORT_ENABLE=False，未发现 UDP 6666、0.0.0.0、230.0.0.1 或 192.168.x.x Messaging 绑定。
- 是否启用 Remote Control：否。
- 是否启用 MCP：否。
- 是否启动 HTTP/WebSocket 服务：否；30010/30020/8000/6666/30000 复核为空闲。
- 是否修改全局 Codex 配置：否。<CODEX_HOME>\config.toml SHA256：B2638BC00D387E95D9BC97AD4ED038FB3AB5A5B4B1692F03224A4A9E31DD5970。

## DataRouter 来源核查结果

详见：<AMARA_ROOT>\07_文档与报告\DataRouter_来源核查.md

结论：DataRouter 来自 UE Editor Analytics / Event Stream。关键证据为 LogAnalytics: [UEEditor.Rocket.Release] APIServer = https://datarouter.ol.epicgames.com/、AnalyticsET 模块关闭、POST URL 内 UploadType=eteventstream。日志状态为 Processing，未证明发送成功完成。

是否修改 UE Bug Reports 隐私设置：否。原因：本次未通过 UE 图形界面操作，且来源更明确指向 Analytics Event Stream；未手动编辑 AppData、注册表、防火墙、网络设置、引擎目录或原项目。

## 新建离线 Agent 文件清单

- <AMARA_ROOT>\03_Amara控制层\amara_build_v01.py | 18126 bytes | 2026-07-05T14:37:07
- <AMARA_ROOT>\03_Amara控制层\Docs\Amara_任务白名单.md | 400 bytes | 2026-07-05T14:56:59
- <AMARA_ROOT>\03_Amara控制层\Docs\Amara_离线执行说明.md | 676 bytes | 2026-07-05T14:56:59
- <AMARA_ROOT>\03_Amara控制层\Logs\Amara_OfflineBridge_任务002执行摘要.md | 298 bytes | 2026-07-05T15:03:35
- <AMARA_ROOT>\03_Amara控制层\Logs\Amara_OfflineBridge_任务002执行结果.json | 6595 bytes | 2026-07-05T15:03:35
- <AMARA_ROOT>\03_Amara控制层\Logs\Amara_OfflineBridge_任务002执行结果_failed_20260705_150246.json | 1347 bytes | 2026-07-05T15:01:40
- <AMARA_ROOT>\03_Amara控制层\Logs\Amara_OfflineBridge_建立日志.md | 466 bytes | 2026-07-05T14:56:59
- <AMARA_ROOT>\03_Amara控制层\Schemas\amara_task_schema.json | 4092 bytes | 2026-07-05T14:57:25
- <AMARA_ROOT>\03_Amara控制层\Scripts\amara_offline_upgrade_v01.py | 22304 bytes | 2026-07-05T15:02:20
- <AMARA_ROOT>\03_Amara控制层\Scripts\__pycache__\amara_offline_upgrade_v01.cpython-314.pyc | 35282 bytes | 2026-07-05T15:02:20
- <AMARA_ROOT>\03_Amara控制层\Tasks\Completed\002_未来城市漫游升级.json | 612 bytes | 2026-07-05T14:57:25
- <AMARA_ROOT>\03_Amara控制层\Tasks\Inbox\002_未来城市漫游升级.json | 612 bytes | 2026-07-05T14:57:25
- <AMARA_ROOT>\03_Amara控制层\__pycache__\amara_build_v01.cpython-314.pyc | 30223 bytes | 2026-07-05T14:46:46


## 新建 UE 蓝图和 UI 清单

- /Game/Amara/EditorTools/EUW_AmaraControlDesk
- /Game/Amara/Blueprints/BP_AmaraOfflineTaskRunner
- /Game/Amara/Blueprints/BP_AmaraCityMoodController
- /Game/Amara/Blueprints/BP_AmaraExplorerPawn
- 已保留既有：BP_AmaraAgentDirector、BP_AmaraSafetyController、BP_AmaraCheckpointManager、BP_AmaraWorldProbe、BP_AmaraCommandRouter、BP_AmaraBlockoutBuilder、BP_CodexControlActor、WBP_AmaraStatus。

## 未来城市新增内容

新增 14 个 Actor，未删除原有 28 个 Amara Actor：

- AMARA_UPG_PlazaLightStrip_A
- AMARA_UPG_PlazaLightStrip_B
- AMARA_UPG_WindowBand_L01
- AMARA_UPG_WindowBand_L02
- AMARA_UPG_WindowBand_R01
- AMARA_UPG_WindowBand_R02
- AMARA_UPG_TowerBeacon
- AMARA_UPG_GuideLine_L
- AMARA_UPG_GuideLine_R
- AMARA_UPG_ZoneMarker_Plaza
- AMARA_UPG_ZoneMarker_Tower
- AMARA_UPG_ObservationPoint
- AMARA_UPG_ExplorerPawn
- AMARA_UPG_MoodController


新增内容覆盖：中央广场灯带、建筑发光窗面、主塔信标灯、低成本地面导向线、两个城市分区标识体、轻量观察点、DefaultPawn 派生 ExplorerPawn、MoodController 占位控制器。

## 升级前后 Actor 数

- 升级前总 Actor：28
- 升级前 AmaraManaged Actor：28
- 升级后总 Actor：42
- 升级后 AmaraManaged Actor：42
- 本次新增 Actor：14
- 单次新增限制：15，结果未超限。
- 总 Actor 限制：60，结果未超限。

## PIE 测试结果

- PIE Smoke Test：passed_20_seconds
- 可进入场景：通过，PIE 创建并启动 M_AmaraBlockoutSandbox。
- 可基础移动：创建 BP_AmaraExplorerPawn，父类为 DefaultPawn，并放置 AMARA_UPG_ExplorerPawn，设置 AutoPossess Player0；未通过自动输入模拟实测 WASD/鼠标。
- E 键昼夜切换：not_verified_by_python。原因：UE Python 本次未构建可验证的运行时 InputKey 蓝图节点；已创建 BP_AmaraCityMoodController 与夜景控制资产/Actor，但 E 键运行时切换仍需下一阶段在蓝图图表内补齐并人工/自动输入验证。
- 蓝图报错：结果 JSON errors=[]；日志未发现 Blueprint 编译错误。

## 性能与温度

- 当前可用内存比例：38.3%
- 当前 CPU 占用：26%
- GPU 状态：7% / 1639MB of 8151MB / 43 C
- 是否读取到温度：GPU 可读取；CPU 未读取。
- 低负载约束：保持，不启用 Lumen、Nanite、Path Tracing、Movie Render Queue、体积雾、外部资产、Cook 或打包。

## 检查点与恢复

- 升级前检查点：<AMARA_ROOT>\05_任务与检查点\checkpoints\checkpoint_002_pre_city_upgrade.json
- 升级完成检查点：<AMARA_ROOT>\05_任务与检查点\checkpoints\checkpoint_002_post_city_upgrade.json
- Restore 测试：passed_property_restore_changed_1_restored_42
- 恢复方法：使用升级完成检查点恢复 AmaraManaged Actor 的 Transform 和可记录属性；本次测试采用非破坏性属性恢复，不删除 Actor，最终保持升级完成状态。

## 当前 Amara 已能做什么

- 从离线任务 JSON 读取白名单任务。
- 校验 actor_limit、build_limit_per_step、allow_network=false、allow_external_assets=false 等安全字段。
- 创建预览计划并计算新增 Actor 数。
- 创建升级前/升级后检查点。
- 在 Content/Amara 内创建低负载材料、蓝图壳、Editor Utility Widget、地图升级内容。
- 在现有未来城市 Blockout 上做可编辑夜景概念升级。
- 运行一次 20 秒 PIE Smoke Test。
- 输出离线执行结果 JSON/Markdown。

## 下一次可评估的接入步骤

1. 不进入网络接入前，先补齐 BP_AmaraExplorerPawn 的真实 E 键输入蓝图节点或改为 Editor Utility Widget 按钮式昼夜切换，并做可重复验证。
2. 继续保持离线任务文件路线，增加任务 003 前先扩展 schema 和白名单。
3. 只有离线流程连续稳定后，再单独评估仅 127.0.0.1 的 Remote Control；本次不要启用。

## 异常与日志位置

- 任务第一次运行失败：任务 JSON 带 UTF-8 BOM，脚本已改为 utf-8-sig 后重跑成功。失败结果已保留在 03_Amara控制层\Logs 的 failed 归档文件中。
- DataRouter Analytics 日志仍出现，已记录来源，不视为 Amara 脚本联网。
- WebSockets 日志仅为 UE 模块关闭，没有服务监听和端口占用。
- UE 日志：<AMARA_ROOT>\02_项目8_Amara增强版\Saved\Logs\我的项目8.log
- 离线执行结果：<AMARA_ROOT>\03_Amara控制层\Logs\Amara_OfflineBridge_任务002执行结果.json
- Offline Bridge 日志目录：<AMARA_ROOT>\03_Amara控制层\Logs

## UE Content/Amara 文件清单

- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraAgentDirector.uasset | 21012 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraBlockoutBuilder.uasset | 20994 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraCheckpointManager.uasset | 21042 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraCityMoodController.uasset | 20797 bytes | 2026-07-05T15:03:04
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraCommandRouter.uasset | 20991 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraExplorerPawn.uasset | 29747 bytes | 2026-07-05T15:03:04
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraOfflineTaskRunner.uasset | 20782 bytes | 2026-07-05T15:03:03
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraSafetyController.uasset | 21047 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_AmaraWorldProbe.uasset | 20967 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Blueprints\BP_CodexControlActor.uasset | 21001 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\EditorTools\EUW_AmaraControlDesk.uasset | 19178 bytes | 2026-07-05T15:03:03
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Maps\M_AmaraBlockoutSandbox.umap | 46133 bytes | 2026-07-05T15:03:15
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Maps\M_AmaraLab.umap | 17370 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Accent.uasset | 8228 bytes | 2026-07-05T14:47:43
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Building.uasset | 7639 bytes | 2026-07-05T14:47:40
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Ground.uasset | 7731 bytes | 2026-07-05T14:47:30
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Plaza.uasset | 7680 bytes | 2026-07-05T14:47:35
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Road.uasset | 6955 bytes | 2026-07-05T14:47:33
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Tower.uasset | 7955 bytes | 2026-07-05T14:47:38
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Upgrade_GuideLine.uasset | 9939 bytes | 2026-07-05T15:03:12
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Upgrade_LightStrip.uasset | 9638 bytes | 2026-07-05T15:03:07
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Upgrade_Observation.uasset | 9695 bytes | 2026-07-05T15:03:15
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\Materials\M_Amara_Upgrade_WindowGlow.uasset | 9483 bytes | 2026-07-05T15:03:09
- <AMARA_ROOT>\02_项目8_Amara增强版\Content\Amara\UI\WBP_AmaraStatus.uasset | 18555 bytes | 2026-07-05T14:47:43
