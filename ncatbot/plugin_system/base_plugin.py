# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-08 11:30:52
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import yaml
import aiofiles
import inspect
from uuid import UUID
from pathlib import Path
from typing import Any, Dict, List, Set, Union, final, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor
from ncatbot.utils import get_log

from .config import config
from .event import EventBus, NcatBotEvent
from .decorator import RegisterServer
from .rbac import RBACManager
from ncatbot.utils import status

if TYPE_CHECKING:
    from .loader import PluginLoader

LOG = get_log("BasePlugin")


class BasePlugin:
    """插件系统基础类，提供插件生命周期管理和事件处理功能。

    插件开发者应继承此类并实现生命周期方法：
    - on_load(): 插件加载时异步初始化
    - on_reload(): 插件重载时异步处理
    - on_close(): 插件卸载时异步清理
    - _init_(): 插件加载时同步初始化
    - _reinit_(): 插件重载时同步处理
    - _close_(): 插件卸载时同步清理

    属性:
        name (str): 插件名称(必须)
        version (str): 插件版本(必须)
        author (str): 插件作者，默认"Unknown"
        description (str): 插件描述，默认占位文本
        dependencies (Dict[str, str]): 依赖插件及版本要求
        config (dict): 插件配置数据(YAML格式)
        first_load (bool): 首次加载标记
        debug (bool): 调试模式标志

    运行时属性:
        workspace (Path): 插件工作目录路径
        source_dir (Path): 插件源码目录路径
        data_file (Path): 插件数据文件路径
        main_file (Path): 插件主文件路径
    """
    # -------- 插件元数据 --------
    name: str
    version: str
    author: str = "Unknown"
    description: str = "这个作者很懒且神秘，没有写一点点描述，真是一个神秘的插件"
    dependencies: Dict[str, str] = {}  # 格式: {"other_plugin": ">=1.0"}
    config: dict = {}   # 使用YAML格式存储的配置数据

    # -------- 运行时属性 --------
    first_load: bool = True
    debug: bool = False

    # -------- 内部属性 --------
    _handlers_id: Set[UUID]  # 注册的事件处理器ID集合
    _loader: 'PluginLoader' # 插件加载器

    def __init__(self, event_bus: EventBus, *, debug: bool = False, rbac_manager: RBACManager = None, plugin_loader: 'PluginLoader' = None, **extras: Any) -> None:
        """初始化插件实例。

        仅做最轻量的装配，不做任何IO操作。

        Args:
            event_bus: 事件总线实例
            debug: 是否启用调试模式，默认为False
            extras: 额外注入的属性键值对

        Raises:
            ValueError: 如果未定义name或version属性
        """
        # 基础校验
        if not getattr(self, "name", None):
            raise ValueError(f"{self.__class__.__name__} 必须定义 name 属性")
        if not getattr(self, "version", None):
            raise ValueError(f"{self.__class__.__name__} 必须定义 version 属性")

        # 保存外部注入
        self._event_bus = event_bus
        self._loader = plugin_loader
        self._debug = debug
        for k, v in extras.items():
            setattr(self, k, v)
            
        # 初始化属性
        self.api = status.global_api
        self._handlers_id = set()
        self._rbac_manager = rbac_manager

        # 路径计算（只算不建）
        self.main_file = Path(inspect.getmodule(self.__class__).__file__).resolve()
        base_plugin_dir = Path(config.plugins_dir).resolve()

        try:
            relative_parts = self.main_file.relative_to(base_plugin_dir).parts
            plugin_root_name = relative_parts[0]
            self.source_dir = base_plugin_dir / plugin_root_name
        except ValueError:
            self.source_dir = self.main_file.parent

        self.workspace = Path(config.plugins_data_dir) / self.name
        self.data_file = self.workspace / f"{self.name}.yaml"

        # 首次运行标记
        self.first_load = not self.data_file.exists()

    # ------------------------------------------------------------------
    # 生命周期方法 (插件开发者应重写这些方法)
    # ------------------------------------------------------------------
    async def on_load(self) -> None:
        """插件加载时异步初始化钩子。"""

    async def on_reload(self) -> None:
        """插件重新加载时异步处理钩子。"""

    async def on_close(self, *args: Any, **kw: Any) -> None:
        """插件卸载时异步清理钩子。"""

    def _init_(self) -> None:
        """插件加载时同步初始化钩子。"""

    def _reinit_(self) -> None:
        """插件重新加载时同步处理钩子。"""

    def _close_(self, *args: Any, **kw: Any) -> None:
        """插件卸载时同步清理钩子。"""

    # ------------------------------------------------------------------
    # 框架专用方法 (禁止插件开发者重写)
    # ------------------------------------------------------------------
    @final
    async def __onload__(self) -> None:
        """由框架在加载插件时调用。"""
        self.workspace.mkdir(exist_ok=True, parents=True)
        if not self.first_load:
            async with aiofiles.open(self.data_file, "r", encoding="utf-8") as f:
                content = await f.read()
                self.config = yaml.safe_load(content) or {}
        else:
            self.config = {}   # 首次加载使用空配置
        
        self._init_()
        await self.on_load()

    @final
    async def __unload__(self, *a: Any, **kw: Any) -> None:
        """由框架在卸载插件时调用。"""
        try:
            self.unregister_all_handler()
            self._close_(*a, **kw)
            await self.on_close(*a, **kw)
        except Exception as e:
            LOG.exception("插件 %s 卸载错误：%s: %s", self.name, type(e), e)
        finally:
            # 保存配置到磁盘
            async with aiofiles.open(self.data_file, "w", encoding="utf-8") as f:
                await f.write(yaml.dump(
                    self.config, 
                    sort_keys=False, 
                    allow_unicode=True
                ))

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------
    @property
    def event_bus(self) -> EventBus:
        """获取事件总线实例。"""
        return self._event_bus
    
    @property
    def debug(self) -> bool:
        """获取调试模式状态。"""
        return self._debug
    
    @property
    def meta_data(self) -> Dict[str, Any]:
        """获取插件元数据字典。"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies,
            "config": self.config
        }.copy()
    
    @property  
    def thread_pool(self) -> ThreadPoolExecutor:
        """获取线程池实例（当前返回None，需子类实现）。"""
        return None

    # ------------------------------------------------------------------
    # 事件系统接口
    # ------------------------------------------------------------------
    def register_handler(self, event_type: str, handler: callable, priority: int = 0, timeout: float = None) -> UUID:
        """注册事件处理器。
        
        Args:
            event_type: 要监听的事件类型
            handler: 事件处理函数
            priority: 处理优先级，数值越大优先级越高
            
        Returns:
            注册生成的事件处理器UUID
        """
        handler_id = self.event_bus.subscribe(event_type, handler, priority, timeout, plugin=self)
        self._handlers_id.add(handler_id)
        LOG.debug(f"{self.name} 注册事件处理器 {event_type}: {handler.__name__}")
        return handler_id

    def unregister_handler(self, handler_id: UUID) -> bool:
        """注销事件处理器。
        
        Args:
            handler_id: 要注销的事件处理器UUID
            
        Returns:
            是否成功注销
        """
        if handler_id in self._handlers_id:
            self._handlers_id.remove(handler_id)
            LOG.debug(f"{self.name} 卸载事件处理器 {handler_id}")
            return self.event_bus.unsubscribe(handler_id)
        return False

    def unregister_all_handler(self) -> None:
        """注销本插件所有事件处理器。"""
        for handler_id in tuple(self._handlers_id):
            self.unregister_handler(handler_id)

    async def publish(self, event_type: str, data: Any) -> List[Any]:
        """发布事件。
        
        Args:
            event_type: 事件类型
            data: 事件数据
            
        Returns:
            所有处理器的返回结果列表
        """
        return await self.event_bus.publish(NcatBotEvent(event_type, data))

    async def request(self, addr: str, data: dict = None) -> Any:
        """发送请求并等待响应。
        
        Args:
            addr: 请求地址(SERVER-前缀的服务)
            data: 请求数据
            
        Returns:
            第一个响应结果，如果没有响应则返回None
        """
        result = await self.event_bus.publish(NcatBotEvent(f"SERVER-{addr}", data))
        return result[0] if result else None

    def get_plugin(self, name: str) -> 'BasePlugin':
        """根据插件名称获取插件实例。

        Args:
            name: 插件名称。

        Returns:
            插件实例；若不存在则返回 None。
        """
        self._loader.get_plugin(name)
    
    def list_plugins(self, *, obj: bool = False) -> List[Union[str, 'BasePlugin']]:
        """插件列表

        Args:
            obj: 实例模式

        Returns:
            插件实例/插件名称列表
        """
        self._loader.list_plugins(obj=obj)
        