"""
TestClient - 直接可用的测试客户端

集成了 ClientMixin 的所有功能，提供开箱即用的测试环境
"""

from typing import List, Type
from ncatbot.core.client import BotClient
from ncatbot.plugin_system.event import EventBus
from ncatbot.plugin_system import BasePlugin
from ncatbot.utils import get_log
from .client_mixin import ClientMixin

LOG = get_log("TestClient")

class TestClient(ClientMixin, BotClient):
    """测试客户端 - 集成了所有测试功能的客户端
    
    开箱即用，自动启用 Mock 模式，提供插件注册功能
    """
    
    def __init__(self, load_plugin=False, *args, **kwargs):
        # 不设置 only_private 模式，支持完整功能
        BotClient.__init__(self, skip_plugin_load=not load_plugin, *args, **kwargs)
        ClientMixin.__init__(self, *args, **kwargs)
        
        LOG.info("TestClient 初始化完成")
    
    def register_plugin(self, plugin_class: Type[BasePlugin]):
        self.plugin_loader.load_plugin(plugin_class)

    def get_registered_plugins(self) -> List[BasePlugin]:
        return list(self.plugin_loader.plugins.values())
    
    def unregister_plugin(self, plugin: BasePlugin):
        """从测试客户端移除插件
        
        Args:
            plugin: 要移除的插件实例
        """
        if plugin in self.get_registered_plugins():
            self.plugin_loader.unload_plugin(plugin.name)
            LOG.info(f"插件 {plugin.name} 已从测试客户端移除")
        else:
            LOG.warning(f"插件 {plugin.name} 未在测试客户端中注册")    
