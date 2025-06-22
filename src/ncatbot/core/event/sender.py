from typing import Literal, Optional

class Sender:
    user_id: str = None # 用户 QQ 号, 需要手动转 str
    nickname: str = None # 用户 QQ 昵称
    card: Optional[str] = None # 用户群昵称
    sex: Optional[Literal["male", "female", "unknown"]] = None
    age: Optional[int] = None
    area: Optional[str] = None
    level: Optional[int] = None # 需要手动转 int
    role: Optional[Literal["owner", "admin", "member"]] = None
    title: Optional[str] = None
    def __init__(self, data: dict):
        for key, value in data.items():
            if key in self.__dict__:
                self.__dict__[key] = value
            else:
                pass
        self.user_id = str(self.user_id)
        if self.level is not None:
            self.level = int(self.level)
