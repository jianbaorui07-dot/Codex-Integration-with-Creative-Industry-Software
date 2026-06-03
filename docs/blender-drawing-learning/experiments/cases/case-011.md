# 案例 011：咖啡机

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `7-其它模型（不定期更新）/练习素材（按需下载））/咖啡机/咖啡机.blend` |
| 案例类型 | 道具/产品 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 7 |
| Mesh | 5 |
| 材质 | 10 |
| 灯光 | 0 |
| 相机 | 0 |

## 结构观察

- 对象类型：`MESH` 5、`CURVE` 1、`EMPTY` 1
- 修改器：`NODES` 4
- Mesh 材质槽数量分布：`2` 2、`1` 1、`4` 1、`0` 1

## 灯光

本案例没有记录到灯光对象。学习时应重点检查 World、材质自发光或手动补灯。

## 相机

未记录到相机。这个案例更适合作为建模/材质研究，需要自己补相机做出图实验。

## 学习重点

- 适合临摹基础体块、材质粗糙度和产品视角构图。
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
