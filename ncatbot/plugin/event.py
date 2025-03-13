# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-06 20:41:46
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
import inspect
import re
import uuid
from enum import Enum
from typing import Any, Callable, List, Union

from ncatbot.core.message import BaseMessage
from ncatbot.RBACManager.RBACManager import RBACManager
from ncatbot.utils.literals import (
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
)


class DefaultPermissions(Enum):
    ACCESS = "access"
    SETADMIN = "setadmin"


class Conf:
    def __init__(self, plugin, key, rptr: Callable[[str], Any] = None):
        self.full_key = f"{plugin.name}.{key}"  # 全限定名 {plugin_name}.{key}
        self.key = key
        self.rptr = rptr
        self.hook_config = plugin.data["config"]

    def modify(self, value):
        # try:
        value = self.rptr(value) if self.rptr else value
        self.hook_config[self.full_key] = value
        # except Exception as e:


class PermissionGroup(Enum):
    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class EventType:
    def __init__(self, plugin_name: str, event_name: str):
        self.plugin_name = plugin_name
        self.event_name = event_name

    def __str__(self):
        return f"{self.plugin_name}.{self.event_name}"


class EventBusRBACManager(RBACManager):
    # TODO: 做好 USER 和 GROUP 的包装
    def __init__(self, case_sensitive=False, is_group: bool = False):
        super().__init__(case_sensitive)
        self.is_group = is_group

    def has_role(self, role_name):
        return role_name in self.roles

    def has_user(self, user: str):
        return user in self.users

    def create_user(self, user_name, base_role=PermissionGroup.USER.value):
        super().create_user(user_name)
        if not self.has_role(base_role):
            self.create_role(base_role)
        self.assign_role_to_user(user_name, base_role)

    def user_has_role(self, user_name: str, role: str):
        pass

    def remove_role(self, user_name: str, role: str):
        pass

    def permission_exists(self, path: str):
        pass

    def remove_user_permission(self, user_name: str, path: str):
        pass

    def assign_user_permission(self, user_name: str, path: str):
        pass


class EventSource:
    def __init__(self, user_id: Union[str, int], group_id: Union[str, int]):
        self.user_id = user_id
        self.group_id = group_id

    def with_permission(
        self,
        ur: EventBusRBACManager,
        gr: EventBusRBACManager,
        path: str,
        permission_raise: bool = False,
    ):
        if not gr.has_user(self.group_id):
            ur.create_user(self.group_id)
        if not ur.has_user(self.user_id):
            ur.create_user(self.user_id)
        group = self.group_id if not permission_raise else "root"
        return ur.has_user_permission(self.user_id, path) and gr.user_has_role(
            group, path
        )


class Event:
    """
    事件类，用于封装事件的类型和数据
    """

    def __init__(self, type: EventType, data: Any, source: EventSource = None):
        """
        初始化事件

        参数:
            type: str - 事件的类型
            data: Any - 事件携带的数据
        """
        self.type = type
        self.data = data
        self.source = source  # 事件源
        self._results: List[Any] = []
        self._propagation_stopped = False

    def stop_propagation(self):
        """
        停止事件的传播
        当调用此方法后，后续的处理器将不会被执行
        """
        self._propagation_stopped = True

    def add_result(self, result: Any):
        """
        添加事件处理结果

        参数:
            result: Any - 处理器返回的结果
        """
        self._results.append(result)

    def __repr__(self):
        return f'Event(type="{self.type}",data={self.data})'


class Func:
    """功能函数"""

    def __init__(
        self,
        name,  # 功能名, 构造权限路径时使用
        plugin_name,  # 插件名, 构造权限路径时使用
        func: Callable[[Event], None],
        filter: Callable[[Event], bool] = None,
        raw_message_filter: str = None,
        permission: PermissionGroup = PermissionGroup.USER,  # 向事件总线传递默认权限设置
        permission_raise: bool = False,  # 是否提权, 判断是否有权限执行时使用
        reply: bool = False,
    ):
        self.name = name
        self.plugin_name = plugin_name
        self.func = func
        self.filter = filter
        self.raw_message_filter = raw_message_filter
        self.permission = permission
        self.permission_raise = permission_raise
        self.reply = reply  # 权限不足是否回复

    def activate(self, event: Event) -> bool:
        """激活功能函数"""
        if self.filter and not self.filter(event):
            return False
        elif isinstance(event.data, BaseMessage):
            if self.raw_message_filter and not re.match(
                self.raw_message_filter, event.data.raw_message
            ):
                return False
        return True


def event_command_warper(func: Callable[[List[str]], Any]) -> Callable[[Event], Any]:
    def wrapper(event: Event):
        args = event.data.raw_message.split(" ")[1:]
        return func(*args)

    return wrapper


class EventBus:
    """
    事件总线类，用于管理和分发事件
    """

    def __init__(self):
        """
        初始化事件总线
        """
        from ncatbot.plugin.base_plugin import BasePlugin

        self._exact_handlers = {}
        self._regex_handlers = []
        self.RBAC_U = EventBusRBACManager()
        self.RBAC_G = EventBusRBACManager()
        self.funcs: List[Func] = []
        self.configs: dict[str, Conf] = {}
        self.plugins: List[BasePlugin] = []
        self._create_basic_roles()
        self._assign_root_permission()
        self.load_builtin_funcs()
        self.subscribe(OFFICIAL_GROUP_MESSAGE_EVENT, self._func_activator, 100)
        self.subscribe(OFFICIAL_PRIVATE_MESSAGE_EVENT, self._func_activator, 100)

    # def _cfg(self, *args):
    #     input:str = event.data.raw_message
    #     pass

    def _sm(self, event: Event):
        message: BaseMessage = event.data
        args = message.raw_message.split(" ")[1:]
        if len(args) != 1:
            message.reply_text_sync(
                "参数个数错误, 命令格式(不含尖括号): /sm <qq_number>"
            )
        else:
            has_role = self.RBAC_U.user_has_role(args[0], PermissionGroup.ADMIN)
            if not has_role:
                self.RBAC_U.assign_role_to_user(args[0], PermissionGroup.ADMIN)
                message.reply_text_sync(f"已经将用户 {args[0]} 设为管理员")
            else:
                self.RBAC_U.remove_role(args[0], PermissionGroup.ADMIN)
                message.reply_text_sync(f"已经将用户 {args[0]} 取消管理员")

    def _acs(self, event: Event):
        # access [-g] <number> path
        message: BaseMessage = event.data
        args = message.raw_message.split(" ")[1:]
        if len(args) >= 4 or len(args) < 2:
            message.reply_text_sync(
                "参数个数错误, 命令格式(不含尖括号): /access [-g] [ban]/[grant] <number> path"
            )
        else:
            path = args[-1]
            number = args[-2]
            option = args[-3]
            RBAC = self.RBAC_U if "-g" not in args else self.RBAC_G
            if RBAC.has_user_permission(number, DefaultPermissions.ACCESS):
                message.reply_text_sync(
                    f"{'群组' if '-g' in args else '用户'} {number} 已经拥有 /acs 权限, 同级用户无法修改其权限"
                )
            elif not RBAC.permission_exists(path):
                message.reply_text_sync(f"权限 {path} 不存在")
            else:
                if option == "ban":
                    RBAC.remove_user_permission(number, path)
                    message.reply_text_sync(
                        f"{'群组' if '-g' in args else '用户'} {number} 已经被禁止访问 {path}"
                    )
                elif option == "grant":
                    RBAC.assign_user_permission(number, path)
                    message.reply_text_sync(
                        f"{'群组' if '-g' in args else '用户'} {number} 已经被授权访问 {path}"
                    )

    def _cfg(self, event: Event):
        # /cfg <plugin_name>.<key> <value>
        message: BaseMessage = event.data
        args = message.raw_message.split(" ")[1:]
        if len(args) != 2:
            message.reply_text_sync(
                "参数个数错误, 命令格式(不含尖括号): /cfg <plugin_name>.<key> <value>"
            )

        full_key, value = tuple(args)
        if full_key not in self.configs:
            message.reply_text_sync(f"配置 {full_key} 不存在")
        else:
            try:
                self.configs[full_key].modify(value)
            except Exception as e:
                message.reply_text_sync(f"配置 {full_key} 修改失败: {e}")

    def _plg(self, event: Event):
        # /plg [<plugin_name>]
        message: BaseMessage = event.data
        args = message.raw_message.split(" ")[1:]
        if len(args) == 0:
            text = "\n".join(
                [f"{plugin.name}-{plugin.version}" for plugin in self.plugins]
            )
        else:
            if args[0] not in [plugin.name for plugin in self.plugins]:
                text = f"插件 {args[0]} 不存在"
            else:
                text = f"插件 {args[0]}-{[plugin.version for plugin in self.plugins if plugin.name == args[0]][0]}"
        message.reply_text_sync(text)

    async def _func_activator(self, event: Event):
        message: BaseMessage = event.data
        for func in self.funcs:
            if func.activate(event):
                print(f"activate_event {func.name}")
                if event.source.with_permission(
                    self.RBAC_U,
                    self.RBAC_G,
                    f"{func.plugin_name}.{func.name}",
                ):
                    func.func(event)
                elif func.reply:
                    message.reply_text_sync("权限不足")

    def _assign_root_permission(self):
        self.RBAC_U.create_user("root")
        self.RBAC_U.assign_role_to_user("root", "root")
        self.RBAC_U.assign_permission("root", "**")
        self.RBAC_G.create_user("root")
        self.RBAC_G.assign_role_to_user("root", "root")
        self.RBAC_G.assign_permission("root", "**")

    def _create_basic_roles(self):
        self.RBAC_U.create_role("root")
        self.RBAC_U.create_role("admin")
        self.RBAC_U.create_role("user")
        self.RBAC_U.add_role_parent("root", "admin")
        self.RBAC_U.add_role_parent("admin", "user")
        self.RBAC_G.create_role("root")
        self.RBAC_G.create_role("user")
        self.RBAC_G.create_role("admin")
        self.RBAC_G.add_role_parent("root", "admin")
        self.RBAC_G.add_role_parent("admin", "user")

    def load_builtin_funcs(self):
        self.funcs.append(
            Func(
                name="plg",
                plugin_name="ncatbot",
                func=self._plg,
                raw_message_filter="/plg",
                permission_raise=True,
                reply=True,
            )
        )
        self.funcs.append(
            Func(
                name=DefaultPermissions.SETADMIN,
                plugin_name="ncatbot",
                func=self._acs,
                raw_message_filter="/acs",
                permission_raise=True,
                reply=True,
            )
        )
        self.funcs.append(
            Func(
                name=DefaultPermissions.ACCESS,
                plugin_name="ncatbot",
                func=self._acs,
                raw_message_filter="/sm",
                permission_raise=True,
                reply=True,
            )
        )

    def add_plugin(self, plugin):
        self.plugins.append(plugin)
        self.set_plugin_funcs(plugin)
        self.set_plugin_configs(plugin)

    def set_plugin_configs(self, plugin):
        for conf in plugin.configs:
            self.RBAC_U.assign_permission(PermissionGroup.ADMIN, f"cfg.{conf.full_key}")
            self.funcs.append(
                Func(
                    name=f"{conf.full_key}",
                    plugin_name="cfg",
                    func=self._cfg,
                    filter=None,
                    raw_message_filter="/cfg",
                    permission=PermissionGroup.ADMIN,
                    permission_raise=True,
                    reply=True,
                )
            )
            self.configs[conf.full_key] = conf

    def set_plugin_funcs(self, plugin):
        for func in plugin.funcs:
            self.RBAC_U.assign_permission(
                func.permission, f"{func.plugin_name}.{func.name}"
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
