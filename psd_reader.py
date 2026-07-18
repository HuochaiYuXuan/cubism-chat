"""PSD 文件图层和剪贴蒙版解析器

从 Java PsdMaskReader.java 移植。零第三方依赖，纯 Python 标准库。
解析 Adobe PSD 二进制格式，提取图层名称、剪贴关系和组结构。
"""

import io
import struct
from typing import Optional


def parse_psd(file_path: str) -> dict:
    """解析 PSD 文件，返回图层信息和蒙版关系。

    Returns:
        {
            "layers": [{"name": str, "clipping": int, "index": int, "is_group": bool, "is_group_end": bool, "depth": int}, ...],
            "relations": [{"masked": str, "source": str}, ...]
        }
    """
    with open(file_path, "rb") as f:
        data = f.read()
    return _parse(data)


def _parse(data: bytes) -> dict:
    buf = io.BytesIO(data)
    reader = _Reader(buf)

    # 文件头
    sig = reader.read(4)
    if sig != b"8BPS":
        raise ValueError("不是有效的 PSD 文件（签名错误）")
    version = reader.u16()
    if version != 1:
        raise ValueError(f"不支持的 PSD 版本: {version}")
    reader.skip(6)   # reserved
    reader.skip(2)   # channels
    reader.skip(8)   # height + width
    reader.skip(2)   # depth
    reader.skip(2)   # color mode

    # 跳过色彩模式数据和图像资源
    _skip_block(reader)

    # 图层与蒙版信息
    layers = _read_layers(reader)
    if not layers:
        return {"layers": [], "relations": []}

    relations = _resolve_mask_relations(layers)
    return {
        "layers": [{"name": l["name"], "clipping": l["clipping"], "index": l["index"],
                     "is_group": l["is_group"], "is_group_end": l["is_group_end"],
                     "depth": l["depth"]} for l in layers],
        "relations": [{"masked": r[0], "source": r[1]} for r in relations],
    }


def _skip_block(reader):
    length = reader.i32()
    if length > 0:
        reader.skip(length)


def _read_layers(reader) -> list:
    """读取图层与蒙版信息块"""
    block_len = reader.i32()
    if block_len == 0:
        return []

    block_end = reader.tell() + block_len
    reader.skip(4)  # layer info length

    layer_count = reader.i16()
    if layer_count < 0:
        layer_count = -layer_count

    layers = []
    depth = 0

    for i in range(layer_count):
        rec = _read_layer_record(reader, i)
        layer_depth = depth
        if rec["is_group_end"] and depth > 0:
            depth -= 1
        layers.append({
            "name": rec["name"],
            "clipping": rec["clipping"],
            "index": i,
            "is_group": rec["is_group"],
            "is_group_end": rec["is_group_end"],
            "depth": layer_depth,
        })
        if rec["is_group"]:
            depth += 1

    # 跳到块末尾
    remain = block_end - reader.tell()
    if remain > 0:
        reader.skip(remain)

    return layers


def _read_layer_record(reader, index: int) -> dict:
    """读取单个图层记录"""
    reader.skip(16)  # top, left, bottom, right

    chan_count = reader.u16()
    reader.skip(chan_count * 6)  # 2B id + 4B len per channel

    reader.skip(4)  # blend signature "8BIM"
    reader.skip(4)  # blend key
    reader.skip(1)  # opacity
    clipping = reader.u8()
    reader.skip(1)  # flags
    reader.skip(1)  # filler

    extra_len = reader.i32()

    unicode_name = ""
    is_group = False
    is_group_end = False

    if extra_len > 0:
        extra_start = reader.tell()
        extra_end = extra_start + extra_len

        mask_len = reader.i32()
        reader.skip(mask_len)

        blend_len = reader.i32()
        reader.skip(blend_len)

        # Pascal 字符串名称
        name_len = reader.u8()
        pascal_name = ""
        if name_len > 0:
            name_bytes = reader.read(name_len)
            pascal_name = _decode_name(name_bytes)
        name_pad = (4 - ((1 + name_len) % 4)) % 4
        reader.skip(name_pad)

        unicode_name = pascal_name

        # 标记的附加图层信息块
        while reader.tell() + 8 <= extra_end:
            sig = reader.i32()
            if sig not in (0x3842494D, 0x38423634):  # "8BIM" or "8B64"
                break

            key = reader.read(4).decode("ascii", errors="replace")
            data_len = reader.i32()
            if data_len < 0 or reader.tell() + data_len > extra_end:
                break

            data_start = reader.tell()

            if key == "luni" and data_len >= 8:
                reader.skip(4)  # version
                str_len = reader.i32()
                if str_len > 0 and reader.tell() + str_len * 2 <= data_start + data_len:
                    utf16_bytes = reader.read(str_len * 2)
                    try:
                        unicode_name = utf16_bytes.decode("utf-16-be")
                    except UnicodeDecodeError:
                        pass

            elif key == "lsct" and data_len >= 4:
                type_val = reader.i32()
                is_group = (type_val in (1, 2))
                is_group_end = (type_val == 3)

            read_bytes = reader.tell() - data_start
            skip_bytes = data_len - read_bytes + (data_len % 2)
            if skip_bytes > 0:
                reader.skip(skip_bytes)

    final_name = unicode_name if unicode_name else f"Layer {index}"
    return {
        "name": final_name,
        "clipping": clipping,
        "is_group": is_group,
        "is_group_end": is_group_end,
    }


def _decode_name(data: bytes) -> str:
    """尝试多种编码解码图层名称"""
    # Photoshop 在本地化 Windows 上使用系统代码页
    # 尝试 UTF-8，然后 GBK，然后 ASCII
    for enc in ("utf-8", "gbk", "ascii"):
        try:
            s = data.decode(enc)
            if _looks_valid(s):
                return s
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("ascii", errors="replace")


def _looks_valid(s: str) -> bool:
    """检查字符串是否看起来有效（不是全替换字符）"""
    if not s:
        return True
    replacement_count = s.count("�")
    return replacement_count < len(s) / 2


def _resolve_mask_relations(layers: list) -> list:
    """解析剪贴蒙版关系"""
    relations = []
    for i, layer in enumerate(layers):
        if layer["clipping"] != 1:  # 只看被剪贴的图层
            continue

        base = _find_base(layers, i)
        if base is None:
            continue

        if base["is_group"]:
            descendants = _collect_descendants(layers, base["index"])
            for desc in descendants:
                relations.append((layer["name"], desc["name"]))
        else:
            relations.append((layer["name"], base["name"]))

    return relations


def _find_base(layers: list, start_index: int) -> Optional[dict]:
    """从被剪贴图层向上扫描，找最近的 clipping=0 基础层"""
    target = layers[start_index]
    for j in range(start_index - 1, -1, -1):
        candidate = layers[j]
        if candidate["is_group_end"]:
            continue
        if candidate["depth"] != target["depth"]:
            continue
        if candidate["clipping"] == 0:
            return candidate
    return None


def _collect_descendants(layers: list, group_index: int) -> list:
    """收集组内的所有后代图层（跳过组标记）"""
    result = []
    group_depth = layers[group_index]["depth"]
    for i in range(group_index + 1, len(layers)):
        li = layers[i]
        if li["is_group_end"] and li["depth"] == group_depth:
            break
        if li["is_group_end"] or li["is_group"]:
            continue
        if li["depth"] > group_depth:
            result.append(li)
    return result


# ---- 读取器 ----

class _Reader:
    """带位置追踪的二进制读取器"""

    def __init__(self, buf: io.BytesIO):
        self._buf = buf

    def tell(self) -> int:
        return self._buf.tell()

    def read(self, n: int) -> bytes:
        return self._buf.read(n)

    def skip(self, n: int):
        self._buf.seek(n, io.SEEK_CUR)

    def u8(self) -> int:
        return struct.unpack("B", self._buf.read(1))[0]

    def u16(self) -> int:
        return struct.unpack(">H", self._buf.read(2))[0]

    def i16(self) -> int:
        return struct.unpack(">h", self._buf.read(2))[0]

    def i32(self) -> int:
        return struct.unpack(">i", self._buf.read(4))[0]
