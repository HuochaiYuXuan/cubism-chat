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
2. 调用 `cubism_read_psd` 读取 PSD，获取图层列表和蒙版关系（relations 数组）
3. 调用 `cubism_get_part_structure` 获取当前模型的 ArtMesh 列表
4. 按 relations 中的 (masked, source) 对，匹配到 Cubism ArtMesh：
   - 同名即匹配（大小写不敏感）
   - 列出所有匹配/未匹配结果
5. 用户确认后：
   a. cubism_edit_begin
   b. 对每个匹配关系，cubism_edit_artmesh(id=被蒙版ArtMesh的ID, clipping_ids=[蒙版源ArtMesh的ID])
   c. cubism_edit_end
6. 报告结果

## 注意事项

- 组作为基础层时会展开为组内所有子层
- 不要自己从 clipping 值推测关系——直接使用 cubism_read_psd 返回的 relations 数组
