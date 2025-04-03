# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-23 21:50:37
# @Description  : 猫娘慢慢看，鱼鱼不急
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import asyncio
import inspect
from pathlib import Path
from typing import final

from ncatbot.core import BotAPI
from ncatbot.plugin.base_plugin.builtin_function import BuiltinFuncMixin
from ncatbot.plugin.base_plugin.event_handler import EventHandlerMixin
from ncatbot.plugin.base_plugin.time_task_scheduler import SchedulerMixin
from ncatbot.plugin.event import Conf, Func
from ncatbot.utils import (
    PERSISTENT_DIR,
    ChangeDir,
    Color,
    PluginLoadError,
    TimeTaskScheduler,
    UniversalLoader,
    get_log,
    visualize_tree,
)
from ncatbot.utils.file_io import (
    FileTypeUnknownError,
    LoadError,
    SaveError,
)

LOG = get_log("BasePlugin")


class BasePlugin(EventHandlerMixin, SchedulerMixin, BuiltinFuncMixin):
    """插件基类

    # 概述
    所有插件必须继承此类来实现插件功能。提供了插件系统所需的基本功能支持。

    # 必需属性
    - `name`: 插件名称
    - `version`: 插件版本号

    # 可选属性
    - `author`: 作者名称 (默认 'Unknown')
    - `info`: 插件描述 (默认为空)
    - `dependencies`: 依赖项配置 (默认 `{}`)
    - `save_type`: 数据保存类型 (默认 'json')

    # 功能特性

    ## 生命周期钩子
    - `_init_()`: 同步初始化
    - `on_load()`: 异步初始化
    - `_close_()`: 同步清理
    - `on_close()`: 异步清理

    ## 数据持久化
    - `data`: `UniversalLoader` 实例，管理插件数据
    - `work_space`: 工作目录上下文管理器
    - `self_space`: 源码目录上下文管理器

    ## 事件处理
    - `register_handler()`: 注册事件处理器
    - `unregister_handlers()`: 注销所有事件处理器

    ## 定时任务
    - `add_scheduled_task()`: 添加定时任务
    - `remove_scheduled_task()`: 移除定时任务

    # 属性说明

    ## 插件标识
    - `name (str)`: 插件名称，必须定义
    - `version (str)`: 插件版本号，必须定义
    - `author (str)`: 作者名称，默认 'Unknown'
    - `info (str)`: 插件描述信息，默认为空
    - `dependencies (dict)`: 插件依赖项配置，默认 `{}`

    ## 路径与数据
    - `self_path (Path)`: 插件源码所在目录路径
    - `this_file_path (Path)`: 插件主文件路径
    - `meta_data (dict)`: 插件元数据字典
    - `data (UniversalLoader)`: 插件数据管理器实例
    - `api (WebSocketHandler)`: API调用接口实例

    ## 目录管理
    - `work_space (ChangeDir)`: 工作目录上下文管理器
    - `self_space (ChangeDir)`: 源码目录上下文管理器

    ## 状态标记
    - `first_load (bool)`: 是否为首次加载
    - `debug (bool)`: 是否处于调试模式

    # 属性方法
    - `@property debug (bool)`: 获取调试模式状态

    # 核心方法
    - `__init__()`: 初始化插件实例
    - `__onload__()`: 加载插件，执行初始化
    - `__unload__()`: 卸载插件，执行清理
    - `on_load()`: 异步初始化钩子，可重写
    - `on_close()`: 异步清理钩子，可重写
    - `_init_()`: 同步初始化钩子，可重写
    - `_close_()`: 同步清理钩子，可重写
    """

    name: str
    version: str
    dependencies: dict
    author: str = "Unknown"
    info: str = "这个作者很懒且神秘,没有写一点点描述,真是一个神秘的插件"
    save_type: str = "json"

    self_path: Path
    this_file_path: Path
    meta_data: dict
    api: BotAPI
    first_load: bool = "True"

    @final
    def __init__(
        self,
        event_bus,
        time_task_scheduler: TimeTaskScheduler,
        debug: bool = False,
        **kwd,
    ):
        """初始化插件实例

        Args:
            event_bus: 事件总线实例
            time_task_scheduler: 定时任务调度器
            debug: 是否启用调试模式
            **kwd: 额外的关键字参数,将被设置为插件属性

        Raises:
            ValueError: 当缺少插件名称或版本号时抛出
            PluginLoadError: 当工作目录无效时抛出
        """
        # 为了类型注解添加的动态导入

        # 插件信息检查
        if not getattr(self, "name", None):
            raise ValueError("缺失插件名称")
        if not getattr(self, "version", None):
            raise ValueError("缺失插件版本号")
        if not getattr(self, "dependencies", None):
            self.dependencies = {}
        # 添加额外属性
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)

        # 固定属性
        plugin_file = Path(inspect.getmodule(self.__class__).__file__).resolve()
        # plugins_dir = Path(PLUGINS_DIR).resolve()
        self.this_file_path = plugin_file
        # 使用插件文件所在目录作为self_path
        self.self_path = plugin_file.parent
        self.lock = asyncio.Lock()  # 创建一个异步锁对象
        self.funcs: list[Func] = []
        self.configs: list[Conf] = []

        # 隐藏属性
        self._debug = debug
        self._event_handlers = []
        self._event_bus = event_bus
        self._time_task_scheduler = time_task_scheduler
        # 使用插件目录名作为工作目录名
        plugin_dir_name = self.self_path.name
        self._work_path = Path(PERSISTENT_DIR).resolve() / plugin_dir_name
        self._data_path = self._work_path / f"{plugin_dir_name}.{self.save_type}"

        # 检查是否为第一次启动
        self.first_load = False
        if not self._work_path.exists():
            self._work_path.mkdir(parents=True)
            self.first_load = True
        elif not self._data_path.exists():
            self.first_load = True

        if not self._work_path.is_dir():
            raise PluginLoadError(self.name, f"{self._work_path} 不是目录文件夹")

        self.data = UniversalLoader(self._data_path, self.save_type)
        self.work_space = ChangeDir(self._work_path)
        self.self_space = ChangeDir(self.self_path)

    @property
    def debug(self) -> bool:
        """是否处于调试模式"""
        return self._debug

    @final
    async def __unload__(self, *arg, **kwd):
        """卸载插件时的清理操作

        执行插件卸载前的清理工作,保存数据并注销事件处理器

        Raises:
            RuntimeError: 保存持久化数据失败时抛出
        """
        self.unregister_handlers()
        await asyncio.to_thread(self._close_, *arg, **kwd)
        await self.on_close(*arg, **kwd)
        try:
            if self.debug:
                LOG.warning(
                    f"{Color.YELLOW}debug模式{Color.RED}取消{Color.RESET}退出时的保存行为"
                )
                print(
                    f"{Color.GRAY}{self.name}\n",
                    "\n".join(visualize_tree(self.data.data)),
                    sep="",
                )
            else:
                self.data.save()
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise RuntimeError(self.name, f"保存持久化数据时出错: {e}")

    @final
    async def __onload__(self):
        """加载插件时的初始化操作

        执行插件加载时的初始化工作,加载数据

        Raises:
            RuntimeError: 读取持久化数据失败时抛出
        """
        # load时传入的参数作为属性被保存在self中
        if isinstance(self.data, (dict, list)):
            self.data = UniversalLoader(self._data_path, self.save_type)
            self.data.data = self.data
        try:
            self.data.load()
        except (FileTypeUnknownError, LoadError, FileNotFoundError):
            if self.debug:
                pass
            else:
                open(self._data_path, "w").write("")
                self.data.save()
                self.data.load()
        await asyncio.to_thread(self._init_)
        await self.on_load()

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
