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
    group_id: int = None
    user_id: int = None
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

    def __init__(self, data):
        super().__init__(data)
        for k, v in data.items():
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
