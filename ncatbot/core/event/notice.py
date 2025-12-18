from .event_data import BaseEventData
from typing import Literal, Optional


class File:
    id: str = None
    name: str = None
    size: str = None
    busid: str = None


class NoticeEvent(BaseEventData):
    # 保留细化能力
    post_type: Literal["notice"] = None
    time: int = None
    self_id: str = None  # 和 OneBot11 标准不一致, 这里采取 str
    notice_type: Literal[
        "group_upload",
        "group_admin",
        "group_decrease",
        "group_increase",
        "friend_add",
        "group_recall",
        "group_ban",
        "notify",
        "group_msg_emoji_like",
    ] = None
    sub_type: Literal[
        "set",
        "unset",
        "leave",
        "kick",
        "kick_me",
        "approve",
        "invite",
        "ban",
        "lift_ban",
        "poke",
        "lucky_king",
        "honor",
    ] = None
    group_id: str = None
    user_id: str = None
    file: Optional[File] = None  # group_upload
    operator_id: Optional[str] = (
        None  # group_decrease, group_increase, group_ban, group_recall
    )
    raw_info: Optional[dict] = None  # notify
    duration: Optional[int] = None  # group_ban
    card_old: Optional[str] = None  # group_increase
    card_new: Optional[str] = None  # group_increase
    message_id: Optional[str] = None  # group_recall, friend_recall
    target_id: Optional[str] = None  # notify.poke, notify.lucky_king
    honor_type: Optional[Literal["talkative", "performer", "emotion"]] = (
        None  # notify.honor
    )
    emoji_like_id: Optional[str] = None  # group_msg_emoji_like
    is_add: Optional[bool] = None  # group_msg_emoji_like

    def __init__(self, data):
        super().__init__(data)
        # 确保group_id、user_id和target_id转换为字符串类型，保持与MessageEventData一致
        if "group_id" in data and data["group_id"] is not None:
            self.group_id = str(data["group_id"])
        if "user_id" in data and data["user_id"] is not None:
            self.user_id = str(data["user_id"])
        if "target_id" in data and data["target_id"] is not None:
            self.target_id = str(data["target_id"])
        if "message_id" in data and data["message_id"] is not None:
            self.message_id = str(data["message_id"])
        if (
            "likes" in data
            and isinstance(data["likes"], list)
            and len(data["likes"]) == 1
            and isinstance(data["likes"][0], dict)
            and data["likes"][0].get("emoji_id") is not None
        ):
            self.emoji_like_id = str(data["likes"][0]["emoji_id"])

        # 处理其他字段
        for k, v in data.items():
            if k not in [
                "group_id",
                "user_id",
                "target_id",
                "message_id",
                "self_id",
                "likes",
            ]:  # 跳过已处理的字段
                setattr(self, k, v)

    def get_core_properties_str(self):
        core_properties = []
        for k, v in self.__dict__.items():
            if v is not None:
                core_properties.append(f"{k}={v}")
        core_properties.remove("post_type=notice")
        core_properties.remove(f"time={self.time}")
        core_properties.remove(f"self_id={self.self_id}")
        return core_properties

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(self.get_core_properties_str())})"

    def __str__(self):
        return self.__repr__()
