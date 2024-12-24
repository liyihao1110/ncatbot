# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

from .base import Base


class System(Base):
    def __init__(self, port_or_http: (int, str), sync: bool = False):
        super().__init__(port_or_http=port_or_http, sync=sync)

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
        return await self.post("/get_online_clients", json=data)

    async def get_robot_uin_range(self) -> dict:
        """
        获取机器人账号范围
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226658975e0
        :rtype: dict
        """
        return await self.post("/get_robot_uin_range")

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
        return await self.post("/ocr_image", json=data)

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
        return await self.post("/translate_en2zh", json=data)

    async def get_login_info(self) -> dict:
        """
        获取登录号信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226656952e0
        :rtype: dict
        """
        return await self.post("/get_login_info")

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
        return await self.post("/set_input_status", json=data)

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
        return await self.post("/download_file", json=data)

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
        return await self.post("/get_cookies", json=data)

    async def get_csrf_token(self) -> dict:
        """
        获取 CSRF Token
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657044e0
        :rtype: dict
        """
        return await self.post("/get_csrf_token")

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
        return await self.post("/_del_group_notice", json=data)

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
        return await self.post("/get_credentials", json=data)

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
        return await self.post("/_get_model_show", json=data)

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
        return await self.post("/_set_model_show", json=data)

    async def can_send_image(self) -> dict:
        """
        检查是否可以发送图片
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657071e0
        :rtype: dict
        """
        return await self.post("/can_send_image")

    async def nc_get_packet_status(self) -> dict:
        """
        获取packet状态
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659280e0
        :rtype: dict
        """
        return await self.post("/nc_get_packet_status")

    async def can_send_record(self) -> dict:
        """
        检查是否可以发送语音
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657080e0
        :rtype: dict
        """
        return await self.post("/can_send_record")

    async def get_status(self) -> dict:
        """
        获取状态
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657083e0
        :rtype: dict
        """
        return await self.post("/get_status")

    async def nc_get_rkey(self) -> dict:
        """
        获取rkey
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659297e0
        :rtype: dict
        """
        return await self.post("/nc_get_rkey")

    async def get_version_info(self) -> dict:
        """
        获取版本信息
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226657087e0
        :rtype: dict
        """
        return await self.post("/get_version_info")

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
