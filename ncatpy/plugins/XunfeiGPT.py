# encoding=utf-8
'''仅供参考'''
from ..wsapi import WsApi
from .. import logging

import yaml
import os
import httpx

_log = logging.get_logger()

class XunfeiGPT:
    def __init__(self):
        try:
            with open(os.path.join(os.getcwd(), "config.yaml"), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            _log.error("[ncatpy] 配置文件不存在，请检查config.yaml是否在当前目录")
            exit(1)
        except yaml.YAMLError:
            _log.error("[ncatpy] 配置文件格式错误，请检查！")
            exit(1)
        except Exception as e:
            _log.error(f"[ncatpy] 配置文件读取错误，请检查config.yaml是否正确，错误信息：{e}")
            exit(1)

        self.url = config["plugin"]["xunfei"]["api_url"]
        self.key = config["plugin"]["xunfei"]["api_key"]
        self.model = config["plugin"]["xunfei"]["model"]
        self.personality = config["plugin"]["xunfei"]["personality"]
        self.wsapi = WsApi()

    async def ai_response(self, input, **kwargs):
        url = self.url
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.personality
                },
                {
                    "role": "user",
                    "content": input
                }
            ]
        }
        headers = {
            "Authorization": "Bearer " + self.key
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

        r = response_json['choices'][0]['message']['content']
        return await self.wsapi.send_msg(text=r, **kwargs)
