import os

import yaml


class SetConfig:
    def __init__(self, config=None):
        pass

    def _load_config(self, path):
        def load_config(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            except FileNotFoundError:
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
                self.hp_uri = config["hp_uri"]
                location = (
                    self.hp_uri.replace("http://", "")
                    if self.hp_uri.startswith("http://")
                    else self.hp_uri.replace("https://", "")
                )
                parts = location.split(":")
                self.http_ip = parts[0]
                self.http_port = parts[1]
                self.token = config["token"]
                self.np_uri = config["np_uri"]
                self.bot_uin = config["bt_uin"]
            except KeyError as e:
                raise KeyError(f"[setting] 缺少配置项，请检查！详情:{e}")

        default_config = os.path.join(os.getcwd(), "config.yaml")
        if path is not None:
            try:
                load_config(path)
            except Exception:
                load_config(default_config)
        else:
            load_config(default_config)

    def update(self, config):
        self._load_config(config)


config = SetConfig()
