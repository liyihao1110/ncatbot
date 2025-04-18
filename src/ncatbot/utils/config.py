# 配置文件

import time
import urllib
import urllib.parse

import yaml

from ncatbot.utils.logger import get_log

LOG = get_log()


class SetConfig:

    default_root = "123456"
    default_bt_uin = "123456"
    default_ws_uri = "ws://localhost:3001"
    default_webui_uri = "http://localhost:6099"
    default_webui_token = "napcat"

    def __init__(self):
        # 内部状态
        # 可设置状态
        self.root = self.default_root  # root 账号
        self.bt_uin = self.default_bt_uin  # bot 账号
        self.ws_uri = self.default_ws_uri  # ws 地址
        self.webui_uri = self.default_webui_uri  # webui 地址
        self.webui_token = self.default_webui_token  # webui 令牌
        self.ws_token = ""  # ws_uri 令牌
        self.ws_listen_ip = "localhost"  # ws 监听 ip, 默认只监听本机
        self.remote_mode = False  # 是否远程模式, 即 NapCat 服务不在本机运行

        """
        如果纯远程模式, 则 NcatBot 不对 NapCat 的行为做任何管理.
        只使用 ws_uri 和 webui_uri 和 NapCat 进行交互, 不会配置启动 NapCat
        """

        # 更新检查
        self.check_napcat_update = False  # 是否检查 napcat 更新
        self.check_ncatbot_update = True  # 是否检查 ncatbot 更新

        # 开发者调试
        self.debug = False  # 是否开启调试模式
        self.skip_ncatbot_install_check = False  # 是否跳过 napcat 安装检查
        self.skip_plugin_load = False  # 是否跳过插件加载

        # NapCat 行为
        self.stop_napcat = False  # NcatBot 下线时是否停止 NapCat
        self.enable_webui_interaction = True  # 是否允许 NcatBot 与 NapCat webui 交互

        """
        如果 enable_webui_interaction 为 False, 则 NcatBot 不会与 NapCat webui 交互
        账号检查, 引导登录等行为均不会发生, 只使用 ws_uri 与 NapCat 交互
        """

        # 自动获取状态
        self.ws_host = None  # ws host
        self.webui_host = None  # webui host
        self.ws_port = None  # ws 端口
        self.webui_port = None  # webui 端口

        # 暂不支持的状态

    def __str__(self):
        return f"[BOTQQ]: {self.bt_uin} | [WSURI]: {self.ws_uri} | [WS_TOKEN]: {self.ws_token} | [ROOT]: {self.root} | [WEBUI]: {self.webui_uri}"

    def _is_localhost(self):
        return (
            self.ws_uri.find("localhost") != -1 or self.ws_uri.find("127.0.0.1") != -1
        )

    def _standardize_ws_uri(self):
        if not (self.ws_uri.startswith("ws://") or self.ws_uri.startswith("wss://")):
            self.ws_uri = "ws://" + self.ws_uri
        self.ws_host = urllib.parse.urlparse(self.ws_uri).hostname
        self.ws_port = urllib.parse.urlparse(self.ws_uri).port

    def _standardize_webui_uri(self):
        if not (
            self.webui_uri.startswith("http://")
            or self.webui_uri.startswith("https://")
        ):
            self.webui_uri = "http://" + self.webui_uri
        self.webui_host = urllib.parse.urlparse(self.webui_uri).hostname
        self.webui_port = urllib.parse.urlparse(self.webui_uri).port

    def load_config(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f)
        except FileNotFoundError:
            LOG.warning("未找到配置文件")
            raise ValueError("[setting] 配置文件不存在，请检查！")
        except yaml.YAMLError:
            raise ValueError("[setting] 配置文件格式错误，请检查！")
        except Exception as e:
            raise ValueError(f"[setting] 未知错误：{e}")
        try:
            self.__dict__.update(conf)
        except KeyError as e:
            raise KeyError(f"[setting] 缺少配置项，请检查！详情:{e}")

    def set_root(self, root: str):
        self.root = root

    def set_ws_uri(self, ws_uri: str):
        self.ws_uri = ws_uri
        self._standardize_ws_uri()

    def set_bot_uin(self, uin: str):
        self.bt_uin = uin

    def set_token(self, token: str):
        # 即将弃用
        self.ws_token = token

    def set_ws_token(self, token: str):
        self.ws_token = token

    def set_webui_token(self, token: str):
        self.webui_token = token

    def set_webui_uri(self, webui_uri: str):
        self.webui_uri = webui_uri
        self._standardize_webui_uri()

    def set_other_config(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def validate_config(self):
        # 检查 bot_uin 和 root
        if self.bt_uin is self.default_bt_uin:
            LOG.warning("配置项中没有设置 QQ 号")
            self.set_bot_uin(input("请输入你的 QQ 号:"))
        if self.root is self.default_root:
            LOG.warning("建议设置好 root 账号保证权限功能能够正常使用")
        LOG.info(self)

        # 检验 ws_uri
        if not self._is_localhost():
            LOG.info(
                "请注意, 当前配置的 NapCat 服务不是本地地址, 请确保远端 NapCat 服务正确配置."
            )
            time.sleep(1)
        self._standardize_ws_uri()

        # 检验 ws_listen_ip
        if self.ws_listen_ip != "0.0.0.0":
            if self.ws_listen_ip != self.ws_host:
                LOG.warning("当前的 ws 监听地址与 ws 地址不一致, 可能无法正确连接")

        # 检验 webui_uri
        self._standardize_webui_uri()


config = SetConfig()
