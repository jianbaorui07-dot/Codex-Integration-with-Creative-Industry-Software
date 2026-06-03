# 案例 024：女法师

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `练习素材（按需下载））/女法师/女法师.blend` |
| 案例类型 | 角色/人体 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 57 |
| Mesh | 19 |
| 材质 | 8 |
| 灯光 | 0 |
| 相机 | 0 |

## 结构观察

- 对象类型：`EMPTY` 38、`MESH` 19
- 修改器：无
- Mesh 材质槽数量分布：`1` 18、`0` 1

## 灯光

本案例没有记录到灯光对象。学习时应重点检查 World、材质自发光或手动补灯。

## 相机

未记录到相机。这个案例更适合作为建模/材质研究，需要自己补相机做出图实验。

## 学习重点

- 先观察身体比例、衣物分层、头发/装饰拆分，再研究骨骼和姿势。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。

## 自动观察备注

- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Render engine is BLENDER_EEVEE: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
