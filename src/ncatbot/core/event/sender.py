from typing import Literal, Optional

class Sender:
    user_id: str = None # 用户 QQ 号
    nickname: str = None # 用户 QQ 昵称
    card: Optional[str] = None # 用户群昵称
    sex: Optional[Literal["male", "female", "unknown"]] = None
    age: Optional[int] = None
    area: Optional[str] = None
    level: Optional[int] = None
    role: Optional[Literal["owner", "admin", "member"]] = None
    title: Optional[str] = None
    def __init__(self, data: dict):
        pass