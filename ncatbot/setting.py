
import os
import yaml

class SetConfig:
    def __init__(self):
        try:
            with open(os.path.join(os.getcwd(), "config.yaml"), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError("[setting] 配置文件不存在，请检查！")
        except yaml.YAMLError:
            raise ValueError("[setting] 配置文件格式错误，请检查！")
        except Exception as e:
            raise ValueError(f"[setting] 未知错误：{e}")
        try:
            self.ws_protocol = config['ws']['protocol']
            self.ws_ip = config['ws']['ip']
            self.ws_port = config['ws']['port']
            self.ws_token = config['ws']['token']
            self.http_protocol = config['http']['protocol']
            self.http_ip = config['http']['ip']
            self.http_port = config['http']['port']
            self.http_token = config['http']['token']
            self.ws_url = f"{self.ws_protocol}://{self.ws_ip}:{self.ws_port}"
            self.http_url = f"{self.http_protocol}://{self.http_ip}:{self.http_port}"
            self.base_url = config['ai']['base_url']
            self.api_key = config['ai']['api_key']
            self.ai_model = config['ai']['model']
            self.personality = config['ai']['personality']
            self.bot_uin = config['qq']['bot']
            self.user_uin = config['qq']['user']
            self.nap_cat = config['nap_cat']
        except KeyError as e:
            raise KeyError(f"[setting] 缺少配置项，请检查！详情:{e}")