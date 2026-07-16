---
name: list-model
description: 查看当前模型的完整结构信息
triggers:
  - 查看模型
  - 模型结构
  - 模型信息
  - /list-model
  - /lm
---

# 查看模型结构

输出当前模型的完整结构报告，包括参数、对象、变形器。

## 步骤

1. 调用 `cubism_get_current_model_uid` 获取当前模型 UID。
2. 调用 `cubism_get_current_edit_mode` 获取当前编辑模式。
3. 调用 `cubism_get_parameter_structure` 获取参数树结构。
4. 调用 `cubism_get_part_structure` 获取部件树结构。
5. 调用 `cubism_get_deformer_structure` 获取变形器树结构。
6. 格式化输出：用树状文本展示参数组和参数（含 Min/Max/Default/键位数）、部件和 ArtMesh、变形器层级。
7. 在报告末尾附上统计摘要（参数总数、对象总数、变形器总数）。
