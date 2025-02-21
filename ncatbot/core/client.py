import asyncio
import json
import os
import platform
import time
import urllib
import urllib.parse

from ncatbot.conn.connect import Websocket
from ncatbot.conn.wsroute import check_websocket
from ncatbot.core.api import BotAPI
from ncatbot.core.launcher import start_napcat
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.plugin import Event, EventBus, PluginLoader
from ncatbot.utils.config import config
from ncatbot.utils.env_checker import check_version
from ncatbot.utils.literals import (
    INSTALL_CHECK_PATH,
    NAPCAT_DIR,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
)
from ncatbot.utils.logger import get_log
from ncatbot.utils.tp_helper import download_napcat, get_proxy_url, get_version

_log = get_log()


class BotClient:
    def __init__(self, plugins_path="plugins"):
        if not config._updated:
            _log.warning("没有主动设置配置项, 配置项将使用默认值")
            time.sleep(0.8)
        _log.info(config)
        time.sleep(1.6)

        self.api = BotAPI()
        self._group_event_handlers = []
        self._private_event_handlers = []
        self._notice_event_handlers = []
        self._request_event_handlers = []
        self.plugins_path = plugins_path
        self.plugin_sys = PluginLoader(EventBus(), self.api)

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
        await self.plugin_sys.load_plugins()
        await websocket_server.on_connect()

    def napcat_server_ok(self):
        return asyncio.run(check_websocket(config.ws_uri))

    def _run(self):
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            _log.info("插件卸载中...")
            asyncio.run(self.plugin_sys._unload_all())
            _log.info("正常退出")
            exit(0)

    def run(self, reload=False, debug=False):
        """
        启动 Bot 客户端

        Args:
            reload: 是否同时启动 NapCat , 默认为 False
            debug: 是否开启调试模式, 默认为 False, 用户不应该修改此参数

        Returns:
            None
        """
        base_path = os.getcwd()

        def check_install_napcat():
            if platform.system() == "Linux":
                napcat_dir = "/opt/QQ/resources/app/app_launcher/napcat"
            else:
                napcat_dir = NAPCAT_DIR

            if platform.system() == "Darwin":
                _log.error("暂不支持 MacOS 系统")
                exit(1)

            if not os.path.exists(napcat_dir):
                if not download_napcat("install", base_path):
                    exit(1)
                with open(
                    os.path.join(napcat_dir, INSTALL_CHECK_PATH), "w", encoding="utf-8"
                ) as f:
                    f.write("installed")
            else:
                # 检查 napcat 版本更新
                with open(
                    os.path.join(napcat_dir, "package.json"), "r", encoding="utf-8"
                ) as f:
                    version = json.load(f)["version"]
                _log.info(f"当前 napcat 版本: {version}")
                _log.info("正在检查更新...")
                github_version = get_version(get_proxy_url())
                if version != github_version:
                    _log.info(f"发现新版本: {github_version}")
                    if not download_napcat("update", base_path):
                        _log.info(f"跳过 napcat {version} 更新")
                else:
                    _log.info("当前 napcat 已是最新版本")

        def connect_napcat():
            MAX_TIME_EXPIRE = time.time() + 60
            INFO_TIME_EXPIRE = time.time() + 20
            _log.info("正在连接 napcat websocket 服务器...")
            while not self.napcat_server_ok():
                time.sleep(2)
                if time.time() > MAX_TIME_EXPIRE:
                    _log.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
                    _log.info("1. 你在另一个黑框框扫码登录了吗?")
                    _log.info("2. 检查 QQ 号是否正确填写?")
                    _log.info("3. 检查网络是否正常?")
                    exit(0)
                if time.time() > INFO_TIME_EXPIRE:
                    _log.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
                    _log.info("1. 你在另一个黑框框扫码登录了吗?")
                    _log.info(f"2. 确认 QQ 号: {config.bt_uin}")
                    INFO_TIME_EXPIRE += 100
            _log.info("连接 napcat websocket 服务器成功!")

        def check_ncatbot_install():
            if not debug:
                # 检查版本和安装方式
                version_ok = check_version()
                if not version_ok:
                    exit(0)

        def ncatbot_quick_start():
            if self.napcat_server_ok():
                _log.info("ncatbot 服务器在线, 连接中...")
                self._run()
            elif reload:
                _log.info("napcat 服务器未启动, 且开启了重加载模式, 运行失败")
                exit(1)
            _log.info("napcat 服务器离线, 启动中...")

        def config_napcat():
            ws_enable = False if config.ws_uri == "" else True
            expected_data = {
                "network": {
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

            def write_start_log():
                _log.info(
                    "NapCatQQ 客户端已启动，如果是第一次启动，请至 WebUI 完成 QQ 登录和其他设置；否则请继续操作"
                )
                _log.info(f"WebUI 地址: {webui_url}, token: {token} (如需要)")
                if token == "napcat" or token == "":
                    _log.warning(
                        "检测到当前 token 为默认初始 token ，如暴露在公网，请登录后立刻在 WebUI 中修改 token"
                    )

            # 切到 config 目录
            if platform.system() == "Linux":
                config_path = "/opt/QQ/resources/app/app_launcher/napcat/config"
                if not os.path.exists(config_path):
                    os.makedirs(config_path)
                os.chdir(config_path)
            else:
                os.chdir(os.path.join(NAPCAT_DIR, "config"))

            # 写 onebot11 qq 数据
            with open(
                "onebot11_" + str(config.bt_uin) + ".json", "w", encoding="utf-8"
            ) as f:
                json.dump(expected_data, f, indent=4, ensure_ascii=False)

            # 配置 qq 快速登录
            os.chdir("../") and os.system(
                f"copy quickLoginExample.bat {config.bt_uin}_quickLogin.bat"
            )

            # 确定 webui 路径
            if platform.system() == "Linux":
                webui_config_path = (
                    "/opt/QQ/resources/app/app_launcher/napcat/config/webui.json"
                )
            else:
                webui_config_path = os.path.join(os.getcwd(), "config", "webui.json")

            # 设置 napcat 连接信息
            webui_url = "无法读取WebUI配置"
            token = ""  # 默认token值
            try:
                with open(webui_config_path, "r") as f:
                    webui_config = json.load(f)
                    host = (
                        "127.0.0.1"
                        if webui_config.get("host") == "0.0.0.0"
                        else webui_config.get("host")
                    )
                    port = webui_config.get("port", 6099)
                    token = webui_config.get("token", "")
                    webui_url = f"http://{host}:{port}/webui?token={token}"
            except FileNotFoundError:
                _log.error("无法读取 WebUI 配置, 将使用默认配置")

            write_start_log()  # 打印启动日志
            os.chdir(base_path)  # 目录切回去

        check_ncatbot_install()  # 检查 ncatbot 安装方式
        ncatbot_quick_start()  # 能够成功连接 napcat 时快速启动

        check_install_napcat()  # 检查和安装 napcat
        config_napcat()  # 配置 napcat
        start_napcat(config, platform.system())  # 启动 napcat
        connect_napcat()  # 连接 napcat
        self._run()
