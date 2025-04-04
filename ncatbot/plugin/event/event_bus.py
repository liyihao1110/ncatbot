import asyncio
import copy
import inspect
import re
import uuid
from typing import Any, Callable, List

from ncatbot.core import BaseMessage
from ncatbot.plugin.event.access_controller import get_global_access_controller
from ncatbot.plugin.event.event import Event, EventType
from ncatbot.plugin.event.function import Conf, Func, builtin_functions
from ncatbot.utils import (
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    PermissionGroup,
    get_log,
)

_log = get_log()


class EventBus:
    """
    事件总线类，用于管理和分发事件
    """

    def __init__(self):
        """
        初始化事件总线
        """
        self._exact_handlers = {}
        self._regex_handlers = []
        self.access_controller = get_global_access_controller()
        self.funcs: List[Func] = []
        self.configs: dict[str, Conf] = {}
        self.plugins: List = []  # List[BasePlugin]
        self.load_builtin_funcs()
        self.subscribe(
            OFFICIAL_GROUP_MESSAGE_EVENT, self._func_activator, 100
        )  # 加载功能注册钩子
        self.subscribe(
            OFFICIAL_PRIVATE_MESSAGE_EVENT, self._func_activator, 100
        )  # 加载功能注册钩子

    # TODO: 支持保护性功能, 激活保护性功能后该消息不会激活其它任何功能
    async def _func_activator(self, event: Event):
        activate_plugin_func = []  # 记录已经被激活功能的插件, 用于判断是否激活默认功能
        message: BaseMessage = event.data
        for func in self.funcs:
            if func.is_activate(event):
                if self.access_controller.with_permission(
                    path=f"{func.plugin_name}.{func.name}",
                    source=event.source,
                    permission_raise=func.permission_raise,
                ):
                    if func.name == "default":
                        # 默认功能, 检查其余激活条件
                        if all(
                            [
                                n not in activate_plugin_func
                                for n in (func.plugin_name, "ncatbot")
                            ]
                        ):
                            await func.func(message)
                    else:
                        activate_plugin_func.append(func.plugin_name)
                        await func.func(message)
                elif func.reply:
                    message.reply_text_sync("权限不足")

    def load_builtin_funcs(self):
        self.access_controller.create_permission_path(
            "ncatbot.cfg.main.placeholder",
            ignore_exist=True
        )  # 创建占位路径
        for func in builtin_functions:
            if func.name == "plg":  # 绑定 plg 的参数
                temp = copy.copy(func.func)
                func.func = lambda message, plugins=self.plugins, temp=temp: temp(
                    plugins, message
                )
            if func.name == "cfg":  # 绑定 cfg 的参数
                temp = copy.copy(func.func)
                func.func = lambda message, configs=self.configs, temp=temp: temp(
                    configs, message
                )

            self.funcs.append(func)
            self.access_controller.assign_permissions_to_role(
                role_name=func.permission,
                path=(
                    f"{func.plugin_name}.{func.name}"
                    if func.name != "cfg"
                    else "ncatbot.cfg.**"
                ),
                mode="white",
                create_permission_path=True,
            )

    def add_plugin(self, plugin):
        self.plugins.append(plugin)
        self.set_plugin_funcs(plugin)
        self.set_plugin_configs(plugin)

    def set_plugin_configs(self, plugin):
        # 为了类型注解添加的额外检查
        from ncatbot.plugin.base_plugin.base_plugin import BasePlugin

        assert isinstance(plugin, BasePlugin)

        if "config" not in plugin.data:
            plugin.data["config"] = {}
        for conf in plugin.configs:
            _log.debug(f"加载插件 {plugin.name} 的配置 {conf.full_key}")
            if conf.key not in plugin.data["config"]:
                plugin.data["config"][conf.key] = conf.default
            self.access_controller.assign_permissions_to_role(
                role_name=PermissionGroup.ADMIN.value,
                path=f"ncatbot.cfg.{conf.full_key}",
                mode="white",
                create_permission_path=True,
            )
            self.configs[conf.full_key] = conf

    def set_plugin_funcs(self, plugin):
        # 为了类型注解添加的额外检查
        from ncatbot.plugin.base_plugin.base_plugin import BasePlugin

        assert isinstance(plugin, BasePlugin)

        for func in plugin.funcs:
            _log.debug(f"加载插件 {plugin.name} 的功能 {func.name}")
            self.access_controller.assign_permissions_to_role(
                role_name=func.permission,
                path=f"{func.plugin_name}.{func.name}",
                mode="white",
                create_permission_path=True,
            )
            self.funcs.append(func)

    def subscribe(
        self, event_type: EventType, handler: Callable[[Event], Any], priority: int = 0
    ) -> uuid.UUID:
        """
        订阅事件处理器，并返回处理器的唯一 ID

        参数:
            event_type: str - 事件类型或正则模式（以 're:' 开头表示正则匹配）
            handler: Callable[[Event], Any] - 事件处理器函数
            priority: int - 处理器的优先级（数字越大，优先级越高）

        返回:
            str - 处理器的唯一 ID
        """
        handler_id = str(uuid.uuid4())
        pattern = None
        if event_type.startswith("re:"):
            pattern = re.compile(event_type[3:])
            self._regex_handlers.append((pattern, priority, handler, handler_id))
        else:
            self._exact_handlers.setdefault(event_type, []).append(
                (pattern, priority, handler, handler_id)
            )
        return handler_id

    def unsubscribe(self, handler_id: uuid.UUID) -> bool:
        """
        取消订阅事件处理器

        参数:
            handler_id: UUID - 处理器的唯一 ID

        返回:
            bool - 是否成功取消订阅
        """
        # 取消精确匹配处理器
        for event_type in list(self._exact_handlers.keys()):
            self._exact_handlers[event_type] = [
                (patt, pr, h, hid)
                for (patt, pr, h, hid) in self._exact_handlers[event_type]
                if hid != handler_id
            ]
            if not self._exact_handlers[event_type]:
                del self._exact_handlers[event_type]
        # 取消正则匹配处理器
        self._regex_handlers = [
            (patt, pr, h, hid)
            for (patt, pr, h, hid) in self._regex_handlers
            if hid != handler_id
        ]
        return True

    async def publish_async(self, event: Event) -> List[Any]:
        """
        异步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表(通常是空列表)
        """
        handlers = []
        if event.type in self._exact_handlers:
            # 处理精确匹配处理器
            for pattern, priority, handler, handler_id in self._exact_handlers[
                event.type
            ]:
                handlers.append((handler, priority, handler_id))
        else:
            # 处理正则匹配处理器
            for pattern, priority, handler, handler_id in self._regex_handlers:
                if pattern and pattern.match(event.type):
                    handlers.append((handler, priority, handler_id))

        # 按优先级排序
        sorted_handlers = sorted(handlers, key=lambda x: (-x[1], x[0].__name__))

        results = []
        # 按优先级顺序调用处理器
        for handler, priority, handler_id in sorted_handlers:
            if event._propagation_stopped:
                break

            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                asyncio.create_task(handler(event))

            # 收集结果
            results.extend(event._results)

        return results

    def publish_sync(self, event: Event) -> List[Any]:
        """
        同步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表
        """
        loop = asyncio.new_event_loop()  # 创建新的事件循环
        try:
            asyncio.set_event_loop(loop)  # 设置为当前事件循环
            return loop.run_until_complete(self.publish_async(event))
        finally:
            loop.close()  # 关闭事件循环
