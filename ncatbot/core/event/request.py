
from typing import Literal
from ncatbot.core.event.event_data import BaseEventData
from ncatbot.utils import status, get_log

LOG = get_log("ncatbot.core.event.request")

class RequestEvent(BaseEventData):
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
        if self.request_type == "friend":
            if reason is not None:
                LOG.warning("好友请求不支持拒绝理由")
            return await status.global_api.set_friend_add_request(self.flag, approve, remark)
        elif self.request_type == "group":
            if remark is not None:
                LOG.warning("加群请求不支持备注")
            return await status.global_api.set_group_add_request(self.flag, approve, reason)
    
    def approve_sync(self, approve: bool = True, remark: str = None, reason: str = None):
        if self.request_type == "friend":
            if reason is not None:
                LOG.warning("好友请求不支持拒绝理由")
            return status.global_api.set_friend_add_request_sync(self.flag, approve, remark)
        elif self.request_type == "group":
            if remark is not None:
                LOG.warning("加群请求不支持备注")
            return status.global_api.set_group_add_request_sync(self.flag, approve, reason)