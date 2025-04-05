import asyncio
import functools
import inspect
from typing import Type, TypeVar, Union

from ncatbot.core.element import MessageChain

T = TypeVar("T")


def async_to_sync(async_func):
    """
    装饰器：将异步函数转换为同步函数
    """

    @functools.wraps(async_func)  # 保留原始函数的文档信息
    def sync_func(*args, **kwargs):
        loop = asyncio.new_event_loop()  # 创建一个新的事件循环
        asyncio.set_event_loop(loop)  # 设置为当前线程的事件循环
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()  # 关闭事件循环

    return sync_func


def add_sync_methods(cls: Type[T]) -> Type[T]:
    """
    类装饰器：为类动态添加同步版本的方法
    """

    for name, method in inspect.getmembers(cls, predicate=inspect.iscoroutinefunction):
        if name.startswith("_"):  # 跳过私有方法
            continue
        sync_method_name = f"{name}_sync"

        # 获取原始方法的签名
        signature = inspect.signature(method)
        # 生成同步方法的文档字符串
        doc = f"""
        同步版本的 {method.__name__}
        {method.__doc__}
        """

        # 动态生成同步方法
        sync_method = async_to_sync(method)
        sync_method.__signature__ = signature  # 设置方法签名
        sync_method.__doc__ = doc  # 设置文档字符串

        setattr(cls, sync_method_name, sync_method)
    return cls


class SYNC_API_MIXIN:
    """
    同步 API 混入类, 仅用于提供文档
    """

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

    def get_msg_sync(self, message_id: Union[int, str]):
        """
        :param message_id: 消息ID
        :return: 获取消息
        """
        loop = asyncio.new_event_loop()
        task = loop.create_task(self.get_msg(message_id))
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
