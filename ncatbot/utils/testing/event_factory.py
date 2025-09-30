import time
import uuid
from typing import Union, Optional
from ncatbot.core.event import (
    GroupMessageEvent,
    PrivateMessageEvent,
    NoticeEvent,
    RequestEvent,
)
from ncatbot.core.event.message_segment import MessageArray, Text


class EventFactory:
    """事件工厂类，用于创建标准化的测试事件"""

    @staticmethod
    def _generate_message_id() -> str:
        """生成唯一消息 ID"""
        return str(int(time.time() * 1000000) + hash(str(uuid.uuid4())) % 10000)

    @staticmethod
    def _get_current_timestamp() -> int:
        """获取当前时间戳"""
        return int(time.time())

    @staticmethod
    def create_group_message(
        message: Union[str, MessageArray],
        group_id: str = "123456789",
        user_id: str = "987654321",
        nickname: str = "TestUser",
        card: Optional[str] = None,
        role: str = "member",
        self_id: str = "123456789",
        message_id: Optional[str] = None,
        **kwargs,
    ) -> GroupMessageEvent:
        """创建群聊消息事件

        Args:
            message: 消息内容，可以是字符串或 MessageArray
            group_id: 群号
            user_id: 发送者 QQ 号
            nickname: 发送者昵称
            card: 群昵称（可选）
            role: 群角色 ("member", "admin", "owner")
            self_id: 机器人 QQ 号
            message_id: 消息 ID（可选，自动生成）
        """
        if isinstance(message, str):
            message_array = MessageArray(Text(message))
            raw_message = message
        else:
            message_array = message
            raw_message = "".join(
                [
                    seg.text if hasattr(seg, "text") else f"[{seg.msg_seg_type}]"
                    for seg in message_array.messages
                ]
            )

        sender_data = {
            "user_id": user_id,
            "nickname": nickname,
            "card": card or nickname,
            "role": role,
        }

        event_data = {
            "post_type": "message",
            "message_type": "group",
            "sub_type": "normal",
            "message_id": message_id or EventFactory._generate_message_id(),
            "group_id": group_id,
            "user_id": user_id,
            "message": message_array.to_list(),
            "raw_message": raw_message,
            "sender": sender_data,
            "self_id": self_id,
            "time": EventFactory._get_current_timestamp(),
            **kwargs,
        }

        return GroupMessageEvent(event_data)

    @staticmethod
    def create_private_message(
        message: Union[str, MessageArray],
        user_id: str = "987654321",
        nickname: str = "TestUser",
        self_id: str = "123456789",
        message_id: Optional[str] = None,
        sub_type: str = "friend",
        **kwargs,
    ) -> PrivateMessageEvent:
        """创建私聊消息事件"""
        if isinstance(message, str):
            message_array = MessageArray(Text(message))
            raw_message = message
        else:
            message_array = message
            raw_message = "".join(
                [
                    seg.text if hasattr(seg, "text") else f"[{seg.msg_seg_type}]"
                    for seg in message_array.messages
                ]
            )

        sender_data = {"user_id": user_id, "nickname": nickname}

        event_data = {
            "post_type": "message",
            "message_type": "private",
            "sub_type": sub_type,
            "message_id": message_id or EventFactory._generate_message_id(),
            "user_id": user_id,
            "message": message_array.to_list(),
            "raw_message": raw_message,
            "sender": sender_data,
            "self_id": self_id,
            "time": EventFactory._get_current_timestamp(),
            **kwargs,
        }

        return PrivateMessageEvent(event_data)

    @staticmethod
    def create_notice_event(
        notice_type: str,
        user_id: str = "987654321",
        group_id: Optional[str] = None,
        self_id: str = "123456789",
        sub_type: Optional[str] = None,
        **kwargs,
    ) -> NoticeEvent:
        """创建通知事件"""
        event_data = {
            "post_type": "notice",
            "notice_type": notice_type,
            "user_id": user_id,
            "self_id": self_id,
            "time": EventFactory._get_current_timestamp(),
            **kwargs,
        }

        if group_id:
            event_data["group_id"] = group_id
        if sub_type:
            event_data["sub_type"] = sub_type

        return NoticeEvent(event_data)

    @staticmethod
    def create_request_event(
        request_type: str,
        user_id: str = "987654321",
        flag: str = "test_flag",
        self_id: str = "123456789",
        sub_type: Optional[str] = None,
        **kwargs,
    ) -> RequestEvent:
        """创建请求事件"""
        event_data = {
            "post_type": "request",
            "request_type": request_type,
            "user_id": user_id,
            "flag": flag,
            "self_id": self_id,
            "time": EventFactory._get_current_timestamp(),
            **kwargs,
        }

        if sub_type:
            event_data["sub_type"] = sub_type

        return RequestEvent(event_data)
