# TestPlugin 测试指南

## 概述

本指南展示了如何使用 NcatBot 的 Mock 测试框架来测试插件的完整功能。以 TestPlugin (FilterRegistryTestPlugin) 为例，演示了从简单命令到复杂权限过滤器的全面测试。

## 核心特性

- ✅ **完整系统测试**: 通过真实的消息流程测试插件
- ✅ **自动插件加载**: 使用系统标准的插件加载机制
- ✅ **权限系统集成**: 测试各种权限级别的命令
- ✅ **消息类型过滤**: 测试群聊和私聊环境
- ✅ **参数解析验证**: 测试各种数据类型的参数处理
- ✅ **Mock API 验证**: 验证插件的回复行为

## 快速开始

### 基础用法

```python
#!/usr/bin/env python3
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

def setup_test():
    """一行代码设置完整环境"""
    client = TestClient()
    helper = TestHelper(client)
    client.start(mock_mode=True)  # 🪄 魔法在这里！
    return client, helper

async def test_basic_command():
    """测试基础命令"""
    client, helper = setup_test()
    
    # 发送命令，触发完整流程
    await helper.send_private_message("hello", user_id="test123")
    
    # 验证回复
    helper.assert_reply_sent("✅ 简单命令测试通过")
    
    print("✅ 基础命令测试通过")

# 运行测试
asyncio.run(test_basic_command())
```

### 参数解析测试

```python
async def test_parameters():
    """测试参数解析"""
    client, helper = setup_test()
    
    # 字符串参数
    await helper.send_private_message("echo Hello World", user_id="test123")
    helper.assert_reply_sent("✅ 字符串参数测试: Hello")
    
    # 整数参数
    await helper.send_private_message("add 10 20", user_id="test123")
    helper.assert_reply_sent("✅ 整数参数测试: 10 + 20 = 30")
    
    # 浮点数参数
    await helper.send_private_message("calc 3.14 2.0", user_id="test123")
    helper.assert_reply_sent("✅ 浮点数参数测试: 3.14 × 2.0 = 6.28")
    
    print("✅ 参数解析测试通过")
```

### 权限测试

```python
async def test_permissions():
    """测试权限过滤器"""
    client, helper = setup_test()
    rbac_manager = client.plugin_loader.rbac_manager
    
    # 普通用户无法执行管理员命令
    await helper.send_private_message("test_admin_permission", user_id="normal_user")
    helper.assert_no_reply()  # 应该没有回复
    
    # 设置管理员权限
    rbac_manager.assign_role_to_user("admin_user", "admin")
    
    # 管理员可以执行管理员命令
    await helper.send_private_message("test_admin_permission", user_id="admin_user")
    helper.assert_reply_sent("✅ 管理员权限测试通过")
    
    print("✅ 权限测试通过")
```

### 消息类型测试

```python
async def test_message_types():
    """测试消息类型过滤器"""
    client, helper = setup_test()
    
    # 群聊过滤器
    await helper.send_group_message("群聊测试", group_id="test_group", user_id="test_user")
    helper.assert_reply_sent("✅ 群聊过滤器测试通过")
    
    # 私聊过滤器
    await helper.send_private_message("私聊测试", user_id="test_user")
    helper.assert_reply_sent("✅ 私聊过滤器测试通过")
    
    print("✅ 消息类型测试通过")
```

## 完整测试示例

查看 `test/unitest/test_test_plugin.py` 获取完整的测试示例，包括：

### 测试覆盖范围

1. **环境验证** - 验证插件系统正确加载
2. **基础命令** (7个) - hello, greet, hi, hey, empty, test_help, test_status
3. **参数解析** (6个) - 字符串、整数、浮点数、布尔、混合、多参数
4. **消息类型过滤器** (2个) - 群聊和私聊过滤器
5. **命令分组** (2个) - 基础分组和带参数分组
6. **自定义过滤器** (1个) - 包含 'special' 的自定义过滤器
7. **错误处理** (3个) - 正确转换和错误输入处理
8. **权限过滤器** (2个) - admin 和 root 权限测试

### 运行完整测试

```bash
# 运行完整测试套件
python test/unitest/test_test_plugin.py

# 运行快速测试
python test/unitest/test_test_plugin_simple.py
```

## 测试原理

### 消息处理流程

```
消息注入 → TestClient.inject_event()
    ↓
事件总线 → EventBus.publish()
    ↓
FilterRegistryPlugin → do_command()
    ↓
命令解析 → 匹配命令和参数
    ↓
过滤器检查 → 权限、消息类型等
    ↓
插件方法调用 → TestPlugin.xxx_command()
    ↓
API 调用 → MockAPI 记录和验证
```

### 关键组件

- **TestClient**: 继承 ClientMixin 和 BotClient，提供完整的测试环境
- **start(mock_mode=True)**: 自动加载所有插件，初始化系统
- **FilterRegistryPlugin**: 自动加载，处理 @filter.command 装饰器
- **MockAPI**: 记录 API 调用，提供回复验证
- **RBACManager**: 内置权限系统，支持用户角色管理

## 测试最佳实践

### 1. 环境隔离

```python
def setUp(self):
    self.client = TestClient()
    self.helper = TestHelper(self.client)
    self.client.start(mock_mode=True)

def tearDown(self):
    self.helper.clear_history()
```

### 2. 验证策略

```python
# 验证回复内容
helper.assert_reply_sent("预期回复")

# 验证无回复
helper.assert_no_reply()

# 检查 API 调用
api_calls = helper.get_api_calls()
assert len(api_calls) > 0

# 获取最新回复
latest = helper.get_latest_reply()
```

### 3. 权限设置

```python
# 获取权限管理器
rbac_manager = client.plugin_loader.rbac_manager

# 设置用户角色
rbac_manager.assign_role_to_user("user_id", "admin")
rbac_manager.assign_role_to_user("user_id", "root")
```

### 4. 错误处理

```python
try:
    await helper.send_private_message("invalid_command", user_id="test")
    helper.assert_no_reply()  # 期望无回复
except AssertionError:
    # 处理断言失败
    pass
except Exception as e:
    # 处理其他异常
    LOG.error(f"测试异常: {e}")
```

## 扩展测试

### 自定义插件测试

要测试你自己的插件：

1. 确保插件在 `plugins/` 目录中
2. 插件需要继承 `BasePlugin`
3. 使用 `@filter.command` 等装饰器
4. 复制测试模板，修改命令和期望回复

### 复杂消息测试

```python
from ncatbot.core.event.message_segment import At, MessageArray, Text

# 创建包含 At 的复杂消息
at_segment = At(qq="123456")
message_array = MessageArray([Text("at "), at_segment])
event = EventFactory.create_group_message(message_array, group_id="test")
await client.inject_event(event)
```

## 故障排除

### 常见问题

1. **插件未加载**: 检查插件是否在 `plugins/` 目录中，是否有 `__all__` 导出
2. **命令不响应**: 检查 `@filter.command` 装饰器是否正确
3. **权限测试失败**: 确认 rbac_manager 角色设置正确
4. **参数解析失败**: 检查函数签名和参数类型注解

### 调试技巧

```python
# 查看已加载插件
plugins = client.plugin_loader.plugins
print(f"已加载插件: {list(plugins.keys())}")

# 查看 API 调用历史
api_calls = helper.get_api_calls()
print(f"API 调用: {api_calls}")

# 查看事件历史
history = client.get_event_history()
print(f"事件历史: {len(history)} 个事件")
```

## 总结

NcatBot 的 Mock 测试框架提供了完整的插件测试能力，通过真实的消息流程验证插件功能。使用 `TestClient.start(mock_mode=True)` 可以一键启动完整的测试环境，无需手动配置复杂的依赖关系。

这种测试方式确保了插件在真实环境中的正确行为，是插件开发过程中不可或缺的验证工具。
