"""DeepSeek API 调用 + Tool-Use 循环

实现 OpenAI 兼容的 function calling 循环。
LLM 理解用户意图 → 返回 tool_call → 执行 Cubism API → 继续对话 → 最终自然语言回复。
"""

import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from tools import ALL_TOOLS
from cubism_client import CubismClient
from rules import Rule

logger = logging.getLogger(__name__)


def _extract_json(content: str) -> dict:
    """从 LLM 回复中提取 JSON，处理各种包裹格式"""
    content = content.strip()
    # 去掉 markdown 代码块
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:])
        if content.endswith("```"):
            content = content[:-3]
    # 找到第一个 { 和最后一个 }
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        content = content[start:end + 1]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "解析失败", "raw": content[:500]}

# System Prompt
SYSTEM_PROMPT = """你是 Live2D Cubism Editor 的 AI 编辑助手。你可以通过对话帮助用户编辑 Live2D 模型。

## 环境
- Editor: Live2D Cubism Editor 5.4 alpha1
- 通信: WebSocket JSON-RPC, 端口 22033
- 当前仅在**建模模式（Modeling）**下可用编辑功能

## 编辑事务规则
所有修改操作（add/edit/delete/move）必须在编辑事务内：
1. 先调用 cubism_edit_begin()
2. 执行修改操作（可以多个）
3. 调用 cubism_edit_end()
- 读操作（get_*）可在事务外随时调用
- 同类操作合并到一个事务
- 编辑前先读当前状态确认对象存在

## 基础流程
1. 用户连接后，先检查连接状态和当前模型
2. 用 cubism_get_current_model_uid 和 cubism_get_current_edit_mode 了解环境
3. 根据用户需求选择合适的 API

## 最佳实践
1. **先查后改**：不确定参数/对象 ID 时，先用 get_parameter_structure 或 get_part_structure 查看
2. **批量操作**：多个相关编辑放在一个事务里
3. **ID 准确性**：用查询返回的精确 ID，不要猜测
4. **错误恢复**：遇到 InvalidParameter/InvalidModel 错误时，重新查询可用 ID 再重试

## 参数
- 每个参数有 ID、名称、最小值/最大值/默认值
- 参数可以分组（ParameterGroup）
- 参数有键位（Keyform）：在特定参数值下对象形状的快照
- Type=0 普通参数，Type=1 混合形状参数

## 对象层级
ArtMesh（图形网格）、WarpDeformer（弯曲变形器）、RotationDeformer（旋转变形器）、Part（部件）、Glue（胶水）

## 规则创建
当用户说"添加规则"、"创建规则"或描述一个想固化为模板的重复操作时，调用 cubism_create_rule 工具。生成规则后会弹出确认卡片让用户审核。

## 回复规则（严格遵守）
1. **任务完成时**：只描述当前完成了什么操作和结果。不要给任何建议、不要问"还需要做什么吗"、不要联想后续步骤。用户知道自己在做什么，不需要你引导下一步。
2. **信息不足时**：只问缺失的关键信息（如参数名称、目标值），不要猜测用户的意图或替用户做决定。问完就停。
3. **操作失败时**：说明失败的具体原因。如果能确定缺失什么信息，问用户提供；如果不能，如实描述错误。
4. **展示数据时**：参数/对象结构用树状文本呈现。只呈现用户问的内容，不要展开无关信息。
5. 始终用中文回复，简洁直接。

{{RULES}}"""


RULE_CREATION_PROMPT = """你是规则创建助手。用户想创建一个可复用的 Cubism 编辑规则（类似 Claude Code 的 Skill）。你将用户的口语化描述转换为结构化的规则定义。

规则由四部分组成：
1. **name**: 英文 kebab-case 标识，用于 /name 调用。如 "batch-add-keys"
2. **description**: 一句中文描述用途
3. **triggers**: 触发词列表。必须包含中英文自然语言触发词和 /name 格式
4. **steps**: 详细的 API 调用步骤（中文），每步明确到具体工具名

要求：
- 步骤必须是可执行的 API 调用序列，不能是笼统的建议
- 对于可能缺少信息的地方，加入"如果用户未指定X，先询问X"
- 不调用任何工具，只返回 JSON

你必须只输出一行有效的 JSON，不要有任何解释、问候语、markdown 代码块或其他文字。格式：
{"name":"xxx","description":"xxx","triggers":["触发1","/cmd"],"steps":["步骤1","步骤2"]}"""


class LLMEngine:
    """DeepSeek LLM 引擎"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(300.0))

    async def chat(self, messages: list, cubism: CubismClient,
                   matched_rule: Optional[Rule] = None,
                   rules_summary: str = "") -> AsyncGenerator[dict, None]:
        """处理一轮对话。自动执行 tool-use 循环，流式输出事件。

        Yields:
            {"type": "text", "content": "..."}          — 最终文本回复
            {"type": "tool_call", "name": "...", "args": {...}}  — 工具调用中
            {"type": "rule_draft", "draft": {...}}       — 规则草案
        """
        system_content = self._render_system_prompt(matched_rule, rules_summary)
        full_messages = [
            {"role": "system", "content": system_content},
            *messages,
        ]

        for _ in range(50):
            response = await self._send_message(full_messages, ALL_TOOLS)
            choice = response["choices"][0]
            msg = choice["message"]

            if msg.get("tool_calls"):
                full_messages.append({
                    "role": "assistant",
                    "content": msg.get("content") or "",
                    "tool_calls": msg["tool_calls"],
                })

                for tc in msg["tool_calls"]:
                    tool_name = tc["function"]["name"]
                    try:
                        tool_args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        tool_args = {}
                    tool_id = tc["id"]

                    yield {"type": "tool_call", "name": tool_name, "args": tool_args}

                    try:
                        result = await self._execute_tool(tool_name, tool_args, cubism)
                    except Exception as e:
                        result = {"error": str(e)}

                    # 规则草案 → 不继续循环，交给 main.py 让用户确认
                    if isinstance(result, dict) and "__rule_draft__" in result:
                        draft = {k: v for k, v in result.items() if k != "__rule_draft__"}
                        yield {"type": "rule_draft", "draft": draft}
                        return

                    tool_result = json.dumps(result, ensure_ascii=False, default=str)
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": tool_result,
                    })

            elif msg.get("content"):
                content = msg["content"].strip()
                if content:
                    yield {"type": "text", "content": content}
                    return
                # content 为空字符串，继续循环（可能是模型在等 tool result）
                full_messages.append({"role": "assistant", "content": ""})

            else:
                reason = choice.get("finish_reason", "?")
                logger.warning(f"No content and no tool_calls. finish_reason={reason}")
                yield {"type": "text", "content": f"（模型未返回有效响应，finish_reason={reason}）"}
                return

        yield {"type": "text", "content": "（达到最大对话轮数，请简化你的请求）"}

    def _render_system_prompt(self, matched_rule: Optional[Rule], rules_summary: str) -> str:
        """渲染 system prompt，注入规则信息"""
        if matched_rule:
            from rules import format_rule_for_prompt
            rules_text = format_rule_for_prompt(matched_rule)
        elif rules_summary:
            rules_text = f"## 可用规则\n{rules_summary}\n\n用户可以用 /规则名 调用规则，也可以用触发词自然调用。"
        else:
            rules_text = ""
        return SYSTEM_PROMPT.replace("{{RULES}}", rules_text)

    async def create_rule(self, user_intent: str, messages: list, cubism: CubismClient) -> dict:
        """根据用户意图生成规则草案。

        Returns:
            {"name": ..., "description": ..., "triggers": [...], "steps": [...], "questions": [...]}
        """
        full_messages = [
            {"role": "system", "content": RULE_CREATION_PROMPT},
            *messages,
            {"role": "user", "content": f"用户想要创建的规则: {user_intent}\n\n请分析并生成规则草案。返回纯 JSON。"},
        ]
        response = await self._send_message(full_messages, [])
        content = response["choices"][0]["message"].get("content", "{}")
        return _extract_json(content)

    async def revise_rule(self, current_draft: dict, user_feedback: str) -> dict:
        """根据用户反馈修改规则草案"""
        full_messages = [
            {"role": "system", "content": RULE_CREATION_PROMPT},
            {"role": "user", "content": f"当前规则草案:\n{json.dumps(current_draft, ensure_ascii=False, indent=2)}\n\n用户反馈: {user_feedback}\n\n请修改规则草案。返回纯 JSON。"},
        ]
        response = await self._send_message(full_messages, [])
        content = response["choices"][0]["message"].get("content", "{}")
        return _extract_json(content)

    async def _send_message(self, messages: list, tools: list) -> dict:
        """发送消息到 DeepSeek API"""
        url = f"{self.base_url}/v1/chat/completions"

        body = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": 0.3,
            "max_tokens": 65536,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        choice = result.get("choices", [{}])[0]
        reason = choice.get("finish_reason", "?")
        msg = choice.get("message", {})
        has_tools = bool(msg.get("tool_calls"))
        has_content = bool(msg.get("content"))
        logger.info(f"LLM: finish_reason={reason}, tool_calls={has_tools}, content_len={len(msg.get('content',''))}")
        return result

    async def _execute_tool(self, name: str, args: dict, cubism: CubismClient) -> dict:
        """执行 Cubism API 调用

        将 LLM 返回的 tool_name 和参数映射到 Cubism WebSocket 方法。
        """
        # 去掉 cubism_ 前缀，转为 CamelCase 方法名
        # e.g. cubism_get_parameter_structure → GetParameterStructure
        # e.g. cubism_edit_parameter → EditParameter
        method = self._tool_to_method(name)

        # 转换参数名：snake_case → PascalCase
        data = self._args_to_cubism_data(name, args)

        logger.info(f"Tool: {name} → Method: {method} | Data: {json.dumps(data, ensure_ascii=False)}")

        # cubism_create_rule 是伪 tool — 不调 Cubism，返回标记让 main.py 处理
        if name == "cubism_create_rule":
            return {"__rule_draft__": True, **args}

        result = await cubism.call(method, data)
        return result

    def _tool_to_method(self, tool_name: str) -> str:
        """将 tool 名称映射到 Cubism API 方法名"""
        # 特殊映射
        mapping = {
            "cubism_register_plugin": "RegisterPlugin",
            "cubism_get_is_approval": "GetIsApproval",
            "cubism_edit_begin": "EditBegin",
            "cubism_edit_end": "EditEnd",
            "cubism_edit_send_log": "EditSendLog",
            "cubism_edit_send_progress": "EditSendProgress",
            "cubism_get_is_edit_approval": "GetIsEditApproval",
            "cubism_notify_undo_cancel": "NotifyUndoCancel",
            "cubism_get_documents": "GetDocuments",
            "cubism_get_document": "GetDocument",
            "cubism_get_current_document_uid": "GetCurrentDocumentUID",
            "cubism_get_current_model_uid": "GetCurrentModelUID",
            "cubism_get_current_edit_mode": "GetCurrentEditMode",
            "cubism_get_parameters": "GetParameters",
            "cubism_get_parameter_groups": "GetParameterGroups",
            "cubism_get_physics_info": "GetPhysicsInfo",
            "cubism_send_cubism_log": "SendCubismLog",
            "cubism_clear_parameter_values": "ClearParameterValues",
            "cubism_get_parameter_values": "GetParameterValues",
            "cubism_set_parameter_values": "SetParameterValues",
            "cubism_get_parameter_structure": "GetParameterStructure",
            "cubism_add_parameter": "AddParameter",
            "cubism_edit_parameter": "EditParameter",
            "cubism_delete_parameter": "DeleteParameter",
            "cubism_move_parameter": "MoveParameter",
            "cubism_add_parameter_group": "AddParameterGroup",
            "cubism_edit_parameter_group": "EditParameterGroup",
            "cubism_delete_parameter_group": "DeleteParameterGroup",
            "cubism_move_parameter_group": "MoveParameterGroup",
            "cubism_add_parameter_key": "AddParameterKey",
            "cubism_delete_parameter_key": "DeleteParameterKey",
            "cubism_move_parameter_key": "MoveParameterKey",
            "cubism_get_parameter_keys": "GetParameterKeys",
            "cubism_get_objects_by_parameter_keys": "GetObjectsByParameterKeys",
            "cubism_get_part_structure": "GetPartStructure",
            "cubism_get_deformer_structure": "GetDeformerStructure",
            "cubism_get_object": "GetObject",
            "cubism_delete_object": "DeleteObject",
            "cubism_move_object_on_parts_palette": "MoveObjectOnPartsPalette",
            "cubism_add_part": "AddPart",
            "cubism_edit_part": "EditPart",
            "cubism_edit_artmesh": "EditArtMesh",
            "cubism_edit_glue": "EditGlue",
            "cubism_add_rotation_deformer": "AddRotationDeformer",
            "cubism_add_warp_deformer": "AddWarpDeformer",
            "cubism_edit_rotation_deformer": "EditRotationDeformer",
            "cubism_edit_warp_deformer": "EditWarpDeformer",
            "cubism_get_selected_objects": "GetSelectedObjects",
            "cubism_add_selected_objects": "AddSelectedObjects",
            "cubism_clear_selected_objects": "ClearSelectedObjects",
        }
        return mapping.get(tool_name, tool_name)

    def _args_to_cubism_data(self, tool_name: str, args: dict) -> dict:
        """将 snake_case 参数转换为 Cubism API 期望的 PascalCase 格式"""
        # 通用 snake_case → PascalCase 映射
        key_map = {
            "model_uid": "ModelUID",
            "document_uid": "DocumentUID",
            "parameter_id": "ParameterId",
            "object_id": "ObjectId",
            "group_id": "GroupId",
            "key_value": "KeyValue",
            "new_id": "NewId",
            "is_repeat": "IsRepeat",
            "is_blend_shape": "IsBlendShape",
            "is_exact_match": "IsExactMatch",
            "is_reverse_mask": "IsReverseMask",
            "is_grouped": "IsGrouped",
            "is_guid_image": "IsGuidImage",
            "is_offscreen": "IsOffscreen",
            "is_culling": "IsCulling",
            "is_nested": "IsNested",
            "parent_id": "ParentId",
            "parent_deformer_id": "ParentDeformerId",
            "insert_index": "InsertIndex",
            "insert_id": "InsertId",
            "draw_order": "DrawOrder",
            "from_value": "FromValue",
            "to_value": "ToValue",
            "force_overwrite": "ForceOverwrite",
            "label_color_type": "LabelColorType",
            "label_custom_color": "LabelCustomColor",
            "multiply_color": "MultiplyColor",
            "screen_color": "ScreenColor",
            "color_blend": "ColorBlend",
            "alpha_blend": "AlphaBlend",
            "clipping_ids": "ClippingIds",
            "target_object_ids": "TargetObjectIds",
            "consider_child_keyforms": "ConsiderChildKeyforms",
            "snap_center": "SnapCenter",
            "warp_div_h": "WarpDivH",
            "warp_div_v": "WarpDivV",
            "bezier_div_h": "BezierDivH",
            "bezier_div_v": "BezierDivV",
            "base_angle": "BaseAngle",
        }

        result = {}
        for k, v in args.items():
            camel_key = key_map.get(k, k[0].upper() + k[1:])  # fallback: 首字母大写
            result[camel_key] = v
        return result
