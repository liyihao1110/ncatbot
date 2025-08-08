from typing import Literal, Optional
from dataclasses import dataclass

@dataclass()
class Sender:
    user_id: str = None # 用户 QQ 号, 需要手动转 str
    nickname: str = "QQ用户" # 用户 QQ 昵称
    card: Optional[str] = None # 用户群昵称
    sex: Optional[Literal["male", "female", "unknown"]] = None
    age: Optional[int] = None
    area: Optional[str] = None
    level: Optional[int] = None # 需要手动转 int
    role: Optional[Literal["owner", "admin", "member"]] = None
    title: Optional[str] = None
    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items() if v is not None
        }
    
    def __init__(self, data: dict):
        for key, value in data.items():
            self.__dict__[key] = value
            
        self.user_id = str(self.user_id)
        if self.level is not None:
            self.level = int(self.level)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.user_id}, {self.nickname})"

    def __str__(self):
        return self.__repr__()