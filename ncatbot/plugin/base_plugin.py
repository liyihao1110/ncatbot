# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-06 19:27:57
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, MIT License 
# -------------------------
import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable, List, final

from ncatbot.core import BotAPI
from ncatbot.plugin.custom_err import PluginLoadError, PluginUnloadError
from ncatbot.plugin.event import Event, EventBus
from ncatbot.utils.change_dir import ChangeDir
from ncatbot.utils.io import (
    FileTypeUnknownError,
    LoadError,
    SaveError,
    UniversalLoader,
)
from ncatbot.utils.literals import PERSISTENT_DIR
from ncatbot.utils.logger import get_log

_log = get_log()


class BasePlugin:
    '''插件基类
    
    所有插件的基类，提供了插件系统的基本功能支持。
    
    属性:
        name (str): 插件名称
        version (str): 插件版本号
        dependencies (dict): 插件依赖项
        meta_data (dict): 插件元数据
        api (BotAPI): API接口处理器
    '''

    name: str
    version: str
    dependencies: dict = {}
    meta_data: dict
    api: BotAPI

    @final
    def __init__(self, event_bus: EventBus, **kwd):
        '''初始化插件实例
        
        Args:
            event_bus (EventBus): 事件总线实例
            **kwd: 额外的关键字参数(将成为类的属性)
        
        Raises:
            ValueError: 当缺少插件名称或版本号时抛出
        '''
        if not self.name:
            raise ValueError("缺失插件名称")
        if not self.version:
            raise ValueError("缺失插件版本号")
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)

        if not self.dependencies:
            self.dependencies = {}

        self.event_bus = event_bus
        self.lock = asyncio.Lock()  # 创建一个异步锁对象
        self.work_path = Path(PERSISTENT_DIR) / self.name
        self._event_handlers = []

        try: 
            self.data = UniversalLoader(self.work_path / f"{self.name}.json") # 好想改成yaml啊
        except FileNotFoundError:
            _log.debug(f"持久化数据文件不存在: {self.name}.json, 数据将被重置")
            self.data = {}
        except LoadError:
            raise RuntimeError(self.name, f"读取持久化数据时出错: {e}")
        except Exception as e:
            _log.error(f"加载持久化数据时出错: {e}")
            raise RuntimeError(self.name, "加载持久化数据时出错")

        if not self.work_path.exists():
            try:
                self.work_path.mkdir(parents=True)
                self.first_load = True  # 表示是第一次启动
            except FileExistsError:
                if not self.work_path.is_dir():
                    raise PluginLoadError(self.name, f"{self.work_path} 不是目录文件夹")
                self.first_load = False

        self.work_space = ChangeDir(self.work_path)

    @final
    async def __unload__(self):
        '''卸载插件时的清理操作
        
        执行插件卸载前的清理工作，保存数据并注销事件处理器
        
        Raises:
            RuntimeError: 保存持久化数据失败时抛出
        '''
        try:
            asyncio.create_task(self._close_())
            await self.on_unload()
            try:
                self.data.save()
            except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
                raise RuntimeError(f"保存持久化数据时出错: {e}")
            self.unregister_handlers()
        except Exception as e:
            PluginUnloadError(self.name,e)

    @final
    async def __onload__(self):
        '''加载插件时的初始化操作
        
        执行插件加载时的初始化工作，加载数据
        
        Raises:
            RuntimeError: 读取持久化数据失败时抛出
        '''
        try:
            asyncio.create_task(self._init_())
            await self.on_load()
            try:
                self.data.load()
            except (FileTypeUnknownError, LoadError, FileNotFoundError) as e:
                raise RuntimeError(f"读取持久化数据时出错: {e}")
        except Exception as e:
            PluginLoadError(self.name,e)

    @final
    def publish_sync(self, event: Event) -> List[Any]:
        '''同步发布事件
        
        Args:
            event (Event): 要发布的事件对象
            
        Returns:
            List[Any]: 事件处理器返回的结果列表
        '''
        return self.event_bus.publish_sync(event)

    @final
    def publish_async(self, event: Event) -> Awaitable[List[Any]]:
        '''异步发布事件
        
        Args:
            event (Event): 要发布的事件对象
            
        Returns:
            Awaitable[List[Any]]: 事件处理器返回的结果列表的可等待对象
        '''
        return self.event_bus.publish_async(event)

    @final
    def register_handler(self, event_type: str, handler: Callable[[Event], Any], priority: int = 0):
        '''注册事件处理器
        
        Args:
            event_type (str): 事件类型
            handler (Callable[[Event], Any]): 事件处理函数
            priority (int, optional): 处理器优先级，默认为0
        '''
        handler_id = self.event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)

    @final
    def unregister_handlers(self):
        '''注销所有已注册的事件处理器'''
        for handler_id in self._event_handlers:
            self.event_bus.unsubscribe(handler_id)

    async def on_load(self):
        '''插件初始化时的钩子函数，可被子类重写'''
        pass

    def _init_(self):
        '''插件初始化时的子函数，可被子类重写'''
        pass

    async def on_unload(self):
        '''插件卸载时的钩子函数，可被子类重写'''
        pass

    def _close_(self):
        '''插件卸载时的子函数，可被子类重写'''
        pass
