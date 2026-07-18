"""PSD 文件图层和剪贴蒙版解析器 — 基于 psd-tools 库

支持 Photoshop CS6 ~ 2025 全系列 PSD/PSB 格式。
"""

from psd_tools import PSDImage
from psd_tools.api.layers import Group, PixelLayer


def parse_psd(file_path: str) -> dict:
    """解析 PSD 文件，返回图层信息和蒙版关系。

    Returns:
        {
            "layers": [{"name": str, "clipping": int, "index": int, "is_group": bool, "depth": int}, ...],
            "relations": [{"masked": str, "source": str}, ...]
        }
    """
    psd = PSDImage.open(file_path)

    layers = []
    relations = []
    _walk(psd, layers, relations, depth=0)

    # 补充 index
    for i, l in enumerate(layers):
        l["index"] = i

    return {"layers": layers, "relations": relations}


def _walk(parent, layers: list, relations: list, depth: int):
    """递归遍历图层树，按 Java mod 的逻辑解析剪贴关系

    核心逻辑（来自 Java PsdMaskReader.resolveMaskRelations）：
    - clipping=0 的图层是基础层（蒙版源）
    - clipping=1 的图层是被剪贴层，剪贴到它下方最近的基础层
    - 连续多个 clipping=1 的图层都剪贴到同一个基础层
    - 如果基础层是组，展开为组内每个直接子层
    """

    # 第一步：收集本层级的普通图层，标记 clipping 状态
    siblings = []
    for layer in parent:
        if isinstance(layer, Group):
            # 组标记
            siblings.append({
                "name": layer.name,
                "clipping": 0,  # 组可作为基础层
                "is_group": True,
                "is_group_end": False,
                "depth": depth,
                "_obj": layer,
            })
            # 递归处理组内图层
            _walk(layer, layers, relations, depth + 1)
            # 组结束标记
            siblings.append({
                "name": "</Layer group>",
                "clipping": 0,
                "is_group": False,
                "is_group_end": True,
                "depth": depth,
                "_obj": None,
            })
        elif isinstance(layer, PixelLayer):
            # psd-tools: clipping_base 非 None 表示该层被剪贴到某个基础层
            is_clipped = getattr(layer, "clipping_base", None) is not None
            clipping = 1 if is_clipped else 0  # 0=基础, 1=被剪贴
            siblings.append({
                "name": layer.name,
                "clipping": clipping,
                "is_group": False,
                "is_group_end": False,
                "depth": depth,
                "_obj": layer,
            })
        # 其他类型（调整层等）跳过

    layers.extend([{k: v for k, v in s.items() if k != "_obj"} for s in siblings])

    # 第二步：在本层级解析蒙版关系
    # 从下往上遍历（i=0 是栈底），找每个 clipping=1 图层的基础层
    for i, sib in enumerate(siblings):
        if sib["clipping"] != 1:
            continue

        base = _find_base(siblings, i)
        if base is None:
            continue

        if base["is_group"] and base["_obj"] is not None:
            # 组作为基础层：展开为组内所有直接子层
            children = _collect_children(base["_obj"])
            for child_name in children:
                relations.append({"masked": sib["name"], "source": child_name})
        else:
            relations.append({"masked": sib["name"], "source": base["name"]})


def _find_base(siblings: list, start_index: int) -> dict | None:
    """从被剪贴层向上扫描，找最近的 clipping=0 基础层（同深度）"""
    target = siblings[start_index]
    for j in range(start_index - 1, -1, -1):
        c = siblings[j]
        if c.get("is_group_end"):
            continue
        if c["depth"] != target["depth"]:
            continue
        if c["clipping"] == 0:
            return c
    return None


def _collect_children(group) -> list:
    """收集组内所有直接子层的名称（非组标记）"""
    names = []
    for layer in group:
        if not isinstance(layer, Group):
            names.append(layer.name)
    return names
