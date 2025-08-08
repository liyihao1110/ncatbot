from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus
from ncatbot.core.event import File

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
        # TODO: 返回值
        result = await self.async_callback("/get_group_essence_msg", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    


    # --------------
    # region 群文件
    # --------------
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
        status.raise_if_failed()
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
    async def get_group_honor_info(self, group_id: Union[str, int], type: Literal["talkative", "performer", "legend", "emotion", "all"]) -> list[dict]:
        # TODO: 返回值
        result = await self.async_callback("/get_group_honor_info", {"group_id": group_id, "type": type})
        status = APIReturnStatus(result)
        return status.data

    async def get_group_info(self, group_id: Union[str, int]) -> dict:
        # TODO: 返回值
        result = await self.async_callback("/get_group_info", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_info_ex(self, group_id: Union[str, int]) -> dict:
        # TODO: 返回值
        result = await self.async_callback("/get_group_info_ex", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_member_info(self, group_id: Union[str, int], user_id: Union[str, int]) -> dict:
        # TODO: 返回值
        result = await self.async_callback("/get_group_member_info", {"group_id": group_id, "user_id": user_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_member_list(self, group_id: Union[str, int]) -> list[dict]:
        # TODO: 返回值
        result = await self.async_callback("/get_group_member_list", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    
    async def get_group_shut_list(self, group_id: Union[str, int]) -> list[dict]:
        # TODO: 返回值
        result = await self.async_callback("/get_group_shut_list", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data
    
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

    