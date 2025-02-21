import yaml

from ncatbot.utils.logger import get_log

_log = get_log()


class SetConfig:
    def __init__(self):
        self._updated = False
        self.bt_uin = "123456"
        self.ws_uri = "localhost:3001"
        self.token = ""

    def __str__(self):
        return (
            f"\n--Configuration--\n"
            f"BOT QQ 号: {self.bt_uin}\n"
            f"WebSocket URI: {self.ws_uri}\n"
            f"Token: {self.token}"
        )

    def load_config(self, path):
        self._updated = True
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            _log.warning("未找到配置文件")
            raise ValueError("[setting] 配置文件不存在，请检查！")
        except yaml.YAMLError:
            raise ValueError("[setting] 配置文件格式错误，请检查！")
        except Exception as e:
            raise ValueError(f"[setting] 未知错误：{e}")
        try:
            self.ws_uri = config["ws_uri"]
            location = (
                self.ws_uri.replace("ws://", "")
                if self.ws_uri.startswith("ws://")
                else self.ws_uri.replace("wss://", "")
            )
            parts = location.split(":")
            self.ws_ip = parts[0]
            self.ws_port = parts[1]
            self.token = config["token"]
            self.bt_uin = config["bt_uin"]
            self.standerize_uri()
        except KeyError as e:
            raise KeyError(f"[setting] 缺少配置项，请检查！详情:{e}")

    def standerize_uri(self):
        if not (self.ws_uri.startswith("ws://") or self.ws_uri.startswith("wss://")):
            self.ws_uri = "ws://" + self.ws_uri

    def set_ws_uri(self, ws_uri: str):
        self._updated = True
        self.ws_uri = ws_uri
        self.standerize_uri()

    def set_bot_uin(self, uin: str):
        self._updated = True
        self.bt_uin = uin

    def set_token(self, token: str):
        self._updated = True
        self.token = token


config = SetConfig()
