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
            ws_protocol = config['ws']['Protocol']
            ws_ip = config['ws']['ip']
            ws_port = config['ws']['port']
            http_protocol = config['http']['Protocol']
            http_ip = config['http']['ip']
            http_port = config['http']['port']
            self.ws_url = f"{ws_protocol}://{ws_ip}:{ws_port}"
            self.http_url = f"{http_protocol}://{http_ip}:{http_port}"
            self.ws_protocol = ws_protocol
            self.ws_ip = ws_ip
            self.ws_port = ws_port
            self.http_protocol = http_protocol
            self.http_ip = http_ip
            self.http_port = http_port
        except KeyError:
            _log.error('[nactpy] 主要配置文件缺少关键设置，请检查！')
