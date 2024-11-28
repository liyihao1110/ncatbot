from .api import BotAPI
from .settings import settings


class BaseMessage(BotAPI):
    def __init__(self, message):
        super().__init__(port_or_http=settings.port_or_http, max_ids=settings.max_ids)
        self.self_id = message.get("self_id", None)
        self.user_id = message.get("user_id", None)
        self.time = message.get("time", None)
        self.post_type = message.get("post_type", None)

class GroupMessage(BaseMessage):
    def __init__(self, message):
        super().__init__(message)
        self.group_id = message.get("group_id", None)
        self.message_type = message.get("message_type", None)
        self.sub_type = message.get("sub_type", None)
        self.raw_message = message.get("raw_message", None)
        self.font = message.get("font", None)
        self.sender = self._Sender(message.get("sender", {}))
        self.message_id = message.get("message_id", None)
        self.message_seq = message.get("message_seq", None)
        self.real_id = message.get("real_id", None)
        self.message = self._Message(message.get("message", []))
        self.message_format = message.get("message_format", None)

    def __str__(self):
        return str({key: value for key, value in self.__dict__.items() if not key.startswith("_")})

    class _Sender:
        def __init__(self, message):
            self.user_id = message.get("user_id", None)
            self.nickname = message.get("nickname", None)
            self.card = message.get("card", None)

        def __str__(self):
            return str(self.__dict__)

    class _Message:
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return str(self.message)

        def __get_messages_by_type(self, msg_type):
            return [msg['data'][list(msg['data'].keys())[0]] for msg in self.message if msg['type'] == msg_type]

        @property
        def text(self):
            return self.__get_messages_by_type('text')

        @property
        def face(self):
            return self.__get_messages_by_type('face')

        @property
        def image(self):
            return self.__get_messages_by_type('image')

        @property
        def record(self):
            return self.__get_messages_by_type('record')

        @property
        def video(self):
            return self.__get_messages_by_type('video')

        @property
        def at(self):
            return self.__get_messages_by_type('at')

        @property
        def rps(self):
            return self.__get_messages_by_type('rps')

        @property
        def dice(self):
            return self.__get_messages_by_type('dice')

        @property
        def poke(self):
            return self.__get_messages_by_type('poke')

        @property
        def share(self):
            return self.__get_messages_by_type('share')

        @property
        def contact(self):
            return self.__get_messages_by_type('contact')

        @property
        def location(self):
            return self.__get_messages_by_type('location')

        @property
        def music(self):
            return self.__get_messages_by_type('music')

        @property
        def reply(self):
            return self.__get_messages_by_type('reply')

        @property
        def forward(self):
            return self.__get_messages_by_type('forward')

        @property
        def node(self):
            return self.__get_messages_by_type('node')

        @property
        def json(self):
            return self.__get_messages_by_type('json')

        @property
        def mface(self):
            return self.__get_messages_by_type('mface')

        @property
        def file(self):
            return self.__get_messages_by_type('file')

        @property
        def lightapp(self):
            return self.__get_messages_by_type('lightapp')

    async def reply(self, reply=False):
        if reply:
            self.add_reply(self.message_id)
        return await self.send_group_msg(self.group_id, clear_message=True)


class PrivateMessage(BaseMessage):
    def __init__(self, message):
        super().__init__(message)
        self.message_id = message.get("message_id", None)
        self.message_seq = message.get("message_seq", None)
        self.real_id = message.get("real_id", None)
        self.message_type = message.get("message_type", None)
        self.sender = self._Sender(message.get("sender", {}))
        self.raw_message = message.get("raw_message", None)
        self.font = message.get("font", None)
        self.sub_type = message.get("sub_type", None)
        self.message = self._Message(message.get("message", []))
        self.message_format = message.get("message_format", None)
        self.target_id = message.get("target_id", None)

    def __str__(self):
        return str({key: value for key, value in self.__dict__.items() if not key.startswith("_")})

    class _Sender:
        def __init__(self, message):
            self.user_id = message.get("user_id", None)
            self.nickname = message.get("nickname", None)
            self.card = message.get("card", None)

        def __str__(self):
            return str(self.__dict__)

    class _Message:
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return str(self.message)


        def __get_messages_by_type(self, msg_type):
            return [msg['data'][list(msg['data'].keys())[0]] for msg in self.message if msg['type'] == msg_type]

        @property
        def text(self):
            return self.__get_messages_by_type('text')

        @property
        def face(self):
            return self.__get_messages_by_type('face')

        @property
        def image(self):
            return self.__get_messages_by_type('image')

        @property
        def record(self):
            return self.__get_messages_by_type('record')

        @property
        def video(self):
            return self.__get_messages_by_type('video')

        @property
        def at(self):
            return self.__get_messages_by_type('at')

        @property
        def rps(self):
            return self.__get_messages_by_type('rps')

        @property
        def dice(self):
            return self.__get_messages_by_type('dice')

        @property
        def poke(self):
            return self.__get_messages_by_type('poke')

        @property
        def share(self):
            return self.__get_messages_by_type('share')

        @property
        def contact(self):
            return self.__get_messages_by_type('contact')

        @property
        def location(self):
            return self.__get_messages_by_type('location')

        @property
        def music(self):
            return self.__get_messages_by_type('music')

        @property
        def reply(self):
            return self.__get_messages_by_type('reply')

        @property
        def forward(self):
            return self.__get_messages_by_type('forward')

        @property
        def node(self):
            return self.__get_messages_by_type('node')

        @property
        def json(self):
            return self.__get_messages_by_type('json')

        @property
        def mface(self):
            return self.__get_messages_by_type('mface')

        @property
        def file(self):
            return self.__get_messages_by_type('file')

        @property
        def lightapp(self):
            return self.__get_messages_by_type('lightapp')

    async def reply(self, reply=False):
        if reply:
            self.add_reply(self.message_id)
        return await self.send_private_msg(self.user_id, clear_message=True)

class NoticeMessage(BaseMessage):
    def __init__(self, message):
        super().__init__(message)
        self.notice_type = message.get("notice_type", None)

    def __str__(self):
        return str({key: value for key, value in self.__dict__.items() if not key.startswith("_")})

