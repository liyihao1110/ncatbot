# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-14 20:46:30
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import asyncio
import inspect

from pathlib import Path
from typing import List, final
from uuid import UUID
from logging import getLogger

from .api import PluginSysApi

from .pluginsys_err import (
    PluginInitError,
    PluginDataError,
    PluginValidationError,
    PluginWorkspaceError,
    PluginUnloadError
)
from .event import EventBus
from ..utils import ChangeDir
from ..utils import Color
from ..utils import UniversalLoader
from ..utils.universal_data_IO import FileTypeUnknownError, SaveError, LoadError
from ..utils import visualize_tree
from .config import config
from .abc_api import IPluginApi
from .plugin_funcs import (
    EventHandlerMixin,
    TimeTaskMixin,
    PluginFunctionMixin
)

LOG = getLogger('BasePlugin')

class BasePlugin(
        IPluginApi, # 插件功能定义
        EventHandlerMixin, # 事件处理器接口(基础功能)
        PluginFunctionMixin, # 快速添加功能(事件处理器接口扩展功能)
        TimeTaskMixin, # 定时任务接口(额外功能)
    ):
    """插件基类
    
    # 概述
    所有插件必须继承此类来实现插件功能。提供了插件系统所需的基本功能支持。
    
    # 必需属性
    - `name`: 插件名称
    - `version`: 插件版本号
    
    ## 插件标识
    - `name (str)`: 插件名称，必须定义
    - `version (str)`: 插件版本号，必须定义
    - `author (str)`: 作者名称，默认 'Unknown'
    - `info (str)`: 插件描述信息，默认为'这个作者很懒且神秘,没有写一点点描述,真是一个神秘的插件'
    - `dependencies (dict)`: 插件依赖项配置，默认 `{}`
    
    ## 路径与数据
    - `self_path (Path)`: 插件源码所在目录路径
    - `this_file_path (Path)`: 插件主文件路径
    - `meta_data (dict)`: 插件元数据字典
    - `data (UniversalLoader)`: 插件数据管理器实例
    - `save_type`: `data` 数据保存类型 (默认 'json')
    
    ## 目录管理
    - `work_space (ChangeDir)`: 工作目录上下文管理器
    - `self_space (ChangeDir)`: 源码目录上下文管理器
    
    ## 状态标记
    - `first_load (bool)`: 是否为首次加载
    - `debug (bool)`: 是否处于调试模式
    
    # 核心方法
    - `__init__()`: 初始化插件实例，不可重写
    - `__onload__()`: 加载插件，执行初始化，不可重写
    - `__unload__()`: 卸载插件，执行清理，不可重写
    - `_init_()`: 同步初始化钩子，可重写
    - `_close_()`: 同步清理钩子，可重写
    - `on_load()`: 异步初始化钩子，可重写
    - `on_close()`: 异步清理钩子，可重写
    
    # 系统功能
    - `sys (PluginSysApi)`: 插件系统提供的接口
    """

    name: str
    version: str
    dependencies: dict
    author: str = 'Unknown'
    info: str = '这个作者很懒且神秘,没有写一点点描述,真是一个神秘的插件'
    save_type: str = 'yaml'
    
    data: UniversalLoader
    self_path: Path
    this_file_path: Path
    _meta_data: dict = {}
    first_load: bool = True
    debug: bool = False  # 调试模式标记

    @final
    def __init__(self,
                event_bus: EventBus,
                sys_api: PluginSysApi,
                debug: bool = False,
                **kwd):
        """初始化插件实例
        
        Args:
            event_bus: 事件总线实例
            time_task_scheduler: 定时任务调度器
            debug: 是否启用调试模式
            **kwd: 额外的关键字参数,将被设置为插件属性
            
        Raises:
            PluginValidationError: 当缺少插件名称或版本号时抛出
            PluginWorkspaceError: 当工作目录无效时抛出
        """
        # 插件信息检查
        missing_attrs = []
        if not getattr(self,'name',None):
            missing_attrs.append('name')
        if not getattr(self,'version',None):
            missing_attrs.append('version')
        if missing_attrs:
            raise PluginValidationError(self.__class__.__name__, missing_attrs)

        if not getattr(self,'dependencies',None):
            self.dependencies: dict = {}
        # 添加额外属性
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)

        # 固定属性
        TimeTaskMixin.init_api()
        plugin_file = Path(inspect.getmodule(self.__class__).__file__).resolve()
        self.this_file_path = plugin_file
        # 使用插件文件所在目录作为self_path
        self.self_path = plugin_file.parent
        if not self.self_path.exists():
            raise PluginWorkspaceError(self.name, self.self_path, "插件目录不存在")
        self.lock = asyncio.Lock()  # 创建一个异步锁对象

        # 隐藏属性
        self._debug: bool = debug
        self._event_handlers: List[UUID] = []
        self._event_bus: EventBus = event_bus
        # 使用插件目录名作为工作目录名
        plugin_dir_name = self.self_path.name
        self._work_path = Path(config.plugins_data_dir).resolve() / plugin_dir_name
        self._data_path = self._work_path / f"{plugin_dir_name}.{self.save_type}"

        # 检查是否为第一次启动
        self.first_load: bool = False
        if not self._work_path.exists():
            self._work_path.mkdir(parents=True)
            self.first_load = True
        elif not self._data_path.exists():
            self.first_load = True

        if not self._work_path.is_dir():
            raise PluginWorkspaceError(self.name, self._work_path, "不是有效的工作目录")

        # 接口
        self._data = UniversalLoader(self._data_path, self.save_type, realtime_save=True, realtime_load=True)
        self.data = self._data
        self.work_space = ChangeDir(self._work_path)
        self.self_space = ChangeDir(self.self_path)
        self.sys: PluginSysApi = sys_api
        self._meta_data: dict = {
            'name': self.name,
            'version': self.version,
            'dependencies': self.dependencies,
        }

    @property
    def debug(self) -> bool:
        """是否处于调试模式"""
        return self._debug

    @property
    def meta_data(self) -> dict:
        """插件元数据"""
        return self._meta_data.copy()

    @final
    async def __unload__(self, *arg, **kwd):
        """卸载插件时的清理操作
        
        执行插件卸载前的清理工作,保存数据并注销事件处理器
        
        Raises:
            PluginDataError: 保存持久化数据失败时抛出
            PluginUnloadError: 卸载插件时发生未知错误时抛出
        """
        try:
            self.unregister_handlers()
            await asyncio.to_thread(self._close_, *arg, **kwd)
            await self.on_close(*arg, **kwd)
            
            if not self.first_load and self.debug:
                LOG.warning(f"{Color.YELLOW}debug模式下将{Color.RED}取消{Color.RESET}退出时的默认保存行为")
                print(f'{Color.GRAY}{self.name}\n', '\n'.join(visualize_tree(self.data.data)), sep='')
            else:
                await self.data.asave()
                
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise PluginDataError(self.name, "保存", str(e))
        except Exception as e:
            raise PluginUnloadError(self.name, str(e))

    @final
    async def __onload__(self):
        """加载插件时的初始化操作
        
        执行插件加载时的初始化工作,加载数据
        
        Raises:
            PluginDataError: 读取持久化数据失败时抛出
            PluginInitError: 插件初始化时发生未知错误时抛出
        """
        try:
            if isinstance(self.data, dict):
                self.data = self._data
            await self.data.aload()
            if 'meta_data' not in self.data:
                self.data['meta_data'] = self._meta_data
                await self.data.asave()
            
        except (FileTypeUnknownError, LoadError, FileNotFoundError) as e:
            if not self.debug or self.first_load:
                open(self._data_path,'w').write('')
            else:
                raise PluginDataError(self.name, "加载", str(e))
        
        try:
            await asyncio.to_thread(self._init_)
            await self.on_load()
            if self.debug and self.first_load:
                await self.data.asave()
        except Exception as e:
            raise PluginInitError(self.name, str(e))

    async def on_load(self):
        """插件初始化时的子函数,可被子类重写"""
        pass

    async def on_close(self, *arg, **kwd):
        """插件卸载时的子函数,可被子类重写"""
        pass

    def _init_(self):
        """插件初始化时的子函数,可被子类重写"""
        pass

    def _close_(self, *arg, **kwd):
        """插件卸载时的子函数,可被子类重写"""
        pass
