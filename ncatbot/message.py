from typing import Union
from .api import BotAPI

class BaseMessage(BotAPI):
    __slots__ = ("self_id", "time", "post_type")

    def __init__(self, message):
        super().__init__(message)
        self.self_id = message.get("self_id", None)
        self.time = message.get("time", None)
        self.post_type = message.get("post_type", None)

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    class _Sender:
        def __init__(self, message):
            self.user_id = message.get("user_id", None)
            self.nickname = message.get("nickname", None)
            self.card = message.get("card", None)

        def __repr__(self):
            return str(self.__dict__)


def replace_none(fun):
    """
    去除 json 参数中为 None 的键值对（装饰器自动操作版）
    """
    def decorator(*args, **kwargs):
        data = kwargs.get('json', {})
        if isinstance(data, dict):
            # 使用字典推导式过滤掉值为 None 的键值对
            filtered_data = {key: value for key, value in data.items() if value is not None}
            if filtered_data:
                kwargs['json'] = filtered_data
            else:
                del kwargs['json']
        return fun(*args, **kwargs)
    return decorator


class MessageBehavior:
    def __init__(self):
        raise RuntimeError("不要使用此初始化行为")
    # def __init__(self,message:list):
    #     self.__messages = message
    #     self.message_cache = []

    @property
    def text(self) -> list:
        text_data = self.__get_messages_by_type('text')
        if text_data:
            return text_data

    @property
    def face(self) -> list:
        face_data = self.__get_messages_by_type('face')
        if face_data:
            return face_data

    @property
    def image(self) -> list:
        image_data = self.__get_messages_by_type('image')
        if image_data:
            return image_data

    @property
    def record(self) -> list:
        record_data = self.__get_messages_by_type('record')
        if record_data:
            return record_data

    @property
    def video(self) -> list:
        video_data = self.__get_messages_by_type('video')
        if video_data:
            return video_data

    @property
    def rps(self) -> list:
        rps_data = self.__get_messages_by_type('rps')
        if rps_data:
            return rps_data

    @property
    def dice(self) -> list:
        dice_data = self.__get_messages_by_type('dice')
        if dice_data:
            return dice_data

    @property
    def poke(self) -> list:
        return self.__get_messages_by_type('poke')

    @property
    def share(self) -> list:
        return self.__get_messages_by_type('share')

    @property
    def contact(self) -> list:
        return self.__get_messages_by_type('contact')

    @property
    def location(self) -> list:
        return self.__get_messages_by_type('location')

    @property
    def music(self) -> list:
        music_data = self.__get_messages_by_type('music')
        if music_data:
            return music_data

    @property
    def reply(self) -> list:
        reply_data = self.__get_messages_by_type('reply')
        if reply_data:
            return reply_data

    @property
    def forward(self) -> list:
        forward_data = self.__get_messages_by_type('forward')
        if forward_data:
            return forward_data

    @property
    def node(self) -> list:
        node_data = self.__get_messages_by_type('node')
        if node_data:
            return node_data

    @property
    def json(self) -> list:
        json_data = self.__get_messages_by_type('json')
        if json_data:
            return json_data

    @property
    def mface(self) -> list:
        mface_data = self.__get_messages_by_type('mface')
        if mface_data:
            return mface_data

    @property
    def file(self) -> list:
        file_data = self.__get_messages_by_type('file')
        if file_data:
            return file_data

    @property
    def lightapp(self) -> list:
        return self.__get_messages_by_type('lightapp')



    def add_text(self, text: str) -> 'MessageBehavior':
        """
        纯文本
        :param text: 文本
        """
        self.__messages.append({
            "type": "text",
            "data": {
                "text": text
            }
        })
        return self

    def add_face(self, face_id: Union[int, str], name: str = None, summary: str = None) -> 'MessageBehavior':
        """
        QQ表情
        :param face_id: QQ表情编号
            表情编号参考（系统表情）：https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#Emoji%20%E5%88%97%E8%A1%A8
        :param name: 表情名称
        :param summary: 表情简介
        """
        self.__messages.append({
            "type": "face",
            "data": {
                "id": str(face_id),
                **replace_none(dict)(json=dict(name=name, summary=summary)).get('json', {})
            }
        })
        return self

    def add_media(self, media_type: str, media_path: str, **kwargs) -> 'MessageBehavior':
        """
        添加媒体资源（复用函数）
        :param media_type: 媒体资源类型
        :param media_path: 媒体资源地址（可以是网络地址）
        """
        media_path = self.get_media_path(media_path)
        if media_path:
            self.__messages.append({
                "type": media_type,
                "data": {
                    "file": media_path,
                    **kwargs
                }
            })
        return self

    def add_image(self, image: str, name: str = None, summary: str = None, sub_type: str = None) -> 'MessageBehavior':
        """
        图片
        :param image: 图片地址
        :param name: 图片名称
        :param summary: 图片简介
        :param sub_type: 子类型
        """
        self.add_media('image', image, **replace_none(dict)(json=dict(name=name, summary=summary, sub_type=sub_type)).get('json', {}))
        return self

    def add_record(self, record: str, name: str = None) -> 'MessageBehavior':
        """
        语音
        :param record: 语音地址
        :param name: 语言名称
        """
        self.add_media('record', record, **replace_none(dict)(json=dict(name=name)).get('json', {}))
        return self

    def add_video(self, video: str, name: str = None, thumb: str = None) -> 'MessageBehavior':
        """
        视频
        :param video: 视频地址
        :param name: 视频名称
        :param thumb: 视频缩略图
        """
        self.add_media('video', video, **replace_none(dict)(json=dict(name=name, thumb=self.get_media_path(thumb))).get('json', {}))
        return self

    def add_at(self, target: Union[int, str] = 'all') -> 'MessageBehavior':
        """
        @某人，all为@全体成员
        :param target: QQ表情编号
        """
        self.__messages.append({
            "type": "at",
            "data": {
                "qq": str(target),
            }
        })
        self.add_text(' ')  # 自动隔开@信息
        return self

    def rps(self) -> 'MessageBehavior':
        """
        超级表情——猜拳（将清空所有消息列表）
        """
        self.__messages = [{
            "type": "rps"
        }]
        return self

    def dice(self) -> 'MessageBehavior':
        """
        超级表情——骰子（将清空所有消息列表）
        """
        self.__messages = [{
            "type": "dice"
        }]
        return self

    def contact(self, qq: Union[int, str] = None, group: Union[int, str] = None) -> 'MessageBehavior':
        """
        推荐好友或群聊（将清空所有消息列表）
        :param qq: user_id
        :param group: group_id
        """
        if qq or group:
            self.__messages =[{
                "type": "contact",
                "data": {
                    "type": "qq" if qq else "group",
                    "id": qq or group
                }
            }]
        return self

    def music(self, music_type: str = 'custom', **kwargs) -> 'MessageBehavior':
        """
        音乐分享（将清空所有消息列表）
        :param music_type: qq / 163 / kugou / migu / kuwo / custom
        :param kwargs: qq / 163 / kugou / migu / kuwo：{id} | custom：{type, url, audio, title, image(选), singer(选)}
        """
        self.__messages = [{
            "type": "music",
            "data": {
                "type": music_type,
                **kwargs
            }
        }]
        return self

    def add_reply(self):
        '''
        已弃用，请使用.reply(reply=True)
        '''
        pass
    # def add_reply(self, message_id: Union[int, str]) -> 'MessageBehavior':
    #     """
    #     回复消息（更新后在发送消息前将会自动排序 reply 至最前面）
    #     :param message_id: 消息id号
    #     """
    #     self.__messages.append({
    #         "type": "reply",
    #         "data": {
    #             "id": str(message_id),
    #         }
    #     })
    #     return self

    def node(self, id_: Union[int, str] = None, content: list = None, user_id: Union[int, str] = None, nickname: str = None) -> 'MessageBehavior':
        """
        构造合并转发消息节点
        :param id_: 消息id号（与消息链二选一）
        :param content: 消息链（与消息id号二选一）
        :param user_id: user_id（伪造消息用，暂时没发现有用）
        :param nickname: 用户昵称（伪造消息用，暂时没发现有用）
        """
        self.__messages = [{
            "type": "node",
            "data": replace_none(dict)(json=dict(id=id_, content=content, user_id=user_id, nickname=nickname)).get('json', {})
        }]
        return self

    def add_json(self, data: Union[int, str]) -> 'MessageBehavior':
        """
        添加json消息
        :param data: json字符串
        """
        self.__messages.append({
            "type": "json",
            "data": {
                "data": data,
            }
        })
        return self

    def add_file(self, file: str, name: str = None) -> 'MessageBehavior':
        """
        文件
        :param file: 文件地址
        :param name: 文件名称
        """
        self.add_media('file', file, **replace_none(dict)(json=dict(name=name)).get('json', {}))
        return self

    # def add_markdown(self, markdown: str) -> 'MessageBehavior':
    #     """
    #     markdown美化图片
    #     :param markdown: 消息id号
    #     """
    #     self.add_media('image', markdown_to_image_beautified(markdown))
    #     return self

    def clear(self) -> 'MessageBehavior':
        """
        清空消息链
        """
        self.__messages = []
        return self

    async def old_send_group_msg(self, group_id: Union[int, str]) -> int:
        """
        发送群聊消息
        :param group_id: 群聊ID
        """
        message_id = None
        for message in self.__messages.copy():
            if message['type'] == 'reply':
                message_id = message
                self.__messages.remove(message)
        if message_id is not None:
            self.__messages = [message_id] + self.__messages
            message_id = message_id['data']['id']
        for message in self.__messages.copy():
            if message['type'] in ['rps', 'dice', 'contact', 'music', 'node']:
                self.__messages = [message]
                break
        if self.__messages:
            data = {
                "group_id": group_id,
                "message": self.__messages.copy()
            }
            result = await self._http.post("/send_group_msg", json=data)
            return result.get('message_id', -1)
        return -1

    async def old_send_private_msg(self, user_id: Union[int, str]) -> int:
        """
        发送私聊消息（自动去除@信息）
        :param user_id: 用户ID
        :param clear_message: 是否清空消息缓存
        """
        for message in self.__messages.copy():
            if message['type'] == 'at':
                self.__messages.remove(message)
        for message in self.__messages.copy():
            if message['type'] in ['rps', 'dice', 'contact', 'music', 'node']:
                self.__messages = [message]
                break
        if self.__messages:
            data = {
                "user_id": user_id,
                "message": self.__messages.copy()
            }
            result = await self._http.post("/send_private_msg", json=data)
            return result.get('message_id', -1)
        return -1

    async def reply(self,reply:bool = False, clear_message:bool = True) -> None:
        """
        回复消息
        :param reply: 引用消息(回复)
        :param clear_message: 清空消息缓存
        :return id: 此消息id，用于检查消息是否被引用(回复)
        """
        if self.message_type == 'group':
            if reply: self.__messages.insert(0, {'type': 'reply', 'data': {'id': self.message_id}})
            re = self.old_send_group_msg(self.group_id)
            if clear_message: self.__messages.clear()
        elif self.message_type == 'private':
            if reply: self.__messages.insert(0, {'type': 'reply', 'data': {'id': self.message_id}})
            re = self.old_send_private_msg(self.user_id)
            if clear_message: self.__messages.clear()
        else:
            raise ValueError(f"错误的消息类型: {self.message_type}")
        return re

    def __get_messages_by_type(self, msg_type) -> list:
        re = []
        for msg in self.message:
            if msg['type'] == msg_type:
                re.append(msg.get('data', {}))
        return re


class GroupMessage(BaseMessage, MessageBehavior):
    __slots__ = (
    "group_id", "user_id", "message_type", "sub_type", "raw_message", "font", "sender", "message_id", "message_seq",
    "real_id", "message", "message_format")

    def __init__(self, message):
        super().__init__(message) # BaseMessage
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

    # async def reply(self, **kwargs):
    #     i_list = ['text', 'face', 'json', 'at', 'reply', 'music', 'dice', 'rps']
    #     if "content" in kwargs:
    #         return await self.send_group_msg(group_id=self.group_id, **kwargs)
    #     elif any(i in kwargs for i in i_list):
    #         return await self.post_group_msg(group_id=self.group_id, **kwargs)
    #     else:
    #         return await self.post_group_file(group_id=self.group_id, **kwargs)

class PrivateMessage(BaseMessage, MessageBehavior):
    __slots__ = (
    "message_id", "user_id", "message_seq", "real_id", "message_type", "sender", "raw_message", "font", "sub_type",
    "message", "message_format", "target_id")

    def __init__(self, message):
        super().__init__(message) # BaseMessage
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

        self.__messages = self.message
        self.message_cache = []

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__})

    # async def reply(self, **kwargs):
    #     i_list = ['text', 'face', 'json', 'at', 'reply', 'music', 'dice', 'rps']
    #     if "content" in kwargs:
    #         return await self.send_private_msg(user_id=self.user_id, **kwargs)
    #     elif any(i in kwargs for i in i_list):
    #         return await self.post_private_msg(user_id=self.user_id, **kwargs)
    #     else:
    #         return await self.post_private_file(user_id=self.user_id, **kwargs)