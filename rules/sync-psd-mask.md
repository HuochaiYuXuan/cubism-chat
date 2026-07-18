---
name: sync-psd-mask
builtin: true
description: 读取 PSD 文件的图层剪贴蒙版信息并应用到模型
triggers:
  - 同步PSD蒙版
  - 加载PSD蒙版
  - PSD遮罩
  - /sync-psd-mask
  - /psd
---

# 同步 PSD 蒙版

将 Adobe PSD 文件中的图层剪贴蒙版（clipping mask）关系匹配并应用到当前 Cubism 模型的 ArtMesh 上。

PSD 剪贴语义：clipping=0 的图层是基础层（蒙版源），clipping=1 的图层是被剪贴的图层。被剪贴图层会以基础层作为蒙版。

## 步骤

1. 如果用户未指定 PSD 文件路径，询问 PSD 文件的绝对路径
2. 调用 `cubism_read_psd` 读取 PSD，获取图层列表和蒙版关系
3. 调用 `cubism_get_part_structure` 获取当前模型的 ArtMesh 列表（含每个 ArtMesh 的名称和 ID）
4. 将 PSD 图层名称与 Cubism ArtMesh 名称进行匹配：
   - 同名即匹配（大小写不敏感）
   - 列出所有匹配结果给用户确认
   - 如果存在无法匹配的图层或 ArtMesh，告知用户
5. 用户确认后：
   a. 调用 `cubism_edit_begin`
   b. 对每个匹配的蒙版关系，调用 `cubism_edit_artmesh`：
      - id：被蒙版 ArtMesh 的 ID
      - clipping_ids：包含蒙版源 ArtMesh ID 的数组
   c. 调用 `cubism_edit_end`
6. 报告最终结果：成功应用 N 个蒙版关系，跳过了哪些未匹配的图层

## 注意事项

- PSD 中的组（group）会展开为组内的每个子图层作为独立蒙版源
- 已有的 clip 设置默认会被保留（只追加新的蒙版关系）
- 建议在应用前让用户确认匹配结果
