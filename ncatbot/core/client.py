import asyncio
import json
import os
import time
import urllib
import urllib.parse
import zipfile

import requests
from tqdm import tqdm

from ncatbot.conn.gateway import Websocket
from ncatbot.conn.http import check_websocket
from ncatbot.core.api import BotAPI
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.plugin.loader import Event, PluginLoader
from ncatbot.utils.config import config
from ncatbot.utils.literals import (
    INSTALL_CHECK_PATH,
    NAPCAT_DIR,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
)
from ncatbot.utils.logger import get_log

_log = get_log()


class BotClient:
    def __init__(self, use_ws=True, plugins_path="plugins"):
        if not config._updated:
            _log.warning("没有主动设置配置项, 配置项将使用默认值")
            time.sleep(0.8)
        _log.info(config)
        time.sleep(1.6)

        self.api = BotAPI(use_ws)
        self._group_event_handlers = []
        self._private_event_handlers = []
        self._notice_event_handlers = []
        self._request_event_handlers = []
        self.plugins_path = plugins_path
        self.plugin_sys = PluginLoader()

    async def handle_group_event(self, msg: dict):
        msg = GroupMessage(msg)
        _log.debug(msg)
        for handler, types in self._group_event_handlers:
            if types is None or any(i["type"] in types for i in msg["message"]):
                await handler(msg)
        await self.plugin_sys.event_bus.publish_async(
            Event(OFFICIAL_GROUP_MESSAGE_EVENT, msg)
        )

    async def handle_private_event(self, msg: dict):
        msg = PrivateMessage(msg)
        _log.debug(msg)
        for handler, types in self._private_event_handlers:
            if types is None or any(i["type"] in types for i in msg["message"]):
                await handler(msg)
        await self.plugin_sys.event_bus.publish_async(
            Event(OFFICIAL_PRIVATE_MESSAGE_EVENT, msg)
        )

    async def handle_notice_event(self, msg: dict):
        _log.debug(msg)
        for handler in self._notice_event_handlers:
            await handler(msg)
        await self.plugin_sys.event_bus.publish_async(Event(OFFICIAL_NOTICE_EVENT, msg))

    async def handle_request_event(self, msg: dict):
        _log.debug(msg)
        for handler in self._request_event_handlers:
            await handler(msg)
        await self.plugin_sys.event_bus.publish_async(
            Event(OFFICIAL_REQUEST_EVENT, msg)
        )

    def group_event(self, types=None):
        def decorator(func):
            self._group_event_handlers.append((func, types))
            return func

        return decorator

    def private_event(self, types=None):
        def decorator(func):
            self._private_event_handlers.append((func, types))
            return func

        return decorator

    def notice_event(self, func):
        self._notice_event_handlers.append(func)
        return func

    def request_event(self, func):
        self._request_event_handlers.append(func)
        return func

    async def run_async(self):
        websocket_server = Websocket(self)
        await self.plugin_sys.load_plugin(self.api)
        await websocket_server.ws_connect()

    def run(self, reload=False):
        def download_napcat():
            if config.np_uri is None:
                raise ValueError("[setting] 缺少配置项，请检查！详情:np_uri")

            if config.np_uri.startswith("https"):
                _log.info("正在下载 napcat 客户端, 请稍等...")
                try:
                    r = requests.get(config.np_uri, stream=True)
                    total_size = int(r.headers.get("content-length", 0))
                    progress_bar = tqdm(
                        total=total_size,
                        unit="iB",
                        unit_scale=True,
                        desc=f"Downloading {NAPCAT_DIR}.zip",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                        colour="green",
                        dynamic_ncols=True,
                        smoothing=0.3,
                        mininterval=0.1,
                        maxinterval=1.0,
                    )
                    with open(f"{NAPCAT_DIR}.zip", "wb") as f:
                        for data in r.iter_content(chunk_size=1024):
                            progress_bar.update(len(data))
                            f.write(data)
                    progress_bar.close()
                except Exception as e:
                    _log.info(
                        "下载 napcat 客户端失败, 请检查网络连接或手动下载 napcat 客户端。"
                    )
                    _log.info("错误信息:", e)
                    return
                try:
                    with zipfile.ZipFile(f"{NAPCAT_DIR}.zip", "r") as zip_ref:
                        zip_ref.extractall(NAPCAT_DIR)
                        _log.info("解压 napcat 客户端成功, 请运行 napcat 客户端.")
                    os.remove(f"{NAPCAT_DIR}.zip")
                except Exception as e:
                    _log.info("解压 napcat 客户端失败, 请检查 napcat 客户端是否正确.")
                    _log.info("错误信息: ", e)
                    return
            else:
                _log.error("不要乱改默认配置谢谢喵~")
                exit(0)
            os.chdir(base_path)

        def config_account():
            os.chdir(os.path.join(NAPCAT_DIR, "config"))
            http_enable = False if config.hp_uri == "" else True
            ws_enable = False if config.ws_uri == "" else True
            expected_data = {
                "network": {
                    "httpServers": [
                        {
                            "name": "httpServer",
                            "enable": http_enable,
                            "port": int(urllib.parse.urlparse(config.hp_uri).port),
                            "host": str(urllib.parse.urlparse(config.hp_uri).hostname),
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
                            "host": str(urllib.parse.urlparse(config.ws_uri).hostname),
                            "port": int(urllib.parse.urlparse(config.ws_uri).port),
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
                "onebot11_" + str(config.bt_uin) + ".json", "w", encoding="utf-8"
            ) as f:
                json.dump(expected_data, f, indent=4, ensure_ascii=False)
            os.chdir("../") and os.system(
                f"copy quickLoginExample.bat {config.bt_uin}_quickLogin.bat"
            )
            if os.system("ver") == 0:
                # win11
                content = f"@echo off\n./launcher.bat {config.bt_uin}"
                with open(f"{config.bt_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{config.bt_uin}_quickLogin.bat")
            else:
                # win10
                content = f"@echo off\n./launcher-win10.bat {config.bt_uin}"
                with open(f"{config.bt_uin}_quickLogin.bat", "w") as f:
                    f.write(content)
                    f.close()
                os.system(f"{config.bt_uin}_quickLogin.bat")
            os.chdir(base_path)

        if reload:
            try:
                asyncio.run(self.run_async())
            except KeyboardInterrupt:
                _log.info("正常退出")
                exit(0)
        elif not reload:
            base_path = os.getcwd()

            # 下载 napcat 客户端
            if not os.path.exists(os.path.join(NAPCAT_DIR, INSTALL_CHECK_PATH)):
                _log.info("未找到 napcat 安装记录, 正在下载 napcat 客户端, 请稍等...")
                download_napcat()
                with open(os.path.join(NAPCAT_DIR, INSTALL_CHECK_PATH), "w") as f:
                    f.write("installed")

            # 配置账号信息
            config_account()
            MAX_TIME_EXPIRE = time.time() + 60

            while (asyncio.run(check_websocket(config.ws_uri))) is False:
                _log.info("正在连接 napcat websocket 服务器...")
                time.sleep(2)
                if time.time() > MAX_TIME_EXPIRE:
                    _log.info("连接 napcat websocket 服务器超时, 请检查以下内容")
                    _log.info("1. 检查 QQ 号是否正确填写")
                    _log.info("2. 检查网络是否正常")
                    exit(0)

            _log.info("连接 napcat websocket 服务器成功!")
            try:
                asyncio.run(self.run_async())
            except KeyboardInterrupt:
                _log.info("正常退出")
                exit(0)
