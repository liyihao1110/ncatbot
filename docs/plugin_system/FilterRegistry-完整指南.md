# FilterRegistry 完整功能指南

## 📖 目录

- [基础概念](#基础概念)
- [装饰器系统](#装饰器系统)
- [权限过滤器](#权限过滤器)
- [消息类型过滤器](#消息类型过滤器)
- [命令系统](#命令系统)
- [参数解析](#参数解析)
- [自定义过滤器](#自定义过滤器)
- [事件处理](#事件处理)
- [装饰器组合](#装饰器组合)

## 基础概念

### FilterRegistry 架构

FilterRegistry 基于装饰器模式，通过在函数上添加装饰器来注册过滤器和命令处理逻辑。

```python
from ncatbot.plugin_system.builtin_plugin.filter_registry import filter
```

### 消息处理流程

```
用户消息 → 事件总线 → FilterRegistry → 过滤器检查 → 函数执行 → 回复消息
```

## 装饰器系统

### 核心装饰器

| 装饰器 | 功能 | 用途 |
|--------|------|------|
| `@filter.command()` | 命令注册 | 注册文本命令 |
| `@filter.admin_only()` | 管理员权限 | 限制管理员使用 |
| `@filter.root_only()` | Root权限 | 限制Root用户使用 |
| `@filter.group_message()` | 群聊过滤 | 仅群聊触发 |
| `@filter.private_message()` | 私聊过滤 | 仅私聊触发 |
| `@filter.custom()` | 自定义过滤 | 自定义条件过滤 |
| `@filter.notice_event()` | 通知事件 | 处理系统通知 |
| `@filter.request_event()` | 请求事件 | 处理好友/群请求 |

## 权限过滤器

### 管理员权限

```python
@filter.admin_only()
async def admin_command(self, event: BaseMessageEvent):
    """仅管理员可使用"""
    await event.reply("管理员功能执行成功")
```

### Root权限

```python
@filter.root_only()
async def root_command(self, event: BaseMessageEvent):
    """仅Root用户可使用"""
    await event.reply("Root级别功能执行成功")
```

### 权限说明

- **管理员权限**: 拥有 `admin` 或 `root` 角色的用户
- **Root权限**: 仅拥有 `root` 角色的用户
- 权限由 RBAC 系统管理，可在配置中设置

## 消息类型过滤器

### 群聊消息过滤

```python
@filter.group_message()
async def group_only_function(self, event: BaseMessageEvent):
    """仅在群聊中响应"""
    group_name = event.group_id
    await event.reply(f"这是群 {group_name} 的专用功能")
```

### 私聊消息过滤

```python
@filter.private_message()
async def private_only_function(self, event: BaseMessageEvent):
    """仅在私聊中响应"""
    user_id = event.user_id
    await event.reply(f"用户 {user_id}，这是私聊专用功能")
```

### 别名方法

```python
# 以下两种写法等价
@filter.group_message()
@filter.group_event()  # 别名

@filter.private_message()
@filter.private_event()  # 别名
```

## 命令系统

### 基础命令

```python
@filter.command("帮助")
async def help_command(self, event: BaseMessageEvent):
    await event.reply("这是帮助信息")
```

### 命令别名

```python
@filter.command("天气", alias=["weather", "tq", "查天气"])
async def weather_command(self, event: BaseMessageEvent):
    await event.reply("今天晴朗 ☀️")
```

用户可以使用：`天气`、`weather`、`tq`、`查天气` 任意一个触发

### 命令分组

```python
# 创建命令组
admin_group = filter.command_group("admin")

@admin_group.command("user")
async def admin_user(self, event: BaseMessageEvent):
    await event.reply("用户管理功能")

@admin_group.command("config")
async def admin_config(self, event: BaseMessageEvent):
    await event.reply("配置管理功能")
```

使用方法：
- `admin user` → 用户管理
- `admin config` → 配置管理

## 参数解析

### 支持的参数类型

```python
@filter.command("demo")
async def parameter_demo(self, event: BaseMessageEvent, 
                        text: str,           # 字符串
                        number: int,         # 整数
                        decimal: float,      # 浮点数
                        flag: bool):         # 布尔值
    await event.reply(f"收到: {text}, {number}, {decimal}, {flag}")
```

### 参数类型转换规则

#### 布尔值 (bool) 转换
布尔类型参数有特殊的转换规则：

- **转换为 `False`**: 输入 `"false"` (不区分大小写) 或 `"0"`
- **转换为 `True`**: 其他任何值

```python
@filter.command("开关")
async def toggle_feature(self, event: BaseMessageEvent, enable: bool):
    if enable:
        await event.reply("功能已启用 ✅")
    else:
        await event.reply("功能已禁用 ❌")
```

使用示例：
- `开关 true` → "功能已启用 ✅"
- `开关 1` → "功能已启用 ✅"  
- `开关 yes` → "功能已启用 ✅"
- `开关 false` → "功能已禁用 ❌"
- `开关 0` → "功能已禁用 ❌"

#### 数值类型转换
- **int**: 将字符串转换为整数，转换失败则命令不执行
- **float**: 将字符串转换为浮点数，转换失败则命令不执行
- **str**: 直接使用字符串，无需转换

### MessageSegment 参数

```python
from ncatbot.core.event.message_segment import At, Image, Face

@filter.command("at测试")
async def at_test(self, event: BaseMessageEvent, target: At):
    await event.reply(f"你@了用户 {target.qq}")

@filter.command("图片测试")
async def image_test(self, event: BaseMessageEvent, pic: Image):
    await event.reply(f"收到图片: {pic.file}")

@filter.command("表情测试")
async def face_test(self, event: BaseMessageEvent, emoji: Face):
    await event.reply(f"收到表情: {emoji.id}")
```

### 句子参数

```python
from ncatbot.core.event.message_segment import Sentence

@filter.command("说话")
async def speak(self, event: BaseMessageEvent, content: Sentence):
    """Sentence 会捕获命令后的所有内容（包含空格）"""
    await event.reply(f"你说: {content}")
```

使用：`说话 hello world` → 回复："你说: hello world"

## 自定义过滤器

### 简单过滤器（Lambda）

```python
@filter.custom(lambda event: '关键词' in event.raw_message)
async def keyword_handler(self, event: BaseMessageEvent):
    await event.reply("检测到关键词！")

@filter.custom(lambda event: len(event.raw_message) > 50)
async def long_message_handler(self, event: BaseMessageEvent):
    await event.reply("这是一条很长的消息")
```

### 独立函数过滤器

```python
def contains_url(event: BaseMessageEvent) -> bool:
    """检查消息是否包含URL"""
    import re
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return bool(re.search(url_pattern, event.raw_message))

@filter.custom(contains_url)
async def url_handler(self, event: BaseMessageEvent):
    await event.reply("检测到链接，请注意安全！🔗")
```

### 高级过滤器

```python
def admin_with_keyword(manager, event: BaseMessageEvent) -> bool:
    """管理员且包含特定关键词"""
    is_admin = manager.rbac_manager.user_has_role(event.user_id, "admin")
    has_keyword = 'urgent' in event.raw_message.lower()
    return is_admin and has_keyword

@filter.custom(admin_with_keyword)
async def urgent_admin_handler(self, event: BaseMessageEvent):
    await event.reply("管理员紧急处理模式激活！⚠️")
```

### 时间相关过滤器

```python
def is_weekend(event: BaseMessageEvent) -> bool:
    """检查是否是周末"""
    import datetime
    weekday = datetime.datetime.now().weekday()
    return weekday >= 5  # 5=周六, 6=周日

@filter.custom(is_weekend)
async def weekend_feature(self, event: BaseMessageEvent):
    await event.reply("周末特殊功能启动！🎉")
```

## 事件处理

### 通知事件

```python
@filter.notice_event()
async def handle_notice(self, event: NoticeEvent):
    """处理群成员变动、撤回消息等通知"""
    if event.notice_type == "group_increase":
        # 处理新成员加群
        pass
    elif event.notice_type == "group_recall":
        # 处理消息撤回
        pass
```

### 请求事件

```python
@filter.request_event()
async def handle_request(self, event: RequestEvent):
    """处理好友申请、群邀请等请求"""
    if event.request_type == "friend":
        # 处理好友申请
        pass
    elif event.request_type == "group":
        # 处理群邀请
        pass
```

## 装饰器组合

### 多重权限

```python
@filter.admin_only()
@filter.group_message()
@filter.command("群管理")
async def group_admin_command(self, event: BaseMessageEvent):
    """仅管理员在群聊中可使用"""
    await event.reply("群管理功能")
```

### 权限 + 自定义过滤器

```python
@filter.root_only()
@filter.custom(lambda event: 'system' in event.raw_message)
async def system_command(self, event: BaseMessageEvent):
    """Root用户且消息包含'system'"""
    await event.reply("系统级命令执行")
```

### 复杂组合示例

```python
def business_hours(event: BaseMessageEvent) -> bool:
    """工作时间过滤器"""
    import datetime
    hour = datetime.datetime.now().hour
    return 9 <= hour <= 18

@filter.admin_only()
@filter.private_message()
@filter.custom(business_hours)
@filter.command("工作报告")
async def work_report(self, event: BaseMessageEvent, report_type: str):
    """管理员在私聊中，工作时间内提交工作报告"""
    await event.reply(f"收到 {report_type} 类型的工作报告")
```

## 错误处理

### 参数转换错误

当参数无法转换时（如：`计算 abc 123`），系统会自动跳过该函数，不会触发执行。

### 过滤器异常

自定义过滤器出现异常时，会返回 `False`，确保系统稳定性。

```python
def safe_filter(event: BaseMessageEvent) -> bool:
    try:
        # 可能出错的逻辑
        return some_complex_check(event)
    except Exception:
        # 出错时返回 False，不触发函数
        return False

@filter.custom(safe_filter)
async def safe_handler(self, event: BaseMessageEvent):
    await event.reply("安全检查通过")
```

## 调试技巧

### 查看注册信息

```python
# 在插件加载时查看已注册的命令
async def on_load(self):
    from ncatbot.plugin_system.builtin_plugin.filter_registry import register
    print(f"已注册命令数量: {len(register.registered_commands)}")
```

### 日志输出

```python
from ncatbot.utils import get_log

LOG = get_log(__name__)

@filter.command("debug")
async def debug_command(self, event: BaseMessageEvent):
    LOG.info(f"收到调试命令，用户: {event.user_id}")
    await event.reply("调试信息已记录")
```

这份完整指南涵盖了 FilterRegistry 的所有核心功能。接下来可以查看最佳实践和实战案例。
