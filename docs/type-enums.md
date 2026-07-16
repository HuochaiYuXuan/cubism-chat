# Cubism Editor 类型枚举参考

## LabelColorType（标签颜色）

| 值 | 说明 |
|----|------|
| `Undefined` | 程序决定颜色 |
| `Red` | 红色 |
| `Orange` | 橙色 |
| `Yellow` | 黄色 |
| `Green` | 绿色 |
| `Blue` | 蓝色 |
| `Purple` | 紫色 |
| `Gray` | 灰色 |
| `Custom` | 自定义颜色（需配合 LabelCustomColor） |

## ColorBlend（颜色混合模式）

| 值 | 说明 |
|----|------|
| `Normal` | 正常 |
| `Add` | 叠加 |
| `AddGlow` | 叠加（发光） |
| `Darken` | 变暗 |
| `Multiply` | 正片叠底 |
| `ColorBurn` | 颜色加深 |
| `LinearBurn` | 线性加深 |
| `Lighten` | 变亮 |
| `Screen` | 滤色 |
| `ColorDodge` | 颜色减淡 |
| `Overlay` | 叠加 |
| `SoftLight` | 柔光 |
| `HardLight` | 强光 |
| `LinearLight` | 线性光 |
| `Hue` | 色相 |
| `Color` | 颜色 |
| `Add_5.2` | 叠加（5.3版之前） |
| `Multiply_5.2` | 正片叠底（5.3版之前） |

## AlphaBlend（Alpha 混合模式）

| 值 | 说明 |
|----|------|
| `Over` | 覆盖 |
| `Atop` | 在上 |
| `Out` | 在外 |
| `Conjoint` | 联合 |
| `Disjoint` | 分离 |

## EditMode（编辑模式）

| 值 | 说明 |
|----|------|
| `Physics` | 物理模拟设置 |
| `Modeling` | 模型编辑 |
| `Animation` | 动画编辑 |
| `ModelingMeshEdit` | 网格编辑 |
| `FormAnimation` | 形状动画编辑（5.1 beta1+） |

## Object Types（对象类型）

| 类型 | 说明 |
|------|------|
| `ArtMesh` | 图形网格 |
| `WarpDeformer` | 弯曲变形器 |
| `RotationDeformer` | 旋转变形器 |
| `Part` | 部件 |
| `Glue` | 胶水 |
| `ArtPath` | 美术路径 |

## API Error Types（错误类型）

| 错误类型 | 说明 |
|----------|------|
| `InvalidJson` | JSON 结构不正确 |
| `UnsupportedVersion` | 版本不兼容 |
| `MethodNotFound` | 未找到指定方法 |
| `InvalidType` | Type 字段无效 |
| `InvalidData` | 参数无效 |
| `PluginNotRegistered` | 插件未注册 |
| `InvalidParameter` | 参数不存在 |
| `InvalidModel` | 模型不存在 |
| `InvalidDocument` | 文档不存在 |
| `InvalidView` | 视图不存在 |
| `InvalidEditOperation` | 编辑操作无效（如未先调用 EditBegin） |
