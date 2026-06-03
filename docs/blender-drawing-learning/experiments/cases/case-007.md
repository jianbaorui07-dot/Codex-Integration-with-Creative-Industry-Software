# 案例 007：ElfSwordmaster

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `6-人物模型（不定期更新）/模型-次时代CG女性人物3D角色/精灵剑士/ElfSwordmaster.blend` |
| 案例类型 | 角色/人体 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 16 |
| Mesh | 13 |
| 材质 | 12 |
| 灯光 | 1 |
| 相机 | 1 |

## 结构观察

- 对象类型：`MESH` 13、`ARMATURE` 1、`CAMERA` 1、`LIGHT` 1
- 修改器：`ARMATURE` 12
- Mesh 材质槽数量分布：`1` 9、`2` 4

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Light` | `POINT` | 1000.0 | [1.0, 1.0, 1.0] |

## 相机

- `Camera`：50.0mm，PERSP，sensor 36.0

## 学习重点

- 先观察身体比例、衣物分层、头发/装饰拆分，再研究骨骼和姿势。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。
- 有相机：记录焦段和构图，按这个镜头复建一张图。

## 自动观察备注

- Camera exists: study focal length and framing before rebuilding the scene.
- Lights exist: study key/fill/rim balance and light color before changing materials.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Render engine is BLENDER_EEVEE: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
