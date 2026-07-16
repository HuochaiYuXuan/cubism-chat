"""Live2D Cubism Editor 外部集成 API 枚举类型"""

# LabelColorType
LABEL_COLOR_TYPES = [
    "Undefined", "Red", "Orange", "Yellow", "Green",
    "Blue", "Purple", "Gray", "Custom"
]

# ColorBlend 颜色混合模式
COLOR_BLEND_TYPES = [
    "Normal", "Add", "AddGlow", "Darken", "Multiply",
    "ColorBurn", "LinearBurn", "Lighten", "Screen",
    "ColorDodge", "Overlay", "SoftLight", "HardLight",
    "LinearLight", "Hue", "Color", "Add_5.2", "Multiply_5.2"
]

# AlphaBlend Alpha混合模式
ALPHA_BLEND_TYPES = [
    "Over", "Atop", "Out", "Conjoint", "Disjoint"
]

# EditMode 编辑模式
EDIT_MODES = [
    "Physics", "Modeling", "Animation", "ModelingMeshEdit", "FormAnimation"
]

# Object Types
OBJECT_TYPES = [
    "ArtMesh", "WarpDeformer", "RotationDeformer", "Part", "Glue", "ArtPath"
]

# API Error Types
ERROR_TYPES = [
    "InvalidJson", "UnsupportedVersion", "MethodNotFound",
    "InvalidType", "InvalidData", "PluginNotRegistered",
    "InvalidParameter", "InvalidModel", "InvalidDocument",
    "InvalidView", "InvalidEditOperation"
]
