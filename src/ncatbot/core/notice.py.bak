import json
from typing import List, Dict, Any, Optional

# 定义 Sender 类
class Sender:
    def __init__(self, data: Dict[str, Any]):
        self.user_id: int = data.get("user_id", None)
        self.nickname: str = data.get("nickname", None)
        self.card: str = data.get("card", None)
        self.sex: str = data.get("sex", None)
        self.age: int = data.get("age", None)
        self.area: str = data.get("area", None)
        self.level: str = data.get("level", None)
        self.title: str = data.get("title", None)
        self.role: str = data.get("role", None)

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 Anonymous 类
class Anonymous:
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data.get("id", None)
        self.name: str = data.get("name", None)
        self.flag: str = data.get("flag", None)

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 File 类（新增）
class File:
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", None)
        self.name: str = data.get("name", None)
        self.size: int = data.get("size", None)
        self.busid: int = data.get("busid", None)
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 GroupMessage 类
class GroupMessage:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = data.get("time", None)
        self.self_id: int = data.get("self_id", None)
        self.post_type: str = data.get("post_type", None)
        self.message_type: str = data.get("message_type", None)
        self.sub_type: str = data.get("sub_type", None)
        self.message_id: int = data.get("message_id", None)
        self.group_id: int = data.get("group_id", None)
        self.user_id: int = data.get("user_id", None)
        self.anonymous: Anonymous = Anonymous(data.get("anonymous", {}))
        self.message: List[Message] = [Message(msg) for msg in data.get("message", []) if isinstance(msg, dict)]
        self.raw_message: str = data.get("raw_message", None)
        self.font: int = data.get("font", None)
        self.sender: Sender = Sender(data.get("sender", {}))
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 Message 类
class Message:
    def __init__(self, data: Dict[str, Any]):
        self.type: str = data.get("type", None)
        self.data: Dict[str, Any] = data.get("data", {})

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 PrivateMessage 类
class PrivateMessage:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = data.get("time", None)
        self.self_id: int = data.get("self_id", None)
        self.post_type: str = data.get("post_type", None)
        self.message_type: str = data.get("message_type", None)
        self.sub_type: str = data.get("sub_type", None)
        self.message_id: int = data.get("message_id", None)
        self.user_id: int = data.get("user_id", None)
        self.message: List[Message] = [Message(msg) for msg in data.get("message", []) if isinstance(msg, dict)]
        self.raw_message: str = data.get("raw_message", None)
        self.font: int = data.get("font", None)
        self.sender: Sender = Sender(data.get("sender", {}))
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 NoticeMessage 类（新增）
class NoticeMessage:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = data.get("time", None)
        self.self_id: int = data.get("self_id", None)
        self.post_type: str = data.get("post_type", None)
        self.notice_type: str = data.get("notice_type", None)
        
        # 公共字段初始化
        self.group_id: Optional[int] = None
        self.user_id: Optional[int] = None
        self.sub_type: Optional[str] = None
        self.file: Optional[File] = None
        self.operator_id: Optional[int] = None
        self.duration: Optional[int] = None
        self.target_id: Optional[int] = None
        self.honor_type: Optional[str] = None
        self.message_id: Optional[int] = None
        
        # 根据不同的 notice_type 处理字段
        if self.notice_type == "group_upload":
            self.group_id = data.get("group_id")
            self.user_id = data.get("user_id")
            self.file = File(data.get("file", {}))
        elif self.notice_type == "group_admin":
            self.sub_type = data.get("sub_type")
            self.group_id = data.get("group_id")
            self.user_id = data.get("user_id")
        elif self.notice_type == "group_decrease":
            self.sub_type = data.get("sub_type")
            self.group_id = data.get("group_id")
            self.operator_id = data.get("operator_id")
            self.user_id = data.get("user_id")
        elif self.notice_type == "group_increase":
            self.sub_type = data.get("sub_type")
            self.group_id = data.get("group_id")
            self.operator_id = data.get("operator_id")
            self.user_id = data.get("user_id")
        elif self.notice_type == "group_ban":
            self.sub_type = data.get("sub_type")
            self.group_id = data.get("group_id")
            self.operator_id = data.get("operator_id")
            self.user_id = data.get("user_id")
            self.duration = data.get("duration")
        elif self.notice_type == "friend_add":
            self.user_id = data.get("user_id")
        elif self.notice_type == "group_recall":
            self.group_id = data.get("group_id")
            self.user_id = data.get("user_id")
            self.operator_id = data.get("operator_id")
            self.message_id = data.get("message_id")
        elif self.notice_type == "friend_recall":
            self.user_id = data.get("user_id")
            self.message_id = data.get("message_id")
        elif self.notice_type == "notify":
            self.sub_type = data.get("sub_type")
            if self.sub_type == "poke":
                self.group_id = data.get("group_id")
                self.user_id = data.get("user_id")
                self.target_id = data.get("target_id")
            elif self.sub_type == "lucky_king":
                self.group_id = data.get("group_id")
                self.user_id = data.get("user_id")
                self.target_id = data.get("target_id")
            elif self.sub_type == "honor":
                self.group_id = data.get("group_id")
                self.user_id = data.get("user_id")
                self.honor_type = data.get("honor_type")
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 RequestMessage 类（新增）
class RequestMessage:
    def __init__(self, data: Dict[str, Any]):
        self.time: int = data.get("time", None)
        self.self_id: int = data.get("self_id", None)
        self.post_type: str = data.get("post_type", None)
        self.request_type: str = data.get("request_type", None)
        self.user_id: int = data.get("user_id", None)
        self.comment: str = data.get("comment", None)
        self.flag: str = data.get("flag", None)
        
        # 处理特定类型的字段
        self.sub_type: Optional[str] = None
        self.group_id: Optional[int] = None
        
        if self.request_type == "group":
            self.sub_type = data.get("sub_type")
            self.group_id = data.get("group_id")
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

# 定义 parse_message 函数（修正逻辑错误）
def parse_message(raw: str):
    try:
        data = json.loads(raw)
        post_type = data.get("post_type")
        if post_type == "message":
            message_type = data.get("message_type")
            if message_type == "group":
                return GroupMessage(data)
            elif message_type == "private":
                return PrivateMessage(data)
        elif post_type == "notice":
            return NoticeMessage(data)
        elif post_type == "request":
            return RequestMessage(data)
        return None
    except json.JSONDecodeError:
        return None