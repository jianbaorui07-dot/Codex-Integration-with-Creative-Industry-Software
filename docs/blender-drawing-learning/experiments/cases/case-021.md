# 案例 021：越野车

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `模型/越野车.blend` |
| 案例类型 | 硬表面/机械 |
| 渲染引擎 | `CYCLES` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 274 |
| Mesh | 266 |
| 材质 | 1 |
| 灯光 | 0 |
| 相机 | 1 |

## 结构观察

- 对象类型：`MESH` 266、`EMPTY` 5、`CURVE` 2、`CAMERA` 1
- 修改器：`SUBSURF` 171、`NODES` 145、`MIRROR` 139、`BEVEL` 33、`SHRINKWRAP` 8、`SOLIDIFY` 2、`LATTICE` 2、`SIMPLE_DEFORM` 1
- Mesh 材质槽数量分布：`0` 261、`1` 5

## 灯光

本案例没有记录到灯光对象。学习时应重点检查 World、材质自发光或手动补灯。

## 相机

- `Camera`：50.0mm，PERSP，sensor 36.0

## 学习重点

- 重点观察镜像、倒角、细分和边缘高光如何服务机械/车辆轮廓。
- 存在 `SUBSURF`：对照低模控制线和最终平滑轮廓。
- 存在 `MIRROR`：学习只建一半再对称的结构拆分。
- 存在 `BEVEL`：观察倒角宽度如何制造高光。
- 存在 `SOLIDIFY`：观察衣物、壳体或薄片如何获得厚度。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有相机：记录焦段和构图，按这个镜头复建一张图。

## 自动观察备注

- Camera exists: study focal length and framing before rebuilding the scene.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Subdivision modifiers exist: compare base mesh simplicity with final smoothed silhouette.
- Bevel modifiers exist: edges are likely softened for product-style highlights.
- Render engine is CYCLES: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
