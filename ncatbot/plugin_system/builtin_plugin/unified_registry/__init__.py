"""统一注册模块

提供过滤器和命令的统一注册功能。
"""

# 主要组件
from .plugin import UnifiedRegistryPlugin
from .registry import filter, register

# 过滤器系统
from .filter_system import (
    BaseFilter, GroupFilter, PrivateFilter, AdminFilter, RootFilter,
    CustomFilter, CustomFilterFunc,
    FilterValidator
)

# 命令系统  
from .command_system import (
    FuncAnalyser, get_subclass_recursive,
    CommandGroup, CommandRouter
)

# 向后兼容导出
__all__ = [
    # 主要插件类
    "UnifiedRegistryPlugin",
    
    # 全局注册实例
    "filter", 
    "register",
    
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
    "CommandGroup",
    "CommandRouter",
]
