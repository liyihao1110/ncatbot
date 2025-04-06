import datetime
import json as j

import websockets

from ncatbot.utils import config, get_log

_log = get_log()


async def check_websocket(uri):
    """
    检查指定的 WebSocket uri 是否可用。

    :return: 如果可用返回 True，否则返回 False
    """
    try:
        async with websockets.connect(
            f"{uri}",
            extra_headers=(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.ws_token}",
                }
                if config.ws_token
                else {"Content-Type": "application/json"}
            ),
        ):
            _log.info(f"WebSocket {uri} 可用.")
            return True
    except Exception:
        # _log.error(f"检查 WebSocket 端口时发生错误: {e}")
        return False


class Route:
    """
    路由类，用于处理 WebSocket 连接。
    """

    def __init__(self):
        self.url = config.ws_uri + "/api"
        self.headers = (
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.ws_token}",
            }
            if config.ws_token
            else {"Content-Type": "application/json"}
        )

    async def post(self, path, params=None, json=None):
        async with websockets.connect(self.url, extra_headers=self.headers) as ws:
            if params:
                await ws.send(
                    j.dumps(
                        {
                            "action": path.replace("/", ""),
                            "params": params,
                            "echo": int(datetime.datetime.now().timestamp()),
                        }
                    )
                )
            elif json:
                await ws.send(
                    j.dumps(
                        {
                            "action": path.replace("/", ""),
                            "params": json,
                            "echo": int(datetime.datetime.now().timestamp()),
                        }
                    )
                )
            return j.loads(await ws.recv())
