from typing import Literal
from ncatbot.core.message_segment.message_segment import MessageSegment

class MessageArray(list):
    messages: list[MessageSegment] = None
    def __init__(self, data: list[dict]):
        pass