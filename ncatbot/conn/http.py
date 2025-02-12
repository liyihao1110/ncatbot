import datetime
import json as j

import httpx
import websockets

from ncatbot.utils.config import config


async def check_websocket(uri):
    """
    检查指定的 WebSocket uri 是否可用。

    :return: 如果可用返回 True，否则返回 False
    """
    headers = (
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.token}",
        }
        if config.token
        else {"Content-Type": "application/json"}
    )
    try:
        # 尝试连接 WebSocket 服务器
        async with websockets.connect(f"{uri}", extra_headers=headers):
            (f"WebSocket {uri} 可用.")
            return True
    except Exception as e:
        print(f"检查 WebSocket 端口时发生错误: {e}")
        return False


class Route:
    def __init__(self):
        self.headers = (
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.token}",
            }
            if config.token
            else {"Content-Type": "application/json"}
        )
        self.url = config.hp_uri

    async def get(self, path, params=None):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.url + path, params=params, headers=self.headers, timeout=10
            )
            return response.json()

    async def post(self, path, params=None, json=None):
        async with httpx.AsyncClient() as client:
            if params:
                response = await client.post(
                    self.url + path, params=params, headers=self.headers, timeout=10
                )
            elif json:
                response = await client.post(
                    self.url + path, json=json, headers=self.headers, timeout=10
                )
            return response.json()


class WsRoute:
    def __init__(self):
        self.url = config.ws_uri + "/api"
        self.headers = (
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.token}",
            }
            if config.token
            else {"Content-Type": "application/json"}
        )

    async def post(self, path, params=None, json=None):
        async with websockets.connect(
            self.url, extra_headers=self.headers
        ) as websocket:
            if params:
                await websocket.send(
                    j.dumps(
                        {
                            "action": path.replace("/", ""),
                            "params": params,
                            "echo": int(datetime.datetime.now().timestamp()),
                        }
                    )
                )
            elif json:
                await websocket.send(
                    j.dumps(
                        {
                            "action": path.replace("/", ""),
                            "params": json,
                            "echo": int(datetime.datetime.now().timestamp()),
                        }
                    )
                )
            response = await websocket.recv()
            return j.loads(response)
