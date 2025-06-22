from typing import Literal
from ncatbot.core.message_segment.message_segment import MessageSegment
"""
self_id, message_id 等无需进行数学运算, 故直接使用 str
"""

class BaseEventData:
    self_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    time: int = None
    post_type: Literal["message", "notice", "request", "meta_event"] = None
    
    def __init__(self, data: dict):
        pass
    
    def __getitem__(self, key):
        if key not in self.__dict__:
            raise KeyError(f"Ivalid key: {key}.")
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        if key not in self.__dict__:
            raise KeyError(f"Ivalid key: {key}.")
        self.__dict__[key] = value

    
class MessageEventData(BaseEventData):
    message_type: Literal["private", "group"] = None
    post_type: Literal["message"] = None
    message_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    user_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    message: list[MessageSegment] = None
    raw_message: str = None
    
    