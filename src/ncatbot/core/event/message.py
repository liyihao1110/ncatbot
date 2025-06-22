from typing import Union, Literal
from abc import abstractmethod
from ncatbot.core.event.event_data import MessageEventData
from ncatbot.core.event.sender import Sender

class BaseMessage(MessageEventData):
    sender: Sender = None
    @abstractmethod
    async def reply(self):
        pass

class AnonymousMessage(BaseMessage):
    id: str = None
    name: str = None
    flag: str = None
    

class GroupMessage(BaseMessage):
    message_type: Literal["group"] = None
    anonymous: Union[None, AnonymousMessage]
    group_id: str = None
    sub_type: Literal["normal", "anonymous", "notice"]
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

class PrivateMessage(BaseMessage):
    message_type: Literal["private"] = None
    sub_type: Literal["friend", "group", "other"]
    async def reply(self):
        pass
    

    
