# 案例 020：蓝紫打光

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `模型/蓝紫打光.blend` |
| 案例类型 | 综合场景 |
| 渲染引擎 | `CYCLES` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 6 |
| Mesh | 2 |
| 材质 | 5 |
| 灯光 | 3 |
| 相机 | 1 |

## 结构观察

- 对象类型：`LIGHT` 3、`MESH` 2、`CAMERA` 1
- 修改器：无
- Mesh 材质槽数量分布：`1` 2

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Area` | `AREA` | 94.2478 | [0.0599, 0.3122, 1.0] |
| `Area.001` | `AREA` | 196.3495 | [1.0, 0.3207, 0.9318] |
| `Area.002` | `AREA` | 235.6194 | [0.2572, 0.2934, 0.8234] |

## 相机

- `Camera`：50.0mm，PERSP，sensor 36.0

## 学习重点

- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。
- 有相机：记录焦段和构图，按这个镜头复建一张图。

## 自动观察备注

- Camera exists: study focal length and framing before rebuilding the scene.
- Lights exist: study key/fill/rim balance and light color before changing materials.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Render engine is CYCLES: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
