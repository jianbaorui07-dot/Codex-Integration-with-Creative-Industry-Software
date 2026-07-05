# Amara E 键与 UI 最小人工补丁操作卡

生成时间：2026-07-05 15:37 +08:00
适用项目：`<AMARA_ROOT>\02_项目8_Amara增强版\我的项目8.uproject`
适用地图：`/Game/Amara/Maps/M_AmaraBlockoutSandbox`

本卡用于 UE 5.2.1 图形界面人工补丁。不得使用 Python、二进制补丁、反序列化修改、C++、Native Plugin 或 Build Tools。

## 0. 启动前

1. 确认无 `UnrealEditor.exe` 残留。
2. 启动增强副本，不启动原项目8。
3. 启动参数继续包含：`-UDPMESSAGING_TRANSPORT_ENABLE=False`
4. 打开地图：`/Game/Amara/Maps/M_AmaraBlockoutSandbox`
5. 创建检查点：`v0.3交互补丁前`

## 1. 输入资源

项目已使用 Enhanced Input：

- `DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput`
- `DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent`

因此只在以下目录补充输入资源：

- 新建文件夹：`/Game/Amara/Input`
- 新建 Input Action：`/Game/Amara/Input/IA_AmaraToggleCityMood`
- 新建 Input Mapping Context：`/Game/Amara/Input/IMC_AmaraExplorer`

`IA_AmaraToggleCityMood`：

- Value Type：Boolean 或 Digital

`IMC_AmaraExplorer`：

- Mapping：`IA_AmaraToggleCityMood`
- Key：`E`

不要修改项目其他 Input Mapping。

## 2. BP_AmaraCityMoodController

资源路径：`/Game/Amara/Blueprints/BP_AmaraCityMoodController`
场景 Actor：`AMARA_UPG_MoodController`

在该蓝图内创建或修正同一个函数：

- Function Name：`ToggleCityMood`

最小变量：

- `bAmaraIsNight`，Boolean，默认 `false`

最小执行线：

1. `ToggleCityMood`
2. `Branch`，Condition 接 `bAmaraIsNight`
3. True 分支：
   - 调用现有 Day 预览/日间逻辑
   - `Set bAmaraIsNight = false`
   - `Print String`：`AMARA_CITY_MOOD=DAY`
4. False 分支：
   - 调用现有 Night 预览/夜间逻辑
   - `Set bAmaraIsNight = true`
   - `Print String`：`AMARA_CITY_MOOD=NIGHT`

约束：

- 只影响 AmaraManaged 灯光、材质、城市效果。
- 不修改项目全局渲染设置。
- 不启用 Lumen、Nanite、Path Tracing、体积雾或复杂粒子。
- 不删除任何已有 AmaraManaged Actor。

## 3. BP_AmaraExplorerPawn

资源路径：`/Game/Amara/Blueprints/BP_AmaraExplorerPawn`
场景 Actor：`AMARA_UPG_ExplorerPawn`

在 Event Graph 中添加最小节点：

1. `Event BeginPlay`
2. `Get Player Controller`
3. `Get Local Player`
4. `Get Enhanced Input Local Player Subsystem`
5. `Add Mapping Context`
   - Mapping Context：`IMC_AmaraExplorer`
   - Priority：`0`

再添加输入触发：

1. `Enhanced Input Action IA_AmaraToggleCityMood`
2. 使用 `Triggered` 执行引脚
3. `Get Actor Of Class`
   - Actor Class：`BP_AmaraCityMoodController`
4. 调用 `ToggleCityMood`

## 4. UI 按钮

优先使用现有控件：

- Editor Utility Widget：`/Game/Amara/EditorTools/EUW_AmaraControlDesk`
- 如已有运行时 UI，则使用：`/Game/Amara/UI/WBP_AmaraStatus`

按钮显示名建议：`切换昼夜`

OnClicked 最小执行线：

1. `OnClicked(切换昼夜按钮)`
2. `Get Actor Of Class`
   - Actor Class：`BP_AmaraCityMoodController`
3. 调用 `ToggleCityMood`

UI 不得直接调用 Day 或 Night 分支；必须和 E 键一样调用 `ToggleCityMood`。

## 5. 验证

1. 保存蓝图并编译。
2. PIE 运行最多 20 秒。
3. 按 `E` 一次。
4. 点击 `切换昼夜` 按钮一次。
5. Output Log 必须出现两条记录，且只允许是：
   - `AMARA_CITY_MOOD=DAY`
   - `AMARA_CITY_MOOD=NIGHT`
6. 保存截图和日志片段到：`<AMARA_ROOT>\06_性能与测试`
7. 保存项目。
8. 创建检查点：`v0.3交互补丁完成`

## 6. 停止条件

遇到以下任一情况立即停止：

- 需要修改原项目8。
- 需要创建 C++、Source、Native Plugin 或 Build Tools。
- 需要通过 Python 修改 K2 节点、WidgetTree 或 OnClicked 图表。
- 需要删除 Actor。
- Actor 总数将超过 60。
- UE 崩溃。
- 出现非回环监听或 UDP Messaging 网络绑定。
