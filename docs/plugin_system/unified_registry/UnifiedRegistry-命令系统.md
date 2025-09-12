# UnifiedRegistry 命令注册系统指南

## 📋 命令系统概述

UnifiedRegistry 的命令系统提供了现代化的命令注册和管理功能。它支持声明式的命令定义、灵活的参数处理、智能的别名系统和完善的错误处理机制。

## 🎯 核心概念

### 命令注册流程

1. **声明式注册**: 使用装饰器声明命令
2. **自动发现**: 系统自动发现并注册命令
3. **类型分析**: 自动分析函数签名和参数类型（除了 `self` 外的所有参数都必须有类型注解）
4. **冲突检测**: 智能检测命令名称和别名冲突

### 关键组件

- **命令注册器** (`command_registry`): 全局命令管理器
- **命令组** (`CommandGroup`): 支持命令分组组织
- **装饰器系统**: 提供丰富的配置选项
- **参数分析器**: 自动处理函数签名

## 🔧 基础命令注册

### 1. 简单命令注册

```python
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        """简单的问候命令"""
        await event.reply("Hello, World!")
    
    @command_registry.command("ping")
    async def ping_cmd(self, event: BaseMessageEvent):
        """检查机器人状态"""
        await event.reply("pong!")
```

**⚠️ 重要提醒**: 除 `self` 外的所有参数都必须有类型注解。

### 2. 带描述的命令

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("info", description="获取机器人信息")
    async def info_cmd(self, event: BaseMessageEvent):
        await event.reply("这是一个示例机器人")
    
    @command_registry.command("version", description="查看版本信息")
    async def version_cmd(self, event: BaseMessageEvent):
        await event.reply(f"插件版本: {self.version}")
```

### 3. 命令别名

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    async def status_cmd(self, event: BaseMessageEvent):
        """支持多个别名的命令"""
        await event.reply("机器人运行正常")
    
    @command_registry.command("help", aliases=["h", "?"], description="帮助信息")
    async def help_cmd(self, event: BaseMessageEvent):
        await event.reply("可用命令: status, help, ping")
```

### 4. 类外命令

```python
from ncatbot.core.event import BaseMessageEvent

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

# 
@command_registry.command("status", aliases=["stat", "st"], description="查看状态")
async def status_cmd(event: BaseMessageEvent):
    """支持多个别名的命令"""
    await event.reply("机器人运行正常")
```

**使用方式**: `/status`, `/stat`, `/st` 都会触发同一个命令
**注意**: 类外命令没有 `self` 参数，所以无法访问插件实例的属性和方法。推荐使用插件类成员方法。

## 📝 参数处理

### 1. 基础参数类型

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("echo")
    async def echo_cmd(self, event: BaseMessageEvent, text: str):
        """字符串参数"""
        await event.reply(f"你说的是: {text}")
    
    @command_registry.command("add")
    async def add_cmd(self, event: BaseMessageEvent, a: int, b: int):
            """整数参数"""
            await event.reply(f"{a} + {b} = {a + b}")
        
    @command_registry.command("calculate")
    async def calc_cmd(self, event: BaseMessageEvent, x: float, y: float):
        """浮点数参数"""
        await event.reply(f"{x} * {y} = {x * y}")
    
    @command_registry.command("toggle")
    async def toggle_cmd(self, event: BaseMessageEvent, enabled: bool):
        """布尔参数"""
        status = "开启" if enabled else "关闭"
        await event.reply(f"功能已{status}")
```

**使用示例**:
- `/echo 测试文本` → "你说的是: 测试文本"
- `/add 10 20` → "10 + 20 = 30"
- `/calculate 3.14 2.0` → "3.14 * 2.0 = 6.28"
- `/toggle true` → "功能已开启"

### 2. 可选参数和默认值

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("greet")
        async def greet_cmd(self, event: BaseMessageEvent, name: str = "朋友"):
            """带默认值的参数"""
            await event.reply(f"你好，{name}！")
        
    @command_registry.command("repeat")
    async def repeat_cmd(self, event: BaseMessageEvent, text: str, count: int = 1):
        """多个参数，部分有默认值"""
        await event.reply("\n".join([text] * count))
```

**使用示例**:
- `/greet` → "你好，朋友！"
- `/greet 小明` → "你好，小明！"
- `/repeat Hello` → "Hello"
- `/repeat Hello 3` → "Hello\nHello\nHello"

## 🎛️ 选项和命名参数

通过使用选项和命名参数修饰器，可以更灵活地定义命令参数。能够接受现代化命令行的传参风格。

### 1. 选项装饰器 (@option)

```python
from ncatbot.plugin_system import option

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("deploy", description="部署应用")
    @option(short_name="v", long_name="verbose", help="显示详细信息")
    @option(short_name="f", long_name="force", help="强制部署")
    async def deploy_cmd(self, event: BaseMessageEvent, app_name: str, 
                    verbose: bool = False, force: bool = False):
        result = f"部署应用: {app_name}"
        if force:
            result += " (强制模式)"
        if verbose:
            result += "\n详细信息: 开始部署流程..."
        await event.reply(result)
```

**使用方式**:
- `/deploy myapp` → "部署应用: myapp"
- `/deploy myapp -v` → "部署应用: myapp\n详细信息: 开始部署流程..."
- `/deploy myapp --verbose --force` → "部署应用: myapp (强制模式)\n详细信息: 开始部署流程..."

### 2. 命名参数 (@param)

```python
from ncatbot.plugin_system import param

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("config", description="配置设置")
    @param(name="env", default="dev", help="运行环境")
    @param(name="port", default=8080, help="端口号")
    async def config_cmd(self, event: BaseMessageEvent, env: str = "dev", port: int = 8080):
        await event.reply(f"配置: 环境={env}, 端口={port}")
```

**使用方式**:
- `/config` → "配置: 环境=dev, 端口=8080"
- `/config --env=prod` → "配置: 环境=prod, 端口=8080"
- `/config --env=prod --port=9000` → "配置: 环境=prod, 端口=9000"

### 3. 选项组 (@option_group)

```python
from ncatbot.plugin_system import option_group

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("export", description="导出数据")
    @option_group(choices=["json", "csv", "xml"], name="format", default="json", help="输出格式")
    async def export_cmd(self, event: BaseMessageEvent, data_type: str, format: str = "json"):
        await event.reply(f"导出 {data_type} 数据为 {format} 格式")
```

**使用方式**:
- `/export users` → "导出 users 数据为 json 格式"
- `/export users --csv` → "导出 users 数据为 csv 格式"
- `/export users --xml` → "导出 users 数据为 xml 格式"

## 🏗️ 命令组织

### 1. 命令分组

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 创建用户管理命令组
    user_group = command_registry.group("user", description="用户管理命令")
    
    @user_group.command("list", description="列出所有用户")
    async def user_list_cmd(self, event: BaseMessageEvent):
        await event.reply("用户列表: user1, user2, user3")
    
    @user_group.command("info", description="查看用户信息")
    async def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"用户 {user_id} 的信息")
    
    # 创建系统管理命令组
    system_group = command_registry.group("system", description="系统管理")
    
    @system_group.command("status", description="系统状态")
    async def system_status_cmd(self, event: BaseMessageEvent):
        await event.reply("系统运行正常")
```

**使用方式**:
- `/user list` → "用户列表: user1, user2, user3"
- `/user info 123` → "用户 123 的信息"
- `/system status` → "系统运行正常"

### 2. 嵌套命令组

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 创建主命令组（类属性）
    admin_group = command_registry.group("admin", description="管理功能")
    # 创建子命令组（类属性）
    user_admin = admin_group.group("user", description="用户管理")
    
    @user_admin.command("ban", description="封禁用户")
    async def ban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已封禁用户: {user_id}")
    
    @user_admin.command("unban", description="解封用户")
    async def unban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已解封用户: {user_id}")
```

**使用方式**:
- `/admin user ban 123` → "已封禁用户: 123"
- `/admin user unban 123` → "已解封用户: 123"

### 3. 组命令别名（端点别名直达）

命令组中的“端点命令”可以声明 `aliases`。这些别名会被提升为“根级别别名”，从而允许你绕过冗长的组前缀，直接触发端点命令。

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # 创建用户组
    user_group = command_registry.group("user", description="用户管理命令")

    @user_group.command("list", aliases=["ul"], description="列出所有用户")
    async def user_list_cmd(self, event: BaseMessageEvent):
        await event.reply("用户列表: user1, user2, user3")

    @user_group.command("info", aliases=["ui"], description="查看用户信息")
    async def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"用户 {user_id} 的信息")

    # 嵌套组：admin -> user
    admin_group = command_registry.group("admin", description="管理功能")
    user_admin = admin_group.group("user", description="用户管理")

    @user_admin.command("ban", aliases=["aub"], description="封禁用户")
    async def ban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已封禁用户: {user_id}")

    @user_admin.command("unban", aliases=["aun"], description="解封用户")
    async def unban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已解封用户: {user_id}")
```

**使用方式**:
- 组路径调用：`/user list`、`/user info 123`、`/admin user ban 123`、`/admin user unban 123`
- 别名直达：`/ul`、`/ui 123`、`/aub 123`、`/aun 123`

## 🔧 高级功能

### 1. 复杂参数组合

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("backup", description="数据备份")
    @option(short_name="c", long_name="compress", help="压缩备份")
    @option(short_name="e", long_name="encrypt", help="加密备份")
    @param(name="path", default="/backup", help="备份路径")
    @param(name="exclude", default="", help="排除文件")
    async def backup_cmd(self, event: BaseMessageEvent, database: str,
                    path: str = "/backup", exclude: str = "",
                    compress: bool = False, encrypt: bool = False):
        result = f"备份数据库 {database} 到 {path}"
        
        features = []
        if compress:
            features.append("压缩")
        if encrypt:
            features.append("加密")
        if exclude:
            features.append(f"排除: {exclude}")
        
        if features:
            result += f" ({', '.join(features)})"
        
        await event.reply(result)
```

**使用方式**:
- `/backup mydb` → "备份数据库 mydb 到 /backup"
- `/backup mydb --path=/data/backup -c -e` → "备份数据库 mydb 到 /data/backup (压缩, 加密)"
- `/backup mydb --exclude=logs` → "备份数据库 mydb 到 /backup (排除: logs)"

### 2. 条件参数

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("send", description="发送消息")
    @option(short_name="a", long_name="all", help="发送给所有人")
    async def send_cmd(self, event: BaseMessageEvent, message: str, 
                    target: str = "", all: bool = False):
        if all:
            await event.reply(f"广播消息: {message}")
        elif target:
            await event.reply(f"发送给 {target}: {message}")
        else:
            await event.reply(f"发送消息: {message} (默认发送给当前用户)")
```

### 3. 自定义前缀

可以通过 `command_registry.get_registry(prefixes=["!", "/"])` 来设置自定义前缀。

通过该接口直接或间接注册的命令均会受到自定义前缀的影响。

```python
from ncatbot.plugin_system import command_registry

my_registry = command_registry.get_registry(prefixes=["", "!"]) # 无前缀触发或者 ! 触发

my_group = my_registry.group("my_group", description="无前缀组")

@my_registry.command("non_prefix_hello")
async def non_prefix_hello_cmd(event: BaseMessageEvent):
    await event.reply("Hello, World!")

@my_group.command("my_group_hello")
async def my_group_hello_cmd(event: BaseMessageEvent):
    await event.reply("Hello, Group World!")
```

- 使用方式: `non_prefix_hello`, `!my_group my_group_hello`

## 📋 装饰器使用最佳实践

### 1. 装饰器顺序

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    # ✅ 正确的装饰器顺序
    @admin_only                    # 过滤器在最上面
    @command_registry.command("admin")  # 命令注册器其次
    @option("v", "verbose")        # 参数装饰器在最后
    @param("level", default=1)
    async def admin_cmd(self, event: BaseMessageEvent, level: int = 1, verbose: bool = False):
        await event.reply(f"管理员命令，级别: {level}")
    
    # ❌ 错误的顺序（会导致错误）
    # @command_registry.command("wrong")
    # @admin_only  # 过滤器装饰器应该在命令装饰器之前
```

### 2. 参数命名规范

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        # ✅ 清晰的参数命名
        pass
    
    @command_registry.command("create_user")
    @param("role", default="user", help="用户角色")
    @option("s", "send_email", help="发送欢迎邮件")
    async def create_user_cmd(self, event: BaseMessageEvent, username: str, 
                        role: str = "user", send_email: bool = False):
        result = f"创建用户: {username}, 角色: {role}"
        if send_email:
            result += " (已发送欢迎邮件)"
        await event.reply(result)
```

## 🔍 错误处理和调试

### 1. 参数验证

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("divide")
    async def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
        """除法命令，包含错误处理"""
        if b == 0:
            await event.reply("错误: 除数不能为0")
            return
        
        result = a / b
        await event.reply(f"{a} ÷ {b} = {result}")
    
    @command_registry.command("age")
    async def age_cmd(self, event: BaseMessageEvent, age: int):
        """年龄验证"""
        if age < 0 or age > 150:
            await event.reply("错误: 请输入有效的年龄 (0-150)")
            return
        
        await event.reply(f"您的年龄是: {age}")
```

### 2. 调试信息

```python
from ncatbot.utils import get_log

LOG = get_log(__name__)

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("debug")
    async def debug_cmd(self, event: BaseMessageEvent, action: str):
        """带调试信息的命令"""
        LOG.debug(f"用户 {event.user_id} 执行调试命令: {action}")
        
        if action == "info":
            await event.reply(f"调试信息: 用户ID={event.user_id}, 时间={event.time}")
        elif action == "status":
            await event.reply("调试状态: 正常")
        else:
            LOG.warning(f"未知的调试动作: {action}")
            await event.reply("未知的调试动作")
```

## 📊 命令注册总结

### 支持的功能

| 功能 | 装饰器 | 示例 |
|------|--------|------|
| 基础命令 | `@command_registry.command()` | `@command_registry.command("hello")` |
| 命令别名 | `aliases=[]` | `@command_registry.command("hi", aliases=["hello"])` |
| 短选项 | `@option(short_name="")` | `@option("v", help="详细模式")` |
| 长选项 | `@option(long_name="")` | `@option(long_name="verbose")` |
| 命名参数 | `@param()` | `@param("env", default="dev")` |
| 选项组 | `@option_group()` | `@option_group(choices=["a", "b"])` |
| 命令组 | `command_registry.group()` | `user_group = command_registry.group("user")` |

### 参数类型支持

- ✅ `str` - 字符串
- ✅ `int` - 整数  
- ✅ `float` - 浮点数
- ✅ `bool` - 布尔值
- ✅ 默认值支持
- ✅ 可选参数

## 🚦 下一步

现在您已经掌握了命令系统的使用！接下来可以：

1. **学习参数解析**: 查看 [参数解析指南](./UnifiedRegistry-参数解析.md) 了解更多高级语法
2. **查看实际应用**: 参考 [实战案例](./UnifiedRegistry-实战案例.md) 学习实用技巧
3. **掌握最佳实践**: 阅读 [最佳实践](./UnifiedRegistry-最佳实践.md) 提升代码质量

---

**💡 提示**: 命令系统设计强调类型安全和声明式配置，充分利用 Python 的类型注解和装饰器特性。
