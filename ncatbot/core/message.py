import asyncio

from ncatbot.core.api import BotAPI


class BaseMessage:
    api_initialized = False
    api = None
    __slots__ = (
        "self_id",
        "time",
        "post_type",
        "raw_message",
    )

    def __init__(self, message):
        if not BaseMessage.api_initialized:
            BaseMessage.api = BotAPI()
            BaseMessage.api_initialized = True
        self.self_id = message.get("self_id", None)
        self.time = message.get("time", None)
        self.post_type = message.get("post_type", None)
        self.raw_message = message.get("raw_message", None)

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    def reply_text_sync(self, text: str = "", **kwargs):
        """同步回复消息, 应该被子类重写"""
        pass

    class _Sender:
        def __init__(self, message):
            self.user_id = message.get("user_id", None)
            self.nickname = message.get("nickname", None)
            self.card = message.get("card", None)

        def __repr__(self):
            return str(self.__dict__)


class GroupMessage(BaseMessage):
    __slots__ = (
        "group_id",
        "user_id",
        "message_type",
        "sub_type",
        "font",
        "sender",
        "message_id",
        "message_seq",
        "real_id",
        "message",
        "message_format",
    )

    def __init__(self, message):
        super().__init__(message)
        self.user_id = message.get("user_id", None)
        self.group_id = message.get("group_id", None)
        self.message_type = message.get("message_type", None)
        self.sub_type = message.get("sub_type", None)
        self.raw_message = message.get("raw_message", None)
        self.font = message.get("font", None)
        self.sender = self._Sender(message.get("sender", {}))
        self.message_id = message.get("message_id", None)
        self.message_seq = message.get("message_seq", None)
        self.real_id = message.get("real_id", None)
        self.message = message.get("message", [])
        self.message_format = message.get("message_format", None)

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    async def reply(self, text: str = "", is_file: bool = False, **kwargs):
        if len(text):
            kwargs["text"] = text
        if is_file:
            return await self.api.post_group_file(self.group_id, **kwargs)
        else:
            return await self.api.post_group_msg(
                self.group_id, reply=self.message_id, **kwargs
            )

    def reply_text_sync(self, text: str = "", **kwargs):
        return asyncio.create_task(self.reply(text=text, **kwargs))


class PrivateMessage(BaseMessage):
    __slots__ = (
        "message_id",
        "user_id",
        "message_seq",
        "real_id",
        "sender",
        "raw_message",
        "font",
        "sub_type",
        "message",
        "message_format",
        "target_id",
        "message_type",
    )

    def __init__(self, message):
        super().__init__(message)

        self.user_id = message.get("user_id", None)
        self.message_id = message.get("message_id", None)
        self.message_seq = message.get("message_seq", None)
        self.real_id = message.get("real_id", None)
        self.message_type = message.get("message_type", None)
        self.sender = self._Sender(message.get("sender", {}))
        self.raw_message = message.get("raw_message", None)
        self.font = message.get("font", None)
        self.sub_type = message.get("sub_type", None)
        self.message = message.get("message", [])
        self.message_format = message.get("message_format", None)
        self.target_id = message.get("target_id", None)

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    async def reply(self, text: str = "", is_file: bool = False, **kwargs):
        if len(text):
            kwargs["text"] = text
        if is_file:
            return await self.api.post_private_file(self.user_id, **kwargs)
        else:
            return await self.api.post_private_msg(self.user_id, **kwargs)

    def reply_text_sync(self, text: str = "", **kwargs):
        return asyncio.create_task(self.reply(text=text, **kwargs))
