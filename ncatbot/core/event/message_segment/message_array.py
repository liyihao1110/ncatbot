import re
from typing import Literal, Optional, Dict, Any, Union, Type, TypeVar, List, Iterable
from ncatbot.core.event.message_segment.message_segment import MessageSegment, get_class_by_name, MessageTypeNotFoundErr
from ncatbot.utils import NcatBotError, status, get_log
from dataclasses import fields
from .message_segment import (
    Text,
    PlainText,
    Face,
    Image,
    Video,
    At,
    AtAll,
    Reply,
    Node,
    Forward,
)

T = TypeVar('T', bound=MessageSegment)
LOG = get_log("MessageArray")

class MessageOperationError(NcatBotError):
    logger = LOG

class MessageFormatError(NcatBotError):
    logger = LOG

def parse_cq_code_to_onebot11(cq_string: str) -> List[Dict[str, Union[str, Dict[str, str]]]]:
    """
    将 CQ 码字符串解析为 OneBot 11 规范的消息数组格式，包含转义字符处理
    
    Args:
        cq_string: 包含 CQ 码的字符串，例如 "[CQ:image,file=123.jpg]这是一段文本[CQ:face,id=123]"
        
    Returns:
        OneBot 11 规范的消息数组，例如:
        [
            {"type": "image", "data": {"file": "123.jpg"}},
            {"type": "text", "data": {"text": "这是一段文本"}},
            {"type": "face", "data": {"id": "123"}}
        ]
    """
    # 正则表达式匹配 CQ 码
    cq_pattern = re.compile(r'\[CQ:([^,\]]+)(?:,([^\]]+))?\]')
    
    # 初始化结果列表
    message_segments = []
    last_pos = 0
    
    # HTML 实体转义映射
    html_unescape_map = {
        '&amp;': '&',
        '&#91;': '[',
        '&#93;': ']',
        '&#44;': ','
    }
    
    def unescape_cq(text: str) -> str:
        """取消 CQ 码中的 HTML 实体转义"""
        for escaped, unescaped in html_unescape_map.items():
            text = text.replace(escaped, unescaped)
        return text
    
    # 遍历所有匹配的 CQ 码
    for match in cq_pattern.finditer(cq_string):
        # 处理 CQ 码之前的文本（如果有）
        text_before = cq_string[last_pos:match.start()]
        if text_before:
            # 普通文本也需要反转义
            message_segments.append({
                "type": "text",
                "data": {"text": unescape_cq(text_before)}
            })
        
        # 处理 CQ 码
        cq_type = match.group(1)
        cq_params_str = match.group(2) or ""
        
        # 解析 CQ 码参数
        params = {}
        for param in cq_params_str.split(','):
            if '=' in param:
                key, value = param.split('=', 1)
                # 对参数值进行反转义处理
                params[key] = unescape_cq(value)
        
        # 添加到结果列表
        message_segments.append({
            "type": cq_type,
            "data": params
        })
        
        # 更新最后位置
        last_pos = match.end()
    
    # 处理最后一个 CQ 码之后的文本（如果有）
    text_after = cq_string[last_pos:]
    if text_after:
        message_segments.append({
            "type": "text",
            "data": {"text": unescape_cq(text_after)}
        })
    
    return message_segments

def process_dict(data: dict) -> MessageSegment:
    msg_seg_type = data.get("type")
    msg_data = data.get("data")
    return get_class_by_name(msg_seg_type).from_dict(msg_data)

def process_iterable(data: list) -> list[MessageSegment]:
    result = []
    for item in data:
        result = result + process_item(item)
    return result

def process_item(item: Union[List[Union[dict, MessageSegment]], Union[dict, MessageSegment]]) -> list[MessageSegment]:
    """
    处理消息(单个或迭代器)，返回对应的 list[MessageSegment] 对象
    
    Args:
        item: 可以是 MessageSegment 对象或字典
        
    Returns:
        处理后的 MessageSegment 对象，如果无法处理则返回 None
    """
    while (isinstance(item, list) or isinstance(item, tuple)) and len(item) == 1:
        item = item[0]
        
    if isinstance(item, MessageSegment):
        return [item]
    if isinstance(item, str):
        # 字符串, 当 CQ 码处理
        item = parse_cq_code_to_onebot11(item)
    if isinstance(item, dict):
        # 字典, 当消息段处理
        return [process_dict(item)]    
    if isinstance(item, Iterable):
        return process_iterable(item)    
    return []

class MessageArray:
    """表示一条消息的数据结构
    支持字典构造和 MessageSegment 构造
    """
    messages: list[MessageSegment] = []
        
    @classmethod
    def from_list(cls, data: list[Union[dict, MessageSegment]]):
        """"其实也支持单个"""
        return cls(data)
    
    def to_list(self) -> list[Dict]:
        data = []
        for item in self.messages:
            data.append(item.to_dict())
        return data
    
    def __init__(self, *args):
        self.messages = process_item(args)
        if self.is_forward_msg():
            mlen = len(self.messages)
            if mlen != len(self.filter(Forward)) and mlen != len(self.filter(Node)):
                raise MessageFormatError("消息格式错误, 合并转发消息严禁和其它类型消息混用")
    
    def add_by_list(self, data: list[Union[dict, MessageSegment]]):
        self.messages.extend(process_item(data))
        return self
    
    def add_by_segment(self, segment: MessageSegment):
        self.messages.append(segment)
        return self
    
    def add_by_dict(self, data: dict):
        self.messages.append(process_dict(data))
        return self
    
    def add_text(self, text: str):
        self.messages.extend(process_item(text))
        return self
    
    def add_image(self, image: str):
        self.messages.append(Image(file=image))
        return self
    
    def add_at(self, user_id: Union[str, int]):
        self.messages.append(At(user_id))
        return self
    
    def add_at_all(self):
        self.messages.append(AtAll())
        return self
    
    def add_reply(self, message_id: Union[str, int]):
        self.messages.append(Reply(message_id))
        return self
    
    def __add__(self, other):
        messages = self.messages + process_item(other)
        return MessageArray(messages)
        
    def __radd__(self, other):
        return self.__add__(other)
    
    def is_forward_msg(self):
        return len(self.filter(Forward)) > 0 or len(self.filter(Node)) > 0
    
    async def plain_forward_msg(self) -> Forward: 
        """把转发id格式的消息展平为解析完毕的 Forward
        Raises:
            MessageTypeError: _description_

        Returns:
            list[Node]: _description_
        """
        if not self.is_forward_msg():
            raise MessageOperationError("此消息不是合并转发消息, 无法展平")
        msg = self.filter(Forward)
        if len(msg) == 0:
            return self.messages
        return await status.global_api.get_forward_msg(msg[0].id)
    
    def filter(self, cls: Union[Type[T], None] = None) -> List[T]:
        if cls is None:
            return self.messages
        msg = []
        if not issubclass(cls, MessageSegment):
            raise MessageTypeNotFoundErr(cls.__name__)
        for item in self.messages:
            # Text 和 PlainText 需要特殊处理
            if isinstance(item, cls) or (cls is Text and isinstance(item, PlainText)):
                msg.append(item)
        return msg
    
    def filter_text(self) -> List[Text]:
        return self.filter(Text)
    
    def filter_at(self) -> List[At]:
        return self.filter(At)
    
    def filter_image(self) -> List[Image]:
        return self.filter(Image)
    
    def filter_video(self) -> List[Video]:
        return self.filter(Video)
    
    def filter_face(self) -> List[Face]:
        return self.filter(Face)
    
    def is_user_at(self, user_id: Union[str, int], all_except: bool = False) -> bool:
        user_id = str(user_id)
        ats = self.filter(At)
        for at in ats:
            if at.qq == user_id:
                return True
        return not all_except and len(self.filter(AtAll)) > 0
    
    def __iter__(self):
        return self.messages.__iter__()
    
    def __len__(self):
        return len(self.messages)
    
    def __str__(self):
        return str(self.messages)
    
    def __repr__(self):
        return repr(self.messages)
    
if __name__ == "__main__":
    msg = MessageArray().filter(Text)
