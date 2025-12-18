from typing import Union, Literal, TYPE_CHECKING
from abc import abstractmethod, ABC
from ...utils import status
from .sender import PrivateSender, GroupSender
from .event_data import MessageEventData

if TYPE_CHECKING:
    from .message_segment import MessageArray


class BaseMessageEvent(MessageEventData, ABC):
    message_type: Literal["private", "group"] = None  # 上级会获取
    sub_type: str = None  # 下级会细化 Literal, 上级会获取

    def is_group_msg(self):
        return hasattr(self, "group_id")

    @abstractmethod
    async def reply(self, *args, **kwargs):
        pass

    @abstractmethod
    def reply_sync(self, *args, **kwargs):
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
    message_type: Literal["group"] = None  # 上级会获取
    anonymous: Union[None, AnonymousMessage]
    group_id: str = None
    sub_type: Literal["normal", "anonymous", "notice"]  # 上级会获取
    sender: GroupSender = None

    def __init__(self, data: dict):
        super().__init__(data)
        self.sender = GroupSender(data.get("sender"))
        self.anonymous = (
            AnonymousMessage(data.get("anonymous"))
            if data.get("anonymous", None)
            else None
        )
        self.group_id = str(data.get("group_id"))

    def get_core_properties_str(self):
        return super().get_core_properties_str() + [f"group_id={self.group_id}"]

    async def delete(self):
        return await status.global_api.delete_msg(self.message_id)

    def delete_sync(self):
        return status.global_api.delete_msg_sync(self.message_id)

    async def kick(self):
        return await status.global_api.set_group_kick(self.group_id, self.user_id)

    def kick_sync(self):
        return status.global_api.set_group_kick_sync(self.group_id, self.user_id)

    async def ban(self, ban_duration: int = 30):
        """禁言消息发送者(秒)"""
        return await status.global_api.set_group_ban(
            self.group_id, self.user_id, ban_duration
        )

    def ban_sync(self, ban_duration: int = 30):
        return status.global_api.set_group_ban_sync(
            self.group_id, self.user_id, ban_duration
        )

    async def reply(
        self,
        text: str = None,
        image: str = None,
        at: bool = True,
        space: bool = True,
        rtf: "MessageArray" = None,
    ):
        if text is not None:
            text = (" " if space else "") + text
        return await status.global_api.post_group_msg(
            self.group_id,
            text,
            self.user_id if at else None,
            reply=self.message_id,
            image=image,
            rtf=rtf,
        )

    def reply_sync(
        self,
        text: str = None,
        image: str = None,
        at: bool = True,
        space: bool = True,
        rtf: "MessageArray" = None,
    ):
        if text is not None:
            text = (" " if space else "") + text
        return status.global_api.post_group_msg_sync(
            self.group_id,
            text,
            self.user_id if at else None,
            reply=self.message_id,
            image=image,
            rtf=rtf,
        )


class PrivateMessageEvent(BaseMessageEvent):
    message_type: Literal["private"] = None  # 上级会获取
    sub_type: Literal["friend", "group", "other"]  # 上级会获取
    sender: PrivateSender = None

    def __init__(self, data: dict):
        super().__init__(data)
        self.sender = PrivateSender(data.get("sender"))

    async def reply(
        self, text: str = None, image: str = None, rtf: "MessageArray" = None
    ):
        return await status.global_api.post_private_msg(
            self.user_id, text, self.message_id, image, rtf
        )

    def reply_sync(
        self, text: str = None, image: str = None, rtf: "MessageArray" = None
    ):
        return status.global_api.post_private_msg_sync(
            self.user_id, text, self.message_id, image, rtf
        )

    def __repr__(self):
        return super().__repr__()


class MessageSentEvent(BaseMessageEvent):
    message_type: Literal["group", "private"] = None  # 上级会获取
    sub_type: Literal["friend", "group", "other", "normal"] = None  # 上级会获取
    sender: Union[PrivateSender, GroupSender] = None
    message_sent_type: Literal["self"] = None
    target_id: str = None
    real_seq: str = None
    group_id: str = None

    def __init__(self, data: dict):
        super().__init__(data)
        self.message_sent_type = data.get("message_sent_type")
        self.target_id = str(data.get("target_id")) if data.get("target_id") else None
        self.real_seq = str(data.get("real_seq")) if data.get("real_seq") else None

        # 根据消息类型初始化不同的 Sender
        if self.message_type == "group":
            self.sender = GroupSender(data.get("sender"))
            self.group_id = str(data.get("group_id")) if data.get("group_id") else None
        elif self.message_type == "private":
            self.sender = PrivateSender(data.get("sender"))
        else:
            self.sender = data.get("sender")

    def is_group_msg(self):
        """
        判断是否为群组消息
        """
        return self.message_type == "group"

    def is_private_msg(self):
        """
        判断是否为私聊消息
        """
        return self.message_type == "private"

    def get_core_properties_str(self):
        """
        获取核心属性字符串表示
        """
        base_props = super().get_core_properties_str()
        if self.is_group_msg():
            base_props.append(f"group_id={self.group_id}")
        base_props.extend(
            [
                f"message_sent_type={self.message_sent_type}",
                f"target_id={self.target_id}",
            ]
        )
        return base_props

    async def reply(
        self, text: str = None, image: str = None, rtf: "MessageArray" = None
    ):
        if self.is_group_msg():
            return await status.global_api.post_group_msg(
                group_id=self.group_id,
                text=text,
                reply=self.message_id,
                image=image,
                rtf=rtf,
            )
        elif self.is_private_msg():
            return await status.global_api.post_private_msg(
                user_id=self.user_id,
                text=text,
                reply=self.message_id,
                image=image,
                rtf=rtf,
            )

    def reply_sync(
        self, text: str = None, image: str = None, rtf: "MessageArray" = None
    ):
        if self.is_group_msg():
            return status.global_api.post_group_msg_sync(
                group_id=self.group_id,
                text=text,
                reply=self.message_id,
                image=image,
                rtf=rtf,
            )
        elif self.is_private_msg():
            return status.global_api.post_private_msg_sync(
                user_id=self.user_id,
                text=text,
                reply=self.message_id,
                image=image,
                rtf=rtf,
            )

    async def delete(self):
        """
        撤回消息
        """
        return await status.global_api.delete_msg(self.message_id)

    def delete_sync(self):
        """
        撤回消息
        """
        return status.global_api.delete_msg_sync(self.message_id)

    def __repr__(self):
        return super().__repr__()
