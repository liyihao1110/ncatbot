#!/usr/bin/env python3
"""
NcatBot 指令注册器与过滤器最小 mock 实现
运行后直接输入消息测试
"""
import asyncio
import inspect
import re
import shlex
from typing import Dict, List, Callable, Any, Optional, Tuple
import enum

from attr import has

# ------------------- NcatBot API Stub -------------------

class EventMessageType(enum.Enum):
    PRIVATE_MESSAGE = 1
    GROUP_MESSAGE   = 2
    ALL             = 3

class PermissionType(enum.Enum):
    USER  = 0
    ADMIN = 1

class BaseMessageEvent:
    """mock 事件对象"""
    def __init__(self, message_str: str, sender_name: str = "User"):
        self.message_str = message_str
        self._sender_name = sender_name

    def get_sender_name(self) -> str:
        return self._sender_name

    def plain_result(self, text: str):
        # 简单生成器包装
        return text

class Context:
    pass

# ------------------- 过滤器装饰器 -------------------

class _FilterStore:
    """存储每个注册函数身上的过滤器元数据"""
    def __init__(self):
        self.cmd: Optional[str] = None
        self.alias: set[str] = set()
        self.group_path: Tuple[str, ...] = ()
        self.event_types: List[EventMessageType] = []
        self.permission: Optional[PermissionType] = None

class _CommandGroupNode:
    """指令组树节点"""
    def __init__(self, name: str):
        self.name = name
        self.decorator: Optional[_GroupDecorator] = None
        self.children: Dict[str, _CommandGroupNode] = {}
        self.commands: Dict[str, Callable] = {}
        self.parent: Optional[_CommandGroupNode] = None

# ------------------- 帮助生成器 -------------------
def _build_usage(cmd: str, func: Callable) -> str:
    """根据函数生成一行用法提示"""
    sig = inspect.signature(func)
    params = []
    for p in list(sig.parameters.values())[1:]:  # 跳过 event
        name = p.name
        if p.annotation != inspect.Parameter.empty:
            name += f"({p.annotation.__name__})"
        if p.default != inspect.Parameter.empty:
            name = f"[{name}={p.default}]"
        params.append(name)
    attach = func.__decs__ if hasattr(func, "__decs__") else ""
    return f"/{cmd} " + " ".join(params) + attach

class Filter:
    """装饰器集合"""
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
        self.store: Dict[Callable, _FilterStore] = {}
        self.command_group_map: Dict[str, _CommandGroupNode] = {}

    # ---------- 装饰器 ----------
    def command(self, name: str, *, alias: set[str] | None = None):
        def deco(func: Callable):
            st = self.store.setdefault(func, _FilterStore())
            st.cmd = name
            st.alias = alias or set()
            setattr(func, "_ncatbot_filter", st)
            return func
        return deco

    def command_group(self, name: str, *, alias: set[str] | None = None):
        """创建/定位一个指令组节点"""
        node = _ensure_group(name)
        self.command_group_map[name] = node
        return _GroupDecorator(node)

    def event_message_type(self, *types: EventMessageType):
        def deco(func: Callable):
            st = self.store.setdefault(func, _FilterStore())
            st.event_types.extend(types)
            return func
        return deco

    def permission_type(self, perm: PermissionType):
        def deco(func: Callable):
            st = self.store.setdefault(func, _FilterStore())
            st.permission = perm
            return func
        return deco

    def build_help(self):
        help_text = "普通指令:\n"
        # 普通指令
        for func, st in self.store.items():
            if st.cmd:
                help_text += f"/{st.cmd} - {_build_usage(st.cmd, func)}\n"
        # 指令组
        if self.command_group_map:
            help_text += "指令组(输入 /<指令组名> 查看指令组具体帮助):\n"
            for name, node in self.command_group_map.items():
                help_text += f"/{name}\n"
        return help_text
        
        

class _GroupDecorator:
    """指令组装饰器，支持 .command / .group 继续嵌套"""
    def __init__(self, node: _CommandGroupNode):
        self._node = node
        self.store: Dict[Callable, _FilterStore] = {}
        self.command_group_map: Dict[str, _CommandGroupNode] = {}

    def command(self, name: str, *, alias: set[str] | None = None):
        def deco(func: Callable):
            st = _FilterStore()
            st.cmd = name
            st.alias = alias or set()
            st.group_path = _build_path(self._node)
            setattr(func, "_ncatbot_filter", st)
            self._node.commands[name] = func
            return func
        return deco

    def group(self, name: str, *, alias: set[str] | None = None):
        child = _ensure_group(name, parent=self._node)
        child.decorator = self
        self.command_group_map[name] = child
        return _GroupDecorator(child)

    def build_help(self):
        help_text = "指令:\n"
        for func, st in self.store.items(): 
            if st.cmd:
                help_text += f"/{st.cmd} - {_build_usage(st.cmd, func)}\n"
        if self.command_group_map:
            help_text += "指令组(输入 /<指令组名> 查看指令组具体帮助):\n"
            for name, node in self.command_group_map.items():
                help_text += f"/{" ".join(_build_path(node))}\n"
        return help_text

_root = _CommandGroupNode("")
def _ensure_group(name: str, parent: _CommandGroupNode | None = None) -> _CommandGroupNode:
    parent = parent or _root
    if name not in parent.children:
        parent.children[name] = _CommandGroupNode(name, parent)
    return parent.children[name]

def _build_path(node: _CommandGroupNode) -> Tuple[str, ...]:
    path = []
    cur = node
    while cur and cur.name:
        path.append(cur.name)
        cur = cur.parent  # mock 简化，真实需回溯 parent
    return tuple(reversed(path))

# ------------------- NcatBotPlugin 基类 -------------------

class NcatBotPlugin:
    def __init__(self, context: Context):
        self.context = context
        self.filter = Filter(self)

# ------------------- 注册器 -------------------

_REGISTRY: List[type] = []

filter = Filter(None)

# ------------------- 简易执行器 -------------------

class Executor:
    def __init__(self):
        self._cmd_map: Dict[Tuple[str, ...], Callable] = {}
        self._alias_map: Dict[str, Tuple[str, ...]] = {}

    def _scan_plugin(self, plugin: NcatBotPlugin):
        for _, method in inspect.getmembers(plugin, predicate=inspect.ismethod):
            if not hasattr(method, "_ncatbot_filter"):
                continue
            st: _FilterStore = method._ncatbot_filter
            full_path = st.group_path + (st.cmd,)
            self._cmd_map[full_path] = method
            # self._alias_map[st.cmd] = full_path
            for alias in st.alias:
                self._alias_map[alias] = full_path
        # print(self._cmd_map)

    def load_plugins(self):
        for cls in _REGISTRY:
            plugin = cls(Context())
            filter.plugin = plugin
            self._scan_plugin(plugin)

    async def dispatch(self, raw: str):
        if not raw.startswith("/"):
            return
        parts = shlex.split(raw[1:])
        if not parts:
            return

        # 查找最长匹配
        for depth in range(len(parts), 0, -1):
            key = tuple(parts[:depth])
            func = self._cmd_map.get(key) or self._cmd_map.get(self._alias_map.get(parts[0]))
            if func:
                args = parts[depth:]
                break
        else:
            return print("未匹配到指令")

        # 过滤器检查（略）
        st: _FilterStore = getattr(func, "_ncatbot_filter")
        if st.event_types and EventMessageType.ALL not in st.event_types:
            return print("事件类型不匹配")
        if st.permission == PermissionType.ADMIN:
            return print("权限不足")

        # 参数解析 & 报错提示
        sig = inspect.signature(func)
        try:
            # 先绑定事件对象
            bound = sig.bind_partial(BaseMessageEvent(raw))
            # 逐个转换剩余参数
            param_list = list(sig.parameters.values())[1:]  # 去掉第一个 event
            if len(args) != len(param_list):
                raise TypeError("参数数量不匹配")
            for val, param in zip(args, param_list):
                if param.annotation != inspect.Parameter.empty:
                    converted = param.annotation(val)
                else:
                    converted = val
                bound.arguments[param.name] = converted
        except (TypeError, ValueError) as e:
            # 构造错误提示
            usage = _build_usage(func)
            msg = f"❌ 参数错误：{e}\n正确用法：\n{usage}"
            print("Bot:", msg)
            return

        # 正常执行
        if inspect.iscoroutinefunction(func):
            async for res in func(*bound.args, **bound.kwargs):
                print("Bot:", res)
        else:
            for res in func(*bound.args, **bound.kwargs):
                print("Bot:", res)

# ------------------- 测试插件 -------------------



class MyPlugin(NcatBotPlugin):
    name = "MyPlugin"
    author = "huan-yp"
    desc = "一个简单的 Hello World 插件"
    ver = "1.0.0"

    def __init__(self, context: Context):
        super().__init__(context)
        self.filter = Filter(self)

    @filter.command("helloworld")
    async def helloworld(self, event: BaseMessageEvent):
        user_name = event.get_sender_name()
        yield event.plain_result(f"Hello, {user_name}!")

    @filter.command("echo")
    def echo(self, event: BaseMessageEvent, message: str):
        yield event.plain_result(f"你发了: {message}")

    @filter.command("add")
    def add(self, event: BaseMessageEvent, a: int, b: int):
        yield event.plain_result(f"结果是: {a + b}")

    # 指令组
    math = filter.command_group("math")

    @math.command("add")
    async def math_add(self, event: BaseMessageEvent, a: int, b: int):
        yield event.plain_result(f"结果是: {a + b}")

    @math.command("sub")
    async def math_sub(self, event: BaseMessageEvent, a: int, b: int):
        yield event.plain_result(f"结果是: {a - b}")

    calc = math.group("calc")

    @calc.command("add")
    async def calc_add(self, event: BaseMessageEvent, a: int, b: int):
        yield event.plain_result(f"结果是: {a + b}")

    @calc.command("sub")
    async def calc_sub(self, event: BaseMessageEvent, a: int, b: int):
        yield event.plain_result(f"结果是: {a - b}")

    @calc.command("help")
    def calc_help(self, event: BaseMessageEvent):
        yield event.plain_result("这是一个计算器插件，拥有 add, sub 指令。")

    # 过滤器示例
    @filter.command("admin_only")
    @filter.permission_type(PermissionType.ADMIN)
    async def admin_only(self, event: BaseMessageEvent):
        yield event.plain_result("管理员你好！")

# ------------------- CLI 交互 -------------------

async def main():
    _REGISTRY.append(MyPlugin)
    ex = Executor()
    ex.load_plugins()
    print("NcatBot Mock 已启动，输入 /quit 退出")
    while True:
        line = input("> ").strip()
        if line == "/quit":
            break
        await ex.dispatch(line)

if __name__ == "__main__":
    asyncio.run(main())