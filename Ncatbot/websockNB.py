
import json
import time
import websockets

from .api import BotAPI
from .client import BotClient  # 注意首字母大写
from .settings import settings
from .log import get_logger

_log = get_logger()

api: BotAPI


def core(http_port: (int, str), ws_port: (int, str), max_ids=100):
    global api
    settings.max_ids = max_ids
    settings.port_or_http = http_port
    api = BotAPI(http_port)
    client = BotWebSocket(ws_port)
    return client, api


class BotWebSocket:
    """
    一个 WebSocket 客户端类，用于与机器人服务器进行通信。
    """
    def __init__(self, port_or_http=None):
        """
        初始化 BotWebSocket 实例。
        :param port_or_http: WebSocket 服务器的 URL或端口号。
        """
        self.url = port_or_http if str(port_or_http).startswith('ws') else f'ws://localhost:{port_or_http}'
        self.client = BotClient()

    async def on_message(self, ws, message):
        """
        处理接收到的消息。
        根据消息类型调用相应的处理器。
        """
        message = json.loads(message)

        event = message.get('post_type')
        event_type = message.get('meta_event_type')
        _time = message.get('time')
        time_tuple = time.localtime(_time)
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)

        if event == "meta_event" and event_type == 'lifecycle':
            nickname = await api.get_login_info()
            _log.info(f"机器人 [{nickname['data']['nickname']}] 成功上线! ({formatted_time})")

        # message_sent 需要去 web 控制台打开 “上报 Bot 自身发送的消息”
        elif event == "message" and "message_sent":
            if message.get('message_type') == 'private':
                await self.client.private_message_handle(message)
            elif message.get('message_type') == 'group':
                await self.client.group_message_handle(message)

        elif event == "request":
            await self.client.request_handle(message)  # 使用 self.client 调用方法

        elif event == "notice":
            await self.client.notice_handle(message)  # 使用 self.client 调用方法

    async def on_error(self, ws, error):
        """
        处理错误。
        """
        _log.error(error)

    async def on_close(self, ws, close_status_code, close_msg):
        """
        处理连接关闭。
        """
        _log.warning("### closed ###")

    async def on_open(self, ws):
        """
        处理连接打开。
        """
        _log.info("### connection success ###")

    async def ws_run(self):
        """
        运行 WebSocket 客户端。
        创建并启动 WebSocket 客户端。
        """
        async with websockets.connect(self.url) as websocket:
            await self.on_open(websocket)
            while True:
                try:
                    message = await websocket.recv()
                    await self.on_message(websocket, message)
                except websockets.ConnectionClosed:
                    _log.info("### closed ###")
                    break
