import asyncio
import json
import os
import platform
import shutil
import time
from urllib.parse import urlparse

from ncatbot.conn import LoginHandler, Websocket, check_websocket
from ncatbot.core.api import BotAPI
from ncatbot.core.launcher import start_napcat
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.env_checker import check_linux_permissions, check_version
from ncatbot.utils.literals import (
    LINUX_NAPCAT_DIR,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    WINDOWS_NAPCAT_DIR,
)
from ncatbot.utils.logger import get_log
from ncatbot.utils.tp_helper import download_napcat, get_version

_log = get_log()


class BotClient:
    registered = False

    def __init__(self, plugins_path="plugins"):
        def check_config():
            if not config._updated:
                _log.info("没有主动设置配置项, 配置项将使用默认值")
            if config.bt_uin is config.default_bt_uin:
                _log.error("请设置正确的 Bot QQ 号")
                exit(1)
            if config.root is config.default_root:
                _log.warning("建议设置好 root 账号保证权限功能能够正常使用")
            _log.info(config)

        def check_duplicate_register():
            if BotClient.registered:
                _log.error(
                    "一个主程序只允许注册一个 BotClient 实例, 请检查你的引导程序"
                )
                exit(1)
            BotClient.registered = True

        check_duplicate_register()
        check_config()
        self.api = BotAPI()
        self._subscribe_group_message_types = []
        self._subscribe_private_message_types = []
        self._group_event_handlers = []
        self._private_event_handlers = []
        self._notice_event_handlers = []
        self._request_event_handlers = []
        self.plugins_path = plugins_path
        from ncatbot.plugin import EventBus, PluginLoader

        self.plugin_sys = PluginLoader(EventBus())

    async def handle_group_event(self, msg: dict):
        msg: GroupMessage = GroupMessage(msg)
        _log.debug(msg)
        for handler, types in self._group_event_handlers:
            if types is None or any(i["type"] in types for i in msg.message):
                await handler(msg)
        from ncatbot.plugin.event import Event, EventSource

        await self.plugin_sys.event_bus.publish_async(
            Event(
                OFFICIAL_GROUP_MESSAGE_EVENT,
                msg,
                EventSource(msg.user_id, msg.group_id),
            )
        )

    async def handle_private_event(self, msg: dict):
        msg: PrivateMessage = PrivateMessage(msg)
        _log.debug(msg)
        for handler, types in self._private_event_handlers:
            if types is None or any(i["type"] in types for i in msg.message):
                await handler(msg)
        from ncatbot.plugin.event import Event, EventSource

        await self.plugin_sys.event_bus.publish_async(
            Event(OFFICIAL_PRIVATE_MESSAGE_EVENT, msg, EventSource(msg.user_id, "root"))
        )

    async def handle_notice_event(self, msg: dict):
        _log.debug(msg)
        for handler in self._notice_event_handlers:
            await handler(msg)
        from ncatbot.plugin import Event

        await self.plugin_sys.event_bus.publish_async(Event(OFFICIAL_NOTICE_EVENT, msg))

    async def handle_request_event(self, msg: dict):
        _log.debug(msg)
        for handler in self._request_event_handlers:
            await handler(msg)
        from ncatbot.plugin import Event

        await self.plugin_sys.event_bus.publish_async(
            Event(OFFICIAL_REQUEST_EVENT, msg)
        )

    def group_event(self, types=None):
        self._subscribe_group_message_types = types

        def decorator(func):
            self._group_event_handlers.append((func, types))
            return func

        return decorator

    def private_event(self, types=None):
        self._subscribe_private_message_types = types

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
        def info_subscribe_message_types():
            subsribe_group_message_types = (
                "全部消息类型"
                if self._subscribe_group_message_types is None
                else self._subscribe_group_message_types
            )
            subsribe_private_message_types = (
                "全部消息类型"
                if self._subscribe_private_message_types is None
                else self._subscribe_private_message_types
            )
            _log.info(f"已订阅消息类型:[群聊]->{subsribe_group_message_types}")
            _log.info(f"已订阅消息类型:[私聊]->{subsribe_private_message_types}")

        async def time_schedule_heartbeat():
            while True:
                await asyncio.sleep(5)
                self.plugin_sys.time_task_scheduler.step()

        info_subscribe_message_types()
        websocket_server = Websocket(self)
        await self.plugin_sys.load_plugins(api=self.api)
        while True:
            try:
                asyncio.create_task(time_schedule_heartbeat())
                await websocket_server.on_connect()
            except Exception:
                _log.info("正在尝试重连服务器...")
                EXPIER = time.time() + 300
                interval = 1
                while not (await check_websocket(config.ws_uri)):
                    _log.info(f"正在尝试重连服务器...第 {interval} s")
                    time.sleep(interval)
                    interval *= 2
                    if time.time() > EXPIER:
                        _log.error("重连服务器超时, 退出程序")
                        exit(1)

            _log.info("重连服务器成功")

    def napcat_server_ok(self):
        return asyncio.run(check_websocket(config.ws_uri))

    def _run(self):
        try:
            asyncio.run(self.run_async())
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        finally:
            _log.info("插件卸载中...")
            self.plugin_sys.unload_all()
            _log.info("正常退出")
            exit(0)

    def run(self, debug=False, *args, **kwargs):
        """
        启动 Bot 客户端

        Args:
            debug: 是否开启调试模式, 默认为 False, 用户不应该修改此参数
            **kwargs: 保持弃用参数的兼容性
        Returns:
            None
        """
        if platform.system() == "Linux":
            napcat_dir = LINUX_NAPCAT_DIR
        elif platform.system() == "Windows":
            napcat_dir = WINDOWS_NAPCAT_DIR
        else:
            _log.error("暂不支持 Windows/Linux 之外的系统")
            exit(1)

        def check_permission():
            if check_linux_permissions("root") != "root":
                _log.error("请使用 root 权限运行 ncatbot")
                exit(1)

        def check_ncatbot_install():
            """检查 ncatbot 版本, 以及是否正确安装"""
            if not debug:
                # 检查版本和安装方式
                version_ok = check_version()
                if not version_ok:
                    exit(0)
            else:
                _log.info("调试模式, 跳过 ncatbot 安装检查")

        def ncatbot_quick_start():
            """在能够链接上 napcat 服务器时跳过检查直接启动"""
            if self.napcat_server_ok():
                _log.info(f"napcat 服务器 {config.ws_uri} 在线, 连接中...")
                self._run()
            elif not config.is_localhost():
                _log.error("napcat 服务器没有配置在本地, 无法连接服务器, 自动退出")
                _log.error(f'服务器参数: uri="{config.ws_uri}", token="{config.token}"')
                _log.info(
                    """可能的错误原因:
                          1. napcat webui 中服务器类型错误, 应该为 "WebSocket 服务器", 而非 "WebSocket 客户端"
                          2. napcat webui 中服务器配置了但没有启用, 请确保勾选了启用服务器"
                          3. napcat webui 中服务器 host 没有设置为监听全部地址, 应该将 host 改为 0.0.0.0
                          4. 检查以上配置后, 在 webui 中使用 error 信息中的的服务器参数, \"接口调试\"选择\"WebSocket\"尝试连接.
                          5. webui 中连接成功后再尝试启动 ncatbot
                          """
                )
                exit(1)
            elif kwargs.get("reload", False):
                _log.info("napcat 服务器未启动, 且开启了重加载模式, 运行失败")
                exit(1)
            _log.info("napcat 服务器离线")

        def check_install_napcat():
            """检查是否已经安装 napcat 客户端, 如果没有, 安装 napcat"""
            if not os.path.exists(napcat_dir):
                if not download_napcat("install"):
                    exit(1)
            else:
                # 检查 napcat 版本更新
                with open(
                    os.path.join(napcat_dir, "package.json"), "r", encoding="utf-8"
                ) as f:
                    version = json.load(f)["version"]
                    _log.info(f"当前 napcat 版本: {version}, 正在检查更新...")

                github_version = get_version()
                if version != github_version:
                    _log.info(
                        f"发现新版本: {github_version}, 是否要更新 napcat 客户端？"
                    )
                    if not download_napcat("update"):
                        _log.info(f"跳过 napcat {version} 更新")
                else:
                    _log.info("当前 napcat 已是最新版本")

        def config_napcat():
            """配置 napcat 服务器"""

            def config_onebot11():
                expected_data = {
                    "network": {
                        "websocketServers": [
                            {
                                "name": "WsServer",
                                "enable": True,
                                "host": str(urlparse(config.ws_uri).hostname),
                                "port": int(urlparse(config.ws_uri).port),
                                "messagePostFormat": "array",
                                "reportSelfMessage": False,
                                "token": (
                                    str(config.token)
                                    if config.token is not None
                                    else ""
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
                try:
                    with open(
                        os.path.join(
                            napcat_dir,
                            "config",
                            "onebot11_" + str(config.bt_uin) + ".json",
                        ),
                        "w",
                        encoding="utf-8",
                    ) as f:
                        json.dump(expected_data, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    _log.error("配置 onebot 失败: " + str(e))
                    if not check_permission():
                        _log.info("请使用 root 权限运行 ncatbot")
                        exit(1)

            def config_quick_login():
                ori = os.path.join(napcat_dir, "quickLoginExample.bat")
                dst = os.path.join(napcat_dir, f"{config.bt_uin}_quickLogin.bat")
                shutil.copy(ori, dst)

            def read_webui_config():
                # 确定 webui 路径
                webui_config_path = os.path.join(napcat_dir, "config", "webui.json")
                try:
                    with open(webui_config_path, "r") as f:
                        webui_config = json.load(f)
                        port = webui_config.get("port", 6099)
                        token = webui_config.get("token", "")
                        config.webui_token = token
                        config.webui_port = port
                    _log.info("Token: " + token + ", Webui port: " + str(port))

                except FileNotFoundError:
                    _log.error("无法读取 WebUI 配置, 将使用默认配置")

            config_onebot11()
            config_quick_login()
            read_webui_config()

        def connect_napcat():
            """启动并尝试连接 napcat 直到成功"""

            def info_windows():
                _log.info("1. 请允许终端修改计算机, 并在弹出的另一个终端扫码登录")
                _log.info(f"2. 确认 QQ 号 {config.bt_uin} 是否正确")
                _log.info(f"3. websocket url 是否正确: {config.ws_uri}")

            def info_linux():
                _log.info(f"1. websocket url 是否正确: {config.ws_uri}")

            def info(quit=False):
                _log.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
                if platform.system() == "Windows":
                    info_windows()
                else:
                    info_linux()
                if quit:
                    exit(1)

            start_napcat(config, platform.system())  # 启动 napcat
            if platform.system() == "Linux":
                LoginHandler().login()

            MAX_TIME_EXPIRE = time.time() + 60
            INFO_TIME_EXPIRE = time.time() + 20
            _log.info("正在连接 napcat websocket 服务器...")
            while not self.napcat_server_ok():
                time.sleep(0.5)
                if time.time() > MAX_TIME_EXPIRE:
                    info(True)
                if time.time() > INFO_TIME_EXPIRE:
                    info()
                    INFO_TIME_EXPIRE += 100

            _log.info("连接 napcat websocket 服务器成功!")

        check_ncatbot_install()  # 检查 ncatbot 安装方式
        ncatbot_quick_start()  # 能够成功连接 napcat 时快速启动
        check_install_napcat()  # 检查和安装 napcat
        config_napcat()  # 配置 napcat
        connect_napcat()  # 启动并连接 napcat
        self._run()
