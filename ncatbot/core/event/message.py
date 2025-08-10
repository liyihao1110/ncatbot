from typing import Union, Literal
from abc import abstractmethod
from ncatbot.core.event.event_data import MessageEventData
from ncatbot.utils import status
from ncatbot.core.event.sender import PrivateSender, GroupSender
class BaseMessageEvent(MessageEventData):
    message_type: Literal["private", "group"] = None # 上级会获取
    sub_type: str = None # 下级会细化 Literal, 上级会获取
    
    def is_group_msg(self):
        return hasattr(self, "group_id")
    
    @abstractmethod
    async def reply(self):
        pass
    
    def get_core_properties_str(self):
        return super().get_core_properties_str() + [
            f"sender={self.sender}",
        ]

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
    sender: GroupSender = None
    
    def __init__(self, data: dict):
        super().__init__(data)
        self.sender = GroupSender(data.get("sender"))
        self.anonymous = AnonymousMessage(data.get("anonymous")) if data.get("anonymous", None) else None
        self.group_id = str(data.get("group_id"))
    
    def get_core_properties_str(self):
        return super().get_core_properties_str() + [
            f"group_id={self.group_id}"
        ]
    
    async def delete(self):
        return await status.global_api.delete_msg(self.message_id)
    
    async def kick(self):
        return await status.global_api.set_group_kick(self.group_id, self.user_id)
    
    async def ban(self, ban_duration: int = 30):
        """禁言消息发送者(秒)
        """
        return await status.global_api.set_group_ban(self.group_id, self.user_id, ban_duration)
    
    async def reply(self, text: str=None, image: str=None):
        return await status.global_api.post_group_msg(self.group_id, self.message_id, text, image)

class PrivateMessageEvent(BaseMessageEvent):
    message_type: Literal["private"] = None # 上级会获取
    sub_type: Literal["friend", "group", "other"] # 上级会获取
    sender: PrivateSender = None
    
    def __init__(self, data: dict):
        super().__init__(data)
        self.sender = PrivateSender(data.get("sender"))
    
    async def reply(self, text: str=None, image: str=None):
        return await status.global_api.post_private_msg(self.user_id, text, image)
    
    def __repr__(self):
        return super().__repr__()
    

    
