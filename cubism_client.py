"""Cubism Editor WebSocket 客户端

管理与 Live2D Cubism Editor 5.4 的 WebSocket 连接。
支持认证、自动重连、持久化 Token。
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional

import websockets
from websockets.asyncio.client import ClientConnection

logger = logging.getLogger(__name__)

# Token 持久化文件
TOKEN_FILE = Path(__file__).parent / ".cubism_token"


def _load_token() -> Optional[str]:
    """从文件加载持久化的 Token"""
    try:
        if TOKEN_FILE.exists():
            data = json.loads(TOKEN_FILE.read_text())
            return data.get("token")
    except Exception:
        pass
    return None


def _save_token(token: str):
    """持久化 Token 到文件"""
    try:
        TOKEN_FILE.write_text(json.dumps({"token": token}, ensure_ascii=False))
        logger.info("Token 已持久化")
    except Exception as e:
        logger.warning(f"Token 持久化失败: {e}")


class CubismClient:
    """Cubism Editor WebSocket 客户端"""

    def __init__(self, ws_url: str = "ws://127.0.0.1:22033"):
        self.ws_url = ws_url
        self._ws: Optional[ClientConnection] = None
        self._token: Optional[str] = _load_token()
        self._connected = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._request_id = 0

        # 状态回调
        self.on_status_change: Optional[Callable] = None  # (connected: bool, info: dict)
        self.on_event: Optional[Callable] = None  # (event_name: str, data: dict)

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def token(self) -> Optional[str]:
        return self._token

    def _next_request_id(self) -> str:
        self._request_id += 1
        return str(self._request_id)

    async def connect(self) -> bool:
        """连接到 Cubism Editor 并注册插件"""
        try:
            self._ws = await websockets.connect(
                self.ws_url,
                ping_interval=15,
                ping_timeout=10,
                max_size=2**20,
            )
            # 注册插件
            result = await self._call_raw("RegisterPlugin", {
                "Name": "Cubism Chat",
                "Token": self._token,
                "Path": "cubism-chat/1.0.0",
            })
            if result and "Token" in result:
                new_token = result["Token"]
                if new_token != self._token:
                    self._token = new_token
                    _save_token(new_token)
                logger.info(f"Cubism 已连接，Token: {self._token[:16]}...")

            self._connected = True
            if self.on_status_change:
                self.on_status_change(True, {"token": self._token})
            return True

        except Exception as e:
            logger.warning(f"Cubism 连接失败: {e}")
            self._connected = False
            if self.on_status_change:
                self.on_status_change(False, {"error": str(e)})
            return False

    async def disconnect(self):
        """断开连接"""
        self._connected = False
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    async def call(self, method: str, data: dict = None) -> dict:
        """调用 Cubism API 方法。

        Args:
            method: API 方法名 (如 "GetParameterValues", "EditParameter")
            data: 请求参数字典

        Returns:
            API 响应数据字典

        Raises:
            RuntimeError: 未连接时调用
            Exception: API 返回错误
        """
        if not self._connected or not self._ws:
            raise RuntimeError("Cubism Editor 未连接")

        return await self._call_raw(method, data or {})

    async def _call_raw(self, method: str, data: dict) -> dict:
        """底层 WebSocket 调用"""
        request = {
            "Version": "1.1.0",
            "Timestamp": int(time.time() * 1000),
            "RequestId": self._next_request_id(),
            "Type": "Request",
            "Method": method,
            "Data": data,
        }
        raw = json.dumps(request, ensure_ascii=False)
        await self._ws.send(raw)

        # 等待响应
        while True:
            resp_raw = await self._ws.recv()
            resp = json.loads(resp_raw)
            resp_type = resp.get("Type")

            if resp_type == "Response":
                return resp.get("Data", {})
            elif resp_type == "Error":
                err_data = resp.get("Data", {})
                err_type = err_data.get("ErrorType", "Unknown")
                raise Exception(f"Cubism API 错误 [{method}]: {err_type} — {err_data}")
            elif resp_type == "Event":
                # 事件通知：交给回调处理，继续等待响应
                if self.on_event:
                    self.on_event(resp.get("Method", ""), resp.get("Data", {}))
            else:
                logger.warning(f"未知响应类型: {resp_type}")

    async def start_reconnect_loop(self):
        """启动自动重连循环"""
        while True:
            if not self._connected:
                logger.info("尝试重连 Cubism Editor...")
                await self.connect()
            await asyncio.sleep(5)

    # ---------- 便捷方法 ----------

    async def get_current_model_uid(self) -> str:
        """获取当前模型 UID"""
        result = await self.call("GetCurrentModelUID")
        return result.get("ModelUID", "")

    async def get_current_edit_mode(self) -> str:
        """获取当前编辑模式"""
        result = await self.call("GetCurrentEditMode")
        return result.get("EditMode", "")

    async def get_parameters(self, model_uid: str = None) -> list:
        """获取参数列表（含 Keyform）"""
        data = {}
        if model_uid:
            data["ModelUID"] = model_uid
        result = await self.call("GetParameters", data)
        return result.get("Parameters", [])

    async def get_parameter_structure(self, model_uid: str) -> dict:
        """获取参数结构树（5.4 新 API）"""
        result = await self.call("GetParameterStructure", {"ModelUID": model_uid})
        return result

    async def get_part_structure(self, model_uid: str) -> dict:
        """获取部件结构树"""
        result = await self.call("GetPartStructure", {"ModelUID": model_uid})
        return result

    async def get_deformer_structure(self, model_uid: str) -> dict:
        """获取变形器结构树"""
        result = await self.call("GetDeformerStructure", {"ModelUID": model_uid})
        return result

    async def get_is_editing(self) -> bool:
        """检查是否有编辑权限"""
        try:
            result = await self.call("GetIsEditApproval")
            return result.get("Result", False)
        except Exception:
            return False
