# FilterRegistry 快速开始指南

## 🚀 什么是 FilterRegistry？

FilterRegistry 是 NCatBot 的核心插件系统，提供了强大而灵活的消息过滤和命令处理功能。通过简单的装饰器，你可以轻松创建功能丰富的 QQ 机器人插件。

## ⚡ 5分钟快速上手

### 1. 基础导入

```python
from ncatbot.plugin_system.builtin_plugin.filter_registry import filter
from ncatbot.core.event.message import BaseMessageEvent
from ncatbot.plugin import BasePlugin
```

### 2. 创建你的第一个插件

```python
class MyFirstPlugin(BasePlugin):
    name = "MyFirstPlugin"
    version = "1.0.0"
    
    @filter.command("hello")
    async def say_hello(self, event: BaseMessageEvent):
        await event.reply("你好！我是机器人 🤖")
    
    @filter.command("ping")
    async def ping_pong(self, event: BaseMessageEvent):
        await event.reply("pong! 🏓")
```

### 3. 测试你的插件

发送以下消息到 QQ：
- `hello` → 机器人回复："你好！我是机器人 🤖"
- `ping` → 机器人回复："pong! 🏓"

## 🎯 核心功能一览

### 📋 基础命令
```python
@filter.command("天气")
async def weather(self, event: BaseMessageEvent):
    await event.reply("今天晴朗 ☀️")
```

### 🔒 权限控制
```python
@filter.admin_only()
@filter.command("管理")
async def admin_command(self, event: BaseMessageEvent):
    await event.reply("管理员专用功能")
```

### 📱 消息类型过滤
```python
@filter.group_message()
@filter.command("群聊功能")
async def group_only(self, event: BaseMessageEvent):
    await event.reply("这是群聊专用功能")

@filter.private_message()
@filter.command("私聊功能")
async def private_only(self, event: BaseMessageEvent):
    await event.reply("这是私聊专用功能")
```

### 🎯 自定义过滤器
```python
@filter.custom(lambda event: '紧急' in event.raw_message)
async def emergency_handler(self, event: BaseMessageEvent):
    await event.reply("收到紧急消息！⚠️")
```

### 📝 参数解析
```python
@filter.command("计算")
async def calculate(self, event: BaseMessageEvent, a: int, b: int):
    result = a + b
    await event.reply(f"{a} + {b} = {result}")
```

使用方法：发送 `计算 5 3` → 回复："5 + 3 = 8"

## 📚 下一步

- 📖 [完整功能指南](./FilterRegistry-完整指南.md) - 了解所有功能
- 🎨 [最佳实践](./FilterRegistry-最佳实践.md) - 专业开发技巧
- 🧪 [测试指南](./FilterRegistry-测试指南.md) - 确保代码质量
- 🎯 [实战案例](./FilterRegistry-实战案例.md) - 真实应用场景

## 💡 提示

- 所有装饰器都支持组合使用
- 参数类型会自动转换（支持 int、float、bool、str）
- 使用 `event.reply()` 快速回复消息
- 查看系统日志了解详细的执行信息

开始你的机器人开发之旅吧！🎉
