
from .api import BotAPI
from .setting import SetConfig

from openai import OpenAI

_set = SetConfig()

class Bot:
    def __init__(self):
        self.__api = BotAPI(use_ws=True)
        self.__url = _set.base_url
        self.__key = _set.api_key
        self.__model = _set.ai_model
        self.__personality = _set.personality
        self.__messages = [{"role": "system", "content": self.__personality}]

    async def ai_response(self, message, input, group_id=None, user_id=None):
        client = OpenAI(
            api_key=self.__key,
            base_url=self.__url,
        )
        completion = client.chat.completions.create(
            model=self.__model,
            messages=[
                {
                    "role": "system",
                    "content": self.__personality
                },
                {
                    "role": "user",
                    "content": input
                }
            ]
        )
        if group_id:
            await self.__api.post_group_msg(group_id, text=message.sender.nickname+','+completion.choices[0].message.content)
        else:
            await self.__api.post_private_msg(user_id, text=message.sender.nickname+','+completion.choices[0].message.content)

    async def ai_response_history(self, message, input, history_num = 5, group_id=None, user_id=None):
        if len(self.__messages)/2 > history_num:
            self.__messages.pop(1)
        elif input == " .clear" and group_id:
            self.__messages = [{"role": "system", "content": self.__personality}]
            await self.__api.post_group_msg(group_id, "已清空历史记录")
            return
        elif input == " .clear" and user_id:
            self.__messages = [{"role": "system", "content": self.__personality}]
            await self.__api.post_private_msg(user_id, "已清空历史记录")
            return
        self.__messages.append({"role": "user", "content": input})
        client = OpenAI(
            api_key=self.__key,
            base_url=self.__url,
        )
        completion = client.chat.completions.create(
            model=self.__model,
            messages=self.__messages
        )
        if group_id:
            await self.__api.post_group_msg(group_id, text=message.sender.nickname+','+completion.choices[0].message.content)
            self.__messages.append({"role": "assistant", "content": completion.choices[0].message.content})
        elif user_id:
            await self.__api.post_private_msg(user_id, text=message.sender.nickname+','+completion.choices[0].message.content)
            self.__messages.append({"role": "assistant", "content": completion.choices[0].message.content})


