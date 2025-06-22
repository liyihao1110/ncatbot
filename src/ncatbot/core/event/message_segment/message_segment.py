from typing import Literal, Optional, Union, Any, TYPE_CHECKING
from ncatbot.utils.file_io import convert_uploadable_object
if TYPE_CHECKING:
    from ncatbot.core.event.message_segment.message_array import MessageArray


class MessageSegment:
    type: Literal["text", "face", "image", "record", "video", "at", "rps", "dice", "shake", "poke", "anonymous", "share", "contact", "location", "music", "reply", "forward", "node", "xml", "json"] = None
    data: dict = {}
    
    def __init__(self, **kwargs):
        # 这个只用于 NcatBot 用户构造消息段
        pass
        
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": self.data.copy()
        }

class DownloadableMixin:
    async def get_download_url(self):
        return self.data["url"]
    

class PlainText(MessageSegment):
    # 不转义的纯文本消息
    type: Literal["text"] = "text"
    def __init__(self, text: str):
        super().__init__()
        self.type = "text"
        self.data["text"] = text


class Text(PlainText):
    # 默认使用的对 CQ 码转义的消息
    type: Literal["text"] = "text"
    def __init__(self, text: str):
        super().__init__(text)
        self.type = "text"


class Face(MessageSegment):
    type: Literal["face"] = "face"
    def __init__(self, id: Union[int, str]):
        super().__init__()
        self.type = "face"
        self.data["id"] = str(id)

class Image(MessageSegment, DownloadableMixin):
    type: Literal["image"] = "image"
    def __init__(self, file: str):
        super().__init__()
        self.type = "image"
        self.data["file"] = convert_uploadable_object(file)


class File(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["file"] = "file"
    def __init__(self, file: str, type: Literal["flash"]=None):
        super().__init__()
        self.type = "file"
        self.data["file"] = convert_uploadable_object(file)
        if type is not None:
            self.data["type"] = type
    

class Record(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["record"] = "record"
    def __init__(self, file: str):
        super().__init__()
        self.type = "record"
        self.data["file"] = convert_uploadable_object(file)


class Video(MessageSegment, DownloadableMixin):
    # 接收时需要维护 url
    type: Literal["video"] = "video"
    def __init__(self, file: str):
        super().__init__()
        self.type = "video"
        self.data["file"] = convert_uploadable_object(file)


class At(MessageSegment):
    type: Literal["at"] = "at"
    def __init__(self, qq: Union[int, str]):
        super().__init__()
        self.type = "at"
        self.data["qq"] = str(qq)

class AtAll(At):
    def __init__(self):
        super().__init__("all")
        
class Rps(MessageSegment):
    type: Literal["rps"] = "rps"
    def __init__(self):
        super().__init__()
        self.type = "rps"
    
class Dice(MessageSegment):
    type: Literal["dice"] = "dice"
    def __init__(self):
        super().__init__()
        self.type = "dice"
    
class Shake(MessageSegment):
    type: Literal["shake"] = "shake"
    def __init__(self):
        super().__init__()
        self.type = "shake"
    
class Poke(MessageSegment):
    type: Literal["poke"] = "poke"
    def __init__(self, type, id):
        super().__init__()
        self.type = "poke"
        self.data["type"] = type
        self.data["id"] = id
    
class Anonymous(MessageSegment):
    type: Literal["anonymous"] = "anonymous"
    def __init__(self):
        super().__init__()
        self.type = "anonymous"

class Share(MessageSegment):
    type: Literal["share"] = "share"
    def __init__(self, url: str, title: str, content: str, image: str):
        super().__init__()
        self.type = "share"
        self.data["url"] = url
        self.data["title"] = title
        self.data["content"] = content
        self.data["image"] = image # optional

class Contact(MessageSegment):
    type: Literal["contact"] = "contact"
    def __init__(self, type: Literal["qq", "group"], id: Union[int, str]):
        super().__init__()
        self.type = "contact"
        self.data["type"] = type
        self.data["id"] = str(id)
        
class Location(MessageSegment):
    type: Literal["location"] = "location"
    def __init__(self, lat: float, lon: float, title: str, content: str):
        super().__init__()
        self.type = "location"
        self.data["lat"] = lat
        self.data["lon"] = lon
        self.data["title"] = title # optional
        self.data["content"] = content # optional

class Music(MessageSegment):
    type: Literal["music"] = "music"
    def __init__(self, type: Literal["qq", "163", "custom"], id: Union[int, str], url: str, title: str, content: str, image: str):
        super().__init__()
        self.type = "music"
        self.data["type"] = type
        if type == "custom":
            self.data["url"] = url
            self.data["title"] = title
            self.data["content"] = content
            self.data["image"] = image
        else:
            self.data["id"] = str(id)
        
class Reply(MessageSegment):
    type: Literal["reply"] = "reply"
    def __init__(self, id: Union[int, str]):
        super().__init__()
        self.type = "reply"
        self.data["id"] = str(id)

class Node(MessageSegment):
    type: Literal["node"] = "node"
    def __init__(self, id: Union[int, str], user_id: Union[int, str], nickname: str):
        super().__init__()
        self.type = "node"
        self.data["user_id"] = str(user_id)
        self.data["id"] = str(id)
        self.data["nickname"] = nickname
    
    # async def to_message_array(self, recursive: bool = False):
    async def to_message_array(self, recursive: bool = False) -> 'MessageArray[Union[MessageArray, MessageSegment]]':
        if "id" in self.data:
            return MessageArray()
        else:
            return MessageArray()

class Forward(MessageSegment):
    type: Literal["forward"] = "forward"
    def __init__(self, id: Union[int, str]):
        super().__init__()
        self.type = "forward"
        self.data["id"] = str(id)
    
    # async def plain(self, recursive: bool = False):
    async def plain(self, recursive: bool = False) -> 'MessageArray[MessageArray]':
        return Node(self.data["id"]).to_message_array(recursive=recursive)


class XML(MessageSegment):
    type: Literal["xml"] = "xml"
    def __init__(self, data: str):
        super().__init__()
        self.type = "xml"
        self.data["data"] = data


class Json(MessageSegment):
    type: Literal["json"] = "json"
    def __init__(self, data: str):
        super().__init__()
        self.type = "json"
        self.data["data"] = data