---
name: three-points
description: 在参数的最小值、最大值、中间值三个位置添加键位
triggers:
  - 打三个参数点
  - 三点键位
  - 均匀三点
  - /three-points
  - /tp
---

# 三点键位

在指定参数的最小值、中间值、最大值三个位置，为选中的对象添加键位。

## 步骤

1. 解析用户输入中的参数名称或 ID。如果用户没有指定参数，询问要操作哪个参数。
2. 调用 `cubism_get_parameter_structure` 获取参数的 Min/Max 值。
3. 计算三个目标值：`Min`, `(Min + Max) / 2`, `Max`。
4. 调用 `cubism_get_selected_objects` 获取当前选中的对象列表。如果没有选中对象，询问用户要操作哪些对象。
5. 调用 `cubism_edit_begin` 开始编辑事务。
6. 对每个选中对象，依次调用 `cubism_add_parameter_key` 在三个目标值处添加键位。
7. 调用 `cubism_edit_end` 提交事务。
8. 报告结果：在哪个参数上、为哪些对象、添加了哪三个键位。
