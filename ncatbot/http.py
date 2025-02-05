import datetime
import json as j

import httpx
from websocket import create_connection

from ncatbot.config import config


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

    def get(self, path, params=None):
        with httpx.Client() as client:
            response = client.get(
                self.url + path, params=params, headers=self.headers, timeout=10
            )
            return response.json()

    def post(self, path, params=None, json=None):
        with httpx.Client() as client:
            if params:
                response = client.post(
                    self.url + path, params=params, headers=self.headers, timeout=10
                )
            elif json:
                response = client.post(
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

    def post(self, path, params=None, json=None):
        websocket = create_connection(self.url, extra_headers=self.headers)
        if params:
            websocket.send(
                j.dumps(
                    {
                        "action": path.replace("/", ""),
                        "params": params,
                        "echo": int(datetime.datetime.now().timestamp()),
                    }
                )
            )
        elif json:
            websocket.send(
                j.dumps(
                    {
                        "action": path.replace("/", ""),
                        "params": json,
                        "echo": int(datetime.datetime.now().timestamp()),
                    }
                )
            )
        response = websocket.recv()
        return j.loads(response)
