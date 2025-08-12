
from email import message
import re
import base64
import os
import asyncio
import time
import httpx
from ncatbot.core.event.message_segment.utils import convert_uploadable_object
import urllib
from dataclasses import dataclass, field, fields
from urllib.parse import urljoin
from typing import Literal, Union, Any, TYPE_CHECKING, TypeVar, Dict, Type, Iterable
from ncatbot.utils import get_log, NcatBotError, status
if TYPE_CHECKING:
    from ncatbot.core.event.message_segment.message_array import MessageArray
    from ncatbot.core.event.event_data import MessageEventData

T = TypeVar('T')
LOG = get_log("MessageSegment")


class MessageTypeNotFoundErr(NcatBotError):
    def __init__(self, type_name):
        super().__init__(f"找不到消息类型: {type_name}")

def create_message_array(obj: Union["MessageArray", Union[list["MessageSegment"], list[dict]], ]) -> "MessageArray":
    from ncatbot.core.event.message_segment.message_array import MessageArray
    if isinstance(obj, MessageArray):
        return obj
    else:
        return MessageArray.from_list(obj)

class MessageSegmentValueError(Exception):
    def __init__(self, info):
        LOG.error(info)
        super().__init__(info)

@dataclass(repr=False)
class MessageSegment():
    msg_seg_type: Literal["text", "face", "image", "record", "video", "at", "rps", "dice", "shake", "poke", "anonymous", "share", "contact", "location", "music", "reply", "forward", "node", "xml", "json", "markdown"] = field(init=False, repr=False)
    _data: dict = field(init=False, repr=False) # 兼容 3xx 版本数据辅助
    
    # -------------
    # region 兼容层
    # -------------
    def __getitem__(self, key: str) -> Any:
        """支持 dict[key] 访问方式"""
        if self._data is None:
            self._data = self.to_dict()  # 第一次访问时生成字典
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """支持 dict[key] = value 修改方式"""
        if self._data is None:
            self._data = self.to_dict()
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """支持 del dict[key] 删除方式"""
        if self._data is None:
            self._data = self.to_dict()
        del self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        """支持 dict.get(key, default)"""
        if self._data is None:
            self._data = self.to_dict()
        return self._data.get(key, default)

    def keys(self):
        """支持 dict.keys()"""
        if self._data is None:
            self._data = self.to_dict()
        return self._data.keys()

    def values(self):
        """支持 dict.values()"""
        if self._data is None:
            self._data = self.to_dict()
        return self._data.values()

    def items(self):
        """支持 dict.items()"""
        if self._data is None:
            self._data = self.to_dict()
        return self._data.items()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        all_fields = fields(cls)
        init_fields = {f.name: f for f in all_fields if f.init}
        non_init_fields = {f.name for f in all_fields if not f.init}
        init_kwargs = {k: data.get(k) for k in init_fields if k in data}
        obj = cls(**init_kwargs)
        for field_name in non_init_fields:
            if field_name in data:
                setattr(obj, field_name, data[field_name])
        return obj
    
    def to_dict(self) -> dict:
        from ncatbot.core.event.message_segment.message_array import MessageArray
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, MessageSegment):
                result[k] = v.to_dict()
            elif isinstance(v, MessageArray):
                result[k] = [vv.to_dict() for vv in v]
            elif isinstance(v, list) and len(v) > 0 and hasattr(v[0], "to_dict"):
                result[k] = [vv.to_dict() for vv in v]
            elif v not in [None, "", "None"]:
                result[k] = v
        return {
            "type": self.msg_seg_type,
            "data": result
        }

    def get_summary(self):
        return self.summary if hasattr(self, "summary") else "该消息不支持预览"
    
    def __repr__(self):
        field_items = [(field.name, getattr(self, field.name)) 
                      for field in fields(self) if hasattr(self, field.name) and field.repr]
        non_none_fields = [f"{name}={value if not isinstance(value, str) else f'\"{value}\"'}" 
                          for name, value in field_items if value is not None]
        return f"{self.__class__.__name__}({', '.join(non_none_fields)})"

    def __str__(self):
        return self.__repr__()

@dataclass(repr=False)
class DownloadableMessageSegment(MessageSegment):
    file: str
    url: str = field(init=False)
    msg_seg_type: Literal["file", "image", "record", "video"] = field(init=False, repr=False, default=None)
    file_id: str = field(init=False, default=None)
    file_size: int = field(init=False, default=None)
    file_name: str = field(default=None)
    file_type: str = field(init=False, default=None)
    base64: str = field(init=False, repr=False)
    def get_file_name(self):
        if self.file_name:
            return self.file_name
        
        is_url = self.file.startswith(('http://', 'https://', 'ftp://', 's3://'))
        if is_url:
            # 解析 URL，提取路径部分（忽略查询参数和哈希）
            parsed = urllib.parse.urlparse(self.file)
            path = parsed.path
            filename = os.path.basename(path)
            if not filename:
                filename = parsed.netloc.split(':')[0]  # 去掉端口号
                # 如果域名也无效（如奇怪的 URL），返回 None 或自定义默认名
                if not filename:
                    filename = "unnamed_file"
            else:
                # 处理可能的查询参数干扰（如 'file.txt?id=1' → 确保保留 .txt）
                filename = filename.split('?')[0].split('#')[0]
        else:
            filename = os.path.basename(self.file)
        return filename
    
    def to_dict(self):
        self.file = convert_uploadable_object(self.file)
        return super().to_dict()
    
    def __post_init__(self):
        pass
    
    def _get_final_path(self, dir: str, name: str):
        name = name if name else self.get_file_name()
        if not os.path.exists(dir):
            raise NcatBotError(f"下载路径不存在: {dir}")
        target_path = os.path.join(dir, name)
        if os.path.exists(target_path):
            path = target_path.split(".")[0] + "_" + str(time.time()) + "." + target_path.split(".")[1]
            LOG.warning(f"文件已存在: {target_path}, 将保存为 {path}")
        else:
            path = target_path
        return path
        
    async def download_to(self, dir: str, name: str=None):
        path = self._get_final_path(dir, name)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url)
                with open(path, "wb") as f:
                    f.write(response.content)
        except httpx.UnsupportedProtocol as e:
            LOG.error(f"不支持的协议: {self.file}")
            return None
        return path

@dataclass(repr=False)
class PlainText(MessageSegment):
    # 不转义的纯文本消息
    text: str
    msg_seg_type: Literal["text"] = field(init=False, repr=False, default="text")
    def get_summary(self):
        return self.text

@dataclass(repr=False)
class Text(PlainText):
    # 默认使用的对 CQ 码转义的消息
    text: str
    msg_seg_type: Literal["text"] = field(init=False, repr=False, default="text")

@dataclass(repr=False)
class Face(MessageSegment):
    id: str
    faceText: str = "[表情]"
    msg_seg_type: Literal["face"] = field(init=False, repr=False, default="face")
    def __init__(self, id: Union[str, int], raw: dict=None, faceText: str=None):
        self.id = id
        if raw:
            self.faceText = raw.get("faceText", "[表情]")
        if faceText:
            self.faceText = faceText
        self.__post_init__()
    
    def __post_init__(self):
        self.id = str(self.id)

    def get_summary(self):
        return self.faceText

@dataclass(repr=False)
class Image(DownloadableMessageSegment):
    msg_seg_type: Literal["image"] = field(init=False, repr=False, default="image")
    summary: str = field(default="[图片]")
    type: Literal["flash"] = None
    def is_flase_image(self) -> bool:
        return getattr(self, "type", None) == "flash"

@dataclass(repr=False)
class File(DownloadableMessageSegment):
    msg_seg_type: Literal["file"] = field(init=False, repr=False, default="file")
    def to_dict(self):
        name = self.get_file_name()
        dict = super().to_dict()
        dict["data"]["name"] = name
        return dict
    
    def get_summary(self):
        return "[文件]" + self.get_file_name()
    
    
@dataclass(repr=False)
class Record(DownloadableMessageSegment):
    msg_seg_type: Literal["record"] = field(init=False, repr=False, default="record")
    def get_summary(self):
        # TODO: 详细解析(秒数)
        return "[语音]"

@dataclass(repr=False)
class Video(DownloadableMessageSegment):
    msg_seg_type: Literal["video"] = field(init=False, repr=False, default="video")
    def get_summary(self):
        return "[视频]"
    
@dataclass(repr=False)
class At(MessageSegment):
    msg_seg_type: Literal["at"] = field(init=False, repr=False, default="at")
    qq: str = None
    
    @classmethod
    def from_dict(cls, data: dict):
        if data.get("qq") == "all":
            return AtAll()
        else:
            return At(qq=str(data.get("qq")))            

@dataclass(repr=False)
class AtAll(At):
    qq: str = field(init=False, default="all")
    def __str__(self):
        return "AtAll()"
    
    def __repr__(self):
        return "AtAll()"

@dataclass(repr=False)                
class Rps(MessageSegment):
    # TODO 测试收发
    msg_seg_type: Literal["rps"] = field(init=False, repr=False, default="rps")

@dataclass(repr=False)
class Dice(MessageSegment):
    # TODO 测试收发
    msg_seg_type: Literal["dice"] = field(init=False, repr=False, default="dice")
    
@dataclass(repr=False)
class Shake(MessageSegment):
    # TODO 测试收发
    msg_seg_type: Literal["shake"] = field(init=False, repr=False, default="shake")

@dataclass(repr=False)
class Poke(MessageSegment):
    id: str
    msg_seg_type: Literal["poke"] = field(init=False, repr=False, default="poke")
    type: Literal["poke"] = None
    
@dataclass(repr=False)
class Anonymous(MessageSegment):
    # TODO 测试收发
    msg_seg_type: Literal["anonymous"] = field(init=False, repr=False, default="anonymous")

@dataclass(repr=False)
class Share(MessageSegment):
    msg_seg_type: Literal["share"] = field(init=False, repr=False, default="share")
    url: str
    title: str = "分享"
    content: str = None
    image: str = None
    def __post_init__(self):
        self.image = convert_uploadable_object(self.image)

@dataclass(repr=False)
class Contact():
    msg_seg_type: Literal["contact"] = field(init=False, repr=False, default="contact")
    type: Literal["qq", "group"]
    id: str

@dataclass(repr=False)        
class Location(MessageSegment):
    # 测试收发
    msg_seg_type: Literal["location"] = field(init=False, repr=False, default="location")
    lat: float
    lon: float
    title: str = "位置分享"
    content: str = None

@dataclass(repr=False)
class Music(MessageSegment):
    # TODO 测试收发
    id: str
    url: str
    title: str
    content: str
    image: str
    msg_seg_type: Literal["music"] = field(init=False, repr=False, default="music")
    type: Literal["qq", "163", "custom"] = None
        
    def __init__(self, type: Literal["qq", "163", "custom"], id: Union[int, str], url: str, title: str, content: str=None, image: str=None):
        self.msg_seg_type = "music"
        self.type = type
        if type == "custom":
            self.url = url
            self.title = title
            self.content = content
            self.image = convert_uploadable_object(image)
        else:
            self.id = str(id)

@dataclass(repr=False)
class Reply(MessageSegment):
    id: str
    msg_seg_type: Literal["reply"] = field(init=False, repr=False, default="reply")
    def __post_init__(self):
        self.id = str(self.id)

@dataclass(repr=False)
class Node(MessageSegment):
    user_id: str = "123456"
    nickname: str = "QQ用户"
    content: "MessageArray" = field(default=None)
    msg_seg_type: Literal["node"] = field(init=False, repr=False, default="node")
    
    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        obj.content = create_message_array(obj.content)
        return obj
    
    @classmethod
    def from_message_event(cls, data: dict):
        from ncatbot.core.event.message_segment.message_array import MessageArray
        message_data = data.get("message", None)
        if message_data[0].get("type") == 'forward':
            content = [Forward.from_content(message_data[0].get("data").get("content"), message_data[0].get("data").get("id"))]
        else:
            content = create_message_array(message_data)
        obj = cls(
            data.get("user_id"),
            data.get("sender").get("nickname"),
            content=MessageArray(content),
        )
        return obj
        
    def __post_init__(self):
        # if (self.id is not None) == (self.content is not None):
        #     raise MessageSegmentValueError("构造消息节点时, id 和 content 二选一")
        self.user_id = str(self.user_id)
    
    def get_summary(self):
        return self.nickname + ": " + "".join(msg.get_summary() for msg in self.content)

@dataclass(repr=False)
class Forward(MessageSegment):
    id: str = field(default=None)
    # summary: str = field(init=False, repr=False, default="[聊天记录]")
    # prompt: str = field(init=False)
    # news: list[str] = field(init=False, repr=False, default=None)
    # source: str = field(init=False, repr=False, default=None)
    message_type: Literal["group", "friend"] = field(default=None) # 用于描述消息节点的来源
    content: list[Node] = field(default=None)
    msg_seg_type: Literal["forward"] = field(init=False, repr=False, default="forward")
    
    @classmethod
    def from_content(cls, content: list[dict], id):
        obj = cls(id)
        obj.content = [Node.from_message_event(msg_event_dict) for msg_event_dict in content]
        return obj
    
    @classmethod
    def from_dict(cls, data):
        obj = super().from_dict(data)
        if obj.content is not None:
            obj.content = create_message_array(obj.content).messages
        return obj        
        
    @classmethod
    def from_messages(cls, messages: list[Union[Node, "MessageEventData"]], message_type: Literal["group", "friend"] = None):
        from ncatbot.core.event.event_data import MessageEventData
        obj = cls(None)
        if len(messages) == 0:
            raise NcatBotError("Forward 转化传入的消息数量不能为零") 
        obj.content = []
        for msg in messages:
            if isinstance(msg, Node):
                obj.content.append(msg)
            elif isinstance(msg, MessageEventData):
                obj.content.append(Node.from_message_event(msg.to_dict()))
        obj.message_type = message_type
        return obj
    
    @classmethod
    async def from_message_id(cls, messages: list[Union[str, int]], message_type: Literal["group", "friend"]):
        from ncatbot.core.event.event_data import MessageEventData
        obj = cls(None)
        if len(messages) == 0:
            raise NcatBotError("Forward 转化传入的消息数量不能为零") 
        for msg in messages:
            obj.content.append(Node.from_message_event(await status.global_api.get_msg(msg)))
        obj.message_type = message_type
        
    def to_forward_dict(self):
        def modify_type(msg_list: list[dict]):
            for msg in msg_list:
                if msg['type'] in ("forward", "node"):
                    msg['type'] = 'node'
                    if "messages" in msg["data"]:
                        msg["data"]["content"] = msg["data"]["messages"]
                        msg["data"].pop("messages")
                    modify_type(msg['data']["content"])
            
        if self.content is None:
            raise ValueError("需要先使用 get_content 方法获取内容")
        nicknames = list(dict.fromkeys([msg.nickname for msg in self.content]))
        prompt = self.get_summary()
        source = "群聊的聊天记录" if self.message_type == "group" or len(nicknames) > 2 else f"{nicknames[0]}{'' if len(nicknames) == 1 else '和' + nicknames[-1]}的聊天记录"
        summary = f"查看{len(self.content)}条聊天记录"
        news = [{"text": msg.get_summary()} for msg in self.content][:4]
        messages = []
        for msg in self.content:
            if msg.content.is_forward_msg():
                _msg_data = msg.content.messages[0].to_forward_dict()
                _msg_data['user_id'] = msg.user_id
                _msg_data['nickname'] = msg.nickname
                msg_data = {
                    "type": "node",
                    "data": _msg_data
                }
                messages.append(msg_data)
            else:
                messages.append(msg.to_dict())
        modify_type(messages)
        return {
            "messages": messages,
            "news": news,
            "prompt": prompt,
            "summary": summary,
            "source": source
        }
    
    async def get_content(self) -> list[Node]:
        fwd = await status.global_api.get_forward_msg(self.id)
        self.__dict__.update(fwd.__dict__)
        return self.content
    
    def filter(self, cls: Type[T]) -> list[T]:
        return self.content[0].content.filter(cls)
    
    def get_summary(self):
        return "[聊天记录]"
    
    def __post_init__(self):
        self.id = str(self.id)

@dataclass(repr=False)
class XML(MessageSegment):
    data: str
    msg_seg_type: Literal["xml"] = field(init=False, repr=False, default="xml")

@dataclass(repr=False)
class Json(MessageSegment):
    data: str
    msg_seg_type: Literal["json"] = field(init=False, repr=False, default="json")

@dataclass(repr=False)
class Markdown(MessageSegment):
    content: str
    msg_seg_type: Literal["markdown"] = field(init=False, repr=False, default="markdown")

def get_class_by_name(name: str) -> Type[MessageSegment]:
    def find_all_subclasses(cls) -> list[Type[MessageSegment]]:
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(find_all_subclasses(subclass))
        return subclasses
    
    for cls in find_all_subclasses(MessageSegment):
        if cls.msg_seg_type == name:
            return cls
    raise MessageTypeNotFoundErr(name)

