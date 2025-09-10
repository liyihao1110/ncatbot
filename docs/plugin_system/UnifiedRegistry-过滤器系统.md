# UnifiedRegistry 过滤器系统指南

## 🛡️ 过滤器系统概述

过滤器系统是 UnifiedRegistry 的核心安全和权限控制机制。它允许您在命令执行前进行各种检查，如权限验证、消息类型过滤、自定义条件判断等。

## 🎯 核心概念

### 过滤器工作原理

1. **拦截机制**: 过滤器在命令执行前运行
2. **链式验证**: 多个过滤器按顺序执行，全部通过才允许命令执行
3. **早期返回**: 任何一个过滤器失败，命令立即被拦截
4. **无副作用**: 过滤器只做检查，不修改数据

### 过滤器类型

- **内置过滤器**: 系统提供的常用过滤器
- **装饰器过滤器**: 使用装饰器语法的便捷过滤器
- **自定义过滤器**: 您可以创建的自定义过滤逻辑

## 🔧 内置过滤器详解

### 1. GroupFilter - 群聊过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import GroupFilter
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # 方式1: 使用装饰器（推荐）
        @group_only
        @command_registry.command("groupcmd")
        def group_command(self, event: BaseMessageEvent):
            return "这是群聊专用命令"
        
        # 方式2: 使用过滤器实例
        @command_registry.command("groupcmd2")
        def group_command2(self, event: BaseMessageEvent):
            return "另一个群聊命令"
        
        # 手动添加过滤器
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry
        filter_registry.add_filter_to_function(group_command2, GroupFilter())
```

**功能**: 只允许在群聊中使用的命令
**使用场景**: 群管理、群游戏、群公告等

### 2. PrivateFilter - 私聊过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import private_only

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        @private_only
        @command_registry.command("secret")
        def secret_command(self, event: BaseMessageEvent):
            return "这是私聊专用命令"
        
        @private_only
        @command_registry.command("profile")
        def profile_command(self, event: BaseMessageEvent):
            return f"您的用户ID: {event.user_id}"
```

**功能**: 只允许在私聊中使用的命令
**使用场景**: 个人设置、隐私查询、账户管理等

### 3. AdminFilter - 管理员过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import admin_only

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        @admin_only
        @command_registry.command("ban")
        def ban_command(self, event: BaseMessageEvent, user_id: str):
            return f"已封禁用户: {user_id}"
        
        @admin_only
        @command_registry.command("config")
        def config_command(self, event: BaseMessageEvent, key: str, value: str):
            return f"已设置配置 {key} = {value}"
```

**功能**: 只允许管理员使用的命令
**前置条件**: 需要配置权限管理系统
**使用场景**: 系统管理、用户管理、配置修改等

### 4. RootFilter - Root权限过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import root_only

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        @root_only
        @command_registry.command("shutdown")
        def shutdown_command(self, event: BaseMessageEvent):
            return "正在关闭机器人..."
        
        @root_only
        @command_registry.command("debug")
        def debug_command(self, event: BaseMessageEvent):
            return "调试信息: ..."
```

**功能**: 只允许 Root 用户使用的命令
**使用场景**: 系统级操作、调试功能、危险操作等

## 🔗 过滤器组合使用

### 组合装饰器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import (
    group_only, admin_only, private_only, admin_group_only, admin_private_only
)

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # 管理员 + 群聊
        @admin_group_only  # 等同于 @admin_only + @group_only
        @command_registry.command("grouppromote")
        def group_promote_command(self, event: BaseMessageEvent, user_id: str):
            return f"在群聊中提升用户权限: {user_id}"
        
        # 管理员 + 私聊
        @admin_private_only  # 等同于 @admin_only + @private_only
        @command_registry.command("adminpanel")
        def admin_panel_command(self, event: BaseMessageEvent):
            return "管理员私聊面板"
        
        # 手动组合多个过滤器
        @admin_only
        @group_only
        @command_registry.command("groupadmin")
        def group_admin_command(self, event: BaseMessageEvent):
            return "群管理员命令"
```

### 多过滤器执行顺序

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # 过滤器按从上到下的顺序执行
        @admin_only      # 第二个执行
        @group_only      # 第一个执行
        @command_registry.command("order")
        def order_command(self, event: BaseMessageEvent):
            """执行顺序: group_only -> admin_only -> 命令函数"""
            return "多重过滤器命令"
```

## 🛠️ 自定义过滤器

### 1. 使用 CustomFilter

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import CustomFilter
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # 时间过滤器
        def time_filter(event: BaseMessageEvent) -> bool:
            import datetime
            current_hour = datetime.datetime.now().hour
            return 9 <= current_hour <= 22  # 只在9:00-22:00之间可用
        
        # 关键词过滤器
        def keyword_filter(event: BaseMessageEvent) -> bool:
            return "机器人" in (event.raw_message or "")
        
        @command_registry.command("timecheck")
        def time_check_command(self, event: BaseMessageEvent):
            return "当前时间允许使用此命令"
        
        # 添加自定义过滤器
        filter_registry.add_filter_to_function(
            time_check_command, 
            CustomFilter(time_filter, name="time_filter")
        )
```

### 2. 注册过滤器函数

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # 注册过滤器函数
        @filter_registry.register("vip_filter")
        def vip_filter(event: BaseMessageEvent) -> bool:
            # 检查用户是否为VIP（这里只是示例）
            vip_users = ["123456", "789012"]
            return event.user_id in vip_users
        
        # 使用注册的过滤器
        @command_registry.command("vip")
        def vip_command(self, event: BaseMessageEvent):
            return "VIP专属功能"
        
        # 通过名称添加过滤器
        filter_registry.add_filter_to_function(vip_command, "vip_filter")
```

### 3. 创建过滤器类

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import BaseFilter

class LevelFilter(BaseFilter):
    """用户等级过滤器"""
    
    def __init__(self, min_level: int):
        super().__init__(f"level_{min_level}")
        self.min_level = min_level
    
    def check(self, event: BaseMessageEvent) -> bool:
        # 这里应该从数据库或其他地方获取用户等级
        user_level = self.get_user_level(event.user_id)
        return user_level >= self.min_level
    
    def get_user_level(self, user_id: str) -> int:
        # 模拟获取用户等级
        return 1  # 实际应用中从数据库获取

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("highlevel")
        def high_level_command(self, event: BaseMessageEvent):
            return "高等级用户专用命令"
        
        # 添加等级过滤器
        filter_registry.add_filter_to_function(
            high_level_command, 
            LevelFilter(min_level=5)
        )
```

## 📋 过滤器最佳实践

### 1. 过滤器设计原则

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # ✅ 好的做法：单一职责
        def is_weekend(event: BaseMessageEvent) -> bool:
            import datetime
            return datetime.datetime.now().weekday() >= 5
        
        def is_daytime(event: BaseMessageEvent) -> bool:
            import datetime
            hour = datetime.datetime.now().hour
            return 6 <= hour <= 18
        
        # ❌ 避免：复合条件在一个过滤器中
        def weekend_and_daytime(event: BaseMessageEvent) -> bool:
            # 不推荐：功能混合
            pass
```

### 2. 错误处理

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        def safe_filter(event: BaseMessageEvent) -> bool:
            try:
                # 可能出错的逻辑
                return self.check_some_condition(event)
            except Exception as e:
                # 记录错误但不阻止命令执行
                LOG.error(f"过滤器执行错误: {e}")
                return True  # 默认允许通过
```

## 🔍 过滤器调试

### 查看过滤器执行

```python
from ncatbot.utils import get_log

LOG = get_log(__name__)

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        def debug_filter(event: BaseMessageEvent) -> bool:
            result = event.user_id != "blocked_user"
            LOG.debug(f"用户 {event.user_id} 过滤器结果: {result}")
            return result
        
        @command_registry.command("test")
        def test_command(self, event: BaseMessageEvent):
            return "测试命令"
        
        filter_registry.add_filter_to_function(
            test_command, 
            CustomFilter(debug_filter, name="debug_filter")
        )
```

## 📚 常用过滤器模式

### 1. 时间段控制

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    def working_hours_filter(event: BaseMessageEvent) -> bool:
        """工作时间过滤器 (9:00-18:00)"""
        import datetime
        hour = datetime.datetime.now().hour
        return 9 <= hour <= 18
    
    @command_registry.command("work")
    def work_command(self, event: BaseMessageEvent):
        return "工作时间专用命令"
    
    filter_registry.add_filter_to_function(
        work_command, 
        CustomFilter(working_hours_filter, name="working_hours")
    )
```

### 2. 冷却时间控制

```python
class MyPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.last_use = {}  # 记录上次使用时间
    
    async def on_load(self):
        pass

    def cooldown_filter(event: BaseMessageEvent) -> bool:
        """冷却时间过滤器 (60秒)"""
        import time
        user_id = event.user_id
        current_time = time.time()
        
        if user_id in self.last_use:
            if current_time - self.last_use[user_id] < 60:
                return False  # 还在冷却中
        
        self.last_use[user_id] = current_time
        return True
    
    @command_registry.command("limited")
    def limited_command(self, event: BaseMessageEvent):
        return "有冷却限制的命令"
    
    filter_registry.add_filter_to_function(
        limited_command, 
        CustomFilter(cooldown_filter, name="cooldown")
    )
```

## 🚦 下一步

掌握过滤器系统后，您可以：

1. **学习命令系统**: 查看 [命令注册系统指南](./UnifiedRegistry-命令系统.md)
2. **了解参数处理**: 阅读 [参数解析指南](./UnifiedRegistry-参数解析.md)
3. **查看实际应用**: 参考 [实战案例](./UnifiedRegistry-实战案例.md)

---

**💡 提示**: 过滤器是 UnifiedRegistry 的强大功能，合理使用可以大大提升插件的安全性和用户体验。
