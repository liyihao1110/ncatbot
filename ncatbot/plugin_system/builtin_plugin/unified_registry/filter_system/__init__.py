"""过滤器系统 v2.0

全新设计的过滤器系统：
- 过滤器函数只接受 event 参数
- 支持过滤器实例直接应用到命令
- 统一注册管理

使用示例:
    # 方式1: 注册过滤器实例
    from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry
    from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import GroupFilter
    
    filter_registry.register_filter("group_only", GroupFilter())
    
    # 方式2: 注册过滤器函数
    @filter_registry.register("time_check")
    def time_filter(event):
        import datetime
        return datetime.datetime.now().hour < 22
    
    # 方式3: 直接应用到命令
    from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter, group_only
    
    @filter(GroupFilter(), AdminFilter())
    def admin_group_command(event):
        return "管理员群聊命令"
    
    @group_only
    def group_command(event):
        return "群聊命令"
"""

# 核心组件
from .registry import FilterRegistry, FilterEntry, filter_registry
from .base import BaseFilter
from .builtin import GroupFilter, PrivateFilter, AdminFilter, RootFilter, CustomFilter
from .decorators import filter, group_only, private_only, admin_only, root_only, admin_group_only, admin_private_only
from .validator import FilterValidator

# 便捷导出
filter = filter_registry  # 兼容简化用法

__all__ = [
    # 核心类
    "FilterRegistry", "FilterEntry", "BaseFilter",
    
    # 内置过滤器
    "GroupFilter", "PrivateFilter", "AdminFilter", "RootFilter", "CustomFilter",
    
    # 注册器实例
    "filter_registry", "filter",
    
    # 装饰器
    "group_only", "private_only", "admin_only", "root_only", 
    "admin_group_only", "admin_private_only",
    
    # 验证器
    "FilterValidator",
]
