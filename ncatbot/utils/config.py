import datetime
import time

import yaml

from ncatbot.utils.logger import get_log

_log = get_log()


class SetConfig:

    default_root = "123456"
    default_bt_uin = "123456"

    def __init__(self):
        self.ws_ip = "localhost"
        self._updated = False  # 内部状态
        self.bt_uin = "123456"  # bot 账号
        self.root = "123456"  # root 账号
        self.ws_uri = "ws://localhost:3001"
        self.stop_napcat = False  # 结束时是否停止 napcat
        self.token = ""  # napcat 令牌
        self.webui_token = ""  # webui 令牌, 自动读取, 无需设置
        self.webui_port = ""  # webui 端口, 自动读取, 无需设置

    def __str__(self):
        return f"[BOTQQ]: {self.bt_uin} | [WSURI]: {self.ws_uri} | [TOKEN]: {self.token}"

    def is_localhost(self):
        return (
            self.ws_uri.find("localhost") != -1 or self.ws_uri.find("127.0.0.1") != -1
        )

    def load_config(self, path):
        self._updated = True
        try:
            with open(path, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f)
        except FileNotFoundError:
            _log.warning("未找到配置文件")
            raise ValueError("[setting] 配置文件不存在，请检查！")
        except yaml.YAMLError:
            raise ValueError("[setting] 配置文件格式错误，请检查！")
        except Exception as e:
            raise ValueError(f"[setting] 未知错误：{e}")
        try:
            self.ws_uri = conf["ws_uri"]
            location = (
                self.ws_uri.replace("ws://", "")
                if self.ws_uri.startswith("ws://")
                else self.ws_uri.replace("wss://", "")
            )
            parts = location.split(":")
            self.ws_ip = parts[0]
            self.ws_port = parts[1]
            self.token = conf["token"]
            self.bt_uin = conf["bt_uin"]
            self.standardize_uri()
        except KeyError as e:
            raise KeyError(f"[setting] 缺少配置项，请检查！详情:{e}")

    def standardize_uri(self):
        if not (self.ws_uri.startswith("ws://") or self.ws_uri.startswith("wss://")):
            self.ws_uri = "ws://" + self.ws_uri

    def set_root(self, root: str):
        self.root = root

    def set_ws_uri(self, ws_uri: str):
        self._updated = True
        self.ws_uri = ws_uri
        self.standardize_uri()
        parts = self.ws_uri.split(":")
        self.ws_ip = parts[0]
        self.ws_port = parts[-1]
        if not self.is_localhost():
            _log.info(
                f'请注意, 当前配置的 ws_uri="{ws_uri}" 不是本地地址, 请确保远端 napcat 服务正确配置.'
            )
            time.sleep(1)

    def set_bot_uin(self, uin: str):
        self._updated = True
        self.bt_uin = uin

    def set_token(self, token: str):
        self._updated = True
        self.token = token


config = SetConfig()
