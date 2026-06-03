# 案例 001：渐变世界环境

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `5-Hdr环境/HDR-108个/HDR-108个/渐变世界环境.blend` |
| 案例类型 | 环境光与世界节点 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [0, 240] |
| 对象数 | 5 |
| Mesh | 0 |
| 材质 | 5 |
| 灯光 | 3 |
| 相机 | 0 |

## 结构观察

- 对象类型：`LIGHT` 3、`EMPTY` 2
- 修改器：无
- Mesh 材质槽数量分布：无

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Point Light 1 (R) ` | `POINT` | 0.0 | [1.0, 0.0, 0.0] |
| `Point Light 2 (G) ` | `POINT` | 0.0 | [0.0, 1.0, 0.0] |
| `Point Light 3 (B) ` | `POINT` | 0.0 | [0.0, 0.0, 1.0] |

## 相机

未记录到相机。这个案例更适合作为建模/材质研究，需要自己补相机做出图实验。

## 学习重点

- 重点研究 World 节点、HDR/EXR 环境光和反射氛围。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。

## 自动观察备注

- Lights exist: study key/fill/rim balance and light color before changing materials.
- Node materials exist: inspect shader graphs for color, roughness, normal, emission, and transparency decisions.
- Render engine is BLENDER_EEVEE: keep lighting and material expectations aligned with that engine.

## 建议实验

1. 先打开白模视图，截图记录剪影和主要体块。
2. 关闭或隐藏灯光，判断模型自身是否成立。
3. 恢复灯光，记录主光、补光、轮廓光或 World 环境光。
4. 逐个检查材质节点，标记 base color、roughness、normal、metallic、emission。
5. 用相同相机角度复建一个简化版本，完成一张临摹渲染。
