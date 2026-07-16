---
name: mirror-part-deformer
description: 从子到父逐层为部件组树结构创建镜像的弯曲变形器结构。每个 Part 节点对应创建一个 WarpDeformer，包裹其所有直接子级对象（ArtMesh 或子 Part 的 WarpDeformer）。
triggers:
  - 创建变形器组
  - 建立变形器结构
  - 部件组变形器
  - 镜像变形器
  - /mirror-part-deformer
---

1. 调用 cubism_get_part_structure(model_uid) 获取完整部件树
2. 从返回结构中提取所有 Part 节点，计算每个 Part 的深度（从根到该节点的层级数）
3. 按深度从大到小（最深优先）排序 Part 节点列表
4. 初始化一个映射表 created_deformer_map = {} 用于记录已创建的 Part→WarpDeformer ID
5. 调用 cubism_edit_begin() 开始编辑事务
6. 对每个 Part（已按深度排序，从最深开始）：
   a. 获取该 Part 的所有直接子节点（非子子孙孙，仅 direct children）
   b. 从中筛选出：直接 ArtMesh 子节点 + 已存在于 created_deformer_map 中的子 Part 对应的 WarpDeformer
   c. 如果筛选结果为空，跳过此 Part（比如空 Part）
   d. 如果筛选结果不为空，调用 cubism_add_warp_deformer：
      - name = Part 的 Name（直接使用部件组名称）
      - id = 自动生成唯一 ID（如 'Warp_' + Part的Id）
      - target_object_ids = 筛选出的所有对象 ID 列表
      - mode = 'AsParent'（使变形器成为这些对象的父级）
   e. 将 Part的Id → 新创建的 WarpDeformer的Id 存入 created_deformer_map
7. 所有 Part 处理完毕后，调用 cubism_edit_end() 结束编辑事务
8. 注意：从最深子级开始创建是为了避免"选择包含于不同父变形器的对象"报错。因为最内层的 ArtMeshes 尚未被任何变形器包裹，可以自由选择；而父级变形器创建时，子级变形器已存在且作为独立对象，同样不会冲突。
