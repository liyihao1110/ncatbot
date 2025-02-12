import asyncio
import json

import websockets

from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log("ncatbot")


class Websocket:
    def __init__(self, client, config=None):
        self.client = client

    async def receive(self, message):
        msg = json.loads(message)
        if msg["post_type"] == "message" or msg["post_type"] == "message_sent":
            if msg["message_type"] == "group":
                asyncio.create_task(self.client.handle_group_event(msg))
            elif msg["message_type"] == "private":
                asyncio.create_task(self.client.handle_private_event(msg))
            else:
                _log.error("这个报错说明message_type不属于group,private\n" + str(msg))
        elif msg["post_type"] == "notice":
            asyncio.create_task(self.client.handle_notice_event(msg))
        elif msg["post_type"] == "request":
            asyncio.create_task(self.client.handle_request_event(msg))
        elif msg["post_type"] == "meta_event":
            if msg["meta_event_type"] == "lifecycle":
                _log.info(f"机器人 {msg.get('self_id')} 成功启动")
            else:
                pass
        else:
            _log.error("这是一个错误，请反馈给开发者\n" + str(msg))

    async def ws_connect(self):
        try:
            async with websockets.connect(
                uri=config.ws_uri + "/event",
                extra_headers=(
                    {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {config.token}",
                    }
                    if config.token
                    else {"Content-Type": "application/json"}
                ),
            ) as ws:
                try:
                    _log.info("websocket连接已建立")
                    while True:
                        message = await ws.recv()
                        try:
                            await self.receive(
                                message
                            )  # 捕获receive内部的异常，不影响程序持续运行
                        except Exception as e:
                            _log.error(f"处理消息时发生错误: {e}")
                except Exception as e:
                    _log.error(f"WebSocket 接收消息异常: {e}")
                    raise e
        except Exception as e:
            _log.error(f"WebSocket 连接错误: {e}")
            raise e
