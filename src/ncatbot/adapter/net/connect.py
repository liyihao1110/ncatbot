import asyncio
import json

import websockets

from ncatbot.utils import config, get_log

_log = get_log()


def connect(uri, *, extra_headers, **kwargs):
    """
    使用自定义的 connect 函数来同时兼容新版和旧版 websockets

    默认使用旧版参数名 ``extra_headers``
    """
    return websockets.connect(
        uri,
        extra_headers=extra_headers,
        **kwargs
    )

try:
    import websockets.asyncio.client

    if websockets.connect == websockets.asyncio.client.connect:
        def connect(uri, *, extra_headers, **kwargs):
            """
            如果 ``websockets.connect`` 对应新版 ``asyncio`` 实现，需要把参数名 ``extra_headers`` 改为 ``additional_headers``
            """
            return websockets.connect(
                uri,
                additional_headers=extra_headers,
                **kwargs
            )
except ImportError:
    pass


class Websocket:
    def __init__(self, client):
        self.client = client
        self._websocket_uri = f"{config.ws_uri}/event"
        self._header = (
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.ws_token}",
            }
            if config.ws_token
            else {"Content-Type": "application/json"}
        )

    def on_message(self, message: dict):
        message_post_type = message.get("post_type")
        message_type = message.get("message_type")
        if message_post_type in {"message", "message_sent"}:
            if message_type == "group":
                asyncio.create_task(self.client.handle_group_event(message))
            elif message_type == "private":
                asyncio.create_task(self.client.handle_private_event(message))
            else:
                _log.error(
                    "Unknown error: Unrecognized message type!Please check log info!"
                ) and _log.debug(message)
        elif message_post_type == "notice":
            asyncio.create_task(self.client.handle_notice_event(message))
        elif message_post_type == "request":
            asyncio.create_task(self.client.handle_request_event(message))
        elif message_post_type == "meta_event":
            if message["meta_event_type"] == "lifecycle":
                asyncio.create_task(self.client.handle_startup_event())
                _log.info(f"机器人 {message.get('self_id')} 成功启动")
            else:
                _log.debug(message)
        else:
            _log.error(
                "Unknown error: Unrecognized message type!Please check log info!"
            ) and _log.debug(message)
        del message_post_type, message_type

    async def on_connect(self):
        async with connect(
            uri=self._websocket_uri, extra_headers=self._header, ping_interval=None
        ) as ws:
            # 我发现你们在client.py中已经进行了websocket连接的测试，故删除了此处不必要的错误处理。
            while True:
                try:
                    message = await ws.recv()
                    message = json.loads(message)
                    self.on_message(message)
                # 这里的错误处理没有进行细分，我觉得没有很大的必要，报错的可能性不大，如果你对websocket了解很深，请完善此部分。
                except Exception as e:
                    _log.error(f"Websocket error: {e}")
                    raise e
