# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

from .base import Base
from .utils import replace_none, markdown_to_image_beautified


class MessageChain(Base):
    def __init__(self, port_or_http: (int, str), max_ids: int = 100, sync: bool = False):
        super().__init__(port_or_http=port_or_http, sync=sync)
        self.messages = []  # 存储消息体
        self.message_ids = []  # 存储消息id
        self.max_ids = max_ids  # 最大保留已发送消息的消息id数量

    def add_id(self, mid):
        self.message_ids.append(mid)
        if len(self.message_ids) >= self.max_ids:
            self.message_ids = self.message_ids[-self.max_ids:]

    async def send_group_msg(self, group_id: (int, str), clear_message: bool = True):
        """
        发送群聊消息
        :param group_id: group_id
        :param clear_message: 是否清空消息缓存
        :return: 群聊消息请求类
        """
        message_id = None
        for message in self.messages.copy():
            if message['type'] == 'reply':
                message_id = message['data']['id']
        if self.messages:
            if message_id:
                data = {
                    "group_id": group_id,
                    'message_id': message_id,
                    "message": self.messages.copy()
                }
            else:
                data = {
                    "group_id": group_id,
                    "message": self.messages.copy()
                }
            if clear_message:
                self.clear()
            result = await self.post("/send_group_msg", json=data)
            if result['data']:
                self.add_id(result['data']['message_id'])
            else:
                print(result)
        return self

    async def send_private_msg(self, user_id: (int, str), clear_message: bool = True):
        """
        发送私聊消息（自动去除@信息）
        :param user_id: user_id
        :param clear_message: 是否清空消息缓存
        :return: 私聊消息请求类
        """
        for message in self.messages.copy():
            if message['type'] == 'at':
                self.messages.remove(message)
        if self.messages:
            data = {
                "user_id": user_id,
                "message": self.messages.copy()
            }
            if clear_message:
                self.clear()
            result = await self.post("/send_private_msg", json=data)
            if result['data']:
                self.add_id(result['data']['message_id'])
            else:
                print(result)
        return self

    def add_text(self, text: str):
        """
        纯文本
        :param text: 文本
        """
        self.messages.append({
            "type": "text",
            "data": {
                "text": text
            }
        })
        return self

    def add_face(self, face_id: (int, str)):
        """
        QQ表情
        :param face_id: QQ表情编号
            表情编号参考（系统表情）：https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#Emoji%20%E5%88%97%E8%A1%A8
        """
        self.messages.append({
            "type": "face",
            "data": {
                "id": str(face_id),
            }
        })
        return self

    def add_media(self, media_type: str, media_path: str, **kwargs):
        """
        添加媒体资源（复用函数）
        :param media_type: 媒体资源类型
        :param media_path: 媒体资源地址（可以是网络地址）
        """
        media_path = self.get_media_path(media_path)
        if media_path:
            self.messages.append({
                "type": media_type,
                "data": {
                    "file": media_path,
                    **kwargs
                }
            })
        return self

    def add_image(self, image: str):
        """
        图片
        :param image: 图片地址
        """
        self.add_media('image', image)
        return self

    def add_record(self, record: str):
        """
        语音
        :param record: 语音地址
        """
        self.add_media('record', record)
        return self

    def add_video(self, video: str):
        """
        视频
        :param video: 视频地址
        """
        self.add_media('video', video)
        return self

    def add_at(self, target: (int, str) = 'all'):
        """
        @某人，all为@全体成员
        :param target: QQ表情编号
        """
        self.messages.append({
            "type": "at",
            "data": {
                "qq": str(target),
            }
        })
        self.add_text(' ')  # 自动隔开@信息
        return self

    def rps(self):
        """
        超级表情——猜拳（将清空所有消息列表）
        """
        self.messages = [{
            "type": "rps"
        }]
        return self

    def dice(self):
        """
        超级表情——骰子（将清空所有消息列表）
        """
        self.messages = [{
            "type": "dice"
        }]
        return self

    def music(self, music_type: str = 'custom', **kwargs):
        """
        音乐分享（将清空所有消息列表）
        :param music_type: qq / 163 / kugou / migu / kuwo / custom
        :param kwargs: qq / 163 / kugou / migu / kuwo：{id} | custom：{type, url, audio, title, image(选), singer(选)}
        """
        self.messages = [{
            "type": "music",
            "data": {
                "type": music_type,
                **kwargs
            }
        }]
        return self

    def add_reply(self, message_id: (int, str)):
        """
        回复消息（建议放在第一个消息参数位置）
        :param message_id: 消息id号
        """
        self.messages.append({
            "type": "reply",
            "data": {
                "id": str(message_id),
            }
        })
        return self

    def add_json(self, data: (int, str)):
        """
        回复消息（建议放在第一个消息参数位置）
        :param data: 消息id号
        """
        self.messages.append({
            "type": "json",
            "data": {
                "data": data,
            }
        })
        return self

    def add_file(self, file: str):
        """
        文件
        :param file: 文件地址
        """
        self.add_media('file', file)
        return self

    def add_markdown(self, markdown: str):
        """
        markdown美化图片
        :param markdown: 消息id号
        """
        self.add_media('image', markdown_to_image_beautified(markdown))
        return self

    def clear(self):
        self.messages = []
        return self
