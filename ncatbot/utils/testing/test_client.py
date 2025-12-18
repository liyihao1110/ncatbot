"""
TestClient - 直接可用的测试客户端

集成了 ClientMixin 的所有功能，提供开箱即用的测试环境
"""

from .client_mixin import ClientMixin
from typing import Type, TypeVar
from ncatbot.core.client import BotClient
from ncatbot.plugin_system import BasePlugin
from ncatbot.utils import get_log
from ncatbot.utils import run_coroutine

T = TypeVar("T")
LOG = get_log("TestClient")


class TestClient(ClientMixin, BotClient):
    """测试客户端 - 集成了所有测试功能的客户端

    开箱即用，自动启用 Mock 模式，提供插件注册功能
    """

    def __init__(self, load_plugin=False, *args, **kwargs):
        # 不设置 only_private 模式，支持完整功能
        BotClient.__init__(self, *args, **kwargs)
        ClientMixin.__init__(self, *args, **kwargs)
        self.skip_plugin_load = not load_plugin

        LOG.info("TestClient 初始化完成")

    def start(self, **kwargs):
        if "bt_uin" not in kwargs:
            kwargs["bt_uin"] = "123456789"
        BotClient.start(self, skip_plugin_load=self.skip_plugin_load, **kwargs)

    def register_plugin(self, plugin_class: Type[BasePlugin]):
        run_coroutine(
            self.plugin_loader.load_plugin_by_class, plugin_class, plugin_class.name
        )

    def unregister_plugin(self, plugin: BasePlugin):
        """从测试客户端移除插件

        Args:
            plugin: 要移除的插件实例
        """
        if plugin in self.get_registered_plugins():
            run_coroutine(self.plugin_loader.unload_plugin, plugin.name)
            LOG.info(f"插件 {plugin.name} 已从测试客户端移除")
        else:
            LOG.warning(f"插件 {plugin.name} 未在测试客户端中注册")
