import asyncio
import os
import json
import time

import requests
import zipfile
from tqdm import tqdm

from .gateway import Websocket
from .message import *
from .api import BotAPI
from .setting import SetConfig
from .bot import Bot

_set = SetConfig()

class BotClient:
    def __init__(self, use_ws=True):
        self._api = BotAPI(use_ws)
        self._bot = Bot()

        self._group_event_handler = None
        self._private_event_handler = None
        self._notice_event_handler = None
        self._request_event_handler = None

    def group_event(self, func):
        self._group_event_handler = func
        return func

    def private_event(self, func):
        self._private_event_handler = func
        return func

    def notice_event(self, func):
        self._notice_event_handler = func
        return func

    def request_event(self, func):
        self._request_event_handler = func
        return func

    async def handle_group_event(self, msg: dict):
        if self._group_event_handler:
            msg = GroupMessage(msg)
            await self._group_event_handler(msg)

    async def handle_private_event(self, msg: dict):
        if self._private_event_handler:
            msg = PrivateMessage(msg)
            await self._private_event_handler(msg)

    async def handle_notice_event(self, msg: dict):
        if self._notice_event_handler:
            await self._notice_event_handler(msg)

    async def handle_request_event(self, msg: dict):
        if self._request_event_handler:
            await self._request_event_handler(msg)

    def run(self, reload=False):
        if reload:
            asyncio.run(Websocket(self).ws_connect())
        elif not reload:
            if _set.nap_cat.startswith("https"):
                # _set.nap_cat是一个下载网址，需要下载到本地，并且解压为NapcatFiles文件夹，并且添加下载进度条
                print("[client] 正在下载Napcat客户端，请稍等...")
                try:
                    r = requests.get(_set.nap_cat, stream=True)
                    total_size = int(r.headers.get('content-length', 0))
                    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
                    with open("NapcatFiles.zip", "wb") as f:
                        for data in r.iter_content(chunk_size=1024):
                            progress_bar.update(len(data))
                            f.write(data)
                except Exception as e:
                    print("[client] 下载Napcat客户端失败，请检查网络连接或手动下载Napcat客户端。")
                    print("[client] 错误信息：", e)
                    return
                try:
                    with zipfile.ZipFile("NapcatFiles.zip", 'r') as zip_ref:
                        zip_ref.extractall("NapcatFiles")
                        print("[client] 解压Napcat客户端成功，请运行Napcat客户端。")
                except Exception as e:
                    print("[client] 解压Napcat客户端失败，请检查Napcat客户端是否正确。")
                    print("[client] 错误信息：", e)
                    return
                _set.nap_cat = os.path.join(os.getcwd(),"NapCatFiles")

            os.chdir(os.path.join(_set.nap_cat, "config"))
            http_enable = False if _set.http_url == "" else True
            ws_enable = False if _set.ws_url == "" else True
            expected_data = {
                "network": {
                    "httpServers": [
                        {
                            "name": "httpServer",
                            "enable": http_enable,
                            "port": int(_set.http_port),
                            "host": str(_set.http_ip),
                            "enableCors": True,
                            "enableWebsocket": True,
                            "messagePostFormat": "array",
                            "token": str(_set.http_token),
                            "debug": False
                        }
                    ],
                    "websocketServers": [
                        {
                            "name": "WsServer",
                            "enable": ws_enable,
                            "host": str(_set.ws_ip),
                            "port": int(_set.ws_port),
                            "messagePostFormat": "array",
                            "reportSelfMessage": False,
                            "token": str(_set.ws_token),
                            "enableForcePushEvent": True,
                            "debug": False,
                            "heartInterval": 30000
                        }
                    ]
                },
                "musicSignUrl": "",
                "enableLocalFile2Url": False,
                "parseMultMsg": False
            }
            with open("onebot11_" + str(_set.bot_uin) + ".json", "w", encoding="utf-8") as f:
                json.dump(expected_data, f, indent=4, ensure_ascii=False)
            os.chdir(_set.nap_cat) and os.system(f"copy quickLoginExample.bat {_set.bot_uin}_quickLogin.bat")
            if os.system("ver") == 0:
                # win11
                content = f"@echo off\n./launcher.bat {_set.bot_uin}"
                with open(f"{_set.bot_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{_set.bot_uin}_quickLogin.bat")
            else:
                # win10
                content = f"@echo off\n./launcher-win10.bat {_set.bot_uin}"
                with open(f"{_set.bot_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{_set.bot_uin}_quickLogin.bat")
            i = input("[client] 需要打开官方配置界面进一步配置吗？(y/n): ")
            os.chdir(os.path.join(_set.nap_cat, "config"))
            with open("webui.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                port = data["port"]
                token = data["token"]
            if i == "y":
                url = f"https://napcat.152710.xyz/web_login?back=http://127.0.0.1:{port}&token={token}"
                os.system(f'start "" "{url}"')
            elif i == "n":
                print("[client] 配置完成，napcat客户端此时应该打开了，不要关闭客户端，将主函数内的reload的值改为True，再次运行即可")



