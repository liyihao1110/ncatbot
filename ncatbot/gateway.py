import websockets
import json

from .config import SetConfig
from .logger import get_log

_log = get_log("ncatbot")
_set = SetConfig()

class Websocket:
    def __init__(self, client):
        self.client = client

    async def receive(self, message):
        msg = json.loads(message)
        if msg['post_type'] == 'message' or msg['post_type'] == 'message_sent':
            if msg['message_type'] == 'group':
                return await self.client.handle_group_event(msg)
            elif msg['message_type'] == 'private':
                return await self.client.handle_private_event(msg)
            else:
                _log.error("这个报错说明message_type不属于group,private\n"+str(msg))
        elif msg['post_type'] == 'notice':
            return await self.client.handle_notice_event(msg)
        elif msg['post_type'] == 'request':
            return await self.client.handle_request_event(msg)
        elif msg['post_type'] == 'meta_event':
            if msg['meta_event_type'] == 'lifecycle':
                _log.info(f"机器人 {msg.get('self_id')} 成功启动")
            else:
                pass
        else:
            _log.error("这是一个错误，请反馈给开发者\n"+str(msg))

    async def ws_connect(self):
        try:
            async with websockets.connect(uri=_set.ws_uri+"/event", extra_headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {_set.token}'} if _set.token else {'Content-Type': 'application/json'}) as ws:
                try:
                    _log.info("websocket连接已建立")
                    while True:
                        message = await ws.recv()
                        await self.receive(message)
                except Exception as e:
                    raise e
        except Exception as e:
            raise e