from ncatbot.core.event.event_data import BaseEventData
from typing import Literal, Optional

class File:
    id: str = None
    name: str = None
    size: str = None
    busid: str = None
    
class NoticeEvent(BaseEventData):
    # 保留细化能力
    post_type: Literal["notice"] = None
    notice_type: Literal["group_upload", "group_admin", "group_decrease", "group_increase", "friend_add", "group_recall", "group_ban", "notify"] = None
    sub_type: Literal["set", "unset", "leave", "kick", "kick_me", "approve", "invite", "ban", "lift_ban", "poke", "lucky_king", "honor"] = None
    group_id: int = None
    user_id: int = None
    file: Optional[File] = None # group_upload
    operator_id: Optional[str] = None # group_decrease, group_increase, group_ban, group_recall
    duration: Optional[int] = None # group_ban
    message_id: Optional[str] = None # group_recall, friend_recall
    target_id: Optional[str] = None # notify.poke, notify.lucky_king
    honor_type: Optional[Literal["talkative", "performer", "emotion"]] # notify.honor
    