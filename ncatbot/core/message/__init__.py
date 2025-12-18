# 3xx 兼容层

from ..event import MessageArray as MessageChain
from ..event import GroupMessageEvent as GroupMessage
from ..event import PrivateMessageEvent as PrivateMessage
from ..event import BaseMessageEvent as BaseMessage

__all__ = [
    "MessageChain",
    "GroupMessage",
    "PrivateMessage",
    "BaseMessage",
]
