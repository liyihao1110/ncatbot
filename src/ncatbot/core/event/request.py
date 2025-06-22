
from typing import Literal
from ncatbot.core.event.event_data import BaseEventData

class Request(BaseEventData):
    post_type: Literal["request"] = None
    request_type: Literal["friend", "group"] = None
    commnet: str = None # 验证信息
    flag: str = None # 验证 flag
    
    async def approve(self, approve: bool = True, remark: str = None, reason: str = None):
        """通过或者拒绝验证
        Args:
            approve (bool, optional): 是否通过. Defaults to True.
            remark (str, optional): 如果是好友请求, 此选项表示好友备注, 否则无效. Defaults to None.
            reason (str, optional): 如果是加群请求, 此选项表示拒绝理由, 否则无效. Defaults to None.
        """
        # 无效参数需要日志打警告
        if self.request_type == "friend":
            pass    
        elif self.request_type == "group":
            pass