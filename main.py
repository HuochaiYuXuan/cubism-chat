"""Cubism Chat — LLM 对话式 Live2D 编辑应用

FastAPI 后端 + WebSocket 聊天 + Cubism Editor 连接
"""

import sys, os, traceback

# 尽早捕获异常写入日志
def _log_error(msg: str):
    try:
        with open(os.path.join(os.path.dirname(sys.executable), "cubism-chat-error.log"), "a") as f:
            f.write(msg + "\n")
    except:
        pass

try:
    import asyncio
    import json
    import logging
    from contextlib import asynccontextmanager
    from pathlib import Path
except Exception as e:
    _log_error(f"Import error: {traceback.format_exc()}")
    raise

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from cubism_client import CubismClient
from llm import LLMEngine
from rules import load_rules, find_rule, list_rules_summary, save_rule, delete_rule

load_dotenv()

# PyInstaller 兼容：打包后 sys._MEIPASS 是临时解压目录
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("cubism-chat")

# ---- 全局状态 ----
cubism = CubismClient(os.getenv("CUBISM_WS_URL", "ws://127.0.0.1:22033"))
llm = LLMEngine(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
rules = load_rules()
logger.info(f"已加载 {len(rules)} 条规则")

# 每个 WebSocket 连接的会话状态
sessions: dict[int, dict] = {}  # {id(ws): {"history": [], "llm": LLMEngine, "settings": {}, "rule_draft": {}}}


# ---- 生命周期 ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭"""
    # 启动时连接 Cubism
    logger.info("正在连接 Cubism Editor...")
    connected = await cubism.connect()
    if connected:
        logger.info("已连接到 Cubism Editor")
    else:
        logger.warning("无法连接到 Cubism Editor，将在后台重试")

    # 启动重连循环
    reconnect_task = asyncio.create_task(_reconnect_loop())

    yield

    # 关闭
    reconnect_task.cancel()
    await cubism.disconnect()


async def _reconnect_loop():
    """后台重连循环"""
    backoff = 5
    while True:
        await asyncio.sleep(backoff)
        if not cubism.connected:
            logger.info(f"尝试重连 (退避 {backoff}s)...")
            ok = await cubism.connect()
            if ok:
                backoff = 5
            else:
                backoff = min(backoff * 2, 60)


# ---- FastAPI ----
app = FastAPI(title="Cubism Chat", lifespan=lifespan)

# 静态文件
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
async def index():
    """聊天界面"""
    return FileResponse("static/index.html")


@app.get("/api/status")
async def status():
    """返回 Cubism 连接状态"""
    info = {"connected": cubism.connected}
    if cubism.connected:
        try:
            uid = await cubism.get_current_model_uid()
            mode = await cubism.get_current_edit_mode()
            has_edit = await cubism.get_is_editing()
            info.update({
                "model_uid": uid,
                "edit_mode": mode,
                "can_edit": has_edit,
            })
        except Exception as e:
            info["error"] = str(e)
    return info


@app.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    """聊天 WebSocket 端点"""
    global rules
    await ws.accept()
    session_id = id(ws)
    sessions[session_id] = {
        "history": [],
        "llm": None,    # 等收到 settings 后创建
        "settings": {},
        "rule_draft": {},
    }

    # 发送连接状态
    await _send_json(ws, {
        "type": "status",
        "connected": cubism.connected,
        "model_uid": await _safe_get_model_uid(),
        "edit_mode": await _safe_get_edit_mode(),
    })

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "chat")

            # ---- 设置更新 ----
            if msg_type == "settings":
                api_key = msg.get("apiKey", "")
                model = msg.get("model", "deepseek-chat")
                base_url = msg.get("baseUrl", os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
                cubism_port = msg.get("cubismPort", "22033")
                sessions[session_id]["settings"] = {
                    "apiKey": api_key,
                    "model": model,
                    "baseUrl": base_url,
                    "cubismPort": cubism_port,
                }
                if api_key:
                    sessions[session_id]["llm"] = LLMEngine(
                        api_key=api_key,
                        base_url=base_url,
                        model=model,
                    )
                    logger.info(f"Session {session_id}: LLM 已配置 (model={model})")
                else:
                    sessions[session_id]["llm"] = None
                await _send_json(ws, {
                    "type": "message",
                    "role": "system",
                    "content": f"设置已更新 (模型: {model})。" if api_key else "API Key 为空，请填入后保存。",
                })
                continue

            # ---- 聊天消息 ----
            user_text = msg.get("content", "").strip()

            # ---- 规则草案确认 ----
            if msg_type == "confirm_rule":
                draft = sessions[session_id].get("rule_draft", {})
                if draft:
                    path = save_rule(
                        name=draft.get("name", "untitled"),
                        description=draft.get("description", ""),
                        triggers=draft.get("triggers", []),
                        body="\n".join(draft.get("steps", [])),
                    )
                    rules = load_rules()
                    sessions[session_id]["rule_draft"] = {}
                    await _send_json(ws, {
                        "type": "message",
                        "role": "system",
                        "content": f"规则已保存: {draft['name']} → {path}",
                    })
                    # 刷新前端规则列表
                    await _send_json(ws, {
                        "type": "rules_list",
                        "rules": [{"name": r.name, "description": r.description, "triggers": r.triggers} for r in rules],
                    })
                continue

            # ---- 删除规则 ----
            if msg_type == "delete_rule":
                rule_name = msg.get("name", "")
                if rule_name:
                    deleted = delete_rule(rule_name)
                    rules = load_rules()
                    await _send_json(ws, {
                        "type": "message",
                        "role": "system",
                        "content": f"规则已删除: {rule_name}" if deleted else f"规则不存在: {rule_name}",
                    })
                    await _send_json(ws, {
                        "type": "rules_list",
                        "rules": [{"name": r.name, "description": r.description, "triggers": r.triggers} for r in rules],
                    })
                continue

            # ---- 列出规则 ----
            is_list_rules = user_text.strip() in ("/", "列出规则", "规则列表", "所有规则")

            sess_llm = sessions[session_id].get("llm")
            if not sess_llm and not is_list_rules:
                default_key = os.getenv("DEEPSEEK_API_KEY", "")
                if default_key:
                    sess_llm = LLMEngine(api_key=default_key)
                    sessions[session_id]["llm"] = sess_llm
                else:
                    await _send_json(ws, {
                        "type": "message", "role": "ai",
                        "content": "请先在右上角设置中填入 DeepSeek API Key。",
                    })
                    continue

            if is_list_rules:
                await _send_json(ws, {
                    "type": "rules_list",
                    "rules": [{"name": r.name, "description": r.description, "triggers": r.triggers} for r in rules],
                })
                continue

            # ---- 规则匹配 ----
            matched = find_rule(user_text, rules)
            matched_rule = matched[0] if matched else None
            user_args = matched[1] if matched else ""

            # 如果匹配到规则，把参数追加到消息中
            if matched_rule and user_args:
                sessions[session_id]["history"].append({
                    "role": "user",
                    "content": f"[规则: {matched_rule.name}] 用户参数: {user_args}\n原始输入: {user_text}",
                })
            else:
                sessions[session_id]["history"].append({"role": "user", "content": user_text})

            # 发送"思考中"状态
            await _send_json(ws, {"type": "thinking", "active": True})

            # 如果匹配到规则，通知前端
            if matched_rule:
                await _send_json(ws, {
                    "type": "rule_triggered",
                    "name": matched_rule.name,
                    "description": matched_rule.description,
                })

            try:
                history = sessions[session_id]["history"]
                rules_summary = list_rules_summary(rules)

                async for event in sess_llm.chat(history, cubism, matched_rule, rules_summary):
                    etype = event.get("type")

                    if etype == "text":
                        history.append({"role": "assistant", "content": event["content"]})
                        if len(history) > 200:
                            sessions[session_id]["history"] = history[-200:]
                        await _send_json(ws, {
                            "type": "message", "role": "ai", "content": event["content"],
                        })

                    elif etype == "tool_call":
                        await _send_json(ws, {
                            "type": "tool_call_progress",
                            "name": event["name"],
                            "args": event.get("args", {}),
                        })

                    elif etype == "rule_draft":
                        draft = event["draft"]
                        sessions[session_id]["rule_draft"] = draft
                        history.append({"role": "assistant", "content": f"[规则草案: {draft.get('name', '?')}]"})
                        await _send_json(ws, {"type": "rule_draft", "draft": draft})

            except Exception as e:
                logger.error(f"LLM error: {e}")
                await _send_json(ws, {
                    "type": "message", "role": "ai",
                    "content": f"处理请求时出错：{e}",
                })

            finally:
                await _send_json(ws, {"type": "thinking", "active": False})

    except WebSocketDisconnect:
        pass
    finally:
        sessions.pop(session_id, None)


async def _send_json(ws: WebSocket, data: dict):
    """安全发送 JSON"""
    try:
        await ws.send_text(json.dumps(data, ensure_ascii=False, default=str))
    except Exception:
        pass


async def _safe_get_model_uid() -> str:
    try:
        return await cubism.get_current_model_uid() if cubism.connected else ""
    except Exception:
        return ""


async def _safe_get_edit_mode() -> str:
    try:
        return await cubism.get_current_edit_mode() if cubism.connected else ""
    except Exception:
        return ""


if __name__ == "__main__":
    import traceback
    import uvicorn
    import webbrowser

    # 全局异常钩子 — 防止 PyInstaller exe 闪退
    def _global_excepthook(etype, value, tb):
        msg = "".join(traceback.format_exception(etype, value, tb))
        print(msg)
        _log_error(msg)
        input("Press Enter to exit...")
    sys.excepthook = _global_excepthook

    try:
        host = os.getenv("APP_HOST", "127.0.0.1")
        port = int(os.getenv("APP_PORT", "8765"))
        webbrowser.open(f"http://{host}:{port}")
        uvicorn.run("main:app", host=host, port=port, reload=False)
    except Exception:
        traceback.print_exc()
        _log_error(traceback.format_exc())
        input("Press Enter to exit...")
