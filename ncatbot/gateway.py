import websockets
import json

from .setting import SetConfig
from .user import User

class Websocket:
    def __init__(self, client):
        self.client = client
        self.user = User()

    async def receive(self, message):
        msg = json.loads(message)
        if msg['post_type'] == 'message':
            if msg['message_type'] == 'group':
                return await self.client.handle_group_event(msg)
            elif msg['message_type'] == 'private':
                return await self.client.handle_private_event(msg)
            else:
                print("[gateway] 这个报错说明message_type不属于group,private\n"+str(msg))
        elif msg['post_type'] == 'notice':
            return await self.client.handle_notice_event(msg)
        elif msg['post_type'] == 'request':
            return await self.client.handle_request_event(msg)
        elif msg['post_type'] == 'meta_event':
            if msg['meta_event_type'] == 'lifecycle':
                print(f"[gateway] 机器人 {msg.get('self_id')} 成功启动")
            else:
                pass
        else:
            print(f"[gateway] 如果没错，这是一个错误，请反馈给开发者\n"+str(msg))

    async def ws_connect(self):
        try:
            async with websockets.connect(uri=SetConfig().ws_url,
                                          extra_headers={"Authorization": SetConfig().ws_token}) as ws:
                try:
                    print("[gateway] websocket连接已建立")
                    while True:
                        message = await ws.recv()
                        await self.receive(message)
                        await self.user.on_private_msg(message)
                except Exception as e:
                    raise e
        except Exception as e:
            raise e
        finally:
            print("[gateway] 切换连接方式...这是一个bug，如果你看见了这条输出内容，请提交issue")
            async with websockets.connect(uri=SetConfig().ws_url,
                                          user_agent_header={"Authorization": SetConfig().ws_token}) as ws:
                try:
                    print("[gateway] websocket连接已建立")
                    while True:
                        message = await ws.recv()
                        await self.receive(message)
                        await self.user.on_private_msg(message)
                except Exception as e:
                    raise e





