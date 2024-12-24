# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

from .base import Base


class Group(Base):
    def __init__(self, port_or_http: (int, str), sync: bool = False):
        super().__init__(port_or_http=port_or_http, sync=sync)

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
        return await self.post("/set_group_kick", json=data)

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
        return await self.post("/set_group_ban", json=data)

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
        return await self.post("/get_group_system_msg", json=data)

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
        return await self.post("/get_essence_msg_list", json=data)

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
        return await self.post("/set_group_whole_ban", json=data)

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
            "file": self.get_media_path(file)
        }
        return await self.post("/set_group_portrait", json=data)

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
        return await self.post("/set_group_admin", json=data)

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
        return await self.post("/set_essence_msg", json=data)

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
        return await self.post("/set_group_card", json=data)

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
        return await self.post("/delete_essence_msg", json=data)

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
        return await self.post("/set_group_name", json=data)

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
        return await self.post("/set_group_leave", json=data)

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
            "image": self.get_media_path(image)
        }
        return await self.post("/_send_group_notice", json=data)

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
        return await self.post("/_get_group_notice", json=data)

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
        return await self.post("/upload_group_file", json=data)

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
        return await self.post("/set_group_add_request", json=data)

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
        return await self.post("/get_group_info", json=data)

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
        return await self.post("/get_group_info_ex", json=data)

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
        return await self.post("/create_group_file_folder", json=data)

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
        return await self.post("/delete_group_file", json=data)

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
        return await self.post("/delete_group_folder", json=data)

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
        return await self.post("/get_group_file_system_info", json=data)

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
        return await self.post("/get_group_root_files", json=data)

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
        return await self.post("/get_group_files_by_folder", json=data)

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
        return await self.post("/get_group_list", json=data)

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
        return await self.post("/get_group_member_info", json=data)

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
        return await self.post("/get_group_member_list", json=data)

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
        return await self.post("/get_group_honor_info", json=data)

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
        return await self.post("/get_group_at_all_remain", json=data)

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
        return await self.post("/get_group_ignored_notifies", json=data)

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
