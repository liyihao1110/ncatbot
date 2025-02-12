import asyncio
import json
import os
import platform
import sys
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
from ncatbot.scripts.check_linux_permissions import check_linux_permissions
from ncatbot.scripts.install_linux_qq import install_linux_qq
from ncatbot.scripts.modify_linux_qq import modify_linux_qq

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
        def get_proxy_url():
            """
            获取 github 代理 URL
            """
            github_proxy_urls = [
                "https://github.7boe.top/",
                "https://cdn.moran233.xyz/",
                "https://gh-proxy.ygxz.in/",
                "https://gh-proxy.lyln.us.kg/",
                "https://github.whrstudio.top/",
                "https://proxy.yaoyaoling.net/",
                "https://ghproxy.net/",
                "https://fastgit.cc/",
                "https://git.886.be/",
                "https://gh-proxy.com/",
                "https://ghfast.top/",
            ]
            github_proxy_url: str = ""
            _log.info("正在尝试连接 GitHub 代理...")
            # 尝试连接 github 代理并自动获取第一个可用的代理
            for url in github_proxy_urls:
                try:
                    _log.info(f"正在尝试连接 {url}")
                    response = requests.get(url, timeout=5)  # 设置超时时间为5秒
                    if response.status_code == 200:
                        # 如果状态码为200，表示成功连接，返回该URL
                        return url
                except requests.RequestException as e:
                    _log.info(f"无法连接到 {url}: {e}, 继续尝试下一个代理...")
                    continue  # 继续尝试下一个URL
            if github_proxy_url == "":
                _log.info("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
                return github_proxy_url

        def get_version(github_proxy_url: str):
            """
            从GitHub获取 napcat 版本号
            """
            version_url = f"{github_proxy_url}https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
            version_response = requests.get(version_url)
            if version_response.status_code == 200:
                version = version_response.json()["version"]
                _log.info(f"获取版本信息成功, 版本号: {version}")
                return version
            else:
                _log.info(
                    f"获取版本信息失败, http 状态码: {version_response.status_code}"
                )
                exit(0)

        def download_napcat(type: str):
            """
            下载 napcat 客户端
            type: str, 可选值为 "install" 或 "update"
            """
            # 下载 napcat 客户端
            try:
                github_proxy_url = get_proxy_url()
                version = get_version(github_proxy_url)
                download_url = f"{github_proxy_url}https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
                _log.info(f"下载链接为 {download_url}...")
                _log.info("正在下载 napcat 客户端, 请稍等...")
                r = requests.get(download_url, stream=True)
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
                _log.error(
                    "下载 napcat 客户端失败, 请检查网络连接或手动下载 napcat 客户端。"
                )
                _log.error("错误信息:", e)
                return
            try:
                with zipfile.ZipFile(f"{NAPCAT_DIR}.zip", "r") as zip_ref:
                    zip_ref.extractall(NAPCAT_DIR)
                    _log.info("解压 napcat 客户端成功, 请运行 napcat 客户端.")
                os.remove(f"{NAPCAT_DIR}.zip")
            except Exception as e:
                _log.error("解压 napcat 客户端失败, 请检查 napcat 客户端是否正确.")
                _log.error("错误信息: ", e)
                return
            os.chdir(base_path)

            if platform.system() == "Linux":
                install_linux_qq(*check_linux_permissions("all"), type)

        def config_account():
            """
            配置账号信息
            """
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
            # 获取操作系统
            system = platform.system()
            if system == "Windows":
                release = platform.release()
                # 对于Windows 10和Windows 11，版本号分别是10和10.0
                if release == "10":
                    # 使用sys.getwindowsversion()获取更详细的版本信息
                    win_version = sys.getwindowsversion()
                    # Windows 11的主版本号是10，次版本号是0，构建号至少为22000
                    if (
                        win_version.major == 10
                        and win_version.minor == 0
                        and win_version.build >= 22000
                    ):
                        # Windows 11
                        _log.info("当前操作系统为: Windows 11")
                        content = f"@echo off\n./launcher.bat {config.bt_uin}"
                    else:
                        # Windows 10
                        _log.info("当前操作系统为: Windows 10")
                        content = f"@echo off\n./launcher-win10.bat {config.bt_uin}"
                    with open(f"{config.bt_uin}_quickLogin.bat", "w") as f:
                        f.write(content)
                        f.close()
                    os.system(f"{config.bt_uin}_quickLogin.bat")
            elif system == "Linux":
                _log.info("当前操作系统为: Linux")
                _log.info("正在启动 QQ ...")
                if check_linux_permissions("root") != "root":
                    _log.error("请使用 root 权限运行 ncatbot")
                    exit(0)
                # 修补QQ
                if not modify_linux_qq():
                    _log.error("安装失败")
                    exit(0)
                # 启动 !
                os.system(
                    f"screen -dmS napcat bash -c 'xvfb-run -a qq --no-sandbox -q {config.bt_uin}'"
                )
            else:
                _log.info(f"当前操作系统为: {system}")
                _log.error("不支持的系统, 请检查错误")
                exit(0)
            os.chdir(base_path)
        if reload:
            asyncio.run(self.run_async())
        elif not reload:
            base_path = os.getcwd()

            # 检查是否存在安装记录
            if not os.path.exists(os.path.join(NAPCAT_DIR, INSTALL_CHECK_PATH)):
                _log.info("未找到 napcat 安装记录, 正在下载 napcat 客户端, 请稍等...")
                download_napcat("install")
                with open(
                    os.path.join(NAPCAT_DIR, INSTALL_CHECK_PATH), "w", encoding="utf-8"
                ) as f:
                    f.write("installed")
            else:
                _log.info("找到 napcat 安装记录, 正在检测版本...")
                with open(
                    os.path.join(NAPCAT_DIR, "package.json"), "r", encoding="utf-8"
                ) as f:
                    version = json.load(f)["version"]
                _log.info(f"当前 napcat 版本为 {version}")
                latest_version = get_version(get_proxy_url())
                if version != latest_version:
                    _log.info("检测到新版本, 正在下载 napcat 客户端, 请稍等...")
                    download_napcat("update")
                else:
                    _log.info("当前 napcat 版本为最新版本, 无需更新")

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
            asyncio.run(self.run_async())
