import json

from websocket import create_connection

from ncatbot.config import config
from ncatbot.logger import get_log

_log = get_log("ncatbot")


class Websocket:
    def __init__(self, client, config=None):
        self.client = client

    def receive(self, message):
        msg = json.loads(message)
        if msg["post_type"] == "message" or msg["post_type"] == "message_sent":
            if msg["message_type"] == "group":
                return self.client.handle_group_event(msg)
            elif msg["message_type"] == "private":
                return self.client.handle_private_event(msg)
            else:
                _log.error("这个报错说明message_type不属于group,private\n" + str(msg))
        elif msg["post_type"] == "notice":
            return self.client.handle_notice_event(msg)
        elif msg["post_type"] == "request":
            return self.client.handle_request_event(msg)
        elif msg["post_type"] == "meta_event":
            if msg["meta_event_type"] == "lifecycle":
                _log.info(f"机器人 {msg.get('self_id')} 成功启动")
            else:
                pass
        else:
            _log.error("这是一个错误，请反馈给开发者\n" + str(msg))

    def ws_connect(self):
        ws = create_connection(
            config.ws_uri, header={"Authorization": f"Bearer {config.token}"}
        )
        while 1:
            try:
                message = ws.recv()
                print(message)
                self.receive(message)
            except Exception as e:
                print(e)
                import traceback

                print(traceback.format_exc())
                return
