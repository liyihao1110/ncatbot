# 插件功能
import re
from typing import Any, Callable, List

from ncatbot.core import BaseMessage
from ncatbot.plugin.event.access_controller import get_global_access_controller
from ncatbot.plugin.event.event import Event, EventSource
from ncatbot.utils import (
    PermissionGroup,
)


class Func:
    """功能函数"""

    def __init__(
        self,
        name,  # 功能名, 构造权限路径时使用
        plugin_name,  # 插件名, 构造权限路径时使用
        func: Callable[[BaseMessage], None],
        filter: Callable[[Event], bool] = None,
        raw_message_filter: str = None,
        permission: PermissionGroup = PermissionGroup.USER.value,  # 向事件总线传递默认权限设置
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

    def is_activate(self, event: Event) -> bool:
        """判断是否应该激活功能"""
        if self.filter and not self.filter(event):
            return False
        elif isinstance(event.data, BaseMessage):
            if self.raw_message_filter and not re.match(
                self.raw_message_filter, event.data.raw_message
            ):
                return False
        return True


class Conf:
    def __init__(
        self, plugin, key, rptr: Callable[[str], Any] = None, default: Any = None
    ):
        self.full_key = f"{plugin.name}.{key}"  # 全限定名 {plugin_name}.{key}
        self.key = key
        self.rptr = rptr
        self.plugin = plugin
        self.default = default

    def modify(self, value):
        # try:
        value = self.rptr(value) if self.rptr else value
        self.plugin.data["config"][self.key] = value
        # except Exception as e:


async def set_admin(message: BaseMessage):
    args = message.raw_message.split(" ")[1:]
    if len(args) != 1:
        message.reply_text_sync("参数个数错误, 命令格式(不含尖括号): /sm <qq_number>")
    else:
        if not get_global_access_controller().user_has_role(
            args[0], PermissionGroup.ADMIN.value
        ):
            get_global_access_controller().assign_role_to_user(
                args[0], PermissionGroup.ADMIN.value
            )
            message.reply_text_sync(f"已经将用户 {args[0]} 设为管理员")
        else:
            get_global_access_controller().unassign_role_to_user(
                args[0],
                PermissionGroup.ADMIN.value,
            )
            message.reply_text_sync(f"已经将用户 {args[0]} 取消管理员")


async def show_plugin(plugins, message: BaseMessage):
    # /plg [<plugin_name>]
    args = message.raw_message.split(" ")[1:]
    if len(args) == 0:
        text = "\n".join([f"{plugin.name}-{plugin.version}" for plugin in plugins])
    else:
        if args[0] not in [plugin.name for plugin in plugins]:
            text = f"插件 {args[0]} 不存在"
        else:
            text = f"插件 {args[0]}-{[plugin.version for plugin in plugins if plugin.name == args[0]][0]}"
    message.reply_text_sync(text)


async def access(message: BaseMessage):
    # /acs [-g] [ban]/[grant] <number> path
    def access_fliter(path):
        """筛除绝对禁止的权限路劲操作"""
        if path.startswith("*"):
            # 禁用通配符起手
            return False

        if path.startswith("ncatbot"):
            # 核心操作都在 ncatbot 下, 其余权限路径均不敏感, 交给插件开发者管理
            second_path = path.split(".")[1]
            if second_path in ["cfg", "plg"]:  # 管理员拥有完全权限
                return True
            elif second_path in ["sm", "acs"]:  # 不应该被 access 操作
                return False
            else:
                return False
        return True

    # 参数检查
    args = message.raw_message.split(" ")[1:]
    if len(args) > 4 or len(args) < 3:
        message.reply_text_sync(
            "参数个数错误, 命令格式(不含尖括号): /acs [-g](可选) [ban]/[grant] <number> path"
        )
        return
    path = args[-1]
    number = args[-2]
    option = args[-3]
    is_group = "-g" in args
    if option not in ["ban", "grant"]:
        message.reply_text_sync(
            "参数个数错误, 命令格式(不含尖括号): /acs [-g](可选) [ban]/[grant] <number> path"
        )
        return

    # 禁止操作敏感权限路径
    if not access_fliter(path):
        message.reply_text_sync("你个小机灵鬼要搞 SQL 注入？没想到吧，我没用 SQL")
        return

    # 检查权限路径是否存在
    if not get_global_access_controller().permission_path_exist(path):
        message.reply_text_sync(f"权限 {path} 不存在")
        return

    # 检查目标是否具有 admin 角色
    if (
        is_group
        and get_global_access_controller().group_has_role(
            number, PermissionGroup.ADMIN.value
        )
    ) or (
        not is_group
        and get_global_access_controller().user_has_role(
            number, PermissionGroup.ADMIN.value
        )
    ):
        message.reply_text_sync(
            f"{'群组' if is_group else '用户'} 是管理员, 无法对他进行操作"
        )
        return

    if option == "ban":
        if is_group:
            get_global_access_controller().add_black_list_to_group(number, path)
        else:
            get_global_access_controller().add_black_list_to_user(number, path)
        message.reply_text_sync(
            f"{'群组' if is_group else '用户'} {number} 已经被禁止访问 {path}"
        )
    if option == "grant":
        if is_group:
            get_global_access_controller().add_white_list_to_group(number, path)
        else:
            get_global_access_controller().add_white_list_to_user(number, path)
        message.reply_text_sync(
            f"{'群组' if is_group else '用户'} {number} 已经被允许访问 {path}"
        )


async def set_config(configs: dict[str, Conf], message: BaseMessage):
    # /cfg <plugin_name>.<key> <value>
    # 权限路径 ncatbot.cfg.<plugin_name>.<key>

    # 格式检查
    args = message.raw_message.split(" ")[1:]
    if len(args) != 2:
        message.reply_text_sync(
            "参数个数错误, 命令格式(不含尖括号): /cfg <plugin_name>.<key> <value>"
        )
    full_key, value = tuple(args)

    # 检查配置项是否存在
    if full_key not in configs:
        message.reply_text_sync(f"配置 {full_key} 不存在")
        return

    # 鉴权
    source = EventSource(
        message.sender.user_id,
        (
            message.group_id
            if hasattr(message, "group_id")
            else PermissionGroup.ROOT.value
        ),
    )
    if not get_global_access_controller().with_permission(
        path=f"ncatbot.cfg.{full_key}", source=source, permission_raise=True
    ):
        message.reply_text_sync(f"你没有权限修改配置 {full_key}")
        return

    # 修改
    try:
        configs[full_key].modify(value)
        message.reply_text_sync(f"配置 {full_key} 已经修改为 {value}")
    except Exception as e:
        message.reply_text_sync(f"配置 {full_key} 修改失败: {e}")


builtin_functions: List[Func] = [
    Func(
        name="sm",
        plugin_name="ncatbot",
        func=set_admin,
        raw_message_filter="/sm",
        permission_raise=True,
        reply=True,
        permission=PermissionGroup.ROOT.value,
    ),
    Func(
        name="plg",
        plugin_name="ncatbot",
        func=show_plugin,
        raw_message_filter="/plg",
        permission_raise=True,
        reply=True,
        permission=PermissionGroup.ADMIN.value,
    ),
    Func(
        name="acs",
        plugin_name="ncatbot",
        func=access,
        raw_message_filter="/acs",
        permission_raise=True,
        reply=True,
        permission=PermissionGroup.ADMIN.value,
    ),
    Func(
        name="cfg",
        plugin_name="ncatbot",
        func=set_config,
        filter=None,
        raw_message_filter="/cfg",
        permission=PermissionGroup.ADMIN.value,
        permission_raise=True,
        reply=True,
    ),
]
