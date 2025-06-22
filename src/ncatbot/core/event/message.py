from typing import Union, Literal
from abc import abstractmethod
from ncatbot.core.event.event_data import MessageEventData
from ncatbot.core.event.sender import Sender

class BaseMessageEvent(MessageEventData):
    sender: Sender = None
    message_type: Literal["private", "group"] = None # 上级会获取
    sub_type: str = None # 下级会细化 Literal, 上级会获取
    def __init__(self, data: dict):
        self.sender = Sender(data.get("sender"))
        super().__init__(data)
        
    @abstractmethod
    async def reply(self):
        pass

class AnonymousMessage(BaseMessageEvent):
    id: str = None
    name: str = None
    flag: str = None
    def __init__(self, data: dict):
        self.id = str(data.get("id"))
        self.name = data.get("name")
        self.flag = data.get("flag")
    

class GroupMessageEvent(BaseMessageEvent):
    message_type: Literal["group"] = None # 上级会获取
    anonymous: Union[None, AnonymousMessage]
    group_id: str = None
    sub_type: Literal["normal", "anonymous", "notice"] # 上级会获取
    def __init__(self, data: dict):
        super().__init__(data)
        self.anonymous = AnonymousMessage(data.get("anonymous")) if data.get("anonymous", None) else None
        self.group_id = str(data.get("group_id"))
        
    async def delete(self):
        pass
    
    async def kick(self):
        pass
    
    async def ban(self, ban_duration: int = 30):
        """禁言消息发送者
        Args:
            ban_duration (int, optional): 禁言时间(分钟). Defaults to 30.
        """
        pass
    
    async def reply(self):
        pass

class PrivateMessageEvent(BaseMessageEvent):
    message_type: Literal["private"] = None # 上级会获取
    sub_type: Literal["friend", "group", "other"] # 上级会获取
    async def reply(self):
        pass
    

    
