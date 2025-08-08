from typing import Literal, Callable
from ncatbot.core.event.message_segment import MessageArray
from ncatbot.core.event.sender import BaseSender
"""
self_id, message_id 等无需进行数学运算, 故直接使用 str
"""

class BaseEventData:
    self_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    time: int = None
    post_type: Literal["message", "notice", "request", "meta_event"] = None
    
    def __init__(self, data: dict):
        self.post_type = data.get("post_type")
        self.self_id = str(data.get("self_id"))
        self.time = data.get("time")
    
    def __getitem__(self, key):
        if key not in self.__dict__:
            raise KeyError(f"Ivalid key: {key}.")
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        if key not in self.__dict__:
            raise KeyError(f"Ivalid key: {key}.")
        self.__dict__[key] = value

    def __repr__(self):
        core_properties_str = self.get_core_properties_str()
        return f"{self.__class__.__name__}(({', '.join(core_properties_str)}))"
    
    def to_dict(self):
        result = {
            
        }
        for k, v in self.__dict__.items():
            if isinstance(v, Callable):
                continue
            if isinstance(v, MessageArray):
                result[k] = v.to_list()
            elif hasattr(v, "to_dict"):
                result[k] = v.to_dict()
            else:
                result[k] = v
        return result
    
    def __str__(self):
        return self.__repr__()
    
    def get_core_properties_str(self):
        return []
        
    
class MessageEventData(BaseEventData):
    message_type: Literal["private", "group"] = None
    sub_type: str = None # 下级会细化 Literal
    post_type: Literal["message"] = None # 上级会获取
    message_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    user_id: str = None # 和 OneBot11 标准不一致, 这里采取 str
    message: MessageArray = None
    raw_message: str = None
    sender: BaseSender = None
    
    def __init__(self, data: dict):
        super().__init__(data)
        self.message_type = data.get("message_type")
        self.sub_type = data.get("sub_type")
        self.message_id = str(data.get("message_id"))
        self.user_id = str(data.get("user_id"))
        self.message = MessageArray(data.get("message"))
        self.raw_message = data.get("raw_message")
        
    def get_core_properties_str(self):
        return super().get_core_properties_str() + [
            f"sub_type={self.sub_type}",
            f"message_id={self.message_id}",
            f"message={self.message}"
        ]
        
    
    