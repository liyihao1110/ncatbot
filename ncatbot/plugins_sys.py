
"""
具有事件处理能力的插件系统

Raises:
    ValueError：未提供插件名称或版本时引发。
    PluginDependencyError：缺少插件依赖项时引发。
    PluginVersionError：当插件版本不符合所需版本时引发。
    PluginCircularDependencyError：当插件之间存在循环依赖关系时引发。
"""
import asyncio
import importlib
import inspect
import re
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Type, Sequence
from types import MappingProxyType
from weakref import WeakMethod, ref, ReferenceType
from .UniversalDataIO import UniversalLoader

# ------------------- 系统异常 -------------------
# 没用上就是懒的检查

class PluginSystemError(Exception):
    """插件系统的基础异常类,所有插件相关的异常都应继承自此类"""
    pass

class PluginCircularDependencyError(PluginSystemError):
    """当插件之间存在循环依赖时抛出此异常"""
    def __init__(self, dependency_chain : Sequence[str]):
        self.dependency_chain = dependency_chain
        super().__init__(f"检测到插件循环依赖: {' -> '.join(dependency_chain)}->... 请检查插件之间的依赖关系")

class PluginNotFoundError(PluginSystemError):
    """当尝试加载或使用一个不存在的插件时抛出此异常"""
    def __init__(self, plugin_name : str):
        self.plugin_name = plugin_name
        super().__init__(f"插件 '{plugin_name}' 未找到 请检查插件名称是否正确,以及插件是否已正确安装")


class PluginLoadError(PluginSystemError):
    """当插件加载过程中出现错误时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"无法加载插件 '{plugin_name}' : {reason}")


class PluginInitializationError(PluginSystemError):
    """当插件初始化失败时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 初始化失败: {reason}")


class PluginDependencyError(PluginSystemError):
    """当插件依赖未满足时抛出此异常"""
    def __init__(self, plugin_name : str, missing_dependency):
        self.plugin_name = plugin_name
        self.missing_dependency = missing_dependency
        super().__init__(f"插件 '{plugin_name}' 缺少必要的依赖项: {'|'.join(missing_dependency)}")


class PluginConfigurationError(PluginSystemError):
    """当插件配置不正确时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 配置错误: {reason}")


class PluginExecutionError(PluginSystemError):
    """当插件执行过程中出现错误时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 执行失败: {reason}")


class PluginCompatibilityError(PluginSystemError):
    """当插件与当前系统或环境不兼容时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 与当前环境不兼容: {reason}")


class PluginAlreadyLoadedError(PluginSystemError):
    """当尝试重复加载同一个插件时抛出此异常"""
    def __init__(self, plugin_name : str):
        self.plugin_name = plugin_name
        super().__init__(f"插件 '{plugin_name}' 已经被加载,无法重复加载")


class PluginUnloadError(PluginSystemError):
    """当插件卸载过程中出现错误时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"无法卸载插件 '{plugin_name}': {reason}")


class PluginSecurityError(PluginSystemError):
    """当插件存在安全问题时抛出此异常"""
    def __init__(self, plugin_name : str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 存在安全问题: {reason}")


class PluginVersionError(PluginSystemError):
    """当插件版本不满足要求时抛出此异常"""
    def __init__(self, plugin_name : str, required_plugin_name : str, required_version : str, actual_version : Version):
        self.plugin_name = plugin_name
        self.required_plugin_name = required_plugin_name
        self.required_version = required_version
        self.actual_version = actual_version
        super().__init__(f"插件 '{required_plugin_name}' 版本不满足要求'{plugin_name}'需要 '{required_plugin_name}' 的版本: {required_version},实际版本: {actual_version.public}")

# ----------------- 系统配置常量 -----------------
PLUGINS_DIR = "plugins"             # 插件目录
PERSISTENT_DIR = "data"             # 插件私有数据目录
EVENT_QUEUE_MAX_SIZE = 1000         # 事件队列最大长度
META_CONFIG_PATH = './config.yaml'  # 元事件，所有插件一份(只读)
# @Todo ALLOW_RAW_FILE_ACCESS = False       # 是否允许直接文件访问
# ----------------- 增强事件对象 -----------------
@dataclass
class Event:
    """
    事件对象,用于在事件总线上传递事件数据
    """
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    _stopped: bool = False
    results: List[Any] = field(default_factory=list)
    source: Optional[str] = None

    def stop_propagation(self):
        """
        停止事件传播,防止事件继续被后续处理器处理
        """
        self._stopped = True

    def add_result(self, result: Any):
        """
        向事件结果列表中添加处理结果
        """
        self.results.append(result)

# ----------------- 完整事件总线实现 -----------------
class EventBus:
    """
    事件总线,用于管理和分发事件
    """
    def __init__(self):
        """
        初始化事件总线,设置事件处理器存储结构和事件队列
        """
        self._exact_handlers: Dict[str, List[Tuple[int, Callable]]] = defaultdict(list)
        self._regex_handlers: List[Tuple[Pattern, int, Callable]] = []
        self._execution_order: Dict[str, List[Callable]] = defaultdict(list)
        self.exception_handlers: List[Callable] = []
        self._queues: Dict[str, asyncio.Queue] = defaultdict(lambda: asyncio.Queue(maxsize=EVENT_QUEUE_MAX_SIZE))
        self._processing_tasks: Dict[str, asyncio.Task] = {}

    def _get_plugin_name(self, handler: Callable) -> str:
        """
        获取处理器所属插件名称
        """
        try:
            if inspect.ismethod(handler):
                return handler.__self__.name
            if isinstance(handler, (ref, WeakMethod, ReferenceType)):
                obj = handler()
                return getattr(obj, 'name', '') if obj else ''
            if hasattr(handler, '__self__') and isinstance(handler.__self__, BasePlugin):
                return handler.__self__.name
            return getattr(handler, '_plugin_name', '')
        except Exception:
            return ''

    def subscribe(self, event_type: str, handler: Callable, priority: int = 0):
        """
        订阅事件,支持正则表达式匹配
        :param event_type: 事件类型,支持正则表达式前缀为're:'
        :param handler: 事件处理器
        :param priority: 事件处理器优先级,数值越高优先级越高
        """
        # 处理弱引用
        if inspect.ismethod(handler):
            handler_ref = WeakMethod(handler)
        elif inspect.isfunction(handler):
            handler_ref = ref(handler)
        else:
            handler_ref = handler

        if event_type.startswith("re:"):
            pattern = re.compile(event_type[3:])
            self._regex_handlers.append((pattern, priority, handler_ref))
        else:
            self._exact_handlers[event_type].append((priority, handler_ref))
        
        self._rebuild_execution_order(event_type)

    def _rebuild_execution_order(self, event_type: str):
        """
        重建事件处理器的执行顺序,考虑优先级和插件名称排序
        """
        # 精确匹配处理
        exact_entries = sorted(
            self._exact_handlers[event_type],
            key=lambda x: (-x[0], self._get_plugin_name(x[1]).lower())
        )
        exact_handlers = [h for _, h in exact_entries]

        # 正则匹配处理
        regex_handlers = []
        for pattern, priority, handler in self._regex_handlers:
            if pattern.search(event_type):
                regex_handlers.append((-priority, self._get_plugin_name(handler).lower(), handler))

        regex_handlers.sort(key=lambda x: (x[0], x[1]))
        regex_handlers = [h for _, _, h in regex_handlers]

        # 合并处理顺序: 精确匹配优先于正则匹配
        combined = []
        seen = set()
        for h in exact_handlers + regex_handlers:
            handler = h() if isinstance(h, (ref, WeakMethod, ReferenceType)) else h
            if handler and id(handler) not in seen:
                combined.append(handler)
                seen.add(id(handler))

        self._execution_order[event_type] = combined

    async def _process_event(self, event: Event):
        """
        核心事件处理逻辑,依次调用事件处理器
        """
        for handler in self._execution_order.get(event.type, []):
            if event._stopped:
                break

            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                event.add_result({"error": str(e)})
                for eh in self.exception_handlers:
                    try:
                        if inspect.iscoroutinefunction(eh):
                            await eh(e, event)
                        else:
                            eh(e, event)
                    except Exception:
                        pass

    async def publish_sync(self, event: Event) -> List[Any]:
        """
        同步发布事件,等待事件处理完成
        :param event: 要发布的事件对象
        :return: 事件处理结果列表
        """
        await self._queues[event.type].put(event)
        await self._process_event(event)
        return event.results

    async def publish_async(self, event: Event) -> None:
        """
        异步发布事件,后台处理
        :param event: 要发布的事件对象
        """
        await self._queues[event.type].put(event)
        if self._queues[event.type].qsize() == 1:  # 避免重复创建任务
            self._processing_tasks[event.type] = asyncio.create_task(self._process_queue(event.type))

    async def _process_queue(self, event_type: str):
        """
        处理指定事件队列中的事件
        """
        while not self._queues[event_type].empty():
            event = await self._queues[event_type].get()
            await self._process_event(event)
            self._queues[event_type].task_done()

# ----------------- 完整插件基类实现 -----------------
class BasePlugin:
    """
    插件基类，所有插件应继承此类
    
    没有非常严格的限制，请开发者注意
    """
    name: str = field(default_factory=str)
    version: str = field(default_factory=str)
    dependencies: Dict[str, str] = field(default_factory=dict) # 插件: 版本需求
    meta_data: Dict[str, Any] # 只读字典(非强制)
    data: Dict[str, Any] = field(default_factory=dict) # 插件系统维护: 每个插件独立
    lock = asyncio.Lock() # 资源保护: 使用 with self.lock: 来确保对共享资源的访问是线程安全的

    def __post_init__(self):
        # 额外的检查或设置
        if not self.name:
            raise ValueError("插件名称不能为空")
        if not self.version:
            raise ValueError("版本信息不能为空")
        if not self.data:
            self.data = dict()
        if not self.dependencies:
            self.dependencies = {}

    def __init__(self, event_bus: EventBus, **kwargs):
        """
        初始化插件,绑定事件总线
        """
        self.event_bus = event_bus
        self.data = self._load_persistent_data()
        self.meta_data: Dict[str, Any] = MappingProxyType(UniversalLoader(META_CONFIG_PATH).load().data) # 只读字典
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        if kwargs:
            for key, var in kwargs:
                setattr(self, key, var)

    def _load_persistent_data(self) -> Dict:
        """
        加载插件的私有数据
        """
        data_dir = Path(PERSISTENT_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{self.name.title()}.json"
        
        if not file_path.exists():
            return {}

        try:
            return UniversalLoader(file_path)
        except Exception as e:
            PluginSystemError(f"加载数据时出错（{self.name}）: {e}")
            return {}

    def _save_persistent_data(self):
        """
        保存插件的私有数据
        """
        data_dir = Path(PERSISTENT_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{self.name.lower()}.yaml"
        
        try:
            with UniversalLoader(file_path) as f:
                f:UniversalLoader
                f.data = self.data
                f.save()
        except Exception as e:
            PluginSystemError(f"保存数据时出错（{self.name}）: {str(e)}")

    def register_handler(self, event_type: str, handler: Callable, priority: int = 0):
        """
        注册事件处理器到事件总线
        :param event_type: 事件类型
        :param handler: 事件处理器
        :param priority: 事件处理器优先级
        """
        self.event_bus.subscribe(event_type, handler, priority)
        self._event_handlers[event_type].append(handler)

    async def on_load(self):
        """
        插件加载时调用的生命周期方法
        """
        pass

    async def on_unload(self):
        """
        插件卸载时调用的生命周期方法
        """
        self._save_persistent_data()
        self._unregister_handlers()

    def _unregister_handlers(self):
        """
        注销插件注册的所有事件处理器
        """
        for event_type, handlers in self._event_handlers.items():
            for handler in handlers:
                # 转换为原始处理器的弱引用形式
                if inspect.ismethod(handler):
                    weak_ref = WeakMethod(handler)
                elif inspect.isfunction(handler):
                    weak_ref = ref(handler)
                else:
                    weak_ref = handler
                
                # 从事件总线移除
                self.event_bus._exact_handlers[event_type] = [
                    (p, h) for (p, h) in self.event_bus._exact_handlers[event_type]
                    if h != weak_ref
                ]
                # 更新正则处理器
                self.event_bus._regex_handlers = [
                    (p, pri, h) for (p, pri, h) in self.event_bus._regex_handlers
                    if h != weak_ref
                ]
        self._event_handlers.clear()

# ----------------- 完整插件加载器实现 -----------------
class PluginLoader:
    """
    插件加载器,用于加载、卸载和管理插件
    """
    def __init__(self):
        """
        初始化插件加载器
        """
        self.plugins: Dict[str, BasePlugin] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._version_constraints: Dict[str, Dict[str, str]] = {}

    def _validate_plugin(self, plugin_cls: Type[BasePlugin]) -> bool:
        """
        验证插件类是否符合规范
        """
        return all(hasattr(plugin_cls, attr) for attr in ('name', 'version', 'dependencies'))

    def _build_dependency_graph(self, plugins: List[Type[BasePlugin]]):
        """
        构建插件依赖关系图
        """
        self._dependency_graph.clear()
        self._version_constraints.clear()
        
        for plugin in plugins:
            self._dependency_graph[plugin.name] = set(plugin.dependencies.keys())
            self._version_constraints[plugin.name] = plugin.dependencies.copy()

    def _validate_dependencies(self):
        """
        验证插件依赖关系是否满足
        """
        # 遍历所有插件及其版本约束
        for plugin_name, deps in self._version_constraints.items():
            # 遍历当前插件的所有依赖项及其版本约束
            for dep_name, constraint in deps.items():
                # 检查依赖项是否存在于已安装的插件中
                if dep_name not in self.plugins:
                    raise PluginDependencyError(plugin_name, dep_name)
                
                # 获取已安装依赖项的版本
                installed_ver = parse_version(self.plugins[dep_name].version)
                # 检查已安装版本是否满足版本约束
                if not SpecifierSet(constraint).contains(installed_ver):
                    raise PluginVersionError(dep_name, plugin_name, constraint, installed_ver)

    def _resolve_load_order(self) -> List[str]:
        """
        解析插件加载顺序,确保依赖关系正确
        """
        in_degree = {k: 0 for k in self._dependency_graph}
        adj_list = defaultdict(list)

        # 遍历依赖图,构建入度表和邻接表
        for dependent, dependencies in self._dependency_graph.items():
            # dependent 是当前插件,dependencies 是它依赖的插件列表
            for dep in dependencies:
                adj_list[dep].append(dependent)
                in_degree[dependent] += 1

        queue = deque([k for k, v in in_degree.items() if v == 0])
        load_order = []

        # 拓扑排序
        while queue:
            node = queue.popleft()
            load_order.append(node)
            # 遍历该插件的所有依赖者
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检测是否存在循环依赖
        print(self._dependency_graph)
        for plugin_name, dependency in self._dependency_graph.items():
            print(set(self._dependency_graph.keys()) , set(dependency))
            if not dependency.issubset(self._dependency_graph.keys()):
                raise PluginDependencyError(plugin_name, dependency)
            
        if len(load_order) != len(self._dependency_graph):
            missing = set(self._dependency_graph.keys()) - set(load_order)
            # 抛出异常,提示循环依赖的插件
            raise PluginCircularDependencyError(missing)

        # 返回最终的加载顺序
        return load_order

    async def load_plugins(self, plugins: List[Type[BasePlugin]]):
        """
        加载插件
        :param plugins: 插件类列表
        """
        valid_plugins = [p for p in plugins if self._validate_plugin(p)]
        self._build_dependency_graph(valid_plugins)
        load_order = self._resolve_load_order()
        
        # 实例化所有插件
        event_bus = EventBus()
        temp_plugins = {}
        for name in load_order:
            plugin_cls = next(p for p in valid_plugins if p.name == name)
            temp_plugins[name] = plugin_cls(event_bus)
        
        # 验证依赖版本
        self.plugins = temp_plugins
        self._validate_dependencies()
        
        # 初始化插件
        for name in load_order:
            await self.plugins[name].on_load()

    async def unload_plugin(self, plugin_name: str):
        """
        卸载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            return

        await self.plugins[plugin_name].on_unload()
        del self.plugins[plugin_name]

    async def reload_plugin(self, plugin_name: str):
        """
        重新加载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            # 有点想报个错
            pass

        old = self.plugins[plugin_name]
        await old.on_unload()
        
        module = importlib.import_module(old.__class__.__module__)
        importlib.reload(module)
        
        new_cls = getattr(module, old.__class__.name)
        new_plugin = new_cls(old.event_bus)
        await new_plugin.on_load()
        self.plugins[plugin_name] = new_plugin










# ----------------- 使用示例 -----------------
class HiPlugin(BasePlugin):
    """
    测试插件
    """
    name = "Hi"
    version = "1.0.0.dev"
    # dependencies = {"Network": ">=2.0.0"}

    async def on_load(self):
        pass

    def handle_log(self, event: Event):
        pass

class LoggerPlugin(BasePlugin):
    """
    日志插件,用于记录日志事件
    """
    name = "Logger"
    version = "2.0.0"
    dependencies = {"Hi": ">=1.0.0"}

    async def on_load(self):
        """
        加载时注册日志事件处理器
        """
        self.register_handler("re:^log\.", self.handle_log, priority=10)

    def handle_log(self, event: Event):
        """
        处理日志事件,将日志数据保存到私有存储中
        """
        self.data.setdefault('logs', []).append(event.data)
        print(f"[日志] {event.type}: {event.data}")

class NetworkPlugin(BasePlugin):
    """
    网络插件,用于处理网络请求事件
    """
    name = "Network"
    dependencies = {"Logger": ">=2.0.0"}

    async def on_load(self):
        """
        加载时注册网络请求事件处理器
        """
        self.register_handler("network.request", self.handle_request)

    async def handle_request(self, event: Event):
        """
        处理网络请求事件,返回模拟的响应结果
        """
        event.add_result({"status": 200})
        print(f"[网络] 处理请求: {event.data}")

# ----------------- 测试用例 -----------------
async def main():
    """
    测试用例,加载插件并发布事件
    """
    loader = PluginLoader()
    await loader.load_plugins([LoggerPlugin, NetworkPlugin, HiPlugin])
    
    # 发布事件
    event = Event("log.system", {"message": "系统已启动"})
    await loader.plugins["Logger"].event_bus.publish_async(event)
    
    network_event = Event("network.request", {"url": "/api/data"})
    results = await loader.plugins["Network"].event_bus.publish_sync(network_event)
    print("同步结果:", results)
    
    await loader.unload_plugin("Network")

if __name__ == "__main__":
    asyncio.run(main())