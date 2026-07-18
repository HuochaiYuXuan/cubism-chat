"""PSD 文件图层和剪贴蒙版解析器 — 基于 psd-tools 库

支持 Photoshop CS6 ~ 2025 全系列 PSD/PSB 格式。
"""

from psd_tools import PSDImage


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
    # 为兼容旧输出格式，补充 index
    for i, l in enumerate(layers):
        l["index"] = i

    return {"layers": layers, "relations": relations}


def _walk(group, layers: list, relations: list, depth: int):
    """递归遍历图层树，提取剪贴蒙版关系"""
    for layer in group:
        if layer.is_group():
            # 组本身
            layers.append({
                "name": layer.name,
                "clipping": 0,
                "index": -1,
                "is_group": True,
                "is_group_end": False,
                "depth": depth,
            })
            _walk(layer, layers, relations, depth + 1)
            layers.append({
                "name": "</Layer group>",
                "clipping": 0,
                "index": -1,
                "is_group": False,
                "is_group_end": True,
                "depth": depth,
            })
        else:
            layers.append({
                "name": layer.name,
                "clipping": 2,  # 默认独立
                "index": -1,
                "is_group": False,
                "is_group_end": False,
                "depth": depth,
            })
            # 检查剪贴蒙版：clipping_base 是被剪贴到的基底图层
            if hasattr(layer, "clipping_base") and layer.clipping_base is not None:
                # 标记当前层为被剪贴 (1)
                layers[-1]["clipping"] = 1
                relations.append({
                    "masked": layer.name,
                    "source": layer.clipping_base.name,
                })
