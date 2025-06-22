from ncatbot.core.api import BotAPI


class Request:
    """请求事件"""

    api_initialized = False
    api = None
    __slots__ = (
        "time",
        "self_id",
        "post_type",
        "request_type",
        "sub_type",
        "user_id",
        "group_id",
        "comment",
        "flag",
    )

    def __init__(self, msg: dict):
        if not self.api_initialized:
            Request.api_initialized = True
            Request.api = BotAPI()

        self.time = msg["time"]
        self.self_id = msg["self_id"]
        self.post_type = msg["post_type"]
        self.request_type = msg["request_type"]
        self.sub_type = msg.get("sub_type", None)
        self.user_id = msg["user_id"]
        self.group_id = msg.get("group_id", None)
        self.comment = msg["comment"]
        self.flag = msg["flag"]

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    def is_friend_add(self):
        return self.request_type == "friend"

    def is_group_add(self):
        return self.request_type == "group"

    async def accept_async(self, comment: str = ""):
        await self.reply(True, comment)

    def accept_sync(self, comment: str = ""):
        self.reply_sync(True, comment)

    async def reply(self, accept: bool = True, comment: str = ""):
        if self.is_friend_add():
            await self.api.set_friend_add_request(self.flag, accept, comment)
        else:
            await self.api.set_group_add_request(self.flag, accept, comment)

    def reply_sync(self, accept: bool = True, comment: str = ""):
        if self.is_friend_add():
            self.api.set_friend_add_request_sync(self.flag, accept, comment)
        else:
            self.api.set_group_add_request_sync(self.flag, accept, comment)
