# 案例 002：兼容blender2.79 guy_with_mask_tattoo

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `6-人物模型（不定期更新）/模型-二次元模型/blender模型/Guy with Mask Tattoo/兼容blender2.79 guy_with_mask_tattoo.blend` |
| 案例类型 | 角色/人体 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 90] |
| 对象数 | 139 |
| Mesh | 129 |
| 材质 | 52 |
| 灯光 | 4 |
| 相机 | 1 |

## 结构观察

- 对象类型：`MESH` 129、`LIGHT` 4、`CURVE` 2、`ARMATURE` 2、`CAMERA` 1、`EMPTY` 1
- 修改器：`ARMATURE` 20、`SUBSURF` 14、`MULTIRES` 9、`MIRROR` 8、`EDGE_SPLIT` 5
- Mesh 材质槽数量分布：`0` 103、`1` 25、`2` 1

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Lamp` | `SPOT` | 100.0 | [1.0, 1.0, 1.0] |
| `Lamp.001` | `SUN` | 0.05 | [1.0, 1.0, 1.0] |
| `Lamp.002` | `SUN` | 0.025 | [1.0, 1.0, 1.0] |
| `Lamp.003` | `SPOT` | 100.0 | [0.6546, 0.6992, 1.0] |

## 相机

- `Camera`：35.0mm，PERSP，sensor 32.0

## 学习重点

- 先观察身体比例、衣物分层、头发/装饰拆分，再研究骨骼和姿势。
- 存在 `SUBSURF`：对照低模控制线和最终平滑轮廓。
- 存在 `MIRROR`：学习只建一半再对称的结构拆分。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。
- 有相机：记录焦段和构图，按这个镜头复建一张图。

## 自动观察备注

- Camera exists: study focal length and framing before rebuilding the scene.
- Lights exist: study key/fill/rim balance and light color before changing materials.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Subdivision modifiers exist: compare base mesh simplicity with final smoothed silhouette.
- Render engine is BLENDER_EEVEE: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
