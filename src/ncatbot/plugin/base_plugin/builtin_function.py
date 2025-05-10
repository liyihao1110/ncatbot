import warnings
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, final

from ncatbot.core import BaseMessage
from ncatbot.plugin.event import Conf, Func
from ncatbot.utils import PermissionGroup


def deprecated(message: str = None):
    """标记函数为弃用

    Args:
        message: 弃用说明
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {message or ''}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BuiltinFuncMixin:
    """内置功能混入类, 提供内置功能注册功能.

    # 描述
    该混入类提供了功能和配置项支持, 即注册功能和配置项.
    """

    @final
    def _register_func(
        self,
        name: str,
        handler: Callable[[BaseMessage], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission: PermissionGroup = PermissionGroup.USER.value,
        permission_raise: bool = False,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        if all([name != var.name for var in self._funcs]):
            # 如果没有指定任何过滤器，使用功能名作为默认前缀
            if filter is None and prefix is None and regex is None:
                prefix = f"/{name}"

            self._funcs.append(
                Func(
                    name,
                    self.name,
                    handler,
                    filter=filter,
                    prefix=prefix,
                    regex=regex,
                    permission=permission,
                    permission_raise=permission_raise,
                    description=description,
                    usage=usage,
                    examples=examples,
                    tags=tags,
                    metadata=metadata,
                )
            )
        else:
            raise ValueError(f"插件 {self.name} 已存在功能 {name}")

    def register_user_func(
        self,
        name: str,
        handler: Callable[[BaseMessage], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission_raise: bool = False,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """注册普通用户功能

        Args:
            name: 功能名
            handler: 处理函数
            filter: 自定义过滤器
            prefix: 前缀匹配
            regex: 正则匹配
            permission_raise: 是否提权
            description: 功能描述
            usage: 使用说明
            examples: 使用示例
            tags: 功能标签
            metadata: 额外元数据
        """
        self._register_func(
            name,
            handler,
            filter,
            prefix,
            regex,
            PermissionGroup.USER.value,
            permission_raise,
            description,
            usage,
            examples,
            tags,
            metadata,
        )

    def register_admin_func(
        self,
        name: str,
        handler: Callable[[BaseMessage], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission_raise: bool = True,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """注册管理员功能

        Args:
            name: 功能名
            handler: 处理函数
            filter: 自定义过滤器
            prefix: 前缀匹配
            regex: 正则匹配
            permission_raise: 是否提权
            description: 功能描述
            usage: 使用说明
            examples: 使用示例
            tags: 功能标签
            metadata: 额外元数据
        """
        self._register_func(
            name,
            handler,
            filter,
            prefix,
            regex,
            PermissionGroup.ADMIN.value,
            permission_raise,
            description,
            usage,
            examples,
            tags,
            metadata,
        )

    @deprecated("请使用 register_user_func 或 register_admin_func 替代")
    def register_default_func(
        self,
        handler: Callable[[BaseMessage], Any],
        permission: PermissionGroup = PermissionGroup.USER.value,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """默认处理功能 (已弃用)

        如果没能触发其它功能, 则触发默认功能.
        请使用 register_user_func 或 register_admin_func 替代.
        """
        self._register_func(
            "default",
            handler,
            None,
            None,
            None,
            permission,
            False,
            description,
            usage,
            examples,
            tags,
            metadata,
        )

    def register_config(
        self,
        key: str,
        default: Any,
        on_change: Callable[[str, BaseMessage], Any] = None,
        description: str = "",
        value_type: Literal["int", "bool", "str", "float"] = "",
        allowed_values: List[Any] = None,
        metadata: Dict[str, Any] = None,
    ):
        """注册配置项
        Args:
            key (str): 配置项键名
            default (Any): 默认值
            on_change (Callable[[str, BaseMessage], Any], optional): 配置变更回调函数. 接收新值和触发修改的消息对象.
            description (str, optional): 配置项描述
            value_type (str, optional): 值类型描述
            allowed_values (List[Any], optional): 允许的值列表
            metadata (Dict[str, Any], optional): 额外元数据
        """
        self._configs.append(
            Conf(
                self,
                key,
                on_change,
                default,
                description,
                value_type,
                allowed_values,
                metadata,
            )
        )
        if key not in self.data["config"]:
            self.data["config"][key] = default
