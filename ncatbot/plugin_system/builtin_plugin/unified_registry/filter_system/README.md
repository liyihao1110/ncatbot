# 过滤器系统 v2.0

## 概述

这是一个全新设计的过滤器系统，相比旧版本有以下改进：

- **简化参数**: 过滤器函数只接受 `event` 参数，不再需要 `manager` 参数
- **统一注册**: 所有过滤器都注册到全局的 `filter_registry` 实例中
- **灵活应用**: 支持实例注册、函数注册和装饰器应用
- **类型安全**: 完整的类型注解支持
- **易于使用**: 提供便捷的装饰器

## 文件结构

```
filter_system/
├── __init__.py          # 主要导出接口
├── base.py             # 过滤器基类
├── builtin.py          # 内置过滤器实现
├── registry.py         # 过滤器注册器
├── decorators.py       # 装饰器支持
├── validator.py        # 过滤器验证器
├── examples.py         # 使用示例
├── legacy/             # 旧版本文件（兼容性）
│   ├── __init__.py
│   ├── base.py
│   ├── builtin.py
│   ├── custom.py
│   └── validator.py
└── filters/            # 已废弃，包含迁移提示
    ├── __init__.py
    ├── base.py
    ├── builtin.py
    └── ...
```

## 快速开始

### 1. 导入过滤器系统

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry,
    GroupFilter,
    PrivateFilter,
    AdminFilter,
    RootFilter,
    filter,
    group_only,
    private_only,
    admin_only,
    root_only
)
```

### 2. 注册过滤器实例

```python
# 注册内置过滤器
filter_registry.register_filter("group_only", GroupFilter())
filter_registry.register_filter("admin_only", AdminFilter())
```

### 3. 注册过滤器函数

```python
@filter_registry.register("time_check")
def time_filter(event):
    """时间检查过滤器"""
    import datetime
    return datetime.datetime.now().hour < 22
```

### 4. 使用装饰器应用过滤器

```python
# 使用便捷装饰器
@group_only
@admin_only
def admin_group_command(event):
    return "管理员群聊命令"

# 使用 filter 装饰器
@filter(GroupFilter(), AdminFilter())
def complex_command(event):
    return "复合过滤器命令"

# 使用已注册的过滤器名称
@filter("group_only", "time_check")
def scheduled_group_command(event):
    return "定时群聊命令"
```

## API 参考

### BaseFilter

所有过滤器的基类。

```python
class BaseFilter(ABC):
    def __init__(self, name: str = None):
        pass
    
    @abstractmethod
    def check(self, event: BaseMessageEvent) -> bool:
        """检查事件是否通过过滤器"""
        pass
```

### FilterRegistry

统一的过滤器注册器。

```python
class FilterRegistry:
    def register_filter(self, name: str, filter_instance: BaseFilter) -> None:
        """注册过滤器实例"""
        
    def register(self, func: Callable = None, name: str = None):
        """注册过滤器函数或用作装饰器"""
        
    def add_filter_to_function(self, func: Callable, *filters) -> Callable:
        """为函数添加过滤器"""
        
    def get_filter_instance(self, name: str) -> Optional[BaseFilter]:
        """获取过滤器实例"""
        
    def list_filters(self) -> List[FilterEntry]:
        """列出所有过滤器"""
```

### 内置过滤器

- `GroupFilter`: 群聊消息过滤器
- `PrivateFilter`: 私聊消息过滤器  
- `AdminFilter`: 管理员权限过滤器
- `RootFilter`: Root权限过滤器
- `CustomFilter`: 自定义函数包装器

### 装饰器

- `@group_only`: 群聊专用
- `@private_only`: 私聊专用
- `@admin_only`: 管理员专用
- `@root_only`: Root专用
- `@admin_group_only`: 管理员群聊专用
- `@admin_private_only`: 管理员私聊专用
- `@filter(...)`: 通用过滤器装饰器

## 迁移指南

### 从旧版本迁移

1. **更新导入语句**:
   ```python
   # 旧版本
   from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.filters import BaseFilter
   
   # 新版本
   from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import BaseFilter
   ```

2. **修改过滤器函数签名**:
   ```python
   # 旧版本
   async def check(self, manager, event):
       return True
   
   # 新版本
   def check(self, event):
       return True
   ```

3. **使用新的注册方式**:
   ```python
   # 旧版本
   filter.add_filter(MyFilter())
   
   # 新版本
   filter_registry.register_filter("my_filter", MyFilter())
   ```

## 注意事项

1. **同步 vs 异步**: 新版本的过滤器 `check` 方法是同步的，不再是异步
2. **权限检查**: `AdminFilter` 和 `RootFilter` 目前返回 `True`，需要实际的权限系统支持
3. **向后兼容**: 旧的 `filters/` 目录文件已移动到 `legacy/`，临时保持兼容

## 示例代码

完整的使用示例请参考 `examples.py` 文件。