# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

from .base import Base


class User(Base):
    def __init__(self, port_or_http: (int, str), sync: bool = False):
        super().__init__(port_or_http=port_or_http, sync=sync)

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
        return await self.post("/set_qq_profile", json=data)

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
        return await self.post("/ArkSharePeer", json=data)

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
        return await self.post("/ArkShareGroup", json=data)

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
        return await self.post("/set_online_status", json=data)

    async def get_friends_with_category(self) -> dict:
        """
        获取好友分组列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658978e0
        :rtype: dict
        """
        return await self.post("/get_friends_with_category")

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
        return await self.post("/set_qq_avatar", json=data)

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
        return await self.post("/send_like", json=data)

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
        return await self.post("/create_collection", json=data)

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
        return await self.post("/set_friend_add_request", json=data)

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
        return await self.post("/set_self_longnick", json=data)

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
        return await self.post("/get_stranger_info", json=data)

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
        return await self.post("/get_friend_list", json=data)

    async def get_profile_like(self) -> dict:
        """
        获取点赞列表
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659197e0
        :rtype: dict
        """
        return await self.post("/get_profile_like")

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
        return await self.post("/fetch_custom_face", json=data)

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
            "file": self.get_media_path(file),
            "name": name
        }
        return await self.post("/upload_private_file", json=data)

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
        return await self.post("/delete_friend", json=data)

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
