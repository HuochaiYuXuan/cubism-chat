"""Cubism API → OpenAI Function Calling Tool 定义

56 个 API 映射为 10 组 tool 定义。
"""

# ====== AUTH (3) ======

TOOL_REGISTER_PLUGIN = {
    "type": "function",
    "function": {
        "name": "cubism_register_plugin",
        "description": "注册外部应用到 Cubism Editor。返回一个 Token 用于后续连接。应用启动时自动调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "应用名称"},
                "token": {"type": "string", "description": "已有 Token（重连时传入）"},
                "icon": {"type": "string", "description": "Base64 PNG 图标（可选，32x32~256x256）"},
                "path": {"type": "string", "description": "应用路径信息（可选）"},
            },
            "required": ["name"]
        }
    }
}

TOOL_GET_IS_APPROVAL = {
    "type": "function",
    "function": {
        "name": "cubism_get_is_approval",
        "description": "检查用户是否在 Cubism Editor 设置中授予了编辑权限。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# ====== EDIT SESSION (6) ======

TOOL_EDIT_BEGIN = {
    "type": "function",
    "function": {
        "name": "cubism_edit_begin",
        "description": "开始编辑事务。所有修改操作之前必须调用此方法。成功后 Editor 会显示对话框并锁定用户操作。",
        "parameters": {
            "type": "object",
            "properties": {
                "silent": {"type": "boolean", "description": "是否隐藏编辑对话框（适用于瞬时操作，默认 false）"},
            },
            "required": []
        }
    }
}

TOOL_EDIT_END = {
    "type": "function",
    "function": {
        "name": "cubism_edit_end",
        "description": "结束编辑事务。commit 修改到撤销栈。",
        "parameters": {
            "type": "object",
            "properties": {
                "cancel": {"type": "boolean", "description": "是否取消编辑（true=恢复到编辑前状态，默认 false）"},
            },
            "required": []
        }
    }
}

TOOL_EDIT_SEND_LOG = {
    "type": "function",
    "function": {
        "name": "cubism_edit_send_log",
        "description": "向 Editor 的编辑对话框发送日志消息。",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "日志消息文本"},
            },
            "required": ["message"]
        }
    }
}

TOOL_EDIT_SEND_PROGRESS = {
    "type": "function",
    "function": {
        "name": "cubism_edit_send_progress",
        "description": "更新编辑对话框的进度条（0.0~1.0）。",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "进度值 0.0 到 1.0"},
            },
            "required": ["value"]
        }
    }
}

TOOL_GET_IS_EDIT_APPROVAL = {
    "type": "function",
    "function": {
        "name": "cubism_get_is_edit_approval",
        "description": "检查是否允许编辑操作。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

TOOL_NOTIFY_UNDO_CANCEL = {
    "type": "function",
    "function": {
        "name": "cubism_notify_undo_cancel",
        "description": "当编辑操作被用户取消时的通知。订阅/取消订阅此事件。",
        "parameters": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "description": "true=订阅, false=取消订阅"},
            },
            "required": ["enabled"]
        }
    }
}

# ====== BASE QUERIES (8) ======

TOOL_GET_DOCUMENTS = {
    "type": "function",
    "function": {
        "name": "cubism_get_documents",
        "description": "获取 Cubism Editor 中打开的所有文档（建模、物理、动画）。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

TOOL_GET_DOCUMENT = {
    "type": "function",
    "function": {
        "name": "cubism_get_document",
        "description": "通过 DocumentUID 获取单个文档的详细信息。",
        "parameters": {
            "type": "object",
            "properties": {
                "document_uid": {"type": "string", "description": "文档 UID"},
            },
            "required": ["document_uid"]
        }
    }
}

TOOL_GET_CURRENT_DOCUMENT_UID = {
    "type": "function",
    "function": {
        "name": "cubism_get_current_document_uid",
        "description": "获取当前活动文档的 UID。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

TOOL_GET_CURRENT_MODEL_UID = {
    "type": "function",
    "function": {
        "name": "cubism_get_current_model_uid",
        "description": "获取当前编辑器中活动模型的 UID。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

TOOL_GET_CURRENT_EDIT_MODE = {
    "type": "function",
    "function": {
        "name": "cubism_get_current_edit_mode",
        "description": "获取当前编辑模式。返回: Physics/Modeling/Animation/ModelingMeshEdit/FormAnimation",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

TOOL_GET_PARAMETERS = {
    "type": "function",
    "function": {
        "name": "cubism_get_parameters",
        "description": "获取模型的参数列表（旧版 API，返回平铺列表）。包含参数 ID/名称/组UID/默认值/范围/类型/键位值。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID（可选，不传则获取当前模型）"},
                "document_uid": {"type": "string", "description": "文档 UID（可选，与 model_uid 二选一）"},
            },
            "required": []
        }
    }
}

TOOL_GET_PARAMETER_GROUPS = {
    "type": "function",
    "function": {
        "name": "cubism_get_parameter_groups",
        "description": "获取模型的参数组列表。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID（可选）"},
                "document_uid": {"type": "string", "description": "文档 UID（可选）"},
            },
            "required": []
        }
    }
}

TOOL_GET_PHYSICS_INFO = {
    "type": "function",
    "function": {
        "name": "cubism_get_physics_info",
        "description": "获取物理模拟设置中的计算 FPS。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_SEND_CUBISM_LOG = {
    "type": "function",
    "function": {
        "name": "cubism_send_cubism_log",
        "description": "向 Cubism Editor 的日志面板发送一条消息（用于调试）。",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "日志级别: info 或 warning，默认 info"},
                "message": {"type": "string", "description": "日志消息，最多 5000 字符"},
                "display": {"type": "boolean", "description": "是否在日志面板显示，默认 true"},
            },
            "required": ["message"]
        }
    }
}

TOOL_CLEAR_PARAMETER_VALUES = {
    "type": "function",
    "function": {
        "name": "cubism_clear_parameter_values",
        "description": "清除通过 SetParameterValues 设置的临时参数缓冲。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

# ====== PARAMETER VALUES (2) ======

TOOL_GET_PARAMETER_VALUES = {
    "type": "function",
    "function": {
        "name": "cubism_get_parameter_values",
        "description": "获取指定参数 ID 的当前值。不指定 ID 列表则返回所有参数值。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要查询的参数 ID 列表（可选，不指定则返回所有）"
                },
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_SET_PARAMETER_VALUES = {
    "type": "function",
    "function": {
        "name": "cubism_set_parameter_values",
        "description": "设置模型参数值。注意：参数值会被放入临时缓冲（0.5s 后自动丢弃），不会直接修改模型文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "参数 ID"},
                            "value": {"type": "number", "description": "参数值"},
                        },
                        "required": ["id", "value"]
                    },
                    "description": "参数 ID 和值的列表"
                },
            },
            "required": ["model_uid", "parameters"]
        }
    }
}

# ====== PARAMETER STRUCTURE (5.4 new API) ======

TOOL_GET_PARAMETER_STRUCTURE = {
    "type": "function",
    "function": {
        "name": "cubism_get_parameter_structure",
        "description": "获取参数结构树（5.4 新 API）。返回嵌套的参数组和参数，包含 KeyValues、IsBlendShape 等完整信息。这是查看参数的首选方法。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

# ====== PARAMETER CRUD (5) ======

TOOL_ADD_PARAMETER = {
    "type": "function",
    "function": {
        "name": "cubism_add_parameter",
        "description": "添加新参数到模型。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "name": {"type": "string", "description": "参数名称"},
                "id": {"type": "string", "description": "参数 ID"},
                "group_id": {"type": "string", "description": "所属参数组 ID（可选）"},
                "min": {"type": "number", "description": "最小值（默认 0）"},
                "default": {"type": "number", "description": "默认值（默认 0）"},
                "max": {"type": "number", "description": "最大值（默认 1）"},
                "is_blend_shape": {"type": "boolean", "description": "是否为混合形状参数"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_EDIT_PARAMETER = {
    "type": "function",
    "function": {
        "name": "cubism_edit_parameter",
        "description": "编辑参数属性（名称、ID、最小最大值、默认值、是否循环等）。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "要编辑的参数 ID（当前 ID）"},
                "new_id": {"type": "string", "description": "新参数 ID（可选）"},
                "name": {"type": "string", "description": "新参数名称（可选）"},
                "min": {"type": "number", "description": "新最小值"},
                "default": {"type": "number", "description": "新默认值"},
                "max": {"type": "number", "description": "新最大值"},
                "is_repeat": {"type": "boolean", "description": "是否循环"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_DELETE_PARAMETER = {
    "type": "function",
    "function": {
        "name": "cubism_delete_parameter",
        "description": "删除参数。需要在编辑事务内调用。注意：会同时删除该参数上的所有键位！",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "要删除的参数 ID"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_MOVE_PARAMETER = {
    "type": "function",
    "function": {
        "name": "cubism_move_parameter",
        "description": "移动参数到指定参数组的指定位置。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "目标参数 ID"},
                "group_id": {"type": "string", "description": "目标参数组 ID"},
                "insert_index": {"type": "number", "description": "插入位置索引"},
            },
            "required": ["model_uid", "id", "group_id"]
        }
    }
}

# ====== PARAMETER GROUP CRUD (4) ======

TOOL_ADD_PARAMETER_GROUP = {
    "type": "function",
    "function": {
        "name": "cubism_add_parameter_group",
        "description": "添加参数组。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "name": {"type": "string", "description": "参数组名称"},
                "id": {"type": "string", "description": "参数组 ID"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_EDIT_PARAMETER_GROUP = {
    "type": "function",
    "function": {
        "name": "cubism_edit_parameter_group",
        "description": "编辑参数组属性（名称、ID、标签颜色等）。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "参数组 ID"},
                "new_id": {"type": "string", "description": "新参数组 ID"},
                "name": {"type": "string", "description": "新参数组名称"},
                "label_color_type": {
                    "type": "string",
                    "enum": ["Undefined", "Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Gray", "Custom"],
                    "description": "标签颜色类型"
                },
                "label_custom_color": {"type": "string", "description": "自定义颜色 #000000~#FFFFFF（仅当 label_color_type=Custom 时有效）"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_DELETE_PARAMETER_GROUP = {
    "type": "function",
    "function": {
        "name": "cubism_delete_parameter_group",
        "description": "删除参数组。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "要删除的参数组 ID"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_MOVE_PARAMETER_GROUP = {
    "type": "function",
    "function": {
        "name": "cubism_move_parameter_group",
        "description": "移动参数组到指定位置。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "参数组 ID"},
                "insert_index": {"type": "number", "description": "目标索引"},
            },
            "required": ["model_uid", "id", "insert_index"]
        }
    }
}

# ====== KEYFORM (5) ======

TOOL_ADD_PARAMETER_KEY = {
    "type": "function",
    "function": {
        "name": "cubism_add_parameter_key",
        "description": "在对象的参数上添加键位。KeyValue 必须在参数的 Min~Max 范围内。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "object_id": {"type": "string", "description": "对象 ID（ArtMesh/Deformer 等）"},
                "parameter_id": {"type": "string", "description": "参数 ID"},
                "key_value": {"type": "number", "description": "键位值（必须在参数范围内）"},
            },
            "required": ["model_uid", "object_id", "parameter_id", "key_value"]
        }
    }
}

TOOL_DELETE_PARAMETER_KEY = {
    "type": "function",
    "function": {
        "name": "cubism_delete_parameter_key",
        "description": "删除参数键位。Strict=true 时精确匹配 ObjectId+ParameterId，Strict=false 时可宽泛匹配。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "object_id": {"type": "string", "description": "对象 ID"},
                "parameter_id": {"type": "string", "description": "参数 ID（Strict=false 时可选）"},
                "strict": {"type": "boolean", "description": "是否精确匹配（默认 true）"},
                "key_value": {"type": "number", "description": "要删除的键位值（可选）"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_MOVE_PARAMETER_KEY = {
    "type": "function",
    "function": {
        "name": "cubism_move_parameter_key",
        "description": "移动参数键位从 FromValue 到 ToValue。ForceOverwrite=true 时覆盖目标位置已有键位。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "object_id": {"type": "string", "description": "对象 ID"},
                "parameter_id": {"type": "string", "description": "参数 ID"},
                "from_value": {"type": "number", "description": "源键位值"},
                "to_value": {"type": "number", "description": "目标键位值"},
                "strict": {"type": "boolean", "description": "是否精确匹配（默认 true）"},
                "force_overwrite": {"type": "boolean", "description": "是否强制覆盖目标位置已有键位（默认 false）"},
            },
            "required": ["model_uid", "from_value", "to_value"]
        }
    }
}

TOOL_GET_PARAMETER_KEYS = {
    "type": "function",
    "function": {
        "name": "cubism_get_parameter_keys",
        "description": "获取对象关联的参数键位值列表。返回每个参数上有哪些键位值。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "object_id": {"type": "string", "description": "对象 ID"},
            },
            "required": ["model_uid", "object_id"]
        }
    }
}

TOOL_GET_OBJECTS_BY_PARAMETER_KEYS = {
    "type": "function",
    "function": {
        "name": "cubism_get_objects_by_parameter_keys",
        "description": "反向查询：通过参数 ID 和键位值，查找关联了该键位值的对象列表。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "parameter_id": {"type": "string", "description": "参数 ID"},
                "key_value": {"type": "number", "description": "键位值"},
            },
            "required": ["model_uid", "parameter_id", "key_value"]
        }
    }
}

# ====== OBJECT STRUCTURE (4) ======

TOOL_GET_PART_STRUCTURE = {
    "type": "function",
    "function": {
        "name": "cubism_get_part_structure",
        "description": "获取部件树结构。返回嵌套的对象树（Part→ArtMesh/Deformer），包含每个节点的 Name/Id/Type。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_GET_DEFORMER_STRUCTURE = {
    "type": "function",
    "function": {
        "name": "cubism_get_deformer_structure",
        "description": "获取变形器树结构。返回嵌套的变形器层级关系。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_GET_OBJECT = {
    "type": "function",
    "function": {
        "name": "cubism_get_object",
        "description": "获取对象的详细信息。根据对象类型（ArtMesh/WarpDeformer/RotationDeformer/Part/Glue）返回不同字段。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "对象 ID"},
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "参数 ID"},
                            "value": {"type": "number", "description": "参数值"},
                        }
                    },
                    "description": "可选参数过滤"
                },
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_DELETE_OBJECT = {
    "type": "function",
    "function": {
        "name": "cubism_delete_object",
        "description": "从部件调色板删除对象。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "要删除的对象 ID"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_MOVE_OBJECT_ON_PARTS_PALETTE = {
    "type": "function",
    "function": {
        "name": "cubism_move_object_on_parts_palette",
        "description": "在部件调色板上移动对象。指定 ParentId/InsertId/InsertIndex。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "要移动的对象 ID"},
                "parent_id": {"type": "string", "description": "目标父部件 ID"},
                "insert_id": {"type": "string", "description": "插入位置参考对象 ID"},
                "insert_index": {"type": "number", "description": "插入位置索引"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

# ====== PART (2) ======

TOOL_ADD_PART = {
    "type": "function",
    "function": {
        "name": "cubism_add_part",
        "description": "添加新部件。IsNested=true 时 Ids 中的对象会被包含为子对象。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "name": {"type": "string", "description": "部件名称"},
                "id": {"type": "string", "description": "部件 ID"},
                "draw_order": {"type": "number", "description": "绘制顺序（0~1000）"},
                "ids": {
                    "type": "array", "items": {"type": "string"},
                    "description": "要包含的对象 ID 列表"
                },
                "is_nested": {"type": "boolean", "description": "是否将 ids 中的对象嵌套为子对象"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_EDIT_PART = {
    "type": "function",
    "function": {
        "name": "cubism_edit_part",
        "description": "编辑部件属性。可修改名称、分组、引导图像、离屏绘制、裁剪、透明度、混合模式等。Parameters 用于指定关联的参数键位（用于在不同键位值下编辑部件属性）。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "部件 ID"},
                "parameters": {
                    "type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "value": {"type": "number"},
                        }
                    },
                    "description": "关联的参数键位（可选）"
                },
                "is_exact_match": {"type": "boolean", "description": "参数精确匹配（默认 true）"},
                "new_id": {"type": "string", "description": "新部件 ID"},
                "name": {"type": "string", "description": "新部件名称"},
                "parent_id": {"type": "string", "description": "父部件 ID"},
                "is_grouped": {"type": "boolean", "description": "是否分组"},
                "is_guid_image": {"type": "boolean", "description": "是否为引导图像"},
                "is_offscreen": {"type": "boolean", "description": "是否离屏绘制"},
                "clipping_ids": {"type": "array", "items": {"type": "string"}, "description": "裁剪 ID 列表"},
                "is_reverse_mask": {"type": "boolean", "description": "是否反向遮罩"},
                "draw_order": {"type": "number", "description": "绘制顺序（0~1000）"},
                "opacity": {"type": "number", "description": "不透明度（0~100）"},
                "multiply_color": {"type": "string", "description": "正片叠底颜色 #000000~#FFFFFF"},
                "screen_color": {"type": "string", "description": "滤色颜色 #000000~#FFFFFF"},
                "color_blend": {"type": "string", "enum": ["Normal","Add","AddGlow","Darken","Multiply","ColorBurn","LinearBurn","Lighten","Screen","ColorDodge","Overlay","SoftLight","HardLight","LinearLight","Hue","Color","Add_5.2","Multiply_5.2"], "description": "颜色混合模式"},
                "alpha_blend": {"type": "string", "enum": ["Over","Atop","Out","Conjoint","Disjoint"], "description": "Alpha 混合模式"},
                "label_color_type": {"type": "string", "enum": ["Undefined","Red","Orange","Yellow","Green","Blue","Purple","Gray","Custom"], "description": "标签颜色类型"},
                "label_custom_color": {"type": "string", "description": "自定义标签颜色"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

# ====== ART MESH (1) ======

TOOL_EDIT_ARTMESH = {
    "type": "function",
    "function": {
        "name": "cubism_edit_artmesh",
        "description": "编辑 ArtMesh 属性。修改名称、父级、裁剪、透明度、混合模式、颜色等。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "ArtMesh ID"},
                "parameters": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "value": {"type": "number"}}}, "description": "关联参数键位"},
                "is_exact_match": {"type": "boolean", "description": "参数精确匹配"},
                "new_id": {"type": "string"},
                "name": {"type": "string"},
                "parent_id": {"type": "string"},
                "parent_deformer_id": {"type": "string"},
                "clipping_ids": {"type": "array", "items": {"type": "string"}},
                "is_reverse_mask": {"type": "boolean"},
                "draw_order": {"type": "number", "description": "0~1000"},
                "opacity": {"type": "number", "description": "0~100"},
                "multiply_color": {"type": "string", "description": "#000000~#FFFFFF"},
                "screen_color": {"type": "string", "description": "#000000~#FFFFFF"},
                "color_blend": {"type": "string", "enum": ["Normal","Add","AddGlow","Darken","Multiply","ColorBurn","LinearBurn","Lighten","Screen","ColorDodge","Overlay","SoftLight","HardLight","LinearLight","Hue","Color","Add_5.2","Multiply_5.2"]},
                "alpha_blend": {"type": "string", "enum": ["Over","Atop","Out","Conjoint","Disjoint"]},
                "is_culling": {"type": "boolean", "description": "是否剔除"},
                "label_color_type": {"type": "string", "enum": ["Undefined","Red","Orange","Yellow","Green","Blue","Purple","Gray","Custom"]},
                "label_custom_color": {"type": "string"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

# ====== GLUE (1) ======

TOOL_EDIT_GLUE = {
    "type": "function",
    "function": {
        "name": "cubism_edit_glue",
        "description": "编辑胶水（Glue）属性。Glue 用于连接 ArtMesh 到变形器。修改名称、父级、兼容性强度等。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "id": {"type": "string", "description": "Glue ID"},
                "new_id": {"type": "string"},
                "name": {"type": "string"},
                "parent_id": {"type": "string"},
                "intensity": {"type": "number", "description": "兼容性强度 0~100"},
                "parameters": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "value": {"type": "number"}}}},
                "label_color_type": {"type": "string", "enum": ["Undefined","Red","Orange","Yellow","Green","Blue","Purple","Gray","Custom"]},
                "label_custom_color": {"type": "string"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

# ====== DEFORMER (4) ======

TOOL_ADD_ROTATION_DEFORMER = {
    "type": "function",
    "function": {
        "name": "cubism_add_rotation_deformer",
        "description": "添加旋转变形器。Mode='AsParent' 设置为目标对象的父级，'AsChild' 设置为子级。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "name": {"type": "string", "description": "变形器名称"},
                "id": {"type": "string", "description": "变形器 ID"},
                "parent_id": {"type": "string", "description": "父部件 ID（省略则用根节点）"},
                "target_object_ids": {
                    "type": "array", "items": {"type": "string"},
                    "description": "要选中的目标对象 ID 列表"
                },
                "mode": {"type": "string", "enum": ["AsParent", "AsChild"], "description": "与目标对象的层级关系，默认 AsParent"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_ADD_WARP_DEFORMER = {
    "type": "function",
    "function": {
        "name": "cubism_add_warp_deformer",
        "description": "添加弯曲变形器。可设置分割数、是否考虑子元素键位、是否对齐中心。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "name": {"type": "string"},
                "id": {"type": "string"},
                "parent_id": {"type": "string"},
                "target_object_ids": {"type": "array", "items": {"type": "string"}},
                "mode": {"type": "string", "enum": ["AsParent", "AsChild"]},
                "warp_div_h": {"type": "number", "description": "转换分割数（水平）2~100"},
                "warp_div_v": {"type": "number", "description": "转换分割数（垂直）2~100"},
                "bezier_div_h": {"type": "number", "description": "贝塞尔分割数（水平）1~100"},
                "bezier_div_v": {"type": "number", "description": "贝塞尔分割数（垂直）1~100"},
                "consider_child_keyforms": {"type": "boolean", "description": "是否考虑子元素键位"},
                "snap_center": {"type": "boolean", "description": "是否对齐中心（仅 consider_child_keyforms=true 时有效）"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_EDIT_ROTATION_DEFORMER = {
    "type": "function",
    "function": {
        "name": "cubism_edit_rotation_deformer",
        "description": "编辑旋转变形器属性。修改角度、基准角度、缩放、不透明度、颜色等。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string"},
                "id": {"type": "string", "description": "变形器 ID"},
                "new_id": {"type": "string"},
                "name": {"type": "string"},
                "parent_id": {"type": "string"},
                "parent_deformer_id": {"type": "string"},
                "angle": {"type": "number", "description": "旋转角度"},
                "base_angle": {"type": "number", "description": "标准角度"},
                "scale": {"type": "number", "description": "缩放比例"},
                "opacity": {"type": "number", "description": "0~100"},
                "multiply_color": {"type": "string"},
                "screen_color": {"type": "string"},
                "parameters": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "value": {"type": "number"}}}},
                "is_exact_match": {"type": "boolean"},
                "label_color_type": {"type": "string", "enum": ["Undefined","Red","Orange","Yellow","Green","Blue","Purple","Gray","Custom"]},
                "label_custom_color": {"type": "string"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

TOOL_EDIT_WARP_DEFORMER = {
    "type": "function",
    "function": {
        "name": "cubism_edit_warp_deformer",
        "description": "编辑弯曲变形器属性。修改分割数、不透明度、颜色等。需要在编辑事务内调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string"},
                "id": {"type": "string"},
                "new_id": {"type": "string"},
                "name": {"type": "string"},
                "parent_id": {"type": "string"},
                "parent_deformer_id": {"type": "string"},
                "opacity": {"type": "number", "description": "0~100"},
                "multiply_color": {"type": "string"},
                "screen_color": {"type": "string"},
                "warp_div_h": {"type": "number", "description": "2~100"},
                "warp_div_v": {"type": "number", "description": "2~100"},
                "bezier_div_h": {"type": "number", "description": "1~100"},
                "bezier_div_v": {"type": "number", "description": "1~100"},
                "parameters": {"type": "array", "items": {"type": "object"}},
                "is_exact_match": {"type": "boolean"},
                "label_color_type": {"type": "string", "enum": ["Undefined","Red","Orange","Yellow","Green","Blue","Purple","Gray","Custom"]},
                "label_custom_color": {"type": "string"},
            },
            "required": ["model_uid", "id"]
        }
    }
}

# ====== SELECTION (3) ======

TOOL_GET_SELECTED_OBJECTS = {
    "type": "function",
    "function": {
        "name": "cubism_get_selected_objects",
        "description": "获取当前在 Editor 中选中的对象 ID 列表。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_ADD_SELECTED_OBJECTS = {
    "type": "function",
    "function": {
        "name": "cubism_add_selected_objects",
        "description": "添加对象到当前选中状态。在已有选中的基础上追加选择。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
                "ids": {
                    "type": "array", "items": {"type": "string"},
                    "description": "要添加到选中的对象 ID 列表"
                },
            },
            "required": ["model_uid"]
        }
    }
}

TOOL_CLEAR_SELECTED_OBJECTS = {
    "type": "function",
    "function": {
        "name": "cubism_clear_selected_objects",
        "description": "取消选择所有对象。",
        "parameters": {
            "type": "object",
            "properties": {
                "model_uid": {"type": "string", "description": "模型 UID"},
            },
            "required": ["model_uid"]
        }
    }
}


# ====== RULE CREATION (1) ======

TOOL_CREATE_RULE = {
    "type": "function",
    "function": {
        "name": "cubism_create_rule",
        "description": "创建一条可复用的编辑规则（类似 Skill）。当用户说'添加规则'、'创建规则'或描述一个想固化为模板的重复操作时调用此工具。规则创建后会保存为文件，之后可通过 /规则名 快速调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "英文 kebab-case 标识，如 'three-points'、'batch-cleanup'"},
                "description": {"type": "string", "description": "一句中文描述规则用途"},
                "triggers": {
                    "type": "array", "items": {"type": "string"},
                    "description": "触发词列表，含中文自然语言和 /name 格式"
                },
                "steps": {
                    "type": "array", "items": {"type": "string"},
                    "description": "详细执行步骤，每步指定具体的 cubism_* 工具调用"
                },
            },
            "required": ["name", "description", "triggers", "steps"]
        }
    }
}

# ====== ALL TOOLS LIST ======

# ====== PSD READER (1) ======

TOOL_READ_PSD = {
    "type": "function",
    "function": {
        "name": "cubism_read_psd",
        "description": "读取 PSD 文件的图层信息和剪贴蒙版关系。返回图层列表（名称、剪贴标志、是否组）和蒙版关系（被蒙版图层名→蒙版源图层名）。",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "PSD 文件的绝对路径"},
            },
            "required": ["file_path"]
        }
    }
}

# ====== ALL TOOLS LIST ======

ALL_TOOLS = [
    # Auth
    TOOL_CREATE_RULE,
    # PSD
    TOOL_READ_PSD,
    TOOL_REGISTER_PLUGIN, TOOL_GET_IS_APPROVAL,
    # Edit Session
    TOOL_EDIT_BEGIN, TOOL_EDIT_END, TOOL_EDIT_SEND_LOG,
    TOOL_EDIT_SEND_PROGRESS, TOOL_GET_IS_EDIT_APPROVAL, TOOL_NOTIFY_UNDO_CANCEL,
    # Base Queries
    TOOL_GET_DOCUMENTS, TOOL_GET_DOCUMENT, TOOL_GET_CURRENT_DOCUMENT_UID,
    TOOL_GET_CURRENT_MODEL_UID, TOOL_GET_CURRENT_EDIT_MODE,
    TOOL_GET_PARAMETERS, TOOL_GET_PARAMETER_GROUPS,
    TOOL_GET_PHYSICS_INFO, TOOL_SEND_CUBISM_LOG, TOOL_CLEAR_PARAMETER_VALUES,
    # Parameter Values
    TOOL_GET_PARAMETER_VALUES, TOOL_SET_PARAMETER_VALUES,
    # Parameter Structure (5.4)
    TOOL_GET_PARAMETER_STRUCTURE,
    # Parameter CRUD
    TOOL_ADD_PARAMETER, TOOL_EDIT_PARAMETER, TOOL_DELETE_PARAMETER,
    TOOL_MOVE_PARAMETER,
    # Parameter Group CRUD
    TOOL_ADD_PARAMETER_GROUP, TOOL_EDIT_PARAMETER_GROUP,
    TOOL_DELETE_PARAMETER_GROUP, TOOL_MOVE_PARAMETER_GROUP,
    # Keyform
    TOOL_ADD_PARAMETER_KEY, TOOL_DELETE_PARAMETER_KEY, TOOL_MOVE_PARAMETER_KEY,
    TOOL_GET_PARAMETER_KEYS, TOOL_GET_OBJECTS_BY_PARAMETER_KEYS,
    # Object Structure
    TOOL_GET_PART_STRUCTURE, TOOL_GET_DEFORMER_STRUCTURE,
    TOOL_GET_OBJECT, TOOL_DELETE_OBJECT, TOOL_MOVE_OBJECT_ON_PARTS_PALETTE,
    # Part
    TOOL_ADD_PART, TOOL_EDIT_PART,
    # ArtMesh
    TOOL_EDIT_ARTMESH,
    # Glue
    TOOL_EDIT_GLUE,
    # Deformer
    TOOL_ADD_ROTATION_DEFORMER, TOOL_ADD_WARP_DEFORMER,
    TOOL_EDIT_ROTATION_DEFORMER, TOOL_EDIT_WARP_DEFORMER,
    # Selection
    TOOL_GET_SELECTED_OBJECTS, TOOL_ADD_SELECTED_OBJECTS, TOOL_CLEAR_SELECTED_OBJECTS,
]
