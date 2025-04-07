import asyncio
from typing import Union

from ncatbot.core.element import MessageChain
from ncatbot.utils import config


class SYNC_API_MIXIN:
    """
    同步 API 混入类, 仅用于提供文档
    """

    def set_qq_profile_sync(self, nickname: str, personal_note: str, sex: str):
        """
        :param nickname: 昵称
        :param personal_note: 个性签名
        :param sex: 性别
        :return: 设置账号信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_qq_profile(nickname, personal_note, sex))
        result = loop.run_until_complete(task)
        return result

    # 用户接口
    def get_user_card_sync(self, user_id: int, phone_number: str):
        """
        :param user_id: QQ号
        :param phone_number: 手机号
        :return: 获取用户名片
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_user_card(user_id, phone_number))
        result = loop.run_until_complete(task)
        return result

    def get_group_card_sync(self, group_id: int, phone_number: str):
        """
        :param group_id: 群号
        :param phone_number: 手机号
        :return: 获取群名片
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_card(group_id, phone_number))
        result = loop.run_until_complete(task)
        return result

    def get_share_group_card_sync(self, group_id: str):
        """
        :param group_id: 群号
        :return: 获取群共享名片
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_share_group_card(group_id))
        result = loop.run_until_complete(task)
        return result

    def set_online_status_sync(self, status: str):
        """
        :param status: 在线状态
        :return: 设置在线状态
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_online_status(status))
        result = loop.run_until_complete(task)
        return result

    def get_friends_with_category_sync(self):
        """
        :return: 获取好友列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_friends_with_category())
        result = loop.run_until_complete(task)
        return result

    def set_qq_avatar_sync(self, avatar: str):
        """
        :param avatar: 头像路径，支持本地路径和网络路径
        :return: 设置头像
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_qq_avatar(avatar))
        result = loop.run_until_complete(task)
        return result

    def send_like_sync(self, user_id: str, times: int):
        """
        :param user_id: QQ号
        :param times: 次数
        :return: 发送赞
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_like(user_id, times))
        result = loop.run_until_complete(task)
        return result

    def create_collection_sync(self, rawdata: str, brief: str):
        """
        :param rawdata: 内容
        :param brief: 标题
        :return: 创建收藏
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.create_collection(rawdata, brief))
        result = loop.run_until_complete(task)
        return result

    def set_friend_add_request_sync(self, flag: str, approve: bool, remark: str):
        """
        :param flag: 请求ID
        :param approve: 是否同意
        :param remark: 备注
        :return: 设置好友请求
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_friend_add_request(flag, approve, remark))
        result = loop.run_until_complete(task)
        return result

    def set_self_long_nick_sync(self, longnick: str):
        """
        :param longnick: 个性签名内容
        :return: 设置个性签名
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_self_long_nick(longnick))
        result = loop.run_until_complete(task)
        return result

    def get_stranger_info_sync(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取陌生人信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_stranger_info(user_id))
        result = loop.run_until_complete(task)
        return result

    def get_friend_list_sync(self, cache: bool):
        """
        :param cache: 是否使用缓存
        :return: 获取好友列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_friend_list(cache))
        result = loop.run_until_complete(task)
        return result

    def get_profile_like_sync(self):
        """
        :return: 获取个人资料卡点赞数
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_profile_like())
        result = loop.run_until_complete(task)
        return result

    def fetch_custom_face_sync(self, count: int):
        """
        :param count: 数量
        :return: 获取收藏表情
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.fetch_custom_face(count))
        result = loop.run_until_complete(task)
        return result

    def upload_private_file_sync(self, user_id: Union[int, str], file: str, name: str):
        """
        :param user_id: QQ号
        :param file: 文件路径
        :param name: 文件名
        :return: 上传私聊文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.upload_private_file(user_id, file, name))
        result = loop.run_until_complete(task)
        return result

    def delete_friend_sync(
        self,
        user_id: Union[int, str],
        friend_id: Union[int, str],
        temp_block: bool,
        temp_both_del: bool,
    ):
        """
        :param user_id: QQ号
        :param friend_id: 好友ID
        :param temp_block: 拉黑
        :param temp_both_del: 双向删除
        :return: 删除好友
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.delete_friend(user_id, friend_id, temp_block, temp_both_del)
        )
        result = loop.run_until_complete(task)
        return result

    def nc_get_user_status_sync(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取用户状态
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.nc_get_user_status(user_id))
        result = loop.run_until_complete(task)
        return result

    def get_mini_app_ark_sync(self, app_json: dict):
        """
        :param app_json: 小程序JSON
        :return: 获取小程序ARK
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_mini_app_ark(app_json))
        result = loop.run_until_complete(task)
        return result

    # 消息接口
    def mark_msg_as_read_sync(
        self, group_id: Union[int, str] = None, user_id: Union[int, str] = None
    ):
        """
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :return: 设置消息已读
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.mark_msg_as_read(group_id, user_id))
        result = loop.run_until_complete(task)
        return result

    def mark_group_msg_as_read_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 设置群聊已读
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.mark_group_msg_as_read(group_id))
        result = loop.run_until_complete(task)
        return result

    def mark_private_msg_as_read_sync(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 设置私聊已读
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.mark_private_msg_as_read(user_id))
        result = loop.run_until_complete(task)
        return result

    def mark_all_as_read_sync(self):
        """
        :return: 设置所有消息已读
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.mark_all_as_read())
        result = loop.run_until_complete(task)
        return result

    def delete_msg_sync(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.delete_msg(message_id))
        result = loop.run_until_complete(task)
        return result

    def get_msg_sync(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 获取消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_msg(message_id))
        result = loop.run_until_complete(task)
        return result

    def get_image_sync(self, image_id: str):
        """
        :param image_id: 图片ID
        :return: 获取图片消息详情
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_image(image_id))
        result = loop.run_until_complete(task)
        return result

    def get_record_sync(self, record_id: str, output_type: str = "mp3"):
        """
        :param record_id: 语音ID
        :param output_type: 输出类型，枚举值:mp3 amr wma m4a spx ogg wav flac,默认为mp3
        :return: 获取语音消息详情
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_record(record_id, output_type))
        result = loop.run_until_complete(task)
        return result

    def get_file_sync(self, file_id: str):
        """
        :param file_id: 文件ID
        :return: 获取文件消息详情
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_file(file_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_msg_history_sync(
        self,
        group_id: Union[int, str],
        message_seq: Union[int, str],
        count: int,
        reverse_order: bool,
    ):
        """
        :param group_id: 群号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取群消息历史记录
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.get_group_msg_history(group_id, message_seq, count, reverse_order)
        )
        result = loop.run_until_complete(task)
        return result

    def set_msg_emoji_like_sync(
        self, message_id: Union[int, str], emoji_id: int, emoji_set: bool
    ):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_set: 设置
        :return: 设置消息表情点赞
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.set_msg_emoji_like(message_id, emoji_id, emoji_set)
        )
        result = loop.run_until_complete(task)
        return result

    def get_friend_msg_history_sync(
        self,
        user_id: Union[int, str],
        message_seq: Union[int, str],
        count: int,
        reverse_order: bool,
    ):
        """
        :param user_id: QQ号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取好友消息历史记录
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.get_friend_msg_history(user_id, message_seq, count, reverse_order)
        )
        result = loop.run_until_complete(task)
        return result

    def get_recent_contact_sync(self, count: int):
        """
        获取的最新消息是每个会话最新的消息
        :param count: 会话数量
        :return: 最近消息列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_recent_contact(count))
        result = loop.run_until_complete(task)
        return result

    def fetch_emoji_like_sync(
        self,
        message_id: Union[int, str],
        emoji_id: str,
        emoji_type: str,
        group_id: Union[int, str] = None,
        user_id: Union[int, str] = None,
        count: int = None,
    ):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_type: 表情类型
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :param count: 数量,可选
        :return: 获取贴表情详情
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.fetch_emoji_like(
                message_id, emoji_id, emoji_type, group_id, user_id, count
            )
        )
        result = loop.run_until_complete(task)
        return result

    def get_forward_msg_sync(self, message_id: str):
        """
        :param message_id: 消息ID
        :return: 获取合并转发消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_forward_msg(message_id))
        result = loop.run_until_complete(task)
        return result

    def send_poke_sync(
        self, user_id: Union[int, str], group_id: Union[int, str] = None
    ):
        """
        :param user_id: QQ号
        :param group_id: 群号,可选，不填则为私聊
        :return: 发送戳一戳
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_poke(user_id, group_id))
        result = loop.run_until_complete(task)
        return result

    def forward_friend_single_msg_sync(self, message_id: str, user_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :param user_id: 发送对象QQ号
        :return: 转发好友消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.forward_friend_single_msg(message_id, user_id))
        result = loop.run_until_complete(task)
        return result

    def send_private_forward_msg_sync(
        self, user_id: Union[int, str], messages: list[str]
    ):
        """
        :param user_id: 发送对象QQ号
        :param messages: 消息列表
        :return: 合并转发私聊消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_private_forward_msg(user_id, messages))
        result = loop.run_until_complete(task)
        return result

    # 群组接口
    def set_group_kick_sync(
        self,
        group_id: Union[int, str],
        user_id: Union[int, str],
        reject_add_request: bool = False,
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param reject_add_request: 是否群拉黑
        :return: 踢出群成员
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.set_group_kick(group_id, user_id, reject_add_request)
        )
        result = loop.run_until_complete(task)
        return result

    def set_group_ban_sync(
        self, group_id: Union[int, str], user_id: Union[int, str], duration: int
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param duration: 禁言时长,单位秒,0为取消禁言
        :return: 群组禁言
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_ban(group_id, user_id, duration))
        result = loop.run_until_complete(task)
        return result

    def get_group_system_msg_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群系统消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_system_msg(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_essence_msg_list_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取精华消息列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_essence_msg_list(group_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_whole_ban_sync(self, group_id: Union[int, str], enable: bool):
        """
        :param group_id: 群号
        :param enable: 是否禁言
        :return: 群组全员禁言
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_whole_ban(group_id, enable))
        result = loop.run_until_complete(task)
        return result

    def set_group_portrait_sync(self, group_id: Union[int, str], file: str):
        """
        :param group_id: 群号
        :param file: 文件路径,支持网络路径和本地路径
        :return: 设置群头像
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_portrait(group_id, file))
        result = loop.run_until_complete(task)
        return result

    def set_group_admin_sync(
        self, group_id: Union[int, str], user_id: Union[int, str], enable: bool
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param enable: 是否设置为管理
        :return: 设置群管理员
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_admin(group_id, user_id, enable))
        result = loop.run_until_complete(task)
        return result

    def set_essence_msg_sync(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 设置精华消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_essence_msg(message_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_card_sync(
        self, group_id: Union[int, str], user_id: Union[int, str], card: str
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param card: 群名片,为空则为取消群名片
        :return: 设置群名片
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_card(group_id, user_id, card))
        result = loop.run_until_complete(task)
        return result

    def delete_essence_msg_sync(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除精华消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.delete_essence_msg(message_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_name_sync(self, group_id: Union[int, str], group_name: str):
        """
        :param group_id: 群号
        :param group_name: 群名
        :return: 设置群名
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_name(group_id, group_name))
        result = loop.run_until_complete(task)
        return result

    def set_group_leave_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 退出群组
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_leave(group_id))
        result = loop.run_until_complete(task)
        return result

    def send_group_notice_sync(
        self, group_id: Union[int, str], content: str, image: str = None
    ):
        """
        :param group_id: 群号
        :param content: 内容
        :param image: 图片路径，可选
        :return: 发送群公告
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_group_notice(group_id, content, image))
        result = loop.run_until_complete(task)
        return result

    def get_group_notice_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群公告
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_notice(group_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_special_title_sync(
        self, group_id: Union[int, str], user_id: Union[int, str], special_title: str
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param special_title: 群头衔
        :return: 设置群头衔
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.set_group_special_title(group_id, user_id, special_title)
        )
        result = loop.run_until_complete(task)
        return result

    def upload_group_file_sync(
        self, group_id: Union[int, str], file: str, name: str, folder_id: str
    ):
        """
        :param group_id: 群号
        :param file: 文件路径
        :param name: 文件名
        :param folder_id: 文件夹ID
        :return: 上传群文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.upload_group_file(group_id, file, name, folder_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_add_request_sync(self, flag: str, approve: bool, reason: str = None):
        """
        :param flag: 请求flag
        :param approve: 是否同意
        :param reason: 拒绝理由
        :return: 处理加群请求
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_add_request(flag, approve, reason))
        result = loop.run_until_complete(task)
        return result

    def get_group_info_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_info(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_info_ex_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息(拓展)
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_info_ex(group_id))
        result = loop.run_until_complete(task)
        return result

    def create_group_file_folder_sync(
        self, group_id: Union[int, str], folder_name: str
    ):
        """
        :param group_id: 群号
        :param folder_name: 文件夹名
        :return: 创建群文件文件夹
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.create_group_file_folder(group_id, folder_name))
        result = loop.run_until_complete(task)
        return result

    def delete_group_file_sync(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 删除群文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.delete_group_file(group_id, file_id))
        result = loop.run_until_complete(task)
        return result

    def delete_group_folder_sync(self, group_id: Union[int, str], folder_id: str):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: 删除群文件文件夹
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.delete_group_folder(group_id, folder_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_file_system_info_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群文件系统信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_file_system_info(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_root_files_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群根目录文件列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_root_files(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_files_by_folder_sync(
        self, group_id: Union[int, str], folder_id: str, file_count: int
    ):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :param file_count: 文件数量
        :return: 获取群文件列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.get_group_files_by_folder(group_id, folder_id, file_count)
        )
        result = loop.run_until_complete(task)
        return result

    def get_group_file_url_sync(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 获取群文件URL
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_file_url(group_id, file_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_list_sync(self, no_cache: bool = False):
        """
        :param no_cache: 不缓存，默认为false
        :return: 获取群列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_list(no_cache))
        result = loop.run_until_complete(task)
        return result

    def get_group_member_info_sync(
        self, group_id: Union[int, str], user_id: Union[int, str], no_cache: bool
    ):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param no_cache: 不缓存
        :return: 获取群成员信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_member_info(group_id, user_id, no_cache))
        result = loop.run_until_complete(task)
        return result

    def get_group_member_list_sync(
        self, group_id: Union[int, str], no_cache: bool = False
    ):
        """
        :param group_id: 群号
        :param no_cache: 不缓存
        :return: 获取群成员列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_member_list(group_id, no_cache))
        result = loop.run_until_complete(task)
        return result

    def get_group_honor_info_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群荣誉信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_honor_info(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_at_all_remain_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群 @全体成员 剩余次数
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_at_all_remain(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_group_ignored_notifies_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群过滤系统消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_ignored_notifies(group_id))
        result = loop.run_until_complete(task)
        return result

    def set_group_sign_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_group_sign(group_id))
        result = loop.run_until_complete(task)
        return result

    def send_group_sign_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_group_sign(group_id))
        result = loop.run_until_complete(task)
        return result

    def get_ai_characters_sync(
        self, group_id: Union[int, str], chat_type: Union[int, str]
    ):
        """
        :param group_id: 群号
        :param chat_type: 聊天类型
        :return: 获取AI语音人物
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_ai_characters(group_id, chat_type))
        result = loop.run_until_complete(task)
        return result

    def send_group_ai_record_sync(
        self, group_id: Union[int, str], character: str, text: str
    ):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 发送群AI语音
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_group_ai_record(group_id, character, text))
        result = loop.run_until_complete(task)
        return result

    def get_ai_record_sync(self, group_id: Union[int, str], character: str, text: str):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 获取AI语音
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_ai_record(group_id, character, text))
        result = loop.run_until_complete(task)
        return result

    def forward_group_single_msg_sync(self, message_id: str, group_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :param group_id: 群号
        :return: 转发群聊消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.forward_group_single_msg(message_id, group_id))
        result = loop.run_until_complete(task)
        return result

    def send_group_forward_msg_sync(
        self, group_id: Union[int, str], messages: list[str]
    ):
        """
        :param group_id: 群号
        :param messages: 消息列表
        :return: 合并转发的群聊消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.send_group_forward_msg(group_id, messages))
        result = loop.run_until_complete(task)
        return result

    # 系统接口
    def get_client_key_sync(self):
        """
        :return: 获取client_key
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_client_key())
        result = loop.run_until_complete(task)
        return result

    def get_robot_uin_range_sync(self):
        """
        :return: 获取机器人QQ号范围
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_robot_uin_range())
        result = loop.run_until_complete(task)
        return result

    def ocr_image_sync(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.ocr_image(image))
        result = loop.run_until_complete(task)
        return result

    def ocr_image_new_sync(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.ocr_image_new(image))
        result = loop.run_until_complete(task)
        return result

    def translate_en2zh_sync(self, words: list):
        """
        :param words: 待翻译的单词列表
        :return: 英文翻译为中文
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.translate_en2zh(words))
        result = loop.run_until_complete(task)
        return result

    def get_login_info_sync(self):
        """
        :return: 获取登录号信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_login_info())
        result = loop.run_until_complete(task)
        return result

    def set_input_status_sync(self, event_type: int, user_id: Union[int, str]):
        """
        :param event_type: 状态类型
        :param user_id: QQ号
        :return: 设置输入状态
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.set_input_status(event_type, user_id))
        result = loop.run_until_complete(task)
        return result

    def download_file_sync(
        self,
        thread_count: int,
        headers: Union[dict, str],
        base64: str = None,
        url: str = None,
        name: str = None,
    ):
        """
        :param thread_count: 下载线程数
        :param headers: 请求头
        :param base64: base64编码的图片,二选一
        :param url: 图片url,二选一
        :param name: 文件名
        :return: 下载文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.download_file(thread_count, headers, base64, url, name)
        )
        result = loop.run_until_complete(task)
        return result

    def get_cookies_sync(self, domain: str):
        """
        :param domain: 域名
        :return: 获取cookies
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_cookies(domain))
        result = loop.run_until_complete(task)
        return result

    def handle_quick_operation_sync(self, context: dict, operation: dict):
        """
        :param context: 事件数据对象
        :param operation: 快速操作对象
        :return: 对事件执行快速操作
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.handle_quick_operation(context, operation))
        result = loop.run_until_complete(task)
        return result

    def get_csrf_token_sync(self):
        """
        :return: 获取 CSRF Token
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_csrf_token())
        result = loop.run_until_complete(task)
        return result

    def del_group_notice_sync(self, group_id: Union[int, str], notice_id: str):
        """
        :param group_id: 群号
        :param notice_id: 通知ID
        :return: 删除群公告
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.del_group_notice(group_id, notice_id))
        result = loop.run_until_complete(task)
        return result

    def get_credentials_sync(self, domain: str):
        """
        :param domain: 域名
        :return: 获取 QQ 相关接口凭证
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_credentials(domain))
        result = loop.run_until_complete(task)
        return result

    def get_model_show_sync(self, model: str):
        """
        :param model: 模型名
        :return: 获取模型显示
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_model_show(model))
        result = loop.run_until_complete(task)
        return result

    def can_send_image_sync(self):
        """
        :return: 检查是否可以发送图片
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.can_send_image())
        result = loop.run_until_complete(task)
        return result

    def nc_get_packet_status_sync(self):
        """
        :return: 获取packet状态
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.nc_get_packet_status())
        result = loop.run_until_complete(task)
        return result

    def can_send_record_sync(self):
        """
        :return: 检查是否可以发送语音
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.can_send_record())
        result = loop.run_until_complete(task)
        return result

    def get_status_sync(self):
        """
        :return: 获取状态
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_status())
        result = loop.run_until_complete(task)
        return result

    def nc_get_rkey_sync(self):
        """
        :return: 获取rkey
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.nc_get_rkey())
        result = loop.run_until_complete(task)
        return result

    def get_version_info_sync(self):
        """
        :return: 获取版本信息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_version_info())
        result = loop.run_until_complete(task)
        return result

    def get_group_shut_list_sync(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群禁言列表
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_group_shut_list(group_id))
        result = loop.run_until_complete(task)
        return result

    # 消息发送接口
    def post_group_msg_sync(
        self,
        group_id: Union[int, str],
        text: str = None,
        face: int = None,
        jsond: str = None,
        markdown: str = None,
        at: Union[int, str] = None,
        reply: Union[int, str] = None,
        music: Union[list, dict] = None,
        dice: bool = False,
        rps: bool = False,
        image: str = None,
        rtf: MessageChain = None,
    ):
        """
        :param group_id: 群号
        :param text: 文本
        :param face: 表情
        :param jsond: JSON
        :param markdown: Markdown
        :param at: at
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :param image: 图片
        :param rtf: 富文本(消息链)
        :return: 发送群消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.post_group_msg(
                group_id,
                text,
                face,
                jsond,
                markdown,
                at,
                reply,
                music,
                dice,
                rps,
                image,
                rtf,
            )
        )
        result = loop.run_until_complete(task)
        return result

    def post_private_msg_sync(
        self,
        user_id: Union[int, str],
        text: str = None,
        face: int = None,
        json: str = None,
        markdown: str = None,
        reply: Union[int, str] = None,
        music: Union[list, dict] = None,
        dice: bool = False,
        rps: bool = False,
        image: str = None,
        rtf: MessageChain = None,
    ):
        """
        :param user_id: QQ号
        :param text: 文本
        :param face: 表情
        :param json: JSON
        :param markdown: Markdown
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :param image: 图片
        :param rtf: 富文本(消息链)
        :return: 发送私聊消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.post_private_msg(
                user_id, text, face, json, markdown, reply, music, dice, rps, image, rtf
            )
        )
        result = loop.run_until_complete(task)
        return result

    def post_group_file_sync(
        self,
        group_id: Union[int, str],
        image: str = None,
        record: str = None,
        video: str = None,
        file: str = None,
        markdown: str = None,
    ):
        """
        :param group_id: 群号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :param markdown: Markdown
        :return: 发送群文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.post_group_file(group_id, image, record, video, file, markdown)
        )
        result = loop.run_until_complete(task)
        return result

    def post_private_file_sync(
        self,
        user_id: Union[int, str],
        image: str = None,
        record: str = None,
        video: str = None,
        file: str = None,
        markdown: str = None,
    ):
        """
        :param user_id: QQ号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :param markdown: Markdown
        :return: 发送私聊文件
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.post_private_file(user_id, image, record, video, file, markdown)
        )
        result = loop.run_until_complete(task)
        return result

    # ncatbot扩展接口
    def send_qqmail_text_sync(
        self,
        receiver: str,
        token: str,
        subject: str,
        content: str,
        sender: str = f"{config.bt_uin}@qq.com" if config.bt_uin else "",
    ):
        """
        :param sender: 发送者QQ邮箱
        :param receiver: 接收者QQ邮箱
        :param token: QQ邮箱授权码
        :param subject: 邮件主题
        :param content: 邮件内容
        :return: 发送结果
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.send_qqmail_text(receiver, token, subject, content, sender)
        )
        result = loop.run_until_complete(task)
        return result
