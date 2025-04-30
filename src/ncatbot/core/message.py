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

    def reply(self, is_file: bool = False, **kwargs):
        raise NotImplementedError

    async def reply_text(self, text: str = "", **kwargs):
        """回复, 文字信息特化"""
        return await self.reply(text=text, **kwargs)

    def reply_text_sync(self, text: str = "", **kwargs):
        """同步回复, 文字信息特化"""
        # 检查是否有正在运行的事件循环
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 如果没有运行的事件循环，创建一个新的事件循环并运行协程
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.reply(text=text, **kwargs))
        else:
            # 如果有运行的事件循环，直接创建任务
            asyncio.create_task(self.reply(text=text, **kwargs))

    def reply_sync(self, is_file: bool = False, **kwargs):
        """同步回复"""
        if not isinstance(is_file, bool):
            kwargs["rtf"] = is_file
            is_file = False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.reply(is_file=is_file, **kwargs))
        else:
            asyncio.create_task(self.reply(is_file=is_file, **kwargs))

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
        "raw_message",
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
