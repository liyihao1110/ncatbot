# 插件功能
import os
from typing import Any, Callable, Dict, List

from ncatbot.core import BaseMessage
from ncatbot.plugin.event.access_controller import get_global_access_controller
from ncatbot.plugin.event.event import Event, EventSource
from ncatbot.plugin.event.filter import create_filter
from ncatbot.utils import (
    PermissionGroup,
    run_func_sync,
)


class Func:
    """功能函数"""

    def __init__(
        self,
        name,  # 功能名, 构造权限路径时使用
        plugin_name,  # 插件名, 构造权限路径时使用
        func: Callable[[BaseMessage], None],
        filter: Callable[[Event], bool] = None,
        prefix: str = None,  # 新增: 前缀匹配
        regex: str = None,  # 新增: 正则匹配
        permission: PermissionGroup = PermissionGroup.USER.value,  # 向事件总线传递默认权限设置
        permission_raise: bool = False,  # 是否提权, 判断是否有权限执行时使用
        reply: bool = False,
        description: str = "",  # 功能描述
        usage: str = "",  # 使用说明
        examples: List[str] = None,  # 使用示例
        tags: List[str] = None,  # 功能标签
        metadata: Dict[str, Any] = None,  # 额外元数据
    ):
        self.name = name
        self.plugin_name = plugin_name
        self.func = func
        self.filter_chain = create_filter(
            prefix=prefix, regex=regex, custom_filter=filter
        )
        self.permission = permission
        self.permission_raise = permission_raise
        self.reply = reply
        self.description = description
        self.usage = usage
        self.examples = examples or []
        self.tags = tags or []
        self.metadata = metadata or {}

    def is_activate(self, event: Event) -> bool:
        """判断是否应该激活功能"""
        if self.filter_chain is None:
            return True
        return self.filter_chain.check(event)


class Conf:
    def __init__(
        self,
        plugin,
        key,
        on_change: Callable[[str, BaseMessage], Any] = None,
        default: Any = None,
        description: str = "",  # 配置项描述
        value_type: str = "",  # 值类型描述
        allowed_values: List[Any] = None,  # 允许的值列表
        metadata: Dict[str, Any] = None,  # 额外元数据
    ):
        self.full_key = f"{plugin.name}.{key}"  # 全限定名 {plugin_name}.{key}
        self.key = key
        self.on_change = on_change
        self.plugin = plugin
        self.default = default
        self.description = description
        self.value_type = value_type
        self.allowed_values = allowed_values or []
        self.metadata = metadata or {}

    def modify(self, value, message: BaseMessage = None):
        """修改配置值

        Args:
            value: 新的配置值
            message: 触发修改的消息对象，如果为None则只修改配置不触发回调
        """
        if self.value_type == "int":
            value = int(value)
        elif self.value_type == "bool":
            value = value.lower()
            if value == "false" or value == "0" or value == "f":
                value = False
            else:
                value = True
        elif self.value_type == "float":
            value = float(value)
        else:
            pass
        self.plugin.data["config"][self.key] = value
        if self.on_change and message:
            run_func_sync(self.on_change, value, message)


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
        return
    full_key, value = tuple(args)

    args = full_key.split(".")
    if len(args) == 1:
        plugin_keys = [full_key.split(".")[1] for full_key in configs.keys()]
        if plugin_keys.count(full_key) == 1:
            for k, v in configs.items():
                if k.split(".")[1] == full_key:
                    full_key = k
                    break
        elif plugin_keys.count(full_key) == 0:
            message.reply_text_sync(f"配置名 {args[0]} 不存在")
            return
        else:
            message.reply_sync(f"配置名 {full_key} 有多个, 请提供插件名")
            return

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
        configs[full_key].modify(value, message)
        message.reply_text_sync(f"配置 {full_key} 已经修改为 {value}")
    except Exception as e:
        message.reply_text_sync(f"配置 {full_key} 修改失败: {e}")


async def reload_plugin_command(message: BaseMessage, event_bus=None):
    """
    热重载插件命令
    命令格式: /reload [-f] <plugin_name>
    -f: 强制加载，即使插件未加载也会尝试加载
    """
    args = message.raw_message.split(" ")[1:]
    if len(args) < 1 or len(args) > 2:
        message.reply_text_sync(
            "参数个数错误, 命令格式(不含尖括号): /reload [-f] <plugin_name>"
        )
        return

    from ncatbot.plugin.event.event_bus import EventBus

    event_bus: EventBus = event_bus

    # 解析参数
    force_load = False
    plugin_name = args[-1]  # 最后一个参数总是插件名

    # 检查是否有 -f 参数
    if len(args) == 2 and args[0] == "-f":
        force_load = True

    # 检查插件是否存在
    if not force_load and plugin_name not in [
        plugin.name for plugin in event_bus.plugins
    ]:
        message.reply_text_sync(f"插件 {plugin_name} 未加载，使用 -f 参数可强制加载")
        return

    try:
        if force_load and plugin_name not in [
            plugin.name for plugin in event_bus.plugins
        ]:
            # 强制加载插件
            plugin_loader = event_bus.plugin_loader

            # 获取插件路径
            from ncatbot.utils import PLUGINS_DIR

            plugin_path = os.path.join(PLUGINS_DIR, plugin_name)

            if not os.path.exists(plugin_path):
                message.reply_text_sync(f"插件 {plugin_name} 不存在")
                return

            # 加载插件
            await plugin_loader.load_plugins(plugin_path, api=event_bus.api)
            message.reply_text_sync(f"插件 {plugin_name} 已成功加载")
        else:
            # 重载插件
            await event_bus.plugin_loader.reload_plugin(plugin_name)
            message.reply_text_sync(f"插件 {plugin_name} 已成功重载")
    except Exception as e:
        message.reply_text_sync(
            f"插件 {plugin_name} {'加载' if force_load else '重载'}失败: {e}"
        )


# 更新内置函数定义，使用新的过滤机制
BUILT_IN_FUNCTIONS = [
    Func(
        name="sm",
        plugin_name="ncatbot",
        func=set_admin,
        prefix="/sm",  # 使用前缀匹配替代raw_message_filter
        permission_raise=True,
        reply=False,
        permission=PermissionGroup.ROOT.value,
    ),
    Func(
        name="plg",
        plugin_name="ncatbot",
        func=show_plugin,
        prefix="/plg",  # 使用前缀匹配替代raw_message_filter
        permission_raise=True,
        reply=False,
        permission=PermissionGroup.ADMIN.value,
    ),
    Func(
        name="acs",
        plugin_name="ncatbot",
        func=access,
        prefix="/acs",  # 使用前缀匹配替代raw_message_filter
        permission_raise=True,
        reply=False,
        permission=PermissionGroup.ADMIN.value,
    ),
    Func(
        name="cfg",
        plugin_name="ncatbot",
        func=set_config,
        filter=None,
        prefix="/cfg",  # 使用前缀匹配替代raw_message_filter
        permission=PermissionGroup.ADMIN.value,
        permission_raise=True,
        reply=False,
    ),
    Func(
        name="reload",
        plugin_name="ncatbot",
        func=reload_plugin_command,
        prefix="/reload",  # 使用前缀匹配
        permission_raise=True,
        reply=False,
        permission=PermissionGroup.ADMIN.value,
        description="热重载插件",
        usage="/reload [-f] <plugin_name>",
        examples=["/reload example_plugin", "/reload -f example_plugin"],
        tags=["admin", "plugin", "reload"],
    ),
]
