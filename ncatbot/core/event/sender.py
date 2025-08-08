from typing import Literal, Optional
from dataclasses import dataclass

@dataclass()
class BaseSender:
    user_id: str = None # 用户 QQ 号, 需要手动转 str
    nickname: str = "QQ用户" # 用户 QQ 昵称
    # card: Optional[str] = None # 用户群昵称
    # sex: Optional[Literal["male", "female", "unknown"]] = None
    # age: Optional[int] = None
    # area: Optional[str] = None
    # level: Optional[int] = None # 需要手动转 int
    # role: Optional[Literal["owner", "admin", "member"]] = None
    # title: Optional[str] = None
    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items() if v is not None
        }
    
    def __init__(self, data: dict):
        for key, value in data.items():
            self.__dict__[key] = value
            
        self.user_id = str(self.user_id)
    
    def __repr__(self):
        return f"{self.__class__.__name__}" + "({" + ", ".join([f"\"{k}\":\"{v}\"" for k, v in self.__dict__.items() if v is not None]) + "})"

    def __str__(self):
        return self.__repr__()

class PrivateSender(BaseSender):
    pass

class GroupSender(BaseSender):
    card: Optional[str] = None # 用户群昵称
    # sex: Optional[Literal["male", "female", "unknown"]] = None
    # age: Optional[int] = None
    # area: Optional[str] = None
    level: Optional[int] = None # 需要手动转 int
    role: Optional[Literal["owner", "admin", "member"]] = None
    title: Optional[str] = None
    
    def __init__(self, data: dict):
        super().__init__(data)
        self.card = data.get("card")
        self.level = int(data.get("level")) if data.get("level") else None