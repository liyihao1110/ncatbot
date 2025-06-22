from typing import Literal, Optional, Union, Any, TYPE_CHECKING
from ncatbot.utils.file_io import convert_uploadable_object
if TYPE_CHECKING:
    from ncatbot.core.message_segment.message_array import MessageArray


class MessageSegment:
    type: Literal["text", "face", "image", "record", "video", "at", "rps", "dice", "shake", "poke", "anonymous", "share", "contact", "location", "music", "reply", "forward", "node", "xml", "json"] = None
    data: dict = {}
    def __init__(self, **kwargs):
        # 这个只用于 NcatBot 用户构造消息段
        pass

class DownloadableMixin:
    async def get_download_url(self):
        return self.data["url"]
    

class PlainText(MessageSegment):
    # 不转义的纯文本消息
    type: Literal["text"] = None
    def __init__(self, text: str):
        self.data["text"] = text


class Text(PlainText):
    # 默认使用的对 CQ 码转义的消息
    type: Literal["text"]
    def __init__(self, text: str):
        self.data["text"] = text


class Face(MessageSegment):
    type: Literal["face"]
    def __init__(self, id: Union[int, str]):
        self.data["id"] = str(id)

class Image(MessageSegment, DownloadableMixin):
    type: Literal["image"]
    def __init__(self, file: str):
        self.data["file"] = convert_uploadable_object(str)


class File(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["file"]
    def __init__(self, file: str, type: Literal["flash"]=None):
        """
        Args:
            file (str): 文件数据, 支持 base64, url, 本地文件路径.
            type: 为 "flash" 时表示闪照.
        """
        self.data["file"] = convert_uploadable_object(file)
        if type is not None:
            self.data["type"] = type
    

class Record(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["record"]
    def __init__(self, file: str, magic: Optional[str]=None):
        """
        Args:
            file (str): 文件数据, 支持 base64, url, 本地文件路径.
        """
        self.data["file"] = convert_uploadable_object(file)


class Video(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["video"]
    def __init__(self, file: str):
        """
        Args:
            file (str): 文件数据, 支持 base64, url, 本地文件路径.
        """
        self.data["file"] = convert_uploadable_object(file)


class At(MessageSegment):
    type: Literal["at"]
    def __init__(self, qq: Union[int, str]):
        self.data["qq"] = str(qq)

class AtAll(At):
    def __init__(self):
        super().__init__("all")
        
class Rps(MessageSegment):
    type: Literal["rps"]
    def __init__(self):
        pass
    
class Dice(MessageSegment):
    type: Literal["dice"]
    def __init__(self):
        pass
    
class Shake(MessageSegment):
    type: Literal["shake"]
    def __init__(self):
        pass
    
class Poke(MessageSegment):
    type: Literal["poke"]
    name: Optional[str] = None # 接收时使用, 名字
    def __init__(self, type, id):
        self.data["type"] = type
        self.data["id"] = id
    
class Anonymous(MessageSegment):
    type: Literal["anonymous"]
    def __init__(self):
        pass

class Share(MessageSegment):
    type: Literal["share"]
    def __init__(self, url: str, title: str, content: str, image: str):
        self.data["url"] = url
        self.data["title"] = title
        self.data["content"] = content
        self.data["image"] = image

class Contact(MessageSegment):
    type: Literal["contact"]
    def __init__(self, type: Literal["qq", "group"], id: Union[int, str]):
        self.data["type"] = type
        self.data["id"] = str(id)
        
class Location(MessageSegment):
    type: Literal["location"]
    def __init__(self, lat: float, lon: float, title: str, content: str):
        self.data["lat"] = lat
        self.data["lon"] = lon
        self.data["title"] = title
        self.data["content"] = content

class Music(MessageSegment):
    type: Literal["music"]
    def __init__(self, type: Literal["qq", "163", "custom"], id: Union[int, str], url: str, title: str, content: str, image: str):
        self.data["type"] = type
        if type == "custom":
            self.data["url"] = url
            self.data["title"] = title
            self.data["content"] = content
            self.data["image"] = image
        else:
            self.data["id"] = str(id)
        
class Reply(MessageSegment):
    type: Literal["reply"]
    def __init__(self, id: Union[int, str]):
        self.data["id"] = str(id)

"""
Node <==> MessageArray[Any...]
"""
class Node(MessageSegment):
    type: Literal["node"]
    def __init__(self, id: Union[int, str], user_id: Union[int, str], nickname: str):
        self.data["user_id"] = str(user_id)
        self.data["id"] = str(id)
        self.data["nickname"] = nickname
    
    async def to_message_array(self, recursive: bool = False) -> MessageArray[Union[MessageArray, MessageSegment]]:
        if "id" in self.data:
            return MessageArray()
        else:
            return MessageArray()

"""
Forward <==> MessageArray[Node1, Node2, Node3...]
        <==> MessageArray[MessageArray1, MessageArray2...]
"""
class Forward(MessageSegment):
    type: Literal["forward"]
    def __init__(self, id: Union[int, str]):
        self.data["id"] = str(id)
    
    async def plain(self, recursive: bool = False) -> MessageArray[MessageArray]:
        return Node(self.data["id"]).to_message_array(recursive=recursive)


class XML(MessageSegment):
    type: Literal["xml"]
    def __init__(self, data: str):
        self.data["data"] = data

class Json(MessageSegment):
    type: Literal["json"]
    def __init__(self, data: str):
        self.data["data"] = data


