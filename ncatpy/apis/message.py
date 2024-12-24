# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

from .base import Base


class Message(Base):
    def __init__(self, port_or_http: (int, str), sync: bool = False):
        super().__init__(port_or_http=port_or_http, sync=sync)

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
        return await self.post("/mark_msg_as_read", json=data)

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
        return await self.post("/mark_group_msg_as_read", json=data)

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
        return await self.post("/mark_private_msg_as_read", json=data)

    async def mark_all_as_read(self) -> dict:
        """
        _设置所有消息已读
        https://apifox.com/apidoc/shared-c3bab595-b4a3-429b-a873-cbbe6b9a1f6a/226659194e0
        :rtype: dict
        """
        return await self.post("/_mark_all_as_read")

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
        return await self.post("/delete_msg", json=data)

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
        return await self.post("/get_msg", json=data)

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
        return await self.post("/get_image", json=data)

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
        return await self.post("/get_record", json=data)

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
        return await self.post("/get_file", json=data)

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
        return await self.post("/get_group_msg_history", json=data)

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
        return await self.post("/set_msg_emoji_like", json=data)

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
        return await self.post("/get_friend_msg_history", json=data)

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
        return await self.post("/get_recent_contact", json=data)

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
        return await self.post("/fetch_emoji_like", json=data)

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
        return await self.post("/get_forward_msg", json=data)

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
