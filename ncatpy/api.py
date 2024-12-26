# encoding: utf-8

from .http import Route
from .faces import Face
from .status import Status
from .http import replace_none

from . import logging
_log = logging.get_logger()

class BotAPI:
    def __init__(self, max_ids: int = 100):
        self._http = Route()
        self._face = Face()
        self._status = Status()

        self.messages = []  # 存储消息体
        self.message_ids = []  # 存储消息id
        self.max_ids = max_ids  # 最大保留已发送消息的消息id数量


    """
    原版本的Group.py
    """
    async def set_group_kick(self, group_id: (str, int), user_id: (str, int), reject_add_request: bool = None) -> dict:
        """
        群踢人
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656748e0
        :param group_id: group_id
        :param user_id: user_id
        :param reject_add_request: 是否群拉黑（默认False）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request
        }
        return await self._http.post("/set_group_kick", json=data)

    async def set_group_ban(self, group_id: (str, int), user_id: (str, int), duration: int) -> dict:
        """
        群禁言
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656791e0
        :param group_id: group_id
        :param user_id: user_id
        :param duration: 禁言时长（单位秒）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        }
        return await self._http.post("/set_group_ban", json=data)

    async def get_group_system_msg(self, group_id: (str, int)) -> dict:
        """
        获取群系统消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658660e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_system_msg", json=data)

    async def get_essence_msg_list(self, group_id: (str, int)) -> dict:
        """
        获取群精华消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658664e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_essence_msg_list", json=data)

    async def set_group_whole_ban(self, group_id: (str, int), enable: bool = None) -> dict:
        """
        全体禁言
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656802e0
        :param group_id: group_id
        :param enable: 是否开启（默认为True）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "enable": enable
        }
        return await self._http.post("/set_group_whole_ban", json=data)

    async def set_group_portrait(self, group_id: (str, int), file: str) -> dict:
        """
        设置群头像
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658669e0
        :param group_id: group_id
        :param file: file
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "file": self._http.get_media_path(file)
        }
        return await self._http.post("/set_group_portrait", json=data)

    async def set_group_admin(self, group_id: (str, int), user_id: (str, int), enable: bool = None) -> dict:
        """
        设置群管理
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656815e0
        :param group_id: group_id
        :param user_id: user_id
        :param enable: 是否设置（默认为False）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "enable": enable
        }
        return await self._http.post("/set_group_admin", json=data)

    async def set_essence_msg(self, message_id: (str, int)) -> dict:
        __import__('warnings').warn('目前自己发的消息自己能稳定添加群精华，但别人发的消息可能会无法添加精华消息', DeprecationWarning)
        """
        设置群精华消息
        目前自己发的消息自己能稳定添加群精华，但别人发的消息可能会无法添加精华消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658674e0
        :param message_id: message_id
        :rtype: dict
        """
        data = {
            "message_id": message_id
        }
        return await self._http.post("/set_essence_msg", json=data)

    async def set_group_card(self, group_id: (str, int), user_id: (str, int), card: str = '') -> dict:
        """
        设置群成员名片
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656913e0
        :param group_id: group_id
        :param user_id: user_id
        :param card: 为空则为取消群名片
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "card": card
        }
        return await self._http.post("/set_group_card", json=data)

    async def delete_essence_msg(self, message_id: (str, int)) -> dict:
        """
        删除群精华消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658678e0
        :param message_id: message_id
        :rtype: dict
        """
        data = {
            "message_id": message_id
        }
        return await self._http.post("/delete_essence_msg", json=data)

    async def set_group_name(self, group_id: (str, int), group_name: str) -> dict:
        """
        设置群名
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656919e0
        :param group_id: group_id
        :param group_name: group_name
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "group_name": group_name
        }
        return await self._http.post("/set_group_name", json=data)

    async def set_group_leave(self, group_id: (str, int)) -> dict:
        """
        退群
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656926e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/set_group_leave", json=data)

    async def send_group_notice(self, group_id: (str, int), content: str, image: str = None) -> dict:
        """
        _发送群公告
        注意机器人是否是管理员！
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658740e0
        :param group_id: group_id
        :param content: 内容
        :param image: 图片路径（测试只能本地图片路径）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "content": content,
            "image": self._http.get_media_path(image)
        }
        return await self._http.post("/_send_group_notice", json=data)

    async def get_group_notice(self, group_id: (str, int)) -> dict:
        """
        _获取群公告
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658742e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/_get_group_notice", json=data)

    # async def set_group_special_title(self, group_id: (str, int), user_id: (str, int), special_title: str) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     设置群头衔
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656931e0
    #     :param group_id: group_id
    #     :param user_id: user_id
    #     :param special_title: special_title
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "user_id": user_id,
    #         "special_title": special_title
    #     }
    #     return await self.post("/set_group_special_title", json=data)

    async def upload_group_file(self, group_id: (str, int), file: str, name: str, folder_id: str) -> dict:
        """
        上传群文件
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658753e0
        :param group_id: group_id
        :param file: file
        :param name: name
        :param folder_id: 文件夹ID
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "file": file,
            "name": name,
            "folder_id": folder_id
        }
        return await self._http.post("/upload_group_file", json=data)

    async def set_group_add_request(self, flag: str, approve: bool = None, reason: str = None) -> dict:
        """
        处理加群请求
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656947e0
        :param flag: 请求id
        :param approve: 是否同意（默认为True）
        :param reason: 拒绝理由
        :rtype: dict
        """
        if approve:
            reason = None
        data = {
            "flag": flag,
            "approve": approve,
            "reason": reason
        }
        return await self._http.post("/set_group_add_request", json=data)

    async def get_group_info(self, group_id: (str, int)) -> dict:
        """
        获取群信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656979e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_info", json=data)

    async def get_group_info_ex(self, group_id: (str, int)) -> dict:
        """
        获取群信息ex
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659229e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_info_ex", json=data)

    async def create_group_file_folder(self, group_id: (str, int), folder_name: str) -> dict:
        """
        创建群文件文件夹
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658773e0
        :param group_id: group_id
        :param folder_name: folder_name
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "folder_name": folder_name
        }
        return await self._http.post("/create_group_file_folder", json=data)

    async def delete_group_file(self, group_id: (str, int), file_id: str) -> dict:
        """
        删除群文件
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658755e0
        :param group_id: group_id
        :param file_id: file_id
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "file_id": file_id
        }
        return await self._http.post("/delete_group_file", json=data)

    async def delete_group_folder(self, group_id: (str, int), folder_id: str) -> dict:
        """
        删除群文件夹
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658779e0
        :param group_id: group_id
        :param folder_id: folder_id
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "folder_id": folder_id
        }
        return await self._http.post("/delete_group_folder", json=data)

    async def get_group_file_system_info(self, group_id: (str, int)) -> dict:
        """
        获取群文件系统信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658789e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_file_system_info", json=data)

    async def get_group_root_files(self, group_id: (str, int)) -> dict:
        """
        获取群根目录文件列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658823e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_root_files", json=data)

    async def get_group_files_by_folder(self, group_id: (str, int), folder_id: str, file_count: int = None) -> dict:
        """
        获取群子目录文件列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658865e0
        :param group_id: group_id
        :param folder_id: folder_id
        :param file_count: 一次性获取的文件数量（为空没数，应该能获取全部）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "folder_id": folder_id,
            "file_count": file_count
        }
        return await self._http.post("/get_group_files_by_folder", json=data)

    # async def get_group_file_url(self, group_id: (str, int), file_id: str) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     获取群文件资源链接
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658867e0
    #     :param group_id: group_id
    #     :param file_id: file_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "file_id": file_id
    #     }
    #     return await self.post("/get_group_file_url", json=data)

    async def get_group_list(self, no_cache: bool = False) -> dict:
        """
        获取群列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656992e0
        :param no_cache: 不缓存
        :rtype: dict
        """
        data = {
            "no_cache": no_cache
        }
        return await self._http.post("/get_group_list", json=data)

    async def get_group_member_info(self, group_id: (str, int), user_id: (str, int)) -> dict:
        """
        获取群成员信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657019e0
        :param group_id: group_id
        :param user_id: user_id
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id
        }
        return await self._http.post("/get_group_member_info", json=data)

    async def get_group_member_list(self, group_id: (str, int), no_cache: bool = False) -> dict:
        """
        获取群成员列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657034e0
        :param group_id: group_id
        :param no_cache: no_cache
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "no_cache": no_cache
        }
        return await self._http.post("/get_group_member_list", json=data)

    async def get_group_honor_info(self, group_id: (str, int)) -> dict:
        """
        获取群荣誉
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657036e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_honor_info", json=data)

    async def get_group_at_all_remain(self, group_id: (str, int)) -> dict:
        """
        获取群 @全体成员 剩余次数
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/227245941e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_at_all_remain", json=data)

    async def get_group_ignored_notifies(self, group_id: (str, int)) -> dict:
        """
        获取群过滤系统消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659323e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/get_group_ignored_notifies", json=data)

    # async def set_group_sign(self, group_id: str) -> dict:
    #     __import__('warnings').warn('报错', DeprecationWarning)
    #     """
    #     设置群打卡
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659329e0
    #     :param group_id: group_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id
    #     }
    #     return await self.post("/set_group_sign", json=data)

    # async def send_group_sign(self, group_id: str) -> dict:
    #     __import__('warnings').warn('报错', DeprecationWarning)
    #     """
    #     发送群打卡
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/230897177e0
    #     :param group_id: group_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id
    #     }
    #     return await self.post("/send_group_sign", json=data)

    # async def get_ai_characters(self, group_id: (str, int), chat_type: (int, str)) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     获取AI语音人物
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/229485683e0
    #     :param group_id: group_id
    #     :param chat_type: chat_type
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "chat_type": chat_type
    #     }
    #     return await self.post("/get_ai_characters", json=data)

    # async def send_group_ai_record(self, group_id: (str, int), character: str, text: str) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     发送群AI语音
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/229486774e0
    #     :param group_id: group_id
    #     :param character: character_id
    #     :param text: 文本
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "character": character,
    #         "text": text
    #     }
    #     return await self.post("/send_group_ai_record", json=data)

    # async def get_ai_record(self, group_id: (str, int), character: str, text: str) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     获取AI语音
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/229486818e0
    #     :param group_id: group_id
    #     :param character: character_id
    #     :param text: 文本
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "character": character,
    #         "text": text
    #     }
    #     return await self.post("/get_ai_record", json=data)


    """
    原版本的message.py
    """

    async def mark_msg_as_read(self, group_id: (str, int) = None, user_id: (str, int) = None) -> dict:
        """
        设置消息已读
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657389e0
        :param group_id: 与user_id二选一
        :param user_id: 与group_id二选一
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id
        }
        return await self._http.post("/mark_msg_as_read", json=data)

    async def mark_group_msg_as_read(self, group_id: (str, int)) -> dict:
        """
        设置群聊已读
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659167e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/mark_group_msg_as_read", json=data)

    async def mark_private_msg_as_read(self, user_id: (str, int)) -> dict:
        """
        设置私聊已读
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659165e0
        :param user_id: user_id
        :rtype: dict
        """
        data = {
            "user_id": user_id
        }
        return await self._http.post("/mark_private_msg_as_read", json=data)

    async def mark_all_as_read(self) -> dict:
        """
        _设置所有消息已读
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659194e0
        :rtype: dict
        """
        return await self._http.post("/_mark_all_as_read")

    async def delete_msg(self, message_id: (str, int)) -> dict:
        """
        撤回消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226919954e0
        :param message_id: message_id
        :rtype: dict
        """
        data = {
            "message_id": message_id
        }
        return await self._http.post("/delete_msg", json=data)

    async def get_msg(self, message_id: (str, int)) -> dict:
        """
        获取消息详情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656707e0
        :param message_id: message_id
        :rtype: dict
        """
        data = {
            "message_id": message_id
        }
        return await self._http.post("/get_msg", json=data)

    async def get_image(self, file_id: str) -> dict:
        """
        获取图片消息详情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657066e0
        :param file_id: file_id
        :rtype: dict
        """
        data = {
            "file_id": file_id
        }
        return await self._http.post("/get_image", json=data)

    async def get_record(self, file_id: str, out_format: str = 'amr') -> dict:
        """
        获取语音消息详情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657058e0
        :param file_id: file_id
        :param out_format: 输出 格式（mp3/amr/wma/m4a/spx/ogg/wav/flac）
        :rtype: dict
        """
        data = {
            "file_id": file_id,
            "out_format": out_format
        }
        return await self._http.post("/get_record", json=data)

    async def get_file(self, file_id: str) -> dict:
        """
        获取文件信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658985e0
        :param file_id: file_id
        :rtype: dict
        """
        data = {
            "file_id": file_id
        }
        return await self._http.post("/get_file", json=data)

    async def get_group_msg_history(self, group_id: (str, int), message_seq: (str, int) = None, count: int = None, reverse_order: bool = None) -> dict:
        """
        获取群历史消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657401e0
        :param group_id: group_id
        :param message_seq: 0为最新
        :param count: 数量（默认20条，如果当中有撤回，实际会小于这个值）
        :param reverse_order: 倒序（默认False）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "message_seq": message_seq,
            "count": count,
            "reverseOrder": reverse_order
        }
        return await self._http.post("/get_group_msg_history", json=data)

    async def set_msg_emoji_like(self, message_id: (str, int), emoji_id: int) -> dict:
        """
        贴表情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659104e0
        :param message_id: message_id
        :param emoji_id: emoji_id
        :rtype: dict
        """
        data = {
            "message_id": message_id,
            "emoji_id": emoji_id
        }
        return await self._http.post("/set_msg_emoji_like", json=data)

    async def get_friend_msg_history(self, user_id: (str, int), message_seq: (str, int) = None, count: int = None, reverse_order: bool = None) -> dict:
        """
        获取好友历史消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659174e0
        :param user_id: user_id
        :param message_seq: 0为最新
        :param count: 数量（默认20条，如果当中有撤回，实际会小于这个值）
        :param reverse_order: 倒序（默认False）
        :rtype: dict
        """
        data = {
            "user_id": user_id,
            "message_seq": message_seq,
            "count": count,
            "reverseOrder": reverse_order
        }
        return await self._http.post("/get_friend_msg_history", json=data)

    async def get_recent_contact(self, count: int) -> dict:
        """
        最近消息列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659190e0
        :param count: 会话数量
        :rtype: dict
        """
        data = {
            "count": count
        }
        return await self._http.post("/get_recent_contact", json=data)

    async def fetch_emoji_like(self, message_id: (str, int), emoji_id: str, emoji_type: str = "1") -> dict:
        """
        获取贴表情详情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659219e0
        :param message_id: message_id
        :param emoji_id: 表情ID
        :param emoji_type: 表情类型
        :rtype: dict
        """
        data = {
            "message_id": message_id,
            "emojiId": emoji_id,
            "emojiType": emoji_type
        }
        return await self._http.post("/fetch_emoji_like", json=data)

    async def get_forward_msg(self, message_id: str) -> dict:
        """
        获取合并转发消息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656712e0
        :param message_id: message_id
        :rtype: dict
        """
        data = {
            "message_id": message_id
        }
        return await self._http.post("/get_forward_msg", json=data)

    # async def send_forward_msg(self, group_id: (str, int), messages: list, text: str, prompt: str, summary: str, source: str, user_id: (str, int)) -> dict:
    #     __import__('warnings').warn('参数过多，懒得搞，先放一边~', DeprecationWarning)
    #     """
    #     发送合并转发消息
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659136e0
    #     :param group_id: group_id
    #     :param messages: 消息体，每一个都是node节点，node节点下的content才放消息链
    #     :param text: text
    #     :param prompt: 外显
    #     :param summary: 底下文本
    #     :param source: 内容
    #     :param user_id: user_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id,
    #         "messages": messages,
    #         "news": [
    #             {
    #                 "text": text
    #             }
    #         ],
    #         "prompt": prompt,
    #         "summary": summary,
    #         "source": source,
    #         "user_id": user_id
    #     }
    #     return await self.post("/send_forward_msg", json=data)

    """
    原版本的system.py
    """

    async def get_online_clients(self, no_cache: bool = False) -> dict:
        """
        获取当前账号在线客户端列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657379e0
        :param no_cache: no_cache
        :rtype: dict
        """
        data = {
            "no_cache": no_cache
        }
        return await self._http.post("/get_online_clients", json=data)

    async def get_robot_uin_range(self) -> dict:
        """
        获取机器人账号范围
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658975e0
        :rtype: dict
        """
        return await self._http.post("/get_robot_uin_range")

    async def ocr_image(self, image: str) -> dict:
        """
        OCR 图片识别
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658231e0
        :param image: image
        :rtype: dict
        """
        data = {
            "image": image
        }
        return await self._http.post("/ocr_image", json=data)

    async def translate_en2zh(self) -> dict:
        """
        英译中
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659102e0
        :rtype: dict
        """
        data = {
            "words": [
                "word",
                "message",
                "group"
            ]
        }
        return await self._http.post("/translate_en2zh", json=data)

    async def get_login_info(self) -> dict:
        """
        获取登录号信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656952e0
        :rtype: dict
        """
        return await self._http.post("/get_login_info")

    async def set_input_status(self, event_type: int, user_id: (str, int)) -> dict:
        """
        设置输入状态
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659225e0
        :param event_type: eventType
        :param user_id: user_id
        :rtype: dict
        """
        data = {
            "eventType": event_type,
            "user_id": user_id
        }
        return await self._http.post("/set_input_status", json=data)

    async def download_file(self, url: str, thread_count: int, name: str) -> dict:
        """
        下载文件到缓存目录
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658887e0
        :param url: 下载地址
        :param thread_count: 下载线程数
        :param name: 自定义文件名称
        :rtype: dict
        """
        data = {
            "url": url,
            "thread_count": thread_count,
            "name": name
        }
        return await self._http.post("/download_file", json=data)

    async def get_cookies(self, domain: str) -> dict:
        """
        获取cookies
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657041e0
        :param domain: domain
        :rtype: dict
        """
        data = {
            "domain": domain
        }
        return await self._http.post("/get_cookies", json=data)

    async def get_csrf_token(self) -> dict:
        """
        获取 CSRF Token
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657044e0
        :rtype: dict
        """
        return await self._http.post("/get_csrf_token")

    async def del_group_notice(self, group_id: (str, int), notice_id: str) -> dict:
        """
        _删除群公告
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659240e0
        :param group_id: group_id
        :param notice_id: notice_id
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "notice_id": notice_id
        }
        return await self._http.post("/_del_group_notice", json=data)

    async def get_credentials(self, domain: str) -> dict:
        """
        获取 QQ 相关接口凭证
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657054e0
        :param domain: domain
        :rtype: dict
        """
        data = {
            "domain": domain
        }
        return await self._http.post("/get_credentials", json=data)

    async def get_model_show(self, model: str) -> dict:
        """
        _获取在线机型
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/227233981e0
        :param model: model
        :rtype: dict
        """
        data = {
            "model": model
        }
        return await self._http.post("/_get_model_show", json=data)

    async def set_model_show(self, model: str, model_show: str) -> dict:
        """
        _设置在线机型
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/227233993e0
        :param model: model
        :param model_show: model_show
        :rtype: dict
        """
        data = {
            "model": model,
            "model_show": model_show
        }
        return await self._http.post("/_set_model_show", json=data)

    async def can_send_image(self) -> dict:
        """
        检查是否可以发送图片
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657071e0
        :rtype: dict
        """
        return await self._http.post("/can_send_image")

    async def nc_get_packet_status(self) -> dict:
        """
        获取packet状态
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659280e0
        :rtype: dict
        """
        return await self._http.post("/nc_get_packet_status")

    async def can_send_record(self) -> dict:
        """
        检查是否可以发送语音
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657080e0
        :rtype: dict
        """
        return await self._http.post("/can_send_record")

    async def get_status(self) -> dict:
        """
        获取状态
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657083e0
        :rtype: dict
        """
        return await self._http.post("/get_status")

    async def nc_get_rkey(self) -> dict:
        """
        获取rkey
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659297e0
        :rtype: dict
        """
        return await self._http.post("/nc_get_rkey")

    async def get_version_info(self) -> dict:
        """
        获取版本信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657087e0
        :rtype: dict
        """
        return await self._http.post("/get_version_info")

    # async def get_group_shut_list(self, group_id: (str, int)) -> dict:
    #     __import__('warning').warn('不知道为啥返回老报错,先丢一边~', DeprecationWarning)
    #     """
    #     获取群禁言列表
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659300e0
    #     :param group_id: group_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "group_id": group_id
    #     }
    #     return await self.post("/get_group_shut_list", json=data)

    """
    原版本的user.py
    """

    async def set_qq_profile(self, nickname: str, personal_note: str = None, sex: str = None) -> dict:
        """
        设置账号信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657374e0
        :param nickname: 昵称
        :param personal_note: 个性签名【可选】
        :param sex: 性别（1为男，2为女）【可选】
        :rtype: dict
        """
        data = {
            "nickname": nickname,
            "personal_note": personal_note,
            "sex": sex
        }
        return await self._http.post("/set_qq_profile", json=data)

    async def ark_share_peer(self, group_id: (str, int) = None, user_id: (str, int) = None, phone_number: str = None) -> dict:
        """
        获取推荐好友/群聊卡片
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658965e0
        :param group_id: 和user_id二选一
        :param user_id: 和group_id二选一
        :param phone_number: 对方手机号（好像没啥用）
        :rtype: dict
        """
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "phoneNumber": phone_number
        }
        return await self._http.post("/ArkSharePeer", json=data)

    async def ark_share_group(self, group_id: str) -> dict:
        """
        获取推荐群聊卡片
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658971e0
        :param group_id: group_id
        :rtype: dict
        """
        data = {
            "group_id": group_id
        }
        return await self._http.post("/ArkShareGroup", json=data)

    async def set_online_status(self, status: int, ext_status: int, battery_status: int = 0) -> dict:
        """
        设置在线状态
        可能会有一点延迟生效
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658977e0
        :param status: 详情看顶部
        :param ext_status: 详情看顶部
        :param battery_status: 电量
        :rtype: dict
        """
        data = {
            "status": status,
            "ext_status": ext_status,
            "battery_status": battery_status
        }
        return await self._http.post("/set_online_status", json=data)

    async def get_friends_with_category(self) -> dict:
        """
        获取好友分组列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658978e0
        :rtype: dict
        """
        return await self._http.post("/get_friends_with_category")

    async def set_qq_avatar(self, file: str) -> dict:
        """
        设置头像
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658980e0
        :param file: 路径或链接
        :rtype: dict
        """
        data = {
            "file": file
        }
        return await self._http.post("/set_qq_avatar", json=data)

    async def send_like(self, user_id: (str, int), times: int) -> dict:
        """
        点赞
        最大点赞数可设置为20，SVIP当日最高点赞20次，普通用户当日最大点赞10次，不能给自己点赞！
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656717e0
        :param user_id: user_id
        :param times: 点赞次数
        :rtype: dict
        """
        data = {
            "user_id": user_id,
            "times": times
        }
        return await self._http.post("/send_like", json=data)

    async def create_collection(self, raw_data: str, brief: str) -> dict:
        """
        创建收藏
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659178e0
        :param raw_data: 内容
        :param brief: 标题
        :rtype: dict
        """
        data = {
            "rawData": raw_data,
            "brief": brief
        }
        return await self._http.post("/create_collection", json=data)

    async def set_friend_add_request(self, flag: str, approve: bool, remark: str) -> dict:
        """
        处理好友请求
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656932e0
        :param flag: 请求id
        :param approve: 是否同意
        :param remark: 好友备注
        :rtype: dict
        """
        data = {
            "flag": flag,
            "approve": approve,
            "remark": remark
        }
        return await self._http.post("/set_friend_add_request", json=data)

    async def set_self_longnick(self, long_nick: str) -> dict:
        """
        设置个性签名
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659186e0
        :param long_nick: 内容
        :rtype: dict
        """
        data = {
            "longNick": long_nick
        }
        return await self._http.post("/set_self_longnick", json=data)

    async def get_stranger_info(self, user_id: (str, int)) -> dict:
        """
        获取账号信息
        可以获取任何QQ的，不限于自己的好友
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656970e0
        :param user_id: user_id
        :rtype: dict
        """
        data = {
            "user_id": user_id
        }
        return await self._http.post("/get_stranger_info", json=data)

    async def get_friend_list(self, no_cache: bool = False) -> dict:
        """
        获取好友列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656976e0
        :param no_cache: 不缓存
        :rtype: dict
        """
        data = {
            "no_cache": no_cache
        }
        return await self._http.post("/get_friend_list", json=data)

    async def get_profile_like(self) -> dict:
        """
        获取点赞列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659197e0
        :rtype: dict
        """
        return await self._http.post("/get_profile_like")

    async def fetch_custom_face(self, count: int) -> dict:
        """
        获取收藏表情
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659210e0
        :param count: count
        :rtype: dict
        """
        data = {
            "count": count
        }
        return await self._http.post("/fetch_custom_face", json=data)

    async def upload_private_file(self, user_id: (str, int), file: str, name: str) -> dict:
        """
        上传私聊文件
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658883e0
        :param user_id: user_id
        :param file: file
        :param name: name
        :rtype: dict
        """
        data = {
            "user_id": user_id,
            "file": self._http.get_media_path(file),
            "name": name
        }
        return await self._http.post("/upload_private_file", json=data)

    async def delete_friend(self, friend_id: (str, int), user_id: (str, int) = None, temp_block: bool = False, temp_both_del: bool = False) -> dict:
        """
        删除好友
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/227237873e0
        :param friend_id: friend_id
        :param user_id: user_id（装饰品，么得也行）
        :param temp_block: 拉黑
        :param temp_both_del: 双向删除
        :rtype: dict
        """
        data = {
            "friend_id": friend_id,
            "temp_block": temp_block,
            "temp_both_del": temp_both_del,
            "user_id": user_id
        }
        return await self._http.post("/delete_friend", json=data)

    # async def nc_get_user_status(self, user_id: (str, int)) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     获取用户状态
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659292e0
    #     :param user_id: user_id
    #     :rtype: dict
    #     """
    #     data = {
    #         "user_id": user_id
    #     }
    #     return await self.post("/nc_get_user_status", json=data)

    # async def get_mini_app_ark(self, type_: str, title: str, desc: str, pic_url: str, jump_url: str) -> dict:
    #     __import__('warnings').warn('需要packetServer服务，等待开发~', DeprecationWarning)
    #     """
    #     获取小程序卡片
    #     https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/227738594e0
    #     :param type_: 只填入必须参数的话该值必须填
    #     :param title: 标题
    #     :param desc: 内容
    #     :param pic_url: 图片链接
    #     :param jump_url: 跳转链接
    #     :rtype: dict
    #     """
    #     data = {
    #         "type": type_,
    #         "title": title,
    #         "desc": desc,
    #         "picUrl": pic_url,
    #         "jumpUrl": jump_url
    #     }
    #     return await self.post("/get_mini_app_ark", json=data)

    """
    原版本的message_chain.py
    """

    def add_id(self, mid):
        """
        存储自身发送的消息，方便确认别人是否引用的是自己的消息
        """
        self.message_ids.append(mid)
        if len(self.message_ids) >= self.max_ids:
            self.message_ids = self.message_ids[-self.max_ids:]

    async def send_group_msg(self, group_id: (int, str), clear_message: bool = True):
        """
        发送群聊消息
        :param group_id: group_id
        :param clear_message: 是否清空消息缓存
        """
        message_id = None
        for message in self.messages.copy():
            if message['type'] == 'reply':
                message_id = message
                self.messages.remove(message)
        # 将reply消息前置
        if message_id is not None:
            self.messages = [message_id] + self.messages
            message_id = message_id['data']['id']
        # 强制保证此类消息独占消息链
        for message in self.messages.copy():
            if message['type'] in ['rps', 'dice', 'contact', 'music', 'node']:
                self.messages = [message]
                break
        if self.messages:
            if message_id:
                data = {
                    "group_id": group_id,
                    'message_id': message_id,
                    "message": self.messages.copy()
                }
            else:
                data = {
                    "group_id": group_id,
                    "message": self.messages.copy()
                }
            if clear_message:
                self.clear()
            result = await self._http.post("/send_group_msg", json=data)
            if result['data']:
                self.add_id(result['data']['message_id'])
            else:
                _log.error(result)
        return self

    async def send_private_msg(self, user_id: (int, str), clear_message: bool = True):
        """
        发送私聊消息（自动去除@信息）
        :param user_id: user_id
        :param clear_message: 是否清空消息缓存
        """
        for message in self.messages.copy():
            # 移除私聊中的 @ 消息
            if message['type'] == 'at':
                self.messages.remove(message)
        # 强制保证此类消息独占消息链
        for message in self.messages.copy():
            if message['type'] in ['rps', 'dice', 'contact', 'music', 'node']:
                self.messages = [message]
                break
        if self.messages:
            data = {
                "user_id": user_id,
                "message": self.messages.copy()
            }
            if clear_message:
                self.clear()
            result = await self._http.post("/send_private_msg", json=data)
            if result['data']:
                self.add_id(result['data']['message_id'])
            else:
                _log.error(result)
        return self

    def add_text(self, text: str):
        """
        纯文本
        :param text: 文本
        """
        self.messages.append({
            "type": "text",
            "data": {
                "text": text
            }
        })
        return self

    def add_face(self, face_id: (int, str), name: str = None, summary: str = None):
        """
        QQ表情
        :param face_id: QQ表情编号
            表情编号参考（系统表情）：https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#Emoji%20%E5%88%97%E8%A1%A8
        :param name: 表情名称
        :param summary: 表情简介
        """
        self.messages.append({
            "type": "face",
            "data": {
                "id": str(face_id),
                **replace_none(dict)(json=dict(name=name, summary=summary)).get('json', {})
            }
        })
        return self

    def add_media(self, media_type: str, media_path: str, **kwargs):
        """
        添加媒体资源（复用函数）
        :param media_type: 媒体资源类型
        :param media_path: 媒体资源地址（可以是网络地址）
        """
        media_path = self._http.get_media_path(media_path)
        if media_path:
            self.messages.append({
                "type": media_type,
                "data": {
                    "file": media_path,
                    **kwargs
                }
            })
        return self

    def add_image(self, image: str, name: str = None, summary: str = None, sub_type: str = None):
        """
        图片
        :param image: 图片地址
        :param name: 图片名称
        :param summary: 图片简介
        :param sub_type: 子类型
        """
        self.add_media('image', image, **replace_none(dict)(json=dict(name=name, summary=summary, sub_type=sub_type)).get('json', {}))
        return self

    def add_record(self, record: str, name: str = None):
        """
        语音
        :param record: 语音地址
        :param name: 语言名称
        """
        self.add_media('record', record, **replace_none(dict)(json=dict(name=name)).get('json', {}))
        return self

    def add_video(self, video: str, name: str = None, thumb: str = None):
        """
        视频
        :param video: 视频地址
        :param name: 视频名称
        :param thumb: 视频缩略图
        """
        self.add_media('video', video, **replace_none(dict)(json=dict(name=name, thumb=self._http.get_media_path(thumb))).get('json', {}))
        return self

    def add_at(self, target: (int, str) = 'all'):
        """
        @某人，all为@全体成员
        :param target: QQ表情编号
        """
        self.messages.append({
            "type": "at",
            "data": {
                "qq": str(target),
            }
        })
        self.add_text(' ')  # 自动隔开@信息
        return self

    def rps(self):
        """
        超级表情——猜拳（将清空所有消息列表）
        """
        self.messages = [{
            "type": "rps"
        }]
        return self

    def dice(self):
        """
        超级表情——骰子（将清空所有消息列表）
        """
        self.messages = [{
            "type": "dice"
        }]
        return self

    def contact(self, qq: (int, str) = None, group: (int, str) = None):
        """
        推荐好友或群聊（将清空所有消息列表）
        :param qq: user_id
        :param group: group_id
        """
        if qq or group:
            self.messages =[{
                "type": "contact",
                "data": {
                    "type": "qq" if qq else "group",
                    "id": qq or group
                }
            }]
        return self

    def music(self, music_type: str = 'custom', **kwargs):
        """
        音乐分享（将清空所有消息列表）
        :param music_type: qq / 163 / kugou / migu / kuwo / custom
        :param kwargs: qq / 163 / kugou / migu / kuwo：{id} | custom：{type, url, audio, title, image(选), singer(选)}
        """
        self.messages = [{
            "type": "music",
            "data": {
                "type": music_type,
                **kwargs
            }
        }]
        return self

    def add_reply(self, message_id: (int, str)):
        """
        回复消息（更新后在发送消息前将会自动排序 reply 至最前面）
        :param message_id: 消息id号
        """
        self.messages.append({
            "type": "reply",
            "data": {
                "id": str(message_id),
            }
        })
        return self

    def node(self, id_: (int, str) = None, content: list = None, user_id: (int, str) = None, nickname: str = None):
        """
        构造合并转发消息节点
        :param id_: 消息id号（与消息链二选一）
        :param content: 消息链（与消息id号二选一）
        :param user_id: user_id（伪造消息用，暂时没发现有用）
        :param nickname: 用户昵称（伪造消息用，暂时没发现有用）
        """
        self.messages = [{
            "type": "node",
            "data": replace_none(dict)(json=dict(id=id_, content=content, user_id=user_id, nickname=nickname)).get('json', {})
        }]
        return self

    def add_json(self, data: (int, str)):
        """
        添加json消息
        :param data: json字符串
        """
        self.messages.append({
            "type": "json",
            "data": {
                "data": data,
            }
        })
        return self

    def add_file(self, file: str, name: str = None):
        """
        文件
        :param file: 文件地址
        :param name: 文件名称
        """
        self.add_media('file', file, **replace_none(dict)(json=dict(name=name)).get('json', {}))
        return self

    def clear(self):
        """
        清空消息链
        """
        self.messages = []
        return self