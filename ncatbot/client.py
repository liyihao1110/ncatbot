import asyncio
import json
import os
import time
import zipfile

import requests
from tqdm import tqdm

from ncatbot.api import BotAPI
from ncatbot.config import config
from ncatbot.gateway import Websocket
from ncatbot.logger import get_log
from ncatbot.message import GroupMessage, PrivateMessage

_log = get_log("ncatbot")

base_path = os.getcwd()


class BotClient:
    def __init__(self, use_ws=True):
        if not config._updated:
            _log.warning("没有主动设置配置项, 配置项将使用默认值")
            time.sleep(0.8)
        _log.info(config)
        time.sleep(1.6)

        self.api = BotAPI(use_ws)
        self._group_event_handler = None
        self._private_event_handler = None
        self._notice_event_handler = None
        self._request_event_handler = None

    def group_event(self, types=None):
        def decorator(func):
            self._group_event_handler = (func, types)
            return func

        return decorator

    def private_event(self, types=None):
        def decorator(func):
            self._private_event_handler = (func, types)
            return func

        return decorator

    def notice_event(self, func):
        self._notice_event_handler = func
        return func

    def request_event(self, func):
        self._request_event_handler = func
        return func

    async def handle_group_event(self, msg: dict):
        if self._group_event_handler:
            func, types = self._group_event_handler
            if types is None or any(i["type"] in types for i in msg["message"]):
                msg = GroupMessage(msg)
                await func(msg)

    async def handle_private_event(self, msg: dict):
        if self._private_event_handler:
            func, types = self._private_event_handler
            if types is None or any(i["type"] in types for i in msg["message"]):
                msg = PrivateMessage(msg)
                await func(msg)

    async def handle_notice_event(self, msg: dict):
        if self._notice_event_handler:
            await self._notice_event_handler(msg)

    async def handle_request_event(self, msg: dict):
        if self._request_event_handler:
            await self._request_event_handler(msg)

    async def run_async(self):
        websocket_server = Websocket(self)
        await websocket_server.ws_connect()

    def run(self, reload=False):
        if reload:
            asyncio.run(self.run_async())
        elif not reload:
            if config.np_uri is None:
                raise ValueError("[setting] 缺少配置项，请检查！详情:np_uri")
            if config.np_uri.startswith("https"):
                if not os.path.exists("NapcatFiles"):
                    _log.info("正在下载Napcat客户端，请稍等...")
                    try:
                        r = requests.get(config.np_uri, stream=True)
                        total_size = int(r.headers.get("content-length", 0))
                        progress_bar = tqdm(
                            total=total_size,
                            unit="iB",
                            unit_scale=True,
                            desc="Downloading NapcatFiles.zip",
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                            colour="green",
                            dynamic_ncols=True,
                            smoothing=0.3,
                            mininterval=0.1,
                            maxinterval=1.0,
                        )
                        with open("NapcatFiles.zip", "wb") as f:
                            for data in r.iter_content(chunk_size=1024):
                                progress_bar.update(len(data))
                                f.write(data)
                        progress_bar.close()
                    except Exception as e:
                        _log.info(
                            "下载Napcat客户端失败，请检查网络连接或手动下载Napcat客户端。"
                        )
                        _log.info("错误信息：", e)
                        return
                    try:
                        with zipfile.ZipFile("NapcatFiles.zip", "r") as zip_ref:
                            zip_ref.extractall("NapcatFiles")
                            _log.info("解压Napcat客户端成功，请运行Napcat客户端。")
                        os.remove("NapcatFiles.zip")
                    except Exception as e:
                        _log.info("解压Napcat客户端失败，请检查Napcat客户端是否正确。")
                        _log.info("错误信息：", e)
                        return
                    config.nap_cat = os.path.join(os.getcwd(), "NapCatFiles")
                else:
                    config.nap_cat = os.path.join(os.getcwd(), "NapCatFiles")

            os.chdir(os.path.join(config.nap_cat, "config"))
            http_enable = False if config.hp_uri == "" else True
            ws_enable = False if config.ws_uri == "" else True
            expected_data = {
                "network": {
                    "httpServers": [
                        {
                            "name": "httpServer",
                            "enable": http_enable,
                            "port": int(config.http_port),
                            "host": str(config.http_ip),
                            "enableCors": True,
                            "enableWebsocket": True,
                            "messagePostFormat": "array",
                            "token": (
                                str(config.token) if config.token is not None else ""
                            ),
                            "debug": False,
                        }
                    ],
                    "websocketServers": [
                        {
                            "name": "WsServer",
                            "enable": ws_enable,
                            "host": str(config.ws_ip),
                            "port": int(config.ws_port),
                            "messagePostFormat": "array",
                            "reportSelfMessage": False,
                            "token": (
                                str(config.token) if config.token is not None else ""
                            ),
                            "enableForcePushEvent": True,
                            "debug": False,
                            "heartInterval": 30000,
                        }
                    ],
                },
                "musicSignUrl": "",
                "enableLocalFile2Url": False,
                "parseMultMsg": False,
            }
            with open(
                "onebot11_" + str(config.bot_uin) + ".json", "w", encoding="utf-8"
            ) as f:
                json.dump(expected_data, f, indent=4, ensure_ascii=False)
            os.chdir(config.nap_cat) and os.system(
                f"copy quickLoginExample.bat {config.bot_uin}_quickLogin.bat"
            )
            if os.system("ver") == 0:
                # win11
                content = f"@echo off\n./launcher.bat {config.bot_uin}"
                with open(f"{config.bot_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{config.bot_uin}_quickLogin.bat")
            else:
                # win10
                content = f"@echo off\n./launcher-win10.bat {config.bot_uin}"
                with open(f"{config.bot_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{config.bot_uin}_quickLogin.bat")
            os.chdir(base_path)
            time.sleep(3)
            asyncio.run(self.run_async())
