"""统一注册模块

提供过滤器和命令的统一注册功能。
"""

# 主要组件
from .plugin import UnifiedRegistryPlugin

# 过滤器系统
from .filter_system import (
    BaseFilter,
    GroupFilter,
    PrivateFilter,
    AdminFilter,
    RootFilter,
    CustomFilter,
    filter_registry,
)

# 过滤器装饰器
from .filter_system.decorators import (
    admin_only,
    root_only,
    private_only,
    group_only,
    on_message,
    on_notice,
    on_request,
)
from .filter_system.decorators import (
    admin_filter,
    root_filter,
    private_filter,
    group_filter,
    admin_group_filter,
    admin_private_filter,
)
from .command_system.registry import option, param, option_group

# 命令系统
from .command_system import (
    FuncAnalyser,
    get_subclass_recursive,
    command_registry,
)


# 向后兼容导出
__all__ = [
    # 主要插件类
    "UnifiedRegistryPlugin",
    # 全局注册实例
    "command_registry",
    "filter_registry",
    # 装饰器
    "on_request",
    "on_notice",
    "admin_only",
    "root_only",
    "admin_only",
    "private_only",
    "group_only",
    "admin_filter",
    "root_filter",
    "private_filter",
    "group_filter",
    "admin_group_filter",
    "admin_private_filter",
    "on_message",
    "option",
    "param",
    "option_group",
    # 过滤器相关
    "BaseFilter",
    "GroupFilter",
    "PrivateFilter",
    "AdminFilter",
    "RootFilter",
    "CustomFilter",
    "CustomFilterFunc",
    "FilterValidator",
    # 命令相关
    "FuncAnalyser",
    "get_subclass_recursive",
]
