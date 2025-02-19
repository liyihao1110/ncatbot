import asyncio
import json

import websockets

from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log()


class Websocket:
    def __init__(self, client):
        self.client = client
        self._websocket_uri = config.ws_uri + "/event"
        self._header = {"Content-Type": "application/json","Authorization": f"Bearer {config.token}"} if config.token else {"Content-Type": "application/json"}

    async def on_message(self, message: dict):
        if message["post_type"] == "message" or message["post_type"] == "message_sent":
            if message["message_type"] == "group":
                asyncio.create_task(self.client.handle_group_event(message))
            elif message["message_type"] == "private":
                asyncio.create_task(self.client.handle_private_event(message))
            else:
                _log.error("Unknown error: Unrecognized message type!Please check log info!") and _log.debug(message)
        elif message["post_type"] == "notice":
            asyncio.create_task(self.client.handle_notice_event(message))
        elif message["post_type"] == "request":
            asyncio.create_task(self.client.handle_request_event(message))
        elif message["post_type"] == "meta_event":
            if message["meta_event_type"] == "lifecycle":
                _log.info(f"机器人 {message.get('self_id')} 成功启动")
            else:
                _log.debug(message)
        else:
            _log.error("Unknown error: Unrecognized message type!Please check log info!") and _log.debug(message)

    async def on_error(self, error):
        _log.error(f"WebSocket 连接错误: {error}")
    
    async def on_close(self):
        _log.info("WebSocket 连接已关闭")
    
    async def on_connect(self):
        async with websockets.connect(uri=self._websocket_uri, extra_headers=self._header) as ws:
            # 我发现你们在client.py中已经进行了websocket连接的测试，故删除了此处不必要的错误处理。
            while True:
                try:
                    message = await ws.recv()
                    message = json.loads(message)
                    await self.on_message(message)
                # 这里的错误处理没有进行细分，我觉得没有很大的必要，报错的可能性不大，如果你对websocket了解很深，请完善此部分。
                except Exception as e:
                    await self.on_error(e)
                    break
            await self.on_close()

