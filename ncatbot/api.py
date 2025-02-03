import os

from .http import Route, WsRoute
from .status import Status

from typing import Union

def convert(i, message_type):
    if i.startswith('http'):
        return {'type': message_type, 'data': {'file': i}}
    elif i.startswith('base64://'):
        return {'type': message_type, 'data': {'file': i}}
    elif os.path.exists(i):
        return {'type': message_type, 'data': {'file': f'file:///{os.path.abspath(i)}'}}
    else:
        return {'type': message_type, 'data': {'file': f'file:///{i}'}}

class BotAPI:
    def __init__(self, use_ws: bool):
        self.__message = []
        self._http = WsRoute() if use_ws else Route()

    # TODO: 用户接口
    async def set_qq_profile(self, nickname: str, personal_note: str, sex: str):
        """
        :param nickname: 昵称
        :param personal_note: 个性签名
        :param sex: 性别
        :return: 设置账号信息
        """
        return await self._http.post('/set_qq_profile', {
            'nickname': nickname,
            'personal_note': personal_note,
            'sex': sex
        })

    async def get_user_card(self, user_id: int, phone_number: str):
        """
        :param user_id: QQ号
        :param phone_number: 手机号
        :return: 获取用户名片
        """
        return await self._http.post('/ArkSharePeer', {
            'user_id': user_id,
            'phoneNumber': phone_number
        })

    async def get_group_card(self, group_id: int, phone_number: str):
        """
        :param group_id: 群号
        :param phone_number: 手机号
        :return: 获取群名片
        """
        return await self._http.post('/ArkSharePeer', {
            'group_id': group_id,
            'phoneNumber': phone_number
        })

    async def get_share_group_card(self, group_id: str):
        """
        :param group_id: 群号
        :return: 获取群共享名片
        """
        return await self._http.post('/ArkShareGroup', {
            'group_id': group_id
        })

    async def set_online_status(self, status: str):
        """
        :param status: 在线状态
        :return: 设置在线状态
        """
        if hasattr(Status, status):
            status = getattr(Status, status)
        return await self._http.post('/set_online_status', params=dict(status))

    async def get_friends_with_category(self):
        """
        :return: 获取好友列表
        """
        return await self._http.post('/get_friends_with_category',{})

    async def set_qq_avatar(self, avatar: str):
        """
        :param avatar: 头像路径，支持本地路径和网络路径
        :return: 设置头像
        """
        return await self._http.post('/set_qq_avatar', {
            'file': avatar
        })

    async def send_like(self, user_id: str, times: int):
        """
        :param user_id: QQ号
        :param times: 次数
        :return: 发送赞
        """
        return await self._http.post('/send_like', {
            'user_id': user_id,
            'times': times
        })

    async def create_collection(self, rawdata: str, brief: str):
        """
        :param rawdata: 内容
        :param brief: 标题
        :return: 创建收藏
        """
        return await self._http.post('/create_collection', {
            'rawData': rawdata,
            'brief': brief
        })

    async def set_friend_add_request(self, flag: str, approve: bool, remark: str):
        """
        :param flag: 请求ID
        :param approve: 是否同意
        :param remark: 备注
        :return: 设置好友请求
        """
        return await self._http.post('/set_friend_add_request', {
            'flag': flag,
            'approve': approve,
            'remark': remark
        })

    async def set_self_long_nick(self, longnick: str):
        """
        :param longnick: 个性签名内容
        :return: 设置个性签名
        """
        return await self._http.post('/set_self_longnick', {
            'longNick': longnick
        })

    async def get_stranger_info(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取陌生人信息
        """
        return await self._http.post('/get_stranger_info', {
            'user_id': user_id
        })

    async def get_friend_list(self, cache: bool):
        """
        :param cache: 是否使用缓存
        :return: 获取好友列表
        """
        return await self._http.post('/get_friend_list', {
            'no_cache': cache
        })

    async def get_profile_like(self):
        """
        :return: 获取个人资料卡点赞数
        """
        return await self._http.post('/get_profile_like', {})

    async def fetch_custom_face(self, count: int):
        """
        :param count: 数量
        :return: 获取收藏表情
        """
        return await self._http.post('/fetch_custom_face', {
            'count': count
        })

    async def upload_private_file(self, user_id: Union[int, str], file: str, name: str):
        """
        :param user_id: QQ号
        :param file: 文件路径
        :param name: 文件名
        :return: 上传私聊文件
        """
        return await self._http.post('/upload_private_file', {
            'user_id': user_id,
            'file': file,
            'name': name
        })

    async def delete_friend(self, user_id: Union[int, str], friend_id: Union[int, str], temp_block: bool, temp_both_del: bool):
        """
        :param user_id: QQ号
        :param friend_id: 好友ID
        :param temp_block: 拉黑
        :param temp_both_del: 双向删除
        :return: 删除好友
        """
        return await self._http.post('/delete_friend', {
            'user_id': user_id,
            'friend_id': friend_id,
            'temp_block': temp_block,
            'temp_both_del': temp_both_del
        })

    async def nc_get_user_status(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 获取用户状态
        """
        return await self._http.post('/nc_get_user_status', {
            'user_id': user_id
        })

    async def get_mini_app_ark(self, app_json: dict):
        """
        :param app_json: 小程序JSON
        :return: 获取小程序ARK
        """
        return await self._http.post('/get_mini_app_ark', params=app_json)

    # TODO: 消息接口
    async def mark_msg_as_read(self, group_id: Union[int, str]=None, user_id: Union[int, str]=None):
        """
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :return: 设置消息已读
        """
        if group_id:
            return await self._http.post('/mark_msg_as_read', {
                'group_id': group_id
            })
        elif user_id:
            return await self._http.post('/mark_msg_as_read', {
                'user_id': user_id
            })

    async def mark_group_msg_as_read(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 设置群聊已读
        """
        return await self._http.post('/mark_group_msg_as_read', {
            'group_id': group_id
        })

    async def mark_private_msg_as_read(self, user_id: Union[int, str]):
        """
        :param user_id: QQ号
        :return: 设置私聊已读
        """
        return await self._http.post('/mark_private_msg_as_read', {
            'user_id': user_id
        })

    async def mark_all_as_read(self):
        """
        :return: 设置所有消息已读
        """
        return await self._http.post('/_mark_all_as_read', {})

    async def delete_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除消息
        """
        return await self._http.post('/delete_msg', {
            'message_id': message_id
        })

    async def get_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 获取消息
        """
        return await self._http.post('/get_msg', {
            'message_id': message_id
        })

    async def get_image(self, image_id: str):
        """
        :param image_id: 图片ID
        :return: 获取图片消息详情
        """
        return await self._http.post('/get_image', {
            'file_id': image_id
        })

    async def get_record(self, record_id: str, output_type: str = 'mp3'):
        """
        :param record_id: 语音ID
        :param output_type: 输出类型，枚举值:mp3 amr wma m4a spx ogg wav flac,默认为mp3
        :return: 获取语音消息详情
        """
        return await self._http.post('/get_record', {
            'file_id': record_id,
            'out_format': output_type
        })

    async def get_file(self, file_id: str):
        """
        :param file_id: 文件ID
        :return: 获取文件消息详情
        """
        return await self._http.post('/get_file', {
            'file_id': file_id
        })

    async def get_group_msg_history(self, group_id: Union[int, str], message_seq: Union[int, str], count: int, reverse_order: bool):
        """
        :param group_id: 群号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取群消息历史记录
        """
        return await self._http.post('/get_group_msg_history', {
            'group_id': group_id,
            'message_seq': message_seq,
            'count': count,
            'reverseOrder': reverse_order
        })

    async def set_msg_emoji_like(self, message_id: Union[int, str], emoji_id: int, emoji_set: bool):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_set: 设置
        :return: 设置消息表情点赞
        """
        return await self._http.post('/set_msg_emoji_like', {
            'message_id': message_id,
            'emoji_id': emoji_id,
            'set': emoji_set
        })

    async def get_friend_msg_history(self, user_id: Union[int, str], message_seq: Union[int, str], count: int, reverse_order: bool):
        """
        :param user_id: QQ号
        :param message_seq: 消息序号
        :param count: 数量
        :param reverse_order: 是否倒序
        :return: 获取好友消息历史记录
        """
        return await self._http.post('/get_friend_msg_history', {
            'user_id': user_id,
            'message_seq': message_seq,
            'count': count,
            'reverseOrder': reverse_order
        })

    async def get_recent_contact(self, count: int):
        """
        获取的最新消息是每个会话最新的消息
        :param count: 会话数量
        :return: 最近消息列表
        """
        return await self._http.post('/get_recent_contact', {
            'count': count
        })

    async def fetch_emoji_like(self, message_id: Union[int, str], emoji_id: str, emoji_type:str, group_id: Union[int, str]=None, user_id: Union[int, str]=None, count: int=None):
        """
        :param message_id: 消息ID
        :param emoji_id: 表情ID
        :param emoji_type: 表情类型
        :param group_id: 群号,二选一
        :param user_id: QQ号,二选一
        :param count: 数量,可选
        :return: 获取贴表情详情
        """
        if group_id:
            if count:
                return await self._http.post('/fetch_emoji_like', {
                    'message_id': message_id,
                    'emojiId': emoji_id,
                    'emojiType': emoji_type,
                    'group_id': group_id,
                    'count': count
                })
            else:
                return await self._http.post('/fetch_emoji_like', {
                    'message_id': message_id,
                    'emojiId': emoji_id,
                    'emojiType': emoji_type,
                    'group_id': group_id
                })
        elif user_id:
            if count:
                return await self._http.post('/fetch_emoji_like', {
                    'message_id': message_id,
                    'emojiId': emoji_id,
                    'emojiType': emoji_type,
                    'user_id': user_id,
                    'count': count
                })
            else:
                return await self._http.post('/fetch_emoji_like', {
                    'message_id': message_id,
                    'emojiId': emoji_id,
                    'emojiType': emoji_type,
                    'user_id': user_id
                })

    async def get_forward_msg(self, message_id: str):
        """
        :param message_id: 消息ID
        :return: 获取合并转发消息
        """
        return await self._http.post('/get_forward_msg', {
            'message_id': message_id
        })

    async def send_poke(self, user_id: Union[int, str], group_id: Union[int, str]=None):
        """
        :param user_id: QQ号
        :param group_id: 群号,可选，不填则为私聊
        :return: 发送戳一戳
        """
        if group_id:
            return await self._http.post('/send_poke', {
                'user_id': user_id,
                'group_id': group_id
            })
        else:
            return await self._http.post('/send_poke', {
                'user_id': user_id
            })

    # TODO: 群组接口
    async def set_group_kick(self, group_id: Union[int, str], user_id: Union[int, str], reject_add_request: bool = False):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param reject_add_request: 是否群拉黑
        :return: 踢出群成员
        """
        return await self._http.post('/set_group_kick', {
            'group_id': group_id,
            'user_id': user_id,
            'reject_add_request': reject_add_request
        })

    async def set_group_ban(self, group_id: Union[int, str], user_id: Union[int, str], duration: int):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param duration: 禁言时长,单位秒,0为取消禁言
        :return: 群组禁言
        """
        return await self._http.post('/set_group_ban', {
            'group_id': group_id,
            'user_id': user_id,
            'duration': duration
        })

    async def get_group_system_msg(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群系统消息
        """
        return await self._http.post('/get_group_system_msg', {
            'group_id': group_id
        })

    async def get_essence_msg_list(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取精华消息列表
        """
        return await self._http.post('/get_essence_msg_list', {
            'group_id': group_id
        })

    async def set_group_whole_ban(self, group_id: Union[int, str], enable: bool):
        """
        :param group_id: 群号
        :param enable: 是否禁言
        :return: 群组全员禁言
        """
        return await self._http.post('/set_group_whole_ban', {
            'group_id': group_id,
            'enable': enable
        })

    async def set_group_portrait(self, group_id: Union[int, str], file: str):
        """
        :param group_id: 群号
        :param file: 文件路径,支持网络路径和本地路径
        :return: 设置群头像
        """
        return await self._http.post('/set_group_portrait', {
            'group_id': group_id,
            'file': file
        })

    async def set_group_admin(self, group_id: Union[int, str], user_id: Union[int, str], enable: bool):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param enable: 是否设置为管理
        :return: 设置群管理员
        """
        return await self._http.post('/set_group_admin', {
            'group_id': group_id,
            'user_id': user_id,
            'enable': enable
        })

    async def set_essence_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 设置精华消息
        """
        return await self._http.post('/set_essence_msg', {
            'message_id': message_id
        })

    async def set_group_card(self, group_id: Union[int, str], user_id: Union[int, str], card: str):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param card: 群名片,为空则为取消群名片
        :return: 设置群名片
        """
        return await self._http.post('/set_group_card', {
            'group_id': group_id,
            'user_id': user_id,
            'card': card
        })

    async def delete_essence_msg(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 删除精华消息
        """
        return await self._http.post('/delete_essence_msg', {
            'message_id': message_id
        })

    async def set_group_name(self, group_id: Union[int, str], group_name: str):
        """
        :param group_id: 群号
        :param group_name: 群名
        :return: 设置群名
        """
        return await self._http.post('/set_group_name', {
            'group_id': group_id,
            'group_name': group_name
        })

    async def set_group_leave(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 退出群组
        """
        return await self._http.post('/set_group_leave', {
            'group_id': group_id
        })

    async def send_group_notice(self, group_id: Union[int, str], content: str, image: str = None):
        """
        :param group_id: 群号
        :param content: 内容
        :param image: 图片路径，可选
        :return: 发送群公告
        """
        if image:
            return await self._http.post('/_send_group_notice', {
                'group_id': group_id,
                'content': content,
                'image': image
            })
        else:
            return await self._http.post('/_send_group_notice', {
                'group_id': group_id,
                'content': content
            })

    async def get_group_notice(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群公告
        """
        return await self._http.post('/_get_group_notice', {
            'group_id': group_id
        })

    async def set_group_special_title(self, group_id: Union[int, str], user_id: Union[int, str], special_title: str):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param special_title: 群头衔
        :return: 设置群头衔
        """
        return await self._http.post('/set_group_special_title', {
            'group_id': group_id,
            'user_id': user_id,
            'special_title': special_title
        })

    async def upload_group_file(self, group_id: Union[int, str], file: str, name: str, folder_id: str):
        """
        :param group_id: 群号
        :param file: 文件路径
        :param name: 文件名
        :param folder_id: 文件夹ID
        :return: 上传群文件
        """
        return await self._http.post('/upload_group_file', {
            'group_id': group_id,
            'file': file,
            'name': name,
            'folder_id': folder_id
        })

    async def set_group_add_request(self, flag: str, approve: bool, reason: str = None):
        """
        :param flag: 请求flag
        :param approve: 是否同意
        :param reason: 拒绝理由
        :return: 处理加群请求
        """
        if approve:
            return await self._http.post('/set_group_add_request', {
                'flag': flag,
                'approve': approve
            })
        else:
            return await self._http.post('/set_group_add_request', {
                'flag': flag,
                'approve': approve,
                'reason': reason
            })

    async def get_group_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息
        """
        return await self._http.post('/get_group_info', {
            'group_id': group_id
        })

    async def get_group_info_ex(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群信息(拓展)
        """
        return await self._http.post('/get_group_info_ex', {
            'group_id': group_id
        })

    async def create_group_file_folder(self, group_id: Union[int, str], folder_name: str):
        """
        :param group_id: 群号
        :param folder_name: 文件夹名
        :return: 创建群文件文件夹
        """
        return await self._http.post('/create_group_file_folder', {
            'group_id': group_id,
            'folder_name': folder_name
        })

    async def delete_group_file(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 删除群文件
        """
        return await self._http.post('/delete_group_file', {
            'group_id': group_id,
            'file_id': file_id
        })

    async def delete_group_folder(self, group_id: Union[int, str], folder_id: str):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: 删除群文件文件夹
        """
        return await self._http.post('/delete_group_folder', {
            'group_id': group_id,
            'folder_id': folder_id
        })

    async def get_group_file_system_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群文件系统信息
        """
        return await self._http.post('/get_group_file_system_info', {
            'group_id': group_id
        })

    async def get_group_root_files(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群根目录文件列表
        """
        return await self._http.post('/get_group_root_files', {
            'group_id': group_id
        })

    async def get_group_files_by_folder(self, group_id: Union[int, str], folder_id: str, file_count: int):
        """
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :param file_count: 文件数量
        :return: 获取群文件列表
        """
        return await self._http.post('/get_group_files_by_folder', {
            'group_id': group_id,
            'folder_id': folder_id,
            'file_count': file_count
        })

    async def get_group_file_url(self, group_id: Union[int, str], file_id: str):
        """
        :param group_id: 群号
        :param file_id: 文件ID
        :return: 获取群文件URL
        """
        return await self._http.post('/get_group_file_url', {
            'group_id': group_id,
            'file_id': file_id
        })

    async def get_group_list(self, no_cache: bool = False):
        """
        :param no_cache: 不缓存，默认为false
        :return: 获取群列表
        """
        return await self._http.post('/get_group_list', {
            'no_cache': no_cache
        })

    async def get_group_member_info(self, group_id: Union[int, str], user_id: Union[int, str], no_cache: bool):
        """
        :param group_id: 群号
        :param user_id: QQ号
        :param no_cache: 不缓存
        :return: 获取群成员信息
        """
        return await self._http.post('/get_group_member_info', {
            'group_id': group_id,
            'user_id': user_id,
            'no_cache': no_cache
        })

    async def get_group_member_list(self, group_id: Union[int, str], no_cache: bool=False):
        """
        :param group_id: 群号
        :param no_cache: 不缓存
        :return: 获取群成员列表
        """
        return await self._http.post('/get_group_member_list', {
            'group_id': group_id,
            'no_cache': no_cache
        })

    async def get_group_honor_info(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群荣誉信息
        """
        return await self._http.post('/get_group_honor_info', {
            'group_id': group_id
        })

    async def get_group_at_all_remain(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群 @全体成员 剩余次数
        """
        return await self._http.post('/get_group_at_all_remain', {
            'group_id': group_id
        })

    async def get_group_ignored_notifies(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群过滤系统消息
        """
        return await self._http.post('/get_group_ignored_notifies', {
            'group_id': group_id
        })

    async def set_group_sign(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        return await self._http.post('/set_group_sign', {
            'group_id': group_id
        })

    async def send_group_sign(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 群打卡
        """
        return await self._http.post('/send_group_sign', {
            'group_id': group_id
        })

    async def get_ai_characters(self, group_id: Union[int, str], chat_type: Union[int, str]):
        """
        :param group_id: 群号
        :param chat_type: 聊天类型
        :return: 获取AI语音人物
        """
        return await self._http.post('/get_ai_characters', {
            'group_id': group_id,
            'chat_type': chat_type
        })

    async def send_group_ai_record(self, group_id: Union[int, str], character: str, text: str):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 发送群AI语音
        """
        return await self._http.post('/send_group_ai_record', {
            'group_id': group_id,
            'character': character,
            'text': text
        })

    async def get_ai_record(self, group_id: Union[int, str], character: str, text: str):
        """
        :param group_id: 群号
        :param character: AI语音人物,即character_id
        :param text: 文本
        :return: 获取AI语音
        """
        return await self._http.post('/get_ai_record', {
            'group_id': group_id,
            'character': character,
            'text': text
        })

    # TODO: 系统接口
    async def get_client_key(self):
        """
        :return: 获取client_key
        """
        return await self._http.post('/get_clientkey', {})

    async def get_robot_uin_range(self):
        """
        :return: 获取机器人QQ号范围
        """
        return await self._http.post('/get_robot_uin_range', {})

    async def ocr_image(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        return await self._http.post('/ocr_image', {
            'image': image
        })

    async def ocr_image_new(self, image: str):
        """
        :param image: 图片路径，支持本地路径和网络路径
        :return: OCR 图片识别
        """
        return await self._http.post('/.ocr_image', {
            'image': image
        })

    async def translate_en2zh(self, words: list):
        """
        :param words: 待翻译的单词列表
        :return: 英文翻译为中文
        """
        return await self._http.post('/translate_en2zh', {
            'words': words
        })

    async def get_login_info(self):
        """
        :return: 获取登录号信息
        """
        return await self._http.post('/get_login_info', {})

    async def set_input_status(self, event_type: int, user_id: Union[int, str]):
        """
        :param event_type: 状态类型
        :param user_id: QQ号
        :return: 设置输入状态
        """
        return await self._http.post('/set_input_status', {
            'eventType': event_type,
            'user_id': user_id
        })

    async def download_file(self, thread_count: int, headers: Union[dict, str], base64: str=None, url: str=None, name: str=None):
        """
        :param thread_count: 下载线程数
        :param headers: 请求头
        :param base64: base64编码的图片,二选一
        :param url: 图片url,二选一
        :param name: 文件名
        :return: 下载文件
        """
        if base64:
            if name:
                return await self._http.post('/download_file', {
                    'thread_count': thread_count,
                    'headers': headers,
                    'base64': base64,
                    'name': name
                })
            else:
                return await self._http.post('/download_file', {
                    'thread_count': thread_count,
                    'headers': headers,
                    'base64': base64
                })
        elif url:
            if name:
                return await self._http.post('/download_file', {
                    'thread_count': thread_count,
                    'headers': headers,
                    'url': url,
                    'name': name
                })
            else:
                return await self._http.post('/download_file', {
                    'thread_count': thread_count,
                    'headers': headers,
                    'url': url
                })

    async def get_cookies(self, domain: str):
        """
        :param domain: 域名
        :return: 获取cookies
        """
        return await self._http.post('/get_cookies', {
            'domain': domain
        })

    async def handle_quick_operation(self, context: dict, operation: dict):
        """
        :param context: 事件数据对象
        :param operation: 快速操作对象
        :return: 对事件执行快速操作
        """
        return await self._http.post('/.handle_quick_operation', {
            'context': context,
            'operation': operation
        })

    async def get_csrf_token(self):
        """
        :return: 获取 CSRF Token
        """
        return await self._http.post('/get_csrf_token', {})

    async def del_group_notice(self, group_id: Union[int, str], notice_id: str):
        """
        :param group_id: 群号
        :param notice_id: 通知ID
        :return: 删除群公告
        """
        return await self._http.post('/_del_group_notice', {
            'group_id': group_id,
            'notice_id': notice_id
        })

    async def get_credentials(self, domain: str):
        """
        :param domain: 域名
        :return: 获取 QQ 相关接口凭证
        """
        return await self._http.post('/get_credentials', {
            'domain': domain
        })

    async def get_model_show(self, model: str):
        """
        :param model: 模型名
        :return: 获取模型显示
        """
        return await self._http.post('/_get_model_show', {
            'model': model
        })

    async def can_send_image(self):
        """
        :return: 检查是否可以发送图片
        """
        return await self._http.post('/can_send_image', {})

    async def nc_get_packet_status(self):
        """
        :return: 获取packet状态
        """
        return await self._http.post('/nc_get_packet_status', {})

    async def can_send_record(self):
        """
        :return: 检查是否可以发送语音
        """
        return await self._http.post('/can_send_record', {})

    async def get_status(self):
        """
        :return: 获取状态
        """
        return await self._http.post('/get_status', {})

    async def nc_get_rkey(self):
        """
        :return: 获取rkey
        """
        return await self._http.post('/nc_get_rkey', {})

    async def get_version_info(self):
        """
        :return: 获取版本信息
        """
        return await self._http.post('/get_version_info', {})

    async def get_group_shut_list(self, group_id: Union[int, str]):
        """
        :param group_id: 群号
        :return: 获取群禁言列表
        """
        return await self._http.post('/get_group_shut_list', {
            'group_id': group_id
        })

    async def post_group_msg(self,
                             group_id: Union[int, str],
                             text: str = None,
                             face: int = None,
                             json: str = None,
                             at: Union[int, str] = None,
                             reply: Union[int, str] = None,
                             music: Union[list, dict] = None,
                             dice: bool = False,
                             rps: bool = False,
                             ):
        """
        :param group_id: 群号
        :param text: 文本
        :param face: 表情
        :param json: JSON
        :param at: at
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :return: 发送群消息
        """
        message: list = []
        if text:
            message.append({'type': 'text', 'data': {'text': text}})
        if face:
            message.append({'type': 'face', 'data': {'id': face}})
        if json:
            message.append({'type': 'json', 'data': {'data': json}})
        if at:
            message.append({'type': 'at', 'data': {'qq': at}})
        if reply:
            message.insert(0, {'type': 'reply', 'data': {'id': reply}})
        if music:
            if isinstance(music, list):
                message.append({'type': 'music', 'data': {'type': music[0], 'id': music[1]}})
            elif isinstance(music, dict):
                message.append({'type': 'music', 'data': music})
        if dice:
            message.append({'type': 'dice'})
        if rps:
            message.append({'type': 'rps'})

        if not message:
            return {'code': 0, 'msg': '消息不能为空'}
        params = {'group_id': group_id, 'message': message}
        return await self._http.post('/send_group_msg', json=params)

    async def post_private_msg(self,
                               user_id: Union[int, str],
                               text: str = None,
                               face: int = None,
                               json: str = None,
                               reply: Union[int, str] = None,
                               music: Union[list, dict] = None,
                               dice:bool = False,
                               rps: bool = False,
                               ):
        """
        :param user_id: QQ号
        :param text: 文本
        :param face: 表情
        :param json: JSON
        :param reply: 回复
        :param music: 音乐
        :param dice: 骰子
        :param rps: 猜拳
        :return: 发送私聊消息
        """
        message: list = []
        if text:
            message.append({'type': 'text', 'data': {'text': text}})
        if face:
            message.append({'type': 'face', 'data': {'id': face}})
        if json:
            message.append({'type': 'json', 'data': {'data': json}})
        if reply:
            message.insert(0, {'type': 'reply', 'data': {'id': reply}})
        if music:
            if isinstance(music, list):
                message.append({'type': 'music', 'data': {'type': music[0], 'id': music[1]}})
            elif isinstance(music, dict):
                message.append({'type': 'music', 'data': music})
        if dice:
            message.append({'type': 'dice'})
        if rps:
            message.append({'type': 'rps'})

        if not message:
            return {'code': 0, 'msg': '消息不能为空'}
        params = {'user_id': user_id, 'message': message}
        return await self._http.post('/send_private_msg', json=params)

    async def post_group_file(self,
                              group_id: Union[int, str],
                              image: str = None,
                              record: str = None,
                              video: str = None,
                              file: str = None,
                              ):
        """
        :param group_id: 群号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :return: 发送群文件
        """
        message: list = []

        if image:
            message.append(convert(image, 'image'))
        elif record:
            message.append(convert(record, 'record'))
        elif video:
            message.append(convert(video, 'video'))
        elif file:
            message.append(convert(file, 'file'))
        else:
            return {'code': 0, 'msg': '请至少选择一种文件'}

        params = {'group_id': group_id, 'message': message}
        return await self._http.post('/send_group_msg', json=params)

    async def post_private_file(self,
                              user_id: Union[int, str],
                              image: str = None,
                              record: str = None,
                              video: str = None,
                              file: str = None,
                              ):
        """
        :param user_id: QQ号
        :param image: 图片
        :param record: 语音
        :param video: 视频
        :param file: 文件
        :return: 发送私聊文件
        """
        message: list = []

        if image:
            message.append(convert(image, 'image'))
        elif record:
            message.append(convert(record, 'record'))
        elif video:
            message.append(convert(video, 'video'))
        elif file:
            message.append(convert(file, 'file'))
        else:
            return {'code': 0, 'msg': '请至少选择一种文件'}

        params = {'user_id': user_id, 'message': message}
        return await self._http.post('/send_private_msg', json=params)

    async def send_group_msg(self, group_id: Union[int, str], reply: str = None):
        if reply:
            self.__message.insert(0, {"type":"reply","data":{"id":reply}})
        params = {"group_id": group_id, "message": self.__message}
        return await self._http.post('/send_group_msg', params)

    async def send_private_msg(self, user_id: Union[int, str], reply: str = None):
        if reply:
            self.__message.insert(0, {"type":"reply","data":{"id":reply}})
        params = {"user_id": user_id, "message": self.__message}
        return await self._http.post('/send_private_msg', params)

    def add_text(self, text):
        self.__message.append({"type":"text","data":{"text":text}})
        return self

    def add_face(self, face_id):
        self.__message.append({"type":"face","data":{"id":face_id}})
        return self

    def add_image(self, file):
        self.__message.append(convert(file, 'image'))
        return self

    def add_at(self, user_id):
        self.__message.append({"type":"at","data":{"qq":user_id}})
        return self