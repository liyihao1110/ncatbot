from typing import Literal, Optional
from ncatbot.core.event.event_data import BaseEventData
from ncatbot.utils import status, get_log

LOG = get_log("ncatbot.core.event.request")


class RequestEvent(BaseEventData):
    post_type: Literal["request"] = None
    request_type: Literal["friend", "group"] = None
    comment: str = None  # 验证信息
    flag: str = None  # 验证 flag
    group_id: Optional[str] = None
    user_id: Optional[str] = None

    def is_friend_request(self) -> bool:
        return self.request_type == "friend"

    def is_group_request(self) -> bool:
        return self.request_type == "group"

    async def approve(
        self, approve: bool = True, remark: str = None, reason: str = None
    ):
        """通过或者拒绝验证
        Args:
            approve (bool, optional): 是否通过. Defaults to True.
            remark (str, optional): 如果是好友请求, 此选项表示好友备注, 否则无效. Defaults to None.
            reason (str, optional): 如果是加群请求, 此选项表示拒绝理由, 否则无效. Defaults to None.
        """
        if self.request_type == "friend":
            if reason is not None:
                LOG.warning("好友请求不支持拒绝理由")
            return await status.global_api.set_friend_add_request(
                self.flag, approve, remark
            )
        elif self.request_type == "group":
            if remark is not None:
                LOG.warning("加群请求不支持备注")
            return await status.global_api.set_group_add_request(
                self.flag, approve, reason
            )

    def approve_sync(
        self, approve: bool = True, remark: str = None, reason: str = None
    ):
        if self.request_type == "friend":
            if reason is not None:
                LOG.warning("好友请求不支持拒绝理由")
            return status.global_api.set_friend_add_request_sync(
                self.flag, approve, remark
            )
        elif self.request_type == "group":
            if remark is not None:
                LOG.warning("加群请求不支持备注")
            return status.global_api.set_group_add_request_sync(
                self.flag, approve, reason
            )

    def __init__(self, data):
        super().__init__(data)
        _group_id = data.get("group_id", None)
        _user_id = data.get("user_id", None)
        self.request_type = data.get("request_type")
        self.comment = data.get("comment")
        self.flag = data.get("flag")
        self.group_id = str(_group_id) if _group_id is not None else None
        self.user_id = str(_user_id) if _user_id is not None else None
