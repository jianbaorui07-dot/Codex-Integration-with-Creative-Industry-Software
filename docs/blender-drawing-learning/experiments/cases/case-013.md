# 案例 013：直升机

## 基本信息

| 项目 | 结果 |
| --- | --- |
| 脱敏标签 | `7-其它模型（不定期更新）/练习素材（按需下载））/直升机文件/直升机.blend` |
| 案例类型 | 硬表面/机械 |
| 渲染引擎 | `BLENDER_EEVEE` |
| 分辨率 | [1920, 1080] |
| 帧范围 | [1, 250] |
| 对象数 | 155 |
| Mesh | 148 |
| 材质 | 26 |
| 灯光 | 2 |
| 相机 | 0 |

## 结构观察

- 对象类型：`MESH` 148、`EMPTY` 5、`LIGHT` 2
- 修改器：`NODES` 101、`SUBSURF` 62、`MIRROR` 11、`SOLIDIFY` 4、`BEVEL` 4
- Mesh 材质槽数量分布：`1` 139、`2` 4、`3` 3、`0` 2

## 灯光

| 灯光 | 类型 | 能量 | 颜色 |
| --- | --- | ---: | --- |
| `Point` | `POINT` | 0.0 | [1.0, 1.0, 1.0] |
| `Point.001` | `POINT` | 0.0 | [1.0, 1.0, 1.0] |

## 相机

未记录到相机。这个案例更适合作为建模/材质研究，需要自己补相机做出图实验。

## 学习重点

- 重点观察镜像、倒角、细分和边缘高光如何服务机械/车辆轮廓。
- 存在 `SUBSURF`：对照低模控制线和最终平滑轮廓。
- 存在 `MIRROR`：学习只建一半再对称的结构拆分。
- 存在 `BEVEL`：观察倒角宽度如何制造高光。
- 存在 `SOLIDIFY`：观察衣物、壳体或薄片如何获得厚度。
- 材质数量不为 0：应检查节点、贴图角色、roughness、normal 和 emission。
- 有灯光：先判断主光、补光、轮廓光，再改材质。

## 自动观察备注

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
