# encoding=utf-8

from ..wsapi import WsApi
from .. import logging

import yaml
import os
import httpx
import json

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
        self.messages = [{"role": "system","content": self.personality}]
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

    async def echo(self, input, **kwargs):
        return await self.wsapi.send_msg(text=f"ECHO {input}", **kwargs)

    async def ai_response_history(self, input, history_num = 5, info = False, **kwargs):
        if len(self.messages)/2 > history_num:
            self.messages.pop(1)
        elif input == "!clear":
            self.messages = [{"role": "system","content": self.personality}]
            return await self.wsapi.send_msg(text="已清空对话记录", **kwargs)

        self.messages.append({"role": "user", "content": input})
        data = {
            "model": self.model,
            "messages": self.messages
        }
        headers = {
            "Authorization": "Bearer " + self.key
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

        r = response_json['choices'][0]['message']['content']
        prompt_tokens = response_json['usage']['prompt_tokens']
        completion_tokens = response_json['usage']['completion_tokens']
        total_tokens = response_json['usage']['total_tokens']
        self.messages.append({"role": "assistant", "content": r})
        if info:
            r = f"{r}\n\n当前对话次数: {int((len(self.messages)-1)/2)}/{history_num}\nprompt_tokens: {prompt_tokens}\ncompletion_tokens: {completion_tokens}\ntotal_tokens: {total_tokens}"
            return await self.wsapi.send_msg(text=r, **kwargs)
        return await self.wsapi.send_msg(text=r, **kwargs)
