import json
from typing import Union

from deprecated import deprecated

from ncatbot.utils import convert_uploadable_object


class MessageChain:
    """消息链"""

    def __init__(self, chain=None):
        self.chain = []
        if chain is None:
            return

        if isinstance(chain, str):
            self.chain = [Text(chain)]
        elif isinstance(chain, list):
            # 处理列表输入
            for item in chain:
                if isinstance(item, dict):
                    self.chain.append(item)
                elif isinstance(item, Element):
                    self.chain.append(item)
                elif isinstance(item, list):
                    # 处理嵌套列表
                    for sub_item in item:
                        if isinstance(sub_item, dict):
                            self.chain.append(sub_item)
                        elif isinstance(sub_item, Element):
                            self.chain.append(sub_item)
                        else:
                            self.chain.append(Text(str(sub_item)))
                else:
                    self.chain.append(Text(str(item)))
        elif isinstance(chain, Element):
            self.chain = [chain]
        else:
            self.chain = [Text(str(chain))]

    def __str__(self):
        """确保字符串表示时保持顺序"""
        return json.dumps(self.chain, ensure_ascii=False)

    @property
    def elements(self) -> list:
        """将消息链转换为可序列化的字典列表"""
        return self.chain

    def __add__(self, other):
        """支持使用 + 连接两个消息链"""
        if isinstance(other, MessageChain):
            return MessageChain(self.chain + other.chain)
        return MessageChain(self.chain + [other])

    def __iadd__(self, other):
        if isinstance(other, MessageChain):
            self.chain += other.chain
        else:
            self.chain += MessageChain([other]).chain
        return self

    def display(self) -> str:
        """获取消息链的字符串表示"""
        result = []
        for elem in self.chain:
            if elem["type"] == "text":
                result.append(elem["data"]["text"])
            elif elem["type"] == "image":
                result.append("[图片]")
            elif elem["type"] == "at":
                result.append(f"@{elem['data']['qq']}")
            elif elem["type"] == "face":
                result.append("[表情]")
            elif elem["type"] == "music":
                result.append("[音乐]")
            elif elem["type"] == "video":
                result.append("[视频]")
            elif elem["type"] == "dice":
                result.append("[骰子]")
            elif elem["type"] == "rps":
                result.append("[猜拳]")
            elif elem["type"] == "json":
                result.append("[JSON]")
        return "".join(result)


class Element:
    """消息元素基类"""

    type: str = "element"

    def __new__(cls, *args, **kwargs):
        """直接返回字典而不是类实例"""
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.to_dict()

    def to_dict(self) -> dict:
        """将消息元素转换为字典"""
        return {"type": self.type, "data": {}}


class Text(Element):
    """文本消息元素"""

    type = "text"

    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> dict:
        if self.text:
            return {"type": "text", "data": {"text": self.text}}
        else:
            return {"type": "text", "data": {"text": ""}}


class At(Element):
    """@消息元素"""

    type = "at"

    def __init__(self, qq: Union[int, str]):
        self.qq = qq

    def to_dict(self) -> dict:
        return {"type": "at", "data": {"qq": self.qq}}


class AtAll(Element):
    """@全体消息元素"""

    type = "at"

    def to_dict(self):
        return {"type": "at", "data": {"qq": "all"}}


class Image(Element):
    """图片消息元素"""

    type = "image"

    def __init__(self, path: str):
        self.path = path

    def to_dict(self) -> dict:
        return convert_uploadable_object(self.path, "image")


class Face(Element):
    """表情消息元素"""

    type = "face"

    def __init__(self, face_id: int):
        self.id = face_id

    def to_dict(self) -> dict:
        return {"type": "face", "data": {"id": self.id}}


class Reply(Element):
    """回复消息元素"""

    type = "reply"

    def __init__(self, message_id: Union[int, str]):
        self.message_id = str(message_id)

    def to_dict(self) -> dict:
        return {"type": "reply", "data": {"id": self.message_id}}


class Json(Element):
    """JSON消息元素"""

    type = "json"

    def __init__(self, data: str):
        self.data = data

    def to_dict(self) -> dict:
        return {"type": "json", "data": {"data": self.data}}


class Record(Element):
    """语音消息元素"""

    type = "record"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return {"type": "record", "data": {"file": self.file}}


class Video(Element):
    """视频消息元素"""

    type = "video"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return {"type": "video", "data": {"file": self.file}}


class Dice(Element):
    """骰子消息元素"""

    type = "dice"

    def to_dict(self) -> dict:
        return {"type": "dice"}


class Rps(Element):
    """猜拳消息元素"""

    type = "rps"

    def to_dict(self) -> dict:
        return {"type": "rps"}


class Music(Element):
    """音乐分享消息元素"""

    type = "music"

    def __init__(self, type: str, id: str):
        self.music_type = type
        self.music_id = id

    def to_dict(self) -> dict:
        return {"type": "music", "data": {"type": self.music_type, "id": self.music_id}}


class CustomMusic(Element):
    """自定义音乐分享消息元素"""

    type = "music"

    def __init__(
        self,
        url: str,
        audio: str,
        title: str,
        image: str = "",
        singer: str = "",
        type: str = "custom",
    ):
        self.url = url
        self.audio = audio
        self.title = title
        self.image = image
        self.singer = singer
        self.type = type

    def to_dict(self) -> dict:
        return {
            "type": "music",
            "data": {
                "type": self.type,
                "url": self.url,
                "audio": self.audio,
                "title": self.title,
                "image": self.image,
                "singer": self.singer,
            },
        }


# TODO
# class Markdown(Element):
#     """Markdown消息元素"""

#     type = "image"

#     def __init__(self, markdown: str):
#         self.markdown = markdown

#     async def to_dict(self) -> dict:
#         return convert(await md_maker(self.markdown), "image")


@deprecated
class File(Element):
    """文件消息元素"""

    type = "file"

    def __init__(self, file: str):
        self.file = file

    def to_dict(self) -> dict:
        return convert_uploadable_object(self.file, "file")


__all__ = [
    "MessageChain",
    "Text",
    "Image",
    "Reply",
    "At",
    "AtAll",
    "Face",
    "Json",
    "Record",
    "Video",
    "Dice",
    "Rps",
    "Music",
    "CustomMusic",
    "File",
]
