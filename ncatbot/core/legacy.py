from ncatbot.core.event import GroupMessageEvent, PrivateMessageEvent
from ncatbot.core.event import MessageArray

class GroupMessage(GroupMessageEvent):
    pass

class PrivateMessage(PrivateMessageEvent):
    pass

class MessageChain(MessageArray):
    pass