# UnifiedRegistry 快速开始指南

## 🎯 5分钟上手 UnifiedRegistry

本指南将帮助您快速掌握 UnifiedRegistry 的基本用法，从零开始创建一个功能完整的插件。

## 📋 前置要求

- 已安装 NCatBot
- 基本的 Python 编程知识
- 了解 QQ 机器人的基本概念

## 🚀 第一个插件

### 1. 基础设置

```python
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only, private_only, admin_only
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent

class HelloPlugin(NcatBotPlugin):
    name = "HelloPlugin"
    version = "1.0.0"
    author = "你的名字"
    description = "我的第一个 UnifiedRegistry 插件"
    
    async def on_load(self):
        """插件加载时注册命令"""
        # 在这里注册命令函数
        pass
```

**⚠️ 重要**: 命令函数的所有参数（除了 `self`）都必须有类型注解，这是 UnifiedRegistry 的严格要求。

### 2. 注册简单命令

这些函数应该写在插件类里面：

```python
class HelloPlugin(NcatBotPlugin):
    # 其他代码

    @command_registry.command("hello")
    def hello_cmd(self, event: BaseMessageEvent):
        """简单的问候命令"""
        return "你好！我是机器人。"

    @command_registry.command("ping")
    def ping_cmd(self, event: BaseMessageEvent):
        """检查机器人状态"""
        return "pong!"
```

**使用方式**: 
- `/hello` -> "你好！我是机器人。"
- `/ping` -> "pong!"

### 3. 带参数的命令

```python
class HelloPlugin(NcatBotPlugin):
    # 其他代码

    @command_registry.command("echo")
    def echo_cmd(self, event: BaseMessageEvent, text: str):
        """回显用户输入的文本"""
        return f"你说的是: {text}"

    @command_registry.command("add")
    def add_cmd(self, event: BaseMessageEvent, a: int, b: int):
        """计算两个数的和"""
        result = a + b
        return f"{a} + {b} = {result}"
```

**使用方式**:
- `/echo 测试文本` -> "你说的是: 测试文本"
- `/add 10 20` -> "10 + 20 = 30"

### 4. 添加权限控制

```python
class HelloPlugin(NcatBotPlugin):
    # 其他代码

    async def on_load(self):
        pass

    # 仅群聊可用
    @group_only
    @command_registry.command("groupinfo")
    def group_info_cmd(self, event: BaseMessageEvent):
        """获取群聊信息"""
        return f"当前群聊ID: {event.group_id}"

    # 仅私聊可用
    @private_only
    @command_registry.command("private")
    def private_cmd(self, event: BaseMessageEvent):
        """私聊专用命令"""
        return "这是一个私聊命令"

    # 仅 Bot 管理员可用
    @admin_only
    @command_registry.command("admin")
    def admin_cmd(self, event: BaseMessageEvent):
        """管理员专用命令"""
        return "你是管理员！"
```

### 5. 复杂参数和选项

支持一些流行的命令行风格参数指定方式。

需要用 option、param、option_group 装饰器来指定参数，这些被指定的参数**必须放在函数参数表的最后面**。

用修饰器声明部分参数后，可以通过 `-v`、`--verbose`、`-f`、`--force`、`--env=dev` 等指定参数值，这些语法是顺序无关的。


```python
class HelloPlugin(NcatBotPlugin):
    # 其他代码

    async def on_load(self):
        pass

    @command_registry.command("deploy", description="部署应用")
    @option(short_name="v", long_name="verbose", help="显示详细信息")
    @option(short_name="f", long_name="force", help="强制部署")
    @param(name="env", default="dev", help="部署环境")
    def deploy_cmd(self, event: BaseMessageEvent, app_name: str, 
                env: str = "dev", verbose: bool = False, force: bool = False):
        """部署应用到指定环境"""
        result = f"正在部署 {app_name} 到 {env} 环境"
        
        if force:
            result += " (强制模式)"
        
        if verbose:
            result += "\n详细信息: 开始部署流程..."
            
        return result
```

**使用方式**:
- `/deploy myapp` -> "正在部署 myapp 到 dev 环境"
- `/deploy myapp --env=prod -v` -> "正在部署 myapp 到 prod 环境\n详细信息: 开始部署流程..."
- `/deploy myapp --force` -> "正在部署 myapp 到 dev 环境 (强制模式)"
- `/deploy --force myapp` -> "正在部署 myapp 到 dev 环境 (强制模式)\n详细信息: 开始部署流程..."（同上条指令）

### 6. 命令别名

别名更常用于快速访问指令组的命令。

```python
class HelloPlugin(NcatBotPlugin):
    # 其他代码

    async def on_load(self):
        pass

    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    def status_cmd(self, event: BaseMessageEvent):
        """查看机器人状态（支持多个别名）"""
        return "机器人运行正常"
```

**使用方式**: `/status`, `/stat`, `/st` 都可以触发同一个命令

## 🎯 完整插件示例

```python
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only, admin_only
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent

class MyFirstPlugin(NcatBotPlugin):
    name = "MyFirstPlugin"
    version = "1.0.0"
    author = "你的名字"
    description = "完整的示例插件"
    
    async def on_load(self):
        pass
    
    # 简单问候
    @command_registry.command("hello", aliases=["hi"], description="问候命令")
    def hello_cmd(self, event: BaseMessageEvent):
        return f"你好！用户 {event.user_id}"
    
    # 计算器
    @command_registry.command("calc", description="简单计算器")
    def calc_cmd(self, event: BaseMessageEvent, a: int, op: str, b: int):
        if op == "add":
            return f"{a} + {b} = {a + b}"
        elif op == "sub":
            return f"{a} - {b} = {a - b}"
        elif op == "mul":
            return f"{a} * {b} = {a * b}"
        elif op == "div":
            if b == 0:
                return "错误：除数不能为0"
            return f"{a} / {b} = {a / b}"
        else:
            return "支持的操作: add, sub, mul, div"
    
    # 群聊管理
    @group_only
    @admin_only
    @command_registry.command("announce", description="发布公告")
    @option(short_name="a", long_name="all", help="发送给所有群员")
    def announce_cmd(self, event: BaseMessageEvent, message: str, all: bool = False):
        result = f"公告: {message}"
        if all:
            result += " [发送给所有群员]"
        return result
    
    # 带默认值的命令
    @command_registry.command("greet", description="个性化问候")
    @param(name="name", default="朋友", help="要问候的名字")
    def greet_cmd(self, event: BaseMessageEvent, name: str = "朋友"):
        return f"你好，{name}！欢迎使用机器人。"
```

## 💡 额外示例：普通函数注册 (Bonus)

除了在插件类中注册命令，您也可以在插件类外定义普通函数：

```python
from ncatbot.core.event import BaseMessageEvent

# 在插件类外定义命令函数
@command_registry.command("outside")
def outside_command(event: BaseMessageEvent):
    """插件类外的命令函数"""
    return "这是在插件类外定义的命令"

@admin_only
@command_registry.command("external_admin")
def external_admin_cmd(event: BaseMessageEvent, action: str):
    """外部的管理员命令"""
    return f"执行管理员操作: {action}"

class MyPlugin(NcatBotPlugin):
    name = "MyPlugin"
    version = "1.0.0"
    
    async def on_load(self):
        pass

    # 类内的命令
    @command_registry.command("inside")
    def inside_cmd(self, event: BaseMessageEvent):
        return "这是类内的命令"
```

**注意**: 普通函数没有 `self` 参数，所以无法访问插件实例的属性和方法。推荐使用插件类成员方法。

## 🚦 下一步

现在您已经掌握了 UnifiedRegistry 的基础用法！接下来可以：

1. **深入学习**: 阅读 [过滤器系统指南](./UnifiedRegistry-过滤器系统.md) 了解更多权限控制
2. **探索功能**: 查看 [命令注册系统](./UnifiedRegistry-命令系统.md) 学习高级命令功能
3. **参数解析**: 学习 [参数解析指南](./UnifiedRegistry-参数解析.md) 掌握复杂参数处理
4. **实战练习**: 参考 [实战案例](./UnifiedRegistry-实战案例.md) 开发实用插件

## ⚠️ 常见注意事项

1. **类型注解必须**: 除 `self` 外的所有参数都必须有类型注解
2. **装饰器顺序**: 过滤器装饰器要在 `@command_registry.command()` 之前
3. **参数顺序**: `@option` 和 `@param` 装饰器要在命令装饰器之前
4. **返回值**: 命令函数应该返回字符串，这将作为机器人的回复

---

**🎉 恭喜**: 您已经掌握了 UnifiedRegistry 的基础用法！开始创建您的第一个插件吧！
