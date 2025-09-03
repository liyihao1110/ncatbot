"""统一注册插件"""

import asyncio
import inspect
from typing import Dict, Callable, TYPE_CHECKING
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.event.event import NcatBotEvent
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core.event.event_data import BaseEventData
from ncatbot.utils import get_log
from .registry import filter
from .trigger.engine import TriggerEngine

if TYPE_CHECKING:
    pass

LOG = get_log(__name__)

class UnifiedRegistryPlugin(NcatBotPlugin):
    """统一注册插件
    
    提供过滤器和命令的统一管理功能。
    保持 plugin.py 简洁，具体逻辑分布在各个子模块中。
    """
    
    name = "UnifiedRegistryPlugin"
    author = "huan-yp"
    desc = "统一的过滤器和命令注册插件"
    version = "2.0.0"
    
    async def on_load(self) -> None:
        """插件加载时的初始化"""
        LOG.info("统一注册插件加载中...")
        
        # 订阅事件
        self.event_bus.subscribe(
            "re:ncatbot.group_message_event|ncatbot.private_message_event", 
            self.handle_message_event, 
            timeout=900
        )
        self.event_bus.subscribe(
            "re:ncatbot.notice_event|ncatbot.request_event", 
            self.handle_legacy_event, 
            timeout=900
        )
        
        # 设置插件管理器
        filter.set_plugin_manager(self)
        
        # 初始化插件映射
        self.func_plugin_map: Dict[Callable, NcatBotPlugin] = {}

        # 触发引擎延迟到首次收到消息时再初始化
        self._trigger_engine = None
        
        await super().on_load()
        LOG.info("统一注册插件加载完成")
    
    async def handle_message_event(self, data: NcatBotEvent) -> bool:
        """处理消息事件（命令和过滤器）"""
        event: BaseMessageEvent = data.data
        
        # 首次收到消息时再初始化触发引擎
        if self._trigger_engine is None:
            self._trigger_engine = TriggerEngine(
                registry=filter,
                plugin=self,
                require_prefix=True,
                prefixes=["/", "!"],
                case_sensitive=False,
                allow_hierarchical=False,
                unknown_command_silent=True,
                enable_filter_scan_when_no_command=True,
            )

        handled = await self._trigger_engine.handle_message_event(event)
        return handled
    
    async def handle_legacy_event(self, data: NcatBotEvent) -> bool:
        """处理通知和请求事件"""
        event: BaseEventData = data.data
        
        if event.post_type == "notice":
            for func in filter.registered_notice_commands:
                await self._execute_function(func, event)
        elif event.post_type == "request":
            for func in filter.registered_request_commands:
                await self._execute_function(func, event)
        
        return False
    
    async def _execute_function(self, func: Callable, *args, **kwargs):
        """执行函数"""
        try:
            # 查找函数所属的插件
            plugin = self._find_plugin_for_function(func)
            if plugin:
                # 将插件实例作为第一个参数
                args = (plugin,) + args
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        except Exception as e:
            LOG.error(f"执行函数 {func.__name__} 时发生错误: {e}")
            return False
    
    def _find_plugin_for_function(self, func: Callable) -> "NcatBotPlugin":
        """查找函数所属的插件"""
        # 缓存查找结果
        if func in self.func_plugin_map:
            return self.func_plugin_map[func]
        
        # 遍历所有插件查找函数归属
        plugins = self.list_plugins(obj=True)
        for plugin in plugins:
            plugin_class = plugin.__class__
            class_methods = [
                value for name, value in inspect.getmembers(plugin_class, predicate=inspect.isfunction)
            ]
            if func in class_methods:
                self.func_plugin_map[func] = plugin
                return plugin
        
        return None
    
    def clear_cache(self):
        """清理缓存"""
        filter.clear()
        self.func_plugin_map.clear()
