# encoding:utf-8

"""
负责WebSocket实现文件
"""

import asyncio
import websockets
import json

from . import logging
from .setting import SetConfig

_log = logging.get_logger()

class BotWebSocket:
    def __init__(self, client):
        self.client = client
        self.ws_port = SetConfig().ws_port

    async def on_message(self, ws, message):
        try:
            data = json.loads(message)
            event_type = data.get("post_type")
            if event_type:
                await self.client.on_event(event_type, data)
        except Exception as e:
            _log.error(f"[ncatpy] 消息处理失败: {e}")

    async def ws_connect(self):
        for attempt in range(3):
            try:
                async with websockets.connect(f"ws://localhost:{self.ws_port}/event") as ws:
                    _log.info("[ncatpy] WebSocket 连接成功")
                    while True:
                        message = await ws.recv()
                        await self.on_message(ws, message)
            except websockets.exceptions.ConnectionClosed:
                _log.warning("[ncatpy] WebSocket 连接关闭，尝试重连")
            except Exception as e:
                _log.error(f"[ncatpy] WebSocket 错误: {e}")
            finally:
                await asyncio.sleep(5)
