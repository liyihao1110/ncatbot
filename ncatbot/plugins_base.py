from abc import ABC, abstractmethod

from ncatbot.message import GroupMessage, PrivateMessage


class PluginBase(ABC):
    @abstractmethod
    async def on_group_message(self, msg: GroupMessage):
        """处理群消息"""
        pass

    @abstractmethod
    async def on_private_message(self, msg: PrivateMessage):
        """处理私聊消息"""
        pass

    @abstractmethod
    async def on_notice(self, msg):
        """处理通知"""
        pass

    @abstractmethod
    async def on_request(self, msg):
        """处理请求"""
        pass
