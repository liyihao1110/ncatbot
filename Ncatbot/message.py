from .api import BotAPI
from .settings import settings

class TextMessage:
    def __init__(self, data):
        self.text = data.get('text', '')

    def __str__(self):
        return str(self.__dict__)

class FaceMessage:
    def __init__(self, data):
        self.id = data.get('id', None)

    def __str__(self):
        return str(self.__dict__)

class ImageMessage:
    def __init__(self, data):
        self.name = data.get('name', None)
        self.summary = data.get('summary', None)
        self.file = data.get('file', None)
        self.sub_type = data.get('sub_type', None)
        self.file_id = data.get('file_id', None)
        self.url = data.get('url', None)
        self.path = data.get('path', None)
        self.file_size = data.get('file_size', None)
        self.file_unique = data.get('file_unique', None)

    def __str__(self):
        return str(self.__dict__)

class RecordMessage:
    def __init__(self, data):
        self.file = data.get('file', None)
        self.name = data.get('name', None)
        self.url = data.get('url', None)
        self.path = data.get('path', None)
        self.file_id = data.get('file_id', None)
        self.file_size = data.get('file_size', None)
        self.file_unique = data.get('file_unique', None)

    def __str__(self):
        return str(self.__dict__)

class VideoMessage:
    def __init__(self, data):
        self.name = data.get('name', None)
        self.file = data.get('file', None)
        self.thumb = data.get('thumb', None)
        self.url = data.get('url', None)
        self.path = data.get('path', None)
        self.file_id = data.get('file_id', None)
        self.file_size = data.get('file_size', None)
        self.file_unique = data.get('file_unique', None)

    def __str__(self):
        return str(self.__dict__)

class AtMessage:
    def __init__(self, data):
        self.qq = data.get('qq', None)

    def __str__(self):
        return str(self.__dict__)

class RpsMessage:
    def __init__(self, data):
        self.result = data.get('result', None)

    def __str__(self):
        return str(self.__dict__)

class DiceMessage:
    def __init__(self, data):
        self.result = data.get('result', None)

    def __str__(self):
        return str(self.__dict__)

class ContactMessage:
    def __init__(self, data):
        self.type = data.get('type', None)
        self.id = data.get('id', None)

    def __str__(self):
        return str(self.__dict__)

class MusicMessage:
    def __init__(self, data):
        self.type = data.get('type', None)
        self.id = data.get('id', None)
        self.url = data.get('url', None)
        self.audio = data.get('audio', None)
        self.title = data.get('title', None)
        self.image = data.get('image', None)
        self.singer = data.get('singer', None)

    def __str__(self):
        return str(self.__dict__)

class ReplyMessage:
    def __init__(self, data):
        self.id = data.get('id', None)

    def __str__(self):
        return str(self.__dict__)

class ForwardMessage:
    def __init__(self, data):
        self.id = data.get('id', None)
        self.content = data.get('content', [])

    def __str__(self):
        return str(self.__dict__)

class NodeMessage:
    def __init__(self, data):
        self.user_id = data.get('user_id', None)
        self.nickname = data.get('nickname', None)
        self.id = data.get('id', None)
        self.content = data.get('content', [])

    def __str__(self):
        return str(self.__dict__)

class JsonMessage:
    def __init__(self, data):
        self.data = data.get('data', None)

    def __str__(self):
        return str(self.__dict__)

class MfaceMessage:
    def __init__(self, data):
        self.emoji_id = data.get('emoji_id', None)
        self.emoji_package_id = data.get('emoji_package_id', None)
        self.key = data.get('key', None)
        self.summary = data.get('summary', None)

    def __str__(self):
        return str(self.__dict__)

class FileMessage:
    def __init__(self, data):
        self.name = data.get('name', None)
        self.file = data.get('file', None)
        self.path = data.get('path', None)
        self.url = data.get('url', None)
        self.file_id = data.get('file_id', None)
        self.file_size = data.get('file_size', None)
        self.file_unique = data.get('file_unique', None)


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
            return str(self.__dict__)

        def __get_messages_by_type(self, msg_type):
            for msg in self.message:
                if msg['type'] == msg_type:
                    return msg.get('data',{})

        @property
        def text(self):
            text_data = self.__get_messages_by_type('text')
            if text_data:
                return TextMessage(text_data)
            return None



        @property
        def face(self):
            face_data = self.__get_messages_by_type('face')
            if face_data:
                return FaceMessage(face_data)
            return None

        @property
        def image(self):
            image_data = self.__get_messages_by_type('image')
            if image_data:
                return ImageMessage(image_data)
            return None

        @property
        def record(self):
            record_data = self.__get_messages_by_type('record')
            if record_data:
                return RecordMessage(record_data)
            return None

        @property
        def video(self):
            video_data = self.__get_messages_by_type('video')
            if video_data:
                return VideoMessage(video_data)
            return None

        @property
        def rps(self):
            rps_data = self.__get_messages_by_type('rps')
            if rps_data:
                return RpsMessage(rps_data)
            return None

        @property
        def dice(self):
            dice_data = self.__get_messages_by_type('dice')
            if dice_data:
                return DiceMessage(dice_data)
            return None

        @property
        def at(self):
            at_data = self.__get_messages_by_type('at')
            if at_data:
                return AtMessage(at_data)
            return None


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
            music_data = self.__get_messages_by_type('music')
            if music_data:
                return MusicMessage(music_data)
            return None

        @property
        def reply(self):
            reply_data = self.__get_messages_by_type('reply')
            if reply_data:
                return ReplyMessage(reply_data)
            return None

        @property
        def forward(self):
            forward_data = self.__get_messages_by_type('forward')
            if forward_data:
                return ForwardMessage(forward_data)
            return None

        @property
        def node(self):
            node_data = self.__get_messages_by_type('node')
            if node_data:
                return NodeMessage(node_data)
            return None

        @property
        def json(self):
            json_data = self.__get_messages_by_type('json')
            if json_data:
                return JsonMessage(json_data)
            return None

        @property
        def mface(self):
            mface_data = self.__get_messages_by_type('mface')
            if mface_data:
                return MfaceMessage(mface_data)
            return None

        @property
        def file(self):
            file_data = self.__get_messages_by_type('file')
            if file_data:
                return FileMessage(file_data)
            return None

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
            return str(self.__dict__)


        def __get_messages_by_type(self, msg_type):
            for msg in self.message:
                if msg['type'] == msg_type:
                    return msg.get('data',{})

        @property
        def text(self):
            text_data = self.__get_messages_by_type('text')
            if text_data:
                return TextMessage(text_data)
            return None



        @property
        def face(self):
            face_data = self.__get_messages_by_type('face')
            if face_data:
                return FaceMessage(face_data)
            return None

        @property
        def image(self):
            image_data = self.__get_messages_by_type('image')
            if image_data:
                return ImageMessage(image_data)
            return None

        @property
        def record(self):
            record_data = self.__get_messages_by_type('record')
            if record_data:
                return RecordMessage(record_data)
            return None

        @property
        def video(self):
            video_data = self.__get_messages_by_type('video')
            if video_data:
                return VideoMessage(video_data)
            return None

        @property
        def rps(self):
            rps_data = self.__get_messages_by_type('rps')
            if rps_data:
                return RpsMessage(rps_data)
            return None

        @property
        def dice(self):
            dice_data = self.__get_messages_by_type('dice')
            if dice_data:
                return DiceMessage(dice_data)
            return None

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
            music_data = self.__get_messages_by_type('music')
            if music_data:
                return MusicMessage(music_data)
            return None

        @property
        def reply(self):
            reply_data = self.__get_messages_by_type('reply')
            if reply_data:
                return ReplyMessage(reply_data)
            return None

        @property
        def forward(self):
            forward_data = self.__get_messages_by_type('forward')
            if forward_data:
                return ForwardMessage(forward_data)
            return None

        @property
        def node(self):
            node_data = self.__get_messages_by_type('node')
            if node_data:
                return NodeMessage(node_data)
            return None

        @property
        def json(self):
            json_data = self.__get_messages_by_type('json')
            if json_data:
                return JsonMessage(json_data)
            return None

        @property
        def mface(self):
            mface_data = self.__get_messages_by_type('mface')
            if mface_data:
                return MfaceMessage(mface_data)
            return None

        @property
        def file(self):
            file_data = self.__get_messages_by_type('file')
            if file_data:
                return FileMessage(file_data)
            return None

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

