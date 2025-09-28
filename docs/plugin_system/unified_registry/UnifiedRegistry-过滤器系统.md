# UnifiedRegistry 过滤器系统指南

## 🛡️ 过滤器系统概述

过滤器系统是 UnifiedRegistry 的核心安全和权限控制机制。它允许您在命令执行前进行各种检查，如权限验证、消息类型过滤、自定义条件判断等。

过滤器系统也可以用来定义**非命令的功能**，如果一个函数没有被 `@command_registry.command` 装饰，但是有装饰器装饰。当消息事件发生时，只要能通过过滤器，那么这个函数就会被调用。

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

### 1. GroupFilter/PrivateFilter - 群聊过滤器/私聊过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import GroupFilter
from ncatbot.plugin_system import group_filter

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 可以在插件类中定义
    @group_filter
    async def group_message(self, event: BaseMessageEvent):
        await event.reply("收到一条群聊消息")
    
# 也可以在插件类外定义
@private_filter
async def private_message(event: BaseMessageEvent):
    await event.reply("收到一条私聊消息")
        
```

**功能**: 只允许在群聊中使用的命令
**使用场景**: 群管理、群游戏、群公告等


### 2. AdminFilter - 管理员过滤器

只允许 **Bot管理员** 使用的命令。

```python
from ncatbot.plugin_system import admin_filter

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 可以和 command 组合使用，作为额外的判断条件
    @admin_filter
    @command_registry.command("ban")
    async def ban_command(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已封禁用户: {user_id}")
    
    # 也可以单独使用，消息只要满足过滤器就触发回调
    @admin_filter
    async def admin_message(self, event: BaseMessageEvent):
        await event.reply("收到一条管理员消息")
```

**功能**: 只允许管理员使用的命令
**前置条件**: 需要配置权限管理系统
**使用场景**: 系统管理、用户管理、配置修改等

### 3. RootFilter - Root权限过滤器

只允许 **Root用户** 使用的命令。（root 用户只能在代码里指定）

```python
from ncatbot.plugin_system import root_filter

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @root_filter
    @command_registry.command("shutdown")
    async def shutdown_command(self, event: BaseMessageEvent):
        await event.reply("正在关闭机器人...")
    
```

**功能**: 只允许 Root 用户使用的命令
**使用场景**: 系统级操作、调试功能、危险操作等

### 4. TrueFilter - 消息专用过滤器

用于在发送消息时回调一个指定的函数。

```python
from ncatbot.plugin_system import on_message

@on_message
async def on_message_callback(event: BaseMessageEvent):
    await event.reply("收到一条消息")
```


## 🔗 过滤器组合使用

### 组合装饰器

```python
from ncatbot.plugin_system import (
    group_filter, admin_filter, private_filter, admin_group_filter, admin_private_filter
)

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 管理员 + 群聊
    @admin_group_filter  # 等同于 @admin_filter + @group_filter
    @command_registry.command("grouppromote")
    async def group_promote_command(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"在群聊中提升用户权限: {user_id}")
    
    # 管理员 + 私聊
    @admin_private_filter  # 等同于 @admin_filter + @private_filter
    @command_registry.command("adminpanel")
    async def admin_panel_command(self, event: BaseMessageEvent):
        await event.reply("管理员私聊面板")
    
    # 手动组合多个过滤器
    @admin_filter
    @group_filter
    async def group_admin_command(self, event: BaseMessageEvent):
        await event.reply("收到一条管理员发送的群聊消息")
        
```

### 一次性注册多个过滤器

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 过滤器按从上到下的顺序执行
    @filter_registry.filters("admin_filter", "group_filter")
    @command_registry.command("order")
    async def order_command(self, event: BaseMessageEvent):
        """执行顺序: group_filter -> admin_filter -> 命令函数"""
        await event.reply("多重过滤器命令")
```

## 🛠️ 自定义过滤器

### 1. 使用 CustomFilter

自定义过滤器时，过滤器函数**只接受一个 `BaseMessageEvent` 对象作为参数**。返回 `bool` 类型，表示是否通过过滤器。

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import CustomFilter
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry

@filter_registry.register("time_filter")
def time_filter(event: BaseMessageEvent) -> bool:
    import datetime
    current_hour = datetime.datetime.now().hour
    return 9 <= current_hour <= 22  # 只在9:00-22:00之间可用

@filter_registry.register("keyword_filter")
def keyword_filter(event: BaseMessageEvent) -> bool:
    return "机器人" in (event.raw_message or "")

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass


@filter_registry.filters("time_filter")
async def time_filter_command(event: BaseMessageEvent):
    await event.reply("当前时间允许使用此命令")

# 插件类外，除了装饰器，还可以使用函数添加自定义过滤器
filter_registry.add_filter_to_function(
    time_check_command, 
    "keyword_filter"
)
```

### 2. 注册过滤器函数

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry

# 注册过滤器函数，注意一般不能在类中注册，过滤器函数不接受 self 参数
@filter_registry.register("vip_filter")
def vip_filter(event: BaseMessageEvent) -> bool:
    # 检查用户是否为VIP（这里只是示例）
    vip_users = ["123456", "789012"]
    return event.user_id in vip_users

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
        
    # 使用注册的过滤器
    @command_registry.command("vip")
    async def vip_command(self, event: BaseMessageEvent):
        await event.reply("VIP专属功能")
        
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
        pass

    # 过滤器类可以直接作为装饰器使用
    @LevelFilter(min_level=5)
    async def high_level_command(self, event: BaseMessageEvent):
        await event.reply("收到一条高等级用户的消息")
        
```

## 📚 常用过滤器模式

### 1. 冷却时间控制

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import CustomFilter
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import filter_registry

@filter_registry.register("cooldown")
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

class MyPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.last_use = {}  # 记录上次使用时间
    
    async def on_load(self):
        pass


    @filter_registry.filters("cooldown")
    @command_registry.command("limited")
    async def limited_command(self, event: BaseMessageEvent):
        await event.reply("有冷却限制的命令")
    
```

## 🚦 下一步

掌握过滤器系统后，您可以：

1. **学习命令系统**: 查看 [命令注册系统指南](./UnifiedRegistry-命令系统.md)
2. **了解参数处理**: 阅读 [参数解析指南](./UnifiedRegistry-参数解析.md)
3. **查看实际应用**: 参考 [实战案例](./UnifiedRegistry-实战案例.md)

---

**💡 提示**: 过滤器是 UnifiedRegistry 的强大功能，合理使用可以大大提升插件的安全性和用户体验。
