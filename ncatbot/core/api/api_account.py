from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus, run_coroutine
from ncatbot.core.event.message_segment.message_segment import convert_uploadable_object
from dataclasses import dataclass

@dataclass
class LoginInfo:
    nickname: str
    user_id: str
    
class CustomFaceList:
    urls: list[str]
    def __init__(self, data: list[dict]):
        self.urls = [item["url"] for item in data]

class AccountAPI(BaseAPI):

    
    # ---------------------
    # region 账号相关
    # ---------------------
    async def set_qq_profile(self, nickname: str, personal_note: str, sex: Literal["未知", "男", "女"]) -> None:
        sex_id = str({"未知": 0, "男": 1, "女": 2}[sex])
        result = await self.async_callback("/set_qq_profile", {"nickname": nickname, "personal_note": personal_note, "sex": sex_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_online_status(self, status: int, ext_status: int, battary_status: int) -> None:
        result = await self.async_callback("/set_online_status", {"status": status, "ext_status": ext_status, "battary_status": battary_status})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_avatar(self, file: str) -> None:
        result = await self.async_callback("/set_avatar", {"file": convert_uploadable_object(file)})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_self_longnick(self, longNick: str) -> None:
        result = await self.async_callback("/set_self_longnick", {"longNick": longNick})
        APIReturnStatus.raise_if_failed(result)
    
    async def get_login_info(self) -> LoginInfo:
        result = await self.async_callback("/get_login_info")
        status = APIReturnStatus(result)
        
        return LoginInfo(**status.data)
    
    async def get_status(self) -> dict:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_status")
        status = APIReturnStatus(result)
        
        return status.data
    
    # ---------------------
    # region 好友
    # ---------------------
    
    async def get_friends_with_cat(self) -> list[dict]:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_friends_with_cat")
        status = APIReturnStatus(result)
        
        return status.data
    
    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None:
        result = await self.async_callback("/send_like", {"user_id": user_id, "times": times})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_friend_add_request(self, flag: str, approve: bool, remark: str = None) -> None:
        """设置通过好友请求

        Args:
            flag (str): 请求 flag
            approve (bool): 是否同意
            remark (str, optional): 通过后好友备注. Defaults to None.
        """
        result = await self.async_callback("/set_friend_add_request", {"flag": flag, "approve": approve, "remark": remark})
        APIReturnStatus.raise_if_failed(result)
    
    async def get_friend_list(self) -> list[dict]:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_friend_list")
        status = APIReturnStatus(result)
        
        return status.data

    async def delete_friend(self, user_id: Union[str, int], block: bool = True, both: bool = True) -> None:
        """删除好友
        Args:
            user_id (Union[str, int]): 目标用户 QQ 号
            block (bool, optional): 是否拉黑. Defaults to True.
            both (bool, optional): 是否双向删除. Defaults to True.
        """
        result = await self.async_callback("/delete_friend", {"user_id": user_id, "block": block, "both": both})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_friend_remark(self, user_id: Union[str, int], remark: str) -> None:
        result = await self.async_callback("/set_friend_remark", {"user_id": user_id, "remark": remark})
        APIReturnStatus.raise_if_failed(result)
    
    # ---------------------
    # region 消息
    # ---------------------

    async def mark_group_msg_as_read(self, group_id: Union[str, int]) -> None:
        result = await self.async_callback("/mark_group_msg_as_read", {"group_id": group_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def mark_private_msg_as_read(self, user_id: Union[str, int]) -> None:
        result = await self.async_callback("/mark_private_msg_as_read", {"user_id": user_id})
        APIReturnStatus.raise_if_failed(result)

    async def create_collection(self, rawData: str, brief: str) -> None:
        result = await self.async_callback("/create_collection", {"rawData": rawData, "brief": brief})
        APIReturnStatus.raise_if_failed(result)
        
    async def get_recent_contact(self) -> list[dict]:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_recent_contact")
        status = APIReturnStatus(result)
        
        return status.data
    
    async def _mark_all_as_read(self) -> None:
        result = await self.async_callback("/_mark_all_as_read")
        APIReturnStatus.raise_if_failed(result)
    

    # ---------------------
    # region 群
    # ---------------------
    
    async def AskShareGroup(self, group_id: Union[str, int]) -> None:
        result = await self.async_callback("/AskShareGroup", {"group_id": group_id})
        APIReturnStatus.raise_if_failed(result)
    
    
    # ---------------------
    # region 其它
    # ---------------------
    async def get_stranger_info(self, user_id: Union[str, int]) -> dict:
        """获取陌生人信息，接口暂不完善，有需求提 PR
        : 解析参考 https://napcat.apifox.cn/226656970e0
        """
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_stranger_info", {"user_id": user_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def fetch_custom_face(self, count: int = 48) -> CustomFaceList:
        result = await self.async_callback("/fetch_custom_face", {"count": count})
        status = APIReturnStatus(result)
        return CustomFaceList(status.data)
    
    async def nc_get_user_status(self, user_id: Union[str, int]) -> dict:
        result = await self.async_callback("/nc_get_user_status", {"user_id": user_id})
        status = APIReturnStatus(result)
        
        return status.data
    
    # ---------------------
    # region 同步版本接口
    # ---------------------
    
    def set_qq_profile_sync(self, nickname: str, personal_note: str, sex: Literal["未知", "男", "女"]) -> None:
        return run_coroutine(self.set_qq_profile, nickname, personal_note, sex)
    
    def set_online_status_sync(self, status: int, ext_status: int, battary_status: int) -> None:
        return run_coroutine(self.set_online_status, status, ext_status, battary_status)
    
    def set_avatar_sync(self, file: str) -> None:
        return run_coroutine(self.set_avatar, file)
    
    def set_self_longnick_sync(self, longNick: str) -> None:
        return run_coroutine(self.set_self_longnick, longNick)
    
    def get_login_info_sync(self) -> LoginInfo:
        return run_coroutine(self.get_login_info)
    
    def get_status_sync(self) -> dict:
        return run_coroutine(self.get_status)
    
    def get_friends_with_cat_sync(self) -> list[dict]:
        return run_coroutine(self.get_friends_with_cat)
    
    def send_like_sync(self, user_id: Union[str, int], times: int = 1) -> None:
        return run_coroutine(self.send_like, user_id, times)
    
    def set_friend_add_request_sync(self, flag: str, approve: bool, remark: str = None) -> None:
        return run_coroutine(self.set_friend_add_request, flag, approve, remark)
    
    def get_friend_list_sync(self) -> list[dict]:
        return run_coroutine(self.get_friend_list)

    def delete_friend_sync(self, user_id: Union[str, int], block: bool = True, both: bool = True) -> None:
        return run_coroutine(self.delete_friend, user_id, block, both)
    
    def set_friend_remark_sync(self, user_id: Union[str, int], remark: str) -> None:
        return run_coroutine(self.set_friend_remark, user_id, remark)
    
    def mark_group_msg_as_read_sync(self, group_id: Union[str, int]) -> None:
        return run_coroutine(self.mark_group_msg_as_read, group_id)
    
    def mark_private_msg_as_read_sync(self, user_id: Union[str, int]) -> None:
        return run_coroutine(self.mark_private_msg_as_read, user_id)

    def create_collection_sync(self, rawData: str, brief: str) -> None:
        return run_coroutine(self.create_collection, rawData, brief)
        
    def get_recent_contact_sync(self) -> list[dict]:
        return run_coroutine(self.get_recent_contact)
    
    def _mark_all_as_read_sync(self) -> None:
        return run_coroutine(self._mark_all_as_read)
    
    def AskShareGroup_sync(self, group_id: Union[str, int]) -> None:
        return run_coroutine(self.AskShareGroup, group_id)
    
    def get_stranger_info_sync(self, user_id: Union[str, int]) -> dict:
        return run_coroutine(self.get_stranger_info, user_id)
    
    def fetch_custom_face_sync(self, count: int = 48) -> CustomFaceList:
        return run_coroutine(self.fetch_custom_face, count)
    
    def nc_get_user_status_sync(self, user_id: Union[str, int]) -> dict:
        return run_coroutine(self.nc_get_user_status, user_id)

 
        