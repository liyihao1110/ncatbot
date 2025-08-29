"""
TestClient - 直接可用的测试客户端

集成了 ClientMixin 的所有功能，提供开箱即用的测试环境
"""

from typing import List
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
    
    def __init__(self, *args, **kwargs):
        # 不设置 only_private 模式，支持完整功能
        super().__init__(*args, **kwargs)
        
        # 存储已加载的插件
        self.plugins: List[BasePlugin] = []
        
        LOG.info("TestClient 初始化完成")
    
    def register_plugin(self, plugin: BasePlugin):
        """注册插件到测试客户端
        
        Args:
            plugin: 要注册的插件实例
        """
        self.plugins.append(plugin)
        
        # TODO: 这里应该集成到插件系统的过滤器注册机制
        # 目前简化处理，插件的 @filter.command 装饰器方法需要手动调用
        
        LOG.info(f"插件 {plugin.name} v{plugin.version} 已注册到测试客户端")
        
        # 触发插件的 on_load 生命周期
        try:
            import asyncio
            if hasattr(plugin, 'on_load'):
                # 如果当前有事件循环就直接运行，否则创建新的
                try:
                    loop = asyncio.get_running_loop()
                    # 在已有循环中创建任务
                    loop.create_task(plugin.on_load())
                except RuntimeError:
                    # 没有运行中的循环，创建新的
                    asyncio.run(plugin.on_load())
        except Exception as e:
            LOG.warning(f"插件 {plugin.name} 的 on_load 执行失败: {e}")
    
    def get_registered_plugins(self) -> List[BasePlugin]:
        """获取已注册的插件列表"""
        return self.plugins.copy()
    
    def unregister_plugin(self, plugin: BasePlugin):
        """从测试客户端移除插件
        
        Args:
            plugin: 要移除的插件实例
        """
        if plugin in self.plugins:
            self.plugins.remove(plugin)
            LOG.info(f"插件 {plugin.name} 已从测试客户端移除")
            
            # 触发插件的 on_close 生命周期
            try:
                import asyncio
                if hasattr(plugin, 'on_close'):
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(plugin.on_close())
                    except RuntimeError:
                        asyncio.run(plugin.on_close())
            except Exception as e:
                LOG.warning(f"插件 {plugin.name} 的 on_close 执行失败: {e}")
    
    def clear_plugins(self):
        """清空所有已注册的插件"""
        for plugin in self.plugins.copy():
            self.unregister_plugin(plugin)
        LOG.info("所有插件已清空")
    
    def get_plugin_by_name(self, name: str) -> BasePlugin:
        """根据名称获取插件
        
        Args:
            name: 插件名称
            
        Returns:
            找到的插件实例，如果没找到返回 None
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None
