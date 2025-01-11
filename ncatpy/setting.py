# encoding: utf-8

"""配置类"""

import os
import yaml

from . import logging

_log = logging.get_logger()

class SetConfig:
    def __init__(self):
        try:
            with open(os.path.join(os.getcwd(), "config.yaml"), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            _log.error("[ncatpy] 配置文件不存在，请检查！")
            exit(1)
        except yaml.YAMLError:
            _log.error("[ncatpy] 配置文件格式错误，请检查！")
            exit(1)
        except Exception as e:
            _log.error(f"[ncatpy] 未知错误：{e}")
            exit(1)
        try:
            self.ws_protocol = config['ws']['Protocol']
            self.ws_ip = config['ws']['ip']
            self.ws_port = config['ws']['port']
            self.http_protocol = config['http']['Protocol']
            self.http_ip = config['http']['ip']
            self.http_port = config['http']['port']
            self.sync = config['http']['sync']
            self.ws_url = f"{self.ws_protocol}://{self.ws_ip}:{self.ws_port}"
            self.http_url = f"{self.http_protocol}://{self.http_ip}:{self.http_port}"
        except KeyError as e:
            _log.error(f"[ncatpy] 缺少配置项，请检查！详情:{e}")
            exit(1)

