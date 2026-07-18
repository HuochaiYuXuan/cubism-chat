---
name: sync-psd-mask
builtin: true
description: 读取 PSD 文件的图层剪贴蒙版信息并应用到模型 ArtMesh 的裁剪关系上
triggers:
  - 同步PSD蒙版
  - 加载PSD蒙版
  - PSD遮罩
  - /sync-psd-mask
  - /psd
---

# 同步 PSD 蒙版

将 Adobe PSD 文件中的图层剪贴蒙版（clipping mask）关系匹配并应用到当前 Cubism 模型的 ArtMesh 裁剪关系上。

PSD 剪贴语义：clipping=0 的图层是基础层（蒙版源），clipping=1 的图层是被剪贴的图层。被剪贴图层会以基础层作为蒙版。

## 步骤

1. 调用 `cubism_get_current_document_uid()` 获取当前文档 UID
2. 调用 `cubism_get_current_model_uid()` 获取当前模型 UID
3. 调用 `cubism_read_psd(file_path)` 读取 PSD 文件的图层列表和蒙版关系
4. 调用 `cubism_get_part_structure(model_uid)` 获取模型所有 ArtMesh 对象列表
5. **匹配阶段：** 遍历每条蒙版关系（Masked ← Source），按以下规则匹配模型 ArtMesh：
   - 先用「图层名称」精确匹配 ArtMesh 的 Name 字段（去头尾空格，大小写不敏感）
   - 若精确匹配到唯一结果，直接使用
   - 若匹配到多个结果（如多个同名的 ArtMesh），用 PSD 图层所在组路径辅助消歧
   - 若仍无法唯一确定，取第一个匹配项并记录日志
6. **特殊去重逻辑（裁剪自引用修正）：** 当一条蒙版关系中 **Masked 图层** 与 **Source 图层** 在模型中匹配到同一名称（如"脸轮廓"←"脸轮廓"），且对应多个 ArtMesh：
   - 找到名称相同且 ID 较小的 ArtMesh（设为 A）和 ID 较大的 ArtMesh（设为 B）
   - 正确做法：A 的 clipping_id 设为 B（A 被 B 裁剪），B 自身不动
7. 调用 `cubism_edit_begin()` 开始编辑事务
8. 遍历所有匹配成功的蒙版关系，调用 `cubism_edit_artmesh(model_uid, id=masked_artmesh_id, clipping_ids=[source_artmesh_id])` 设置裁剪关系
9. 调用 `cubism_edit_end()` 结束编辑事务
10. 返回处理结果：总蒙版关系数、成功匹配数、未匹配数、以及特殊去重的修正记录

## 核心修复说明

当同名图层（如"脸轮廓"）同时作为蒙版源和被蒙版对象时，按 ArtMesh ID 的大小决定方向——**小 ID 剪贴到大 ID**，避免因同名匹配错乱导致裁剪关系方向反掉。
