# 案例 006：yang_guifei_v1.0

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `6-人物模型（不定期更新）/模型-二次元模型/blender模型/yangguifei/yang_guifei_v1.0.blend` |
| 案例类型 | 角色/人体 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1080, 1080] |
| 帧范围 | [1, 40] |
| 对象数 | 288 |
| Mesh | 267 |
| 材质 | 23 |
| 灯光 | 4 |
| 相机 | 10 |

## 结构观察

- 对象类型：`MESH` 267、`CAMERA` 10、`LIGHT` 4、`CURVE` 3、`LIGHT_PROBE` 2、`ARMATURE` 2
- 修改器：`NODES` 33、`MIRROR` 25、`SUBSURF` 24、`ARMATURE` 19、`SOLIDIFY` 13、`CURVE` 6、`PARTICLE_SYSTEM` 5、`BEVEL` 1
- Mesh 材质槽数量分布：`0` 186、`1` 71、`2` 6、`3` 4

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Area` | `AREA` | 7.854 | [1.0, 0.2874, 0.2736] |
| `Area.001` | `AREA` | 7.854 | [0.9264, 0.9378, 1.0] |
| `Lamp` | `SPOT` | 50.0 | [1.0, 1.0, 1.0] |
| `Lamp.001` | `SPOT` | 150.0 | [1.0, 0.9752, 0.89] |

## 相机

- `Camera`：120.0mm，PERSP，sensor 36.0
- `Camera.007`：50.0mm，ORTHO，sensor 36.0
- `Camera.008`：50.0mm，ORTHO，sensor 36.0
- `Camera.009`：50.0mm，ORTHO，sensor 36.0
- `Camera.010`：50.0mm，ORTHO，sensor 36.0
- `Camera.011`：50.0mm，ORTHO，sensor 36.0
- `Camera.012`：50.0mm，ORTHO，sensor 36.0
- `Camera.013`：50.0mm，ORTHO，sensor 36.0

## 学习重点

- 先观察身体比例、衣物分层、头发/装饰拆分，再研究骨骼和姿势。
- 存在 `SUBSURF`：对照低模控制线和最终平滑轮廓。
- 存在 `MIRROR`：学习只建一半再对称的结构拆分。
- 存在 `BEVEL`：观察倒角宽度如何制造高光。
- 存在 `SOLIDIFY`：观察衣物、壳体或薄片如何获得厚度。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。
- 有相机：记录焦段和构图，按这个镜头复建一张图。

## 自动观察备注

- Camera exists: study focal length and framing before rebuilding the scene.
- Lights exist: study key/fill/rim balance and light color before changing materials.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Subdivision modifiers exist: compare base mesh simplicity with final smoothed silhouette.
- Bevel modifiers exist: edges are likely softened for product-style highlights.
- Render engine is BLENDER_EEVEE: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
