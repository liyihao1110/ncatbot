# 现代化命令注册系统

一个功能强大、类型安全的命令注册框架，专为聊天机器人设计。

## 🌟 核心特性

### ✨ 直观的API设计
- **链式装饰器**: 支持任意顺序的装饰器组合
- **类型安全**: 完整的类型注解和自动转换
- **智能提示**: 详细的错误信息和修正建议

### 🔧 多类型参数支持
- **联合类型**: 一个参数支持多种类型（如 `str | MessageSegment`）
- **自动推断**: 智能类型推断和转换
- **用户友好**: 针对不同类型提供专门的提示和示例

### 📋 完善的错误处理
- **分层异常**: 注册时、解析时、执行时的不同错误类型
- **上下文感知**: 根据错误发生的场景提供精确提示
- **智能建议**: 不仅指出错误，还提供修正方案

### 🏗️ 灵活的组织结构
- **命令组**: 支持嵌套的命令组织结构
- **权限控制**: 集成权限系统和自定义过滤器
- **别名支持**: 命令别名和快捷方式

## 🚀 快速开始

### 基础命令

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.modern_registry import registry

@registry.command("hello", description="简单问候")
def hello_command(event):
    """返回问候信息"""
    return "Hello, World! 👋"

@registry.command("greet", description="个性化问候")
def greet_command(event, name: str, times: int = 1):
    """问候指定用户
    
    Args:
        name: 用户名
        times: 问候次数（默认1次）
    """
    return f"Hello {name}! " * times
```

### 带选项的命令

```python
@registry.command("backup", description="备份文件")
@registry.option("-v", "--verbose", help="显示详细信息")
@registry.option("-f", "--force", help="强制备份")
def backup_command(event, path: str, verbose=False, force=False):
    """备份指定路径的文件"""
    result = f"备份路径: {path}"
    if verbose:
        result += "\n详细信息: 正在备份..."
    if force:
        result += "\n强制模式已启用"
    return result
```

### 命名参数

```python
@registry.command("deploy", description="部署应用")
@registry.param("env", type=str, choices=["dev", "test", "prod"], default="dev")
@registry.param("port", type=int, default=8080)
@registry.option("-d", "--dry-run", help="试运行")
def deploy_command(event, app_name: str, env="dev", port=8080, dry_run=False):
    """部署应用到指定环境"""
    return f"部署 {app_name} 到 {env} 环境，端口 {port}"
```

### 多类型参数

```python
from .types import CommonUnionTypes

@registry.command("mention", description="提及用户")
@registry.param("target", type=CommonUnionTypes.USER_IDENTIFIER, 
                help="目标用户（用户名或@用户）")
def mention_command(event, target, message: str = "你好"):
    """提及用户并发送消息"""
    if isinstance(target, str):
        return f"发送给用户 {target}: {message}"
    else:  # MessageSegment
        return f"发送给 @{target.qq}: {message}"
```

## 🎯 高级特性

### 互斥选项组

```python
@registry.command("format", description="格式化数据")
@registry.option_group(1, mutually_exclusive=True, name="输出格式")
@registry.option("-j", "--json", group=1, help="JSON格式")
@registry.option("-x", "--xml", group=1, help="XML格式")
@registry.option("-y", "--yaml", group=1, help="YAML格式")
def format_command(event, data: str, json=False, xml=False, yaml=False):
    """格式化数据（只能选择一种格式）"""
    if json:
        return f"JSON: {data}"
    elif xml:
        return f"XML: {data}"
    elif yaml:
        return f"YAML: {data}"
```

### 权限控制

```python
@registry.command("shutdown", description="关闭系统")
@registry.admin_only(error_message="此命令需要管理员权限")
@registry.option("-f", "--force", help="强制关机")
def shutdown_command(event, force=False):
    """关闭系统（仅管理员）"""
    return "系统关机中..." if force else "准备关机"

@registry.command("vip", description="VIP功能")
@registry.filter(lambda event: event.user_id in vip_users, "仅VIP用户可用")
def vip_command(event):
    """VIP专用功能"""
    return "欢迎VIP用户!"
```

### 命令组

```python
# 创建管理员命令组
admin_group = registry.group("admin", description="管理员专用命令")

@admin_group.command("user", description="用户管理")
@registry.option("--list", help="列出用户")
@registry.option("--add", help="添加用户")
def admin_user_command(event, username: str = "", list_users=False, add=False):
    """管理用户账户"""
    if list_users:
        return "用户列表: Alice, Bob, Charlie"
    elif add and username:
        return f"添加用户: {username}"

# 嵌套命令组
db_group = admin_group.group("db", description="数据库管理")

@db_group.command("backup", description="数据库备份")
@registry.param("target", type=str, help="备份目标路径")
def db_backup_command(event, target: str):
    """备份数据库"""
    return f"备份数据库到: {target}"
```

## 🔧 类型系统

### 基础类型

支持的基础类型：
- `str` - 文本字符串
- `int` - 整数
- `float` - 浮点数
- `bool` - 布尔值
- `MessageSegment` - 消息段（图片、@用户等）

### 联合类型

```python
from typing import Union
from .types import UnionType, CommonUnionTypes

# 方式1: 使用预定义联合类型
@registry.param("user", type=CommonUnionTypes.USER_IDENTIFIER)

# 方式2: 使用类型注解
def command(event, user: Union[str, MessageSegment]):
    pass

# 方式3: 使用列表定义
@registry.param("input", type=[str, MessageSegment])
```

### 预定义联合类型

```python
CommonUnionTypes.USER_IDENTIFIER    # str | MessageSegment (用户标识)
CommonUnionTypes.STR_OR_AT          # str | MessageSegment (@用户或文本)
CommonUnionTypes.STR_OR_IMAGE       # str | MessageSegment (文本或图片)
CommonUnionTypes.INT_OR_STR         # int | str (数字或文本)
CommonUnionTypes.TEXT_OR_SEGMENT    # str | MessageSegment (文本或任意消息段)
```

## 🛡️ 错误处理

### 智能错误提示

系统提供分层的错误处理：

1. **命令不存在**：
```
❌ 未知命令 'deploi'
💡 你可能想要: deploy
📋 可用命令: deploy, backup, status...
❓ 输入 /help 查看所有命令
```

2. **参数类型错误**：
```
❌ 参数 'port' 类型错误

📝 您的输入: abc (str)

✅ 支持的类型:
  1. 整数 - 数字端口号
     示例: 8080 | 3000

💡 建议: 请输入有效的端口号
```

3. **多类型转换失败**：
```
❌ 参数 'target' 类型错误

📝 您的输入: invalid (str)

✅ 支持的类型:
  1. 文本 - 用户名或用户ID
     示例: Alice | 123456789
  2. 消息元素 - @用户
     示例: [@Alice]

💡 建议: 请检查输入格式是否正确
```

### 自定义验证

```python
@registry.param("age", type=int, 
                validator=lambda x: 0 <= x <= 150,
                error_messages={"validator": "年龄必须在0-150之间"})
```

## 📚 帮助系统

### 自动生成帮助

```python
# 查看所有命令
/help

# 查看特定命令帮助
/deploy --help
```

帮助文档会自动包含：
- 命令描述和用法
- 参数说明和类型
- 选项列表
- 使用示例
- 类型提示

### 自定义帮助

```python
@registry.command("complex", description="复杂命令")
@registry.param("input", type=[str, MessageSegment],
                type_hints={
                    str: "文件路径或文本内容",
                    MessageSegment: "图片或文件"
                },
                type_examples={
                    str: ["/path/file.txt", "文本内容"],
                    MessageSegment: ["[图片]", "[文件]"]
                })
def complex_command(event, input_data):
    """
    处理复杂输入的命令
    
    这个命令可以处理多种类型的输入：
    - 文件路径
    - 直接文本
    - 图片文件
    - 其他文件类型
    
    示例：
        /complex /path/to/file.txt
        /complex "直接输入的文本"
        /complex [图片]
    """
    pass
```

## ⚙️ 配置选项

### 全局配置

```python
registry.configure(
    prefix="/",                    # 命令前缀
    case_sensitive=False,          # 大小写敏感
    auto_help=True,               # 自动生成帮助
    strict_typing=True,           # 严格类型检查
    allow_unknown_options=False,  # 允许未知选项
    debug=False                   # 调试模式
)
```

### 命令级配置

```python
@registry.command("flexible", strict_mode=False, auto_help=False)
def flexible_command(event):
    """灵活的命令，关闭严格模式"""
    pass
```

## 🔌 集成现有系统

这个注册系统设计为与现有的统一注册系统无缝集成：

1. **保持向后兼容**: 不影响现有命令
2. **渐进式迁移**: 可以逐步迁移现有命令
3. **共享过滤器**: 复用现有的权限和过滤器系统
4. **统一接口**: 通过统一的入口点管理所有命令

## 📝 最佳实践

### 1. 命令设计
- 使用清晰的命令名和描述
- 提供完整的文档字符串
- 合理设置参数默认值

### 2. 参数设计
- 优先使用位置参数
- 为可选参数提供合理默认值
- 使用联合类型提高灵活性

### 3. 错误处理
- 提供有意义的错误信息
- 使用自定义验证器确保数据质量
- 为用户提供明确的修正建议

### 4. 组织结构
- 使用命令组组织相关功能
- 设置合适的权限控制
- 保持命令层次结构清晰

## 🎉 总结

这个现代化命令注册系统为聊天机器人提供了：

- **开发友好**: 直观的装饰器API，类型安全
- **用户友好**: 智能错误提示，自动帮助生成
- **功能完整**: 多类型支持，权限控制，命令组织
- **易于扩展**: 模块化设计，可定制的类型和验证器

通过这个系统，开发者可以快速创建功能丰富、用户体验良好的聊天机器人命令。
