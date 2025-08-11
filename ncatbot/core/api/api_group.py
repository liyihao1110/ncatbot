from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus, run_coroutine
from ncatbot.core.event import File
from dataclasses import dataclass
import time

class UserInfo:
    def __init__(self, user_dict):
        self._data = user_dict
        self.user_id = user_dict['user_id']
        self.nickname = user_dict['nickname']
        self.avatar = user_dict['avatar']
        self.description = user_dict['description']

class GroupChatActivity:
    def __init__(self, data_dict):
        self._data = data_dict
        self.group_id = data_dict['group_id']
        self.current_talkative = UserInfo(data_dict['current_talkative'])
        self.talkative_list = [UserInfo(user) for user in data_dict['talkative_list']]
        self.performer_list = [UserInfo(user) for user in data_dict.get('performer_list', [])]
        self.legend_list = [UserInfo(user) for user in data_dict.get('legend_list', [])]
        self.emotion_list = [UserInfo(user) for user in data_dict.get('emotion_list', [])]
        self.strong_newbie_list = [UserInfo(user) for user in data_dict.get('strong_newbie_list', [])]

@dataclass
class GroupInfo:
    group_all_shut: bool
    group_remark: str
    group_id: int
    group_name: str
    member_count: int
    max_member_count: int

@dataclass
class GroupMemberInfo:
    group_id: int
    user_id: int
    nickname: str
    card: str
    sex: Literal["male", "female"]
    age: int
    area: str
    level: str
    qq_level: int
    join_time: int
    last_sent_time: int
    title_expire_time: int
    unfriendly: bool
    card_changeable: bool
    is_robot: bool
    shut_up_timestamp: int
    role: Literal["admin", "owner", "member"]
    title: str

    @classmethod
    def from_shut_list_dict(cls, shut_list_dict: dict) -> "GroupMemberInfo":
        # 从原始数据中提取并转换字段
        role_mapping = {
            2: "admin",
            3: "owner",
            1: "member"
        }
        
        # 处理性别字段，原始数据中可能没有这个字段
        sex = shut_list_dict.get('sex', 'unknown')
        if isinstance(sex, int):
            sex = 'male' if sex == 1 else 'female' if sex == 2 else 'unknown'
        
        # 构造GroupMemberInfo对象
        return cls(
            group_id=int(shut_list_dict.get('group_id', 0)),
            user_id=int(shut_list_dict.get('uin', shut_list_dict.get('user_id', 0))),
            nickname=shut_list_dict.get('nick', ''),
            card=shut_list_dict.get('cardName', shut_list_dict.get('nick', '')),
            sex=sex,
            age=int(shut_list_dict.get('age', 0)),
            area=shut_list_dict.get('area', ''),
            level=str(shut_list_dict.get('memberLevel', '')),
            qq_level=int(shut_list_dict.get('qq_level', 0)),
            join_time=int(shut_list_dict.get('joinTime', 0)),
            last_sent_time=int(shut_list_dict.get('lastSpeakTime', 0)),
            title_expire_time=int(shut_list_dict.get('specialTitleExpireTime', 0)),
            unfriendly=bool(shut_list_dict.get('unfriendly', False)),
            card_changeable=bool(shut_list_dict.get('card_changeable', True)),
            is_robot=bool(shut_list_dict.get('isRobot', False)),
            shut_up_timestamp=int(shut_list_dict.get('shutUpTime', 0)),
            role=role_mapping.get(shut_list_dict.get('memberLevel', 1), 'member'),
            title=shut_list_dict.get('memberSpecialTitle', '')
        )
       

class GroupMemberList:
    def __init__(self, data: list[dict]):
        self.members = [GroupMemberInfo(**item) for item in data]
    
    @classmethod
    def from_shut_list(cls, shut_list_dict: list[dict]) -> "GroupMemberList":
        obj = cls([])
        for item in shut_list_dict:
            obj.members.append(GroupMemberInfo.from_shut_list_dict(item))
        return obj
    
    @property
    def member_count(self) -> int:
        return len(self.members)
    
    def filter_by_another_list_not_in(self, another_list: "GroupMemberList") -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member not in another_list.members])

    def filter_by_level_ge(self, level: int) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.level >= level])
    
    def filter_by_level_le(self, level: int) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.level <= level])
    
    def filter_by_last_sent_time_upto_now(self, seconds: int) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.last_sent_time > time.time() - seconds])
    
    def filter_by_role(self, role: Literal["admin", "owner", "member"]) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.role == role])
    
    def filter_by_role_not_in(self, roles: list[Literal["admin", "owner", "member"]]) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.role not in roles])
    
    def filter_by_have_title(self) -> "GroupMemberList":
        return GroupMemberList([member for member in self.members if member.title])
    
    def __repr__(self) -> str:
        return f"GroupMemberList(members={self.members})"

class GroupAPI(BaseAPI):
    # ---------------------
    # region 群成员管理
    # ---------------------    
    async def set_group_kick_members(self, group_id: Union[str, int], user_id: Union[str, int], reject_add_request: bool = False) -> None:
        result = await self.async_callback("/set_group_kick_members", {"group_id": group_id, "user_id": user_id, "reject_add_request": reject_add_request})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_kick(self, group_id: Union[str, int], user_id: Union[str, int], reject_add_request: bool = False) -> None:
        result = await self.async_callback("/set_group_kick", {"group_id": group_id, "user_id": user_id, "reject_add_request": reject_add_request})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_ban(self, group_id: Union[str, int], user_id: Union[str, int], duration: int = 30 * 60) -> None:
        """设置群禁言

        Args:
            duration (int, optional): 禁言秒数. Defaults to 30*60.
        """
        result = await self.async_callback("/set_group_ban", {"group_id": group_id, "user_id": user_id, "duration": duration})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_whole_ban(self, group_id: Union[str, int], enable: bool) -> None:
        result = await self.async_callback("/set_group_whole_ban", {"group_id": group_id, "enable": enable})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_admin(self, group_id: Union[str, int], user_id: Union[str, int], enable: bool) -> None:
        result = await self.async_callback("/set_group_admin", {"group_id": group_id, "user_id": user_id, "enable": enable})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_leave(self, group_id: Union[str, int], is_dismiss: bool = False) -> None:
        result = await self.async_callback("/set_group_leave", {"group_id": group_id, "is_dismiss": is_dismiss})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_special_title(self, group_id: Union[str, int], user_id: Union[str, int], special_title: str = "") -> None:
        result = await self.async_callback("/set_group_special_title", {"group_id": group_id, "user_id": user_id, "special_title": special_title})
        APIReturnStatus.raise_if_failed(result)
        
    async def set_group_add_request(self, flag: str, approve: bool, reason: str = None) -> None:
        result = await self.async_callback("/set_group_add_request", {"flag": flag, "approve": approve, "reason": reason})
        APIReturnStatus.raise_if_failed(result)

    async def set_group_card(self, group_id: Union[str, int], user_id: Union[str, int], card: str = "") -> None:
        """改群友的群昵称"""
        result = await self.async_callback("/set_group_card", {"group_id": group_id, "user_id": user_id, "card": card})
        APIReturnStatus.raise_if_failed(result)

    # --------------
    # region 群消息管理
    # --------------
    
    async def set_essence_msg(self, message_id: Union[str, int]) -> None:
        result = await self.async_callback("/set_essence_msg", {"message_id": message_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def delete_essence_msg(self, message_id: Union[str, int]) -> None:
        result = await self.async_callback("/delete_essence_msg", {"message_id": message_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def get_group_essence_msg(self, group_id: Union[str, int]) -> list[dict]:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_group_essence_msg", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    


    # --------------
    # region 群文件
    # --------------
    async def post_group_file(self, group_id: Union[str, int], image: str = None, record: str=None, video: str=None, file: str=None) -> str:
        count = sum(1 for arg in [image, record, video, file] if arg is not None)
        if count != 1:
            raise ValueError("只能上传一个文件")
        if image is not None:
            return await self.send_group_image(group_id, image)
        elif record is not None:
            return await self.send_group_record(group_id, record)
        elif video is not None:
            return await self.send_group_video(group_id, video)
        elif file is not None:
            return await self.send_group_file(group_id, file)
    
    async def move_group_file(self, group_id: Union[str, int], file_id: str, current_parent_directory: str, target_parent_directory: str) -> None:
        result = await self.async_callback("/move_group_file", {"group_id": group_id, "file_id": file_id, "current_parent_directory": current_parent_directory, "target_parent_directory": target_parent_directory})
        APIReturnStatus.raise_if_failed(result)
    
    async def trans_group_file(self, group_id: Union[str, int], file_id: str) -> None:
        """转存为永久文件"""
        result = await self.async_callback("/trans_group_file", {"group_id": group_id, "file_id": file_id})
        APIReturnStatus.raise_if_failed(result)
        
    async def rename_group_file(self, group_id: Union[str, int], file_id: str, new_name: str) -> None:
        result = await self.async_callback("/rename_group_file", {"group_id": group_id, "file_id": file_id, "new_name": new_name})
        APIReturnStatus.raise_if_failed(result)
        
    async def get_file(self, file_id: str, file: str) -> File:
        result = await self.async_callback("/get_file", {"file_id": file_id, "file": file})
        status = APIReturnStatus(result)
        
        return File(status.data)

    async def upload_group_file(self, group_id: Union[str, int], file: str, name: str, folder) -> str:
        """上传群文件"""
        result = await self.async_callback("/upload_group_file", {"group_id": group_id, "file": file, "name": name, "folder": folder})
        APIReturnStatus.raise_if_failed(result)        

    async def create_group_file_folder(self, group_id: Union[str, int], folder_name: str) -> None:
        """创建群文件文件夹"""
        result = await self.async_callback("/create_group_file_folder", {"group_id": group_id, "folder_name": folder_name})
        APIReturnStatus.raise_if_failed(result)
    
    async def group_file_folder_makedir(self, group_id: Union[str, int], path: str) -> str:
        # 自定义函数, 按照路径创建群文件夹
        pass
    
    async def delete_group_file(self, group_id: Union[str, int], file_id: str) -> None:
        """删除群文件"""
        result = await self.async_callback("/delete_group_file", {"group_id": group_id, "file_id": file_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def delete_group_folder(self, group_id: Union[str, int], folder_id: str) -> None:
        result = await self.async_callback("/delete_group_folder", {"group_id": group_id, "folder_id": folder_id})
        APIReturnStatus.raise_if_failed(result)
        
    async def get_group_root_files(self, group_id: Union[str, int], file_count: int = 50) -> dict:
        result = await self.async_callback("/get_group_root_files", {"group_id": group_id, "file_count": file_count})
        # TODO: 规范化返回方式
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_files_by_folder(self, group_id: Union[str, int], folder_id: str, file_count: int = 50) -> dict:
        result = await self.async_callback("/get_group_files_by_folder", {"group_id": group_id, "folder_id": folder_id, "file_count": file_count})
        # TODO: 规范化返回方式
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_file_url(self, group_id: Union[str, int], file_id: str) -> str:
        result = await self.async_callback("/get_group_file_url", {"group_id": group_id, "file_id": file_id})
        status = APIReturnStatus(result)
        return status.data.get("url")
    
    # --------------
    # region 其它(用户功能)
    # --------------
    async def get_group_honor_info(self, group_id: Union[str, int], type: Literal["talkative", "performer", "legend", "emotion", "all"]) -> GroupChatActivity:
        result = await self.async_callback("/get_group_honor_info", {"group_id": group_id, "type": type})
        status = APIReturnStatus(result)
        return GroupChatActivity(status.data)

    async def get_group_info(self, group_id: Union[str, int]) -> GroupInfo:
        result = await self.async_callback("/get_group_info", {"group_id": group_id})
        status = APIReturnStatus(result)
        return GroupInfo(**status.data)
    
    async def get_group_info_ex(self, group_id: Union[str, int]) -> dict:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/get_group_info_ex", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_member_info(self, group_id: Union[str, int], user_id: Union[str, int]) -> GroupMemberInfo:
        result = await self.async_callback("/get_group_member_info", {"group_id": group_id, "user_id": user_id})
        status = APIReturnStatus(result)
        return GroupMemberInfo(**status.data)
    
    async def get_group_member_list(self, group_id: Union[str, int]) -> GroupMemberList:
        result = await self.async_callback("/get_group_member_list", {"group_id": group_id})
        status = APIReturnStatus(result)
        return GroupMemberList(status.data)
    
    async def get_group_shut_list(self, group_id: Union[str, int]) -> GroupMemberList:
        result = await self.async_callback("/get_group_shut_list", {"group_id": group_id})
        status = APIReturnStatus(result)
        return GroupMemberList.from_shut_list(status.data)
    
    async def set_group_remark(self, group_id: Union[str, int], remark: str) -> None:
        result = await self.async_callback("/set_group_remark", {"group_id": group_id, "remark": remark})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_sign(self, group_id: Union[str, int]) -> None:
        """群签到"""
        result = await self.async_callback("/set_group_sign", {"group_id": group_id})
        APIReturnStatus.raise_if_failed(result)

    async def send_group_sign(self, group_id: Union[str, int]) -> None:
        result = await self.async_callback("/send_group_sign", {"group_id": group_id})
        APIReturnStatus.raise_if_failed(result)
    
    # --------------
    # region 其它(管理员功能)
    # --------------
    async def set_group_avatar(self, group_id: Union[str, int], file: str) -> None:
        """设置群头像 
        Args:
            file (str): 文件路径（只支持 url）
        """
        # TODO: 支持本地文件
        result = await self.async_callback("/set_group_avatar", {"group_id": group_id, "file": file})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_group_name(self, group_id: Union[str, int], name: str) -> None:
        """设置群名"""
        result = await self.async_callback("/set_group_name", {"group_id": group_id, "name": name})
        APIReturnStatus.raise_if_failed(result)

    async def _send_group_notice(self, group_id: Union[str, int], content: str, confirm_required: bool = False, image: str = None, is_show_edit_card: bool = False, pinned: bool = False) -> None:
        """发送群公告
        """
        # TODO: 测试
        confirm_required = 1 if confirm_required else 0
        is_show_edit_card = 1 if is_show_edit_card else 0
        pinned = 1 if pinned else 0
        tip_window_type = 0
        type = 0
        result = await self.async_callback("/send_group_notice", {"group_id": group_id, "content": content, "confirm_required": confirm_required, "image": image, "is_show_edit_card": is_show_edit_card, "pinned": pinned, "tip_window_type": tip_window_type, "type": type})
        APIReturnStatus.raise_if_failed(result)

    # ---------------------
    # region 同步版本接口
    # ---------------------
    
    def set_group_kick_members_sync(self, group_id: Union[str, int], user_id: Union[str, int], reject_add_request: bool = False) -> None:
        return run_coroutine(self.set_group_kick_members, group_id, user_id, reject_add_request)
    
    def set_group_kick_sync(self, group_id: Union[str, int], user_id: Union[str, int], reject_add_request: bool = False) -> None:
        return run_coroutine(self.set_group_kick, group_id, user_id, reject_add_request)
    
    def set_group_ban_sync(self, group_id: Union[str, int], user_id: Union[str, int], duration: int = 30 * 60) -> None:
        return run_coroutine(self.set_group_ban, group_id, user_id, duration)
    
    def set_group_whole_ban_sync(self, group_id: Union[str, int], enable: bool) -> None:
        return run_coroutine(self.set_group_whole_ban, group_id, enable)
    
    def set_group_admin_sync(self, group_id: Union[str, int], user_id: Union[str, int], enable: bool) -> None:
        return run_coroutine(self.set_group_admin, group_id, user_id, enable)
    
    def set_group_leave_sync(self, group_id: Union[str, int], is_dismiss: bool = False) -> None:
        return run_coroutine(self.set_group_leave, group_id, is_dismiss)
    
    def set_group_special_title_sync(self, group_id: Union[str, int], user_id: Union[str, int], special_title: str = "") -> None:
        return run_coroutine(self.set_group_special_title, group_id, user_id, special_title)
        
    def set_group_add_request_sync(self, flag: str, approve: bool, reason: str = None) -> None:
        return run_coroutine(self.set_group_add_request, flag, approve, reason)

    def set_group_card_sync(self, group_id: Union[str, int], user_id: Union[str, int], card: str = "") -> None:
        return run_coroutine(self.set_group_card, group_id, user_id, card)
    
    def set_essence_msg_sync(self, message_id: Union[str, int]) -> None:
        return run_coroutine(self.set_essence_msg, message_id)
    
    def delete_essence_msg_sync(self, message_id: Union[str, int]) -> None:
        return run_coroutine(self.delete_essence_msg, message_id)
    
    def get_group_essence_msg_sync(self, group_id: Union[str, int]) -> list[dict]:
        return run_coroutine(self.get_group_essence_msg, group_id)
    
    def post_group_file_sync(self, group_id: Union[str, int], image: str = None, record: str=None, video: str=None, file: str=None) -> str:
        return run_coroutine(self.post_group_file, group_id, image, record, video, file)
    
    def move_group_file_sync(self, group_id: Union[str, int], file_id: str, current_parent_directory: str, target_parent_directory: str) -> None:
        return run_coroutine(self.move_group_file, group_id, file_id, current_parent_directory, target_parent_directory)
    
    def trans_group_file_sync(self, group_id: Union[str, int], file_id: str) -> None:
        return run_coroutine(self.trans_group_file, group_id, file_id)
        
    def rename_group_file_sync(self, group_id: Union[str, int], file_id: str, new_name: str) -> None:
        return run_coroutine(self.rename_group_file, group_id, file_id, new_name)
        
    def get_file_sync(self, file_id: str, file: str) -> File:
        return run_coroutine(self.get_file, file_id, file)

    def upload_group_file_sync(self, group_id: Union[str, int], file: str, name: str, folder) -> str:
        return run_coroutine(self.upload_group_file, group_id, file, name, folder)

    def create_group_file_folder_sync(self, group_id: Union[str, int], folder_name: str) -> None:
        return run_coroutine(self.create_group_file_folder, group_id, folder_name)
    
    def group_file_folder_makedir_sync(self, group_id: Union[str, int], path: str) -> str:
        return run_coroutine(self.group_file_folder_makedir, group_id, path)
    
    def delete_group_file_sync(self, group_id: Union[str, int], file_id: str) -> None:
        return run_coroutine(self.delete_group_file, group_id, file_id)
    
    def delete_group_folder_sync(self, group_id: Union[str, int], folder_id: str) -> None:
        return run_coroutine(self.delete_group_folder, group_id, folder_id)
        
    def get_group_root_files_sync(self, group_id: Union[str, int], file_count: int = 50) -> dict:
        return run_coroutine(self.get_group_root_files, group_id, file_count)
    
    def get_group_files_by_folder_sync(self, group_id: Union[str, int], folder_id: str, file_count: int = 50) -> dict:
        return run_coroutine(self.get_group_files_by_folder, group_id, folder_id, file_count)
    
    def get_group_file_url_sync(self, group_id: Union[str, int], file_id: str) -> str:
        return run_coroutine(self.get_group_file_url, group_id, file_id)
    
    def get_group_honor_info_sync(self, group_id: Union[str, int], type: Literal["talkative", "performer", "legend", "emotion", "all"]) -> GroupChatActivity:
        return run_coroutine(self.get_group_honor_info, group_id, type)

    def get_group_info_sync(self, group_id: Union[str, int]) -> GroupInfo:
        return run_coroutine(self.get_group_info, group_id)
    
    def get_group_info_ex_sync(self, group_id: Union[str, int]) -> dict:
        return run_coroutine(self.get_group_info_ex, group_id)
    
    def get_group_member_info_sync(self, group_id: Union[str, int], user_id: Union[str, int]) -> GroupMemberInfo:
        return run_coroutine(self.get_group_member_info, group_id, user_id)
    
    def get_group_member_list_sync(self, group_id: Union[str, int]) -> GroupMemberList:
        return run_coroutine(self.get_group_member_list, group_id)
    
    def get_group_shut_list_sync(self, group_id: Union[str, int]) -> GroupMemberList:
        return run_coroutine(self.get_group_shut_list, group_id)
    
    def set_group_remark_sync(self, group_id: Union[str, int], remark: str) -> None:
        return run_coroutine(self.set_group_remark, group_id, remark)
    
    def set_group_sign_sync(self, group_id: Union[str, int]) -> None:
        return run_coroutine(self.set_group_sign, group_id)

    def send_group_sign_sync(self, group_id: Union[str, int]) -> None:
        return run_coroutine(self.send_group_sign, group_id)
    
    def set_group_avatar_sync(self, group_id: Union[str, int], file: str) -> None:
        return run_coroutine(self.set_group_avatar, group_id, file)
    
    def set_group_name_sync(self, group_id: Union[str, int], name: str) -> None:
        return run_coroutine(self.set_group_name, group_id, name)

    def _send_group_notice_sync(self, group_id: Union[str, int], content: str, confirm_required: bool = False, image: str = None, is_show_edit_card: bool = False, pinned: bool = False) -> None:
        return run_coroutine(self._send_group_notice, group_id, content, confirm_required, image, is_show_edit_card, pinned)
    