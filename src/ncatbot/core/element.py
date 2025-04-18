import json
import re
from typing import Iterable, Union

from deprecated import deprecated

from ncatbot.utils import convert_uploadable_object, get_log

LOG = get_log("Element")


class MessageChain:
    """消息链"""

    def __init__(self, chain=None, *args):
        def decode_message(message_list):
            if isinstance(message_list, str):
                return [Text(message_list)]
            elif isinstance(message_list, (Element, dict)):
                return [message_list]
            elif isinstance(message_list, Iterable):
                return sum([decode_message(item) for item in message_list], [])
            elif message_list is None:
                return []
            else:
                return [Text(str(message_list))]

        self.chain = decode_message([chain, *args])

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
    """文本消息元素, 支持 CQ 码"""

    type = "text"

    def __init__(self, text: str):
        self.text = str(text)

    def to_dict(self) -> dict:
        if self.text:
            return {"type": "text", "data": {"text": self.text}}
        else:
            return {"type": "text", "data": {"text": ""}}


class At(Element):
    """@消息元素"""

    type = "at"

    def __init__(self, qq: Union[int, str]):
        self.qq = str(qq)

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
        self.id = str(face_id)

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

    def __init__(self, file: str, url: str = None):
        self.file = file
        self.url = url
        if not file.endswith(".mp4"):
            self.url = self.file
            self.file = self.file + ".mp4"

    def to_dict(self) -> dict:
        return {"type": "video", "data": {"file": self.file, "url": self.url}}


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


def decode_message_sent(
    text: str = None,
    face: int = None,
    json: str = None,
    markdown: str = None,
    at: str = None,
    reply: Union[int, str] = None,
    music: Union[list, dict] = None,
    dice: bool = False,
    rps: bool = False,
    image: str = None,
    rtf: MessageChain = None,
):
    message: list = []
    if text:
        message.append(
            text if isinstance(text, dict) else Text(text)
        )  # dict 是兼容不符合要求的构造. 唉...
    if face:
        message.append(face if isinstance(face, dict) else Face(face))
    if json:
        message.append(Json(json))
    if markdown:
        raise NotImplementedError("Markdown is not implemented yet")
        # message.append(convert_uploadable_object(await md_maker(markdown), "image"))
    if at:
        message.append(at if isinstance(at, dict) else At(at))
    if reply:
        message.insert(0, reply if isinstance(reply, dict) else Reply(reply))
    if music:
        if isinstance(music, list):
            message.append(Music(music[0], music[1]))
        elif isinstance(music, dict):
            message.append(CustomMusic(**music))
    if dice:
        message.append(Dice())
    if rps:
        message.append(Rps())
    if image:
        message.append(image if isinstance(image, dict) else Image(image))
    if rtf:
        message.extend(rtf.elements)

    new_message = []
    # 解析 CQ 码
    for elem in message:
        if elem["type"] == "text":

            def extract_unmatched(text: str, matches):
                """
                提取未被正则捕获的部分，并构造为 Text 对象。
                """
                # 获取所有已匹配的跨度
                matched_spans = [span for _, span in matches]
                matched_spans.sort()  # 按跨度排序

                # 提取未匹配的部分
                unmatched_parts = []
                current_pos = 0

                for span in matched_spans:
                    start, end = span
                    if current_pos < start:
                        # 当前位置到匹配跨度的起始位置之间的部分是未匹配的
                        unmatched_text = text[current_pos:start]
                        unmatched_parts.append(
                            (Text(unmatched_text), (current_pos, start))
                        )
                    current_pos = end

                # 检查文本末尾是否有未匹配的部分
                if current_pos < len(text):
                    unmatched_text = text[current_pos:]
                    unmatched_parts.append(
                        (Text(unmatched_text), (current_pos, len(text)))
                    )

                return unmatched_parts

            raw = elem["data"]["text"]
            ats: list[re.Match] = re.finditer(r"\[CQ:at,\s?qq=(\d+|all)\]", raw)
            faces: list[re.Match] = re.finditer(r"\[CQ:face,\s?id=(\d+).*?\]", raw)
            images: list[re.Match] = re.finditer(
                r"\[CQ:image,(summary=(.+?),)?(file=(.+?),)?(sub_type=(.+?),)?(url=(.+?),?)?(file_size=(\d+),?)?\]",
                raw,
            )
            replys: list[re.Match] = re.finditer(r"\[CQ:reply,id=(\d+)\]", raw)
            l = []
            for _at in ats:
                l.append((At(_at.group(1)), _at.span()))
            for _face in faces:
                l.append((Face(_face.group(1)), _face.span()))
            for _image in images:
                l.append((Image(_image.group(8)), _image.span()))
            for _reply in replys:
                l.append((Reply(_reply.group(1)), _reply.span()))
            # 提取未匹配的部分并加入到 l 中
            unmatched_parts = extract_unmatched(raw, l)
            l.extend(unmatched_parts)

            # 按跨度排序
            l.sort(key=lambda x: x[1][0])
            for elem, span in l:
                new_message.append(elem)
        else:
            new_message.append(elem)
    message = new_message

    # 首先检查是否有 reply，只取第一个
    reply_elem = None
    for elem in message:
        if elem["type"] == "reply":
            reply_elem = Reply(elem["data"]["id"])
            break

    message = [msg for msg in message if msg["type"] != "reply"]
    if reply_elem:
        message.insert(0, reply_elem)

    # 检查是否包含非基本元素(音乐卡片等)
    basic_types = {"image", "text", "face", "reply", "at", "atall"}
    has_none_basic_elem = (
        len([elem for elem in message if elem["type"] not in basic_types]) != 0
    )

    if has_none_basic_elem:  # 如果存在非基本元素
        # 只添加第一个非基本元素
        none_basic_elem = [elem for elem in message if elem["type"] not in basic_types]
        if len(none_basic_elem) == 2:
            LOG.warning("存在多个非基本元素，只添加第一个非基本元素")
        return none_basic_elem[0]
    else:
        # 返回基本元素消息链
        return message


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
    "decode_message_sent",
]
