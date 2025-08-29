# NcatBot 测试模块使用指南

## 概述

NcatBot 提供了一个完整的测试工具包，位于 `ncatbot/utils/testing/` 目录下，用于帮助开发者测试插件和机器人功能。该测试模块包含四个核心组件：

- **EventFactory**: 事件工厂，用于创建标准化的测试事件
- **ClientMixin**: 客户端混入类，为 BotClient 添加测试功能
- **TestHelper**: 测试助手类，提供高级测试工具
- **MockAPIAdapter**: 模拟 API 适配器，用于测试 API 调用

## 核心组件详解

### 1. EventFactory - 事件工厂

`EventFactory` 用于创建各种类型的标准化测试事件。

#### 主要方法

```python
from ncatbot.utils.testing import EventFactory

# 创建群聊消息事件
group_event = EventFactory.create_group_message(
    message="测试消息",
    group_id="123456789",
    user_id="987654321",
    nickname="测试用户",
    card="群昵称",
    role="member"  # member, admin, owner
)

# 创建私聊消息事件
private_event = EventFactory.create_private_message(
    message="私聊测试",
    user_id="987654321",
    nickname="测试用户",
    sub_type="friend"  # friend, group, other
)

# 创建通知事件
notice_event = EventFactory.create_notice_event(
    notice_type="group_increase",
    user_id="987654321",
    group_id="123456789",
    sub_type="approve"
)

# 创建请求事件
request_event = EventFactory.create_request_event(
    request_type="friend",
    user_id="987654321",
    flag="test_flag",
    sub_type="add"
)
```

#### 支持复杂消息

```python
from ncatbot.core.event.message_segment import MessageArray, Text

# 使用 MessageArray 创建复杂消息
message_array = MessageArray(Text("复杂消息内容"))
event = EventFactory.create_group_message(
    message=message_array,
    group_id="123456789"
)
```

### 2. ClientMixin - 客户端混入类

`ClientMixin` 为 BotClient 添加了测试功能，包括事件注入和历史记录。

#### 基础用法

```python
from ncatbot.core.client import BotClient
from ncatbot.utils.testing import ClientMixin
from ncatbot.plugin_system.event import EventBus

class TestBotClient(ClientMixin, BotClient):
    def __init__(self, *args, **kwargs):
        self.event_bus = EventBus()
        super().__init__(*args, **kwargs)

# 创建测试客户端
client = TestBotClient(only_private=True)

# 启用 Mock 模式
client.enable_mock_mode()

# 注入事件进行测试
import asyncio

async def test_event_injection():
    event = EventFactory.create_private_message("测试消息")
    await client.inject_event(event)
    
    # 检查事件历史
    history = client.get_event_history()
    print(f"处理了 {len(history)} 个事件")

# 运行测试
asyncio.run(test_event_injection())
```

#### 主要方法

- `enable_mock_mode()`: 启用 Mock 模式
- `disable_mock_mode()`: 禁用 Mock 模式
- `inject_event(event)`: 注入事件到客户端
- `get_event_history()`: 获取事件历史记录
- `clear_event_history()`: 清空事件历史记录

### 3. TestHelper - 测试助手类

`TestHelper` 提供了高级的测试工具和断言方法。

#### 基础用法

```python
from ncatbot.utils.testing import TestHelper

# 创建测试助手
helper = TestHelper(client)

async def test_plugin_response():
    # 发送群聊消息并处理
    await helper.send_group_message(
        message="测试命令",
        group_id="123456789",
        user_id="987654321"
    )
    
    # 断言发送了回复
    helper.assert_reply_sent("预期回复内容")
    
    # 获取最新回复
    latest_reply = helper.get_latest_reply()
    print(f"最新回复: {latest_reply}")
```

#### 主要方法

```python
# 发送消息测试
await helper.send_group_message(message, group_id, user_id, **kwargs)
await helper.send_private_message(message, user_id, **kwargs)

# 断言方法
helper.assert_reply_sent(expected_text=None)  # 断言发送了回复
helper.assert_no_reply()  # 断言没有发送回复

# 历史记录
helper.get_api_calls()  # 获取所有 API 调用
helper.get_latest_reply()  # 获取最新回复
helper.clear_history()  # 清空历史记录

# API 响应配置
helper.set_api_response("/endpoint", response_data)
```

### 4. MockAPIAdapter - 模拟 API 适配器

`MockAPIAdapter` 用于模拟 API 调用，提供可配置的响应并记录调用历史。

#### 基础用法

```python
from ncatbot.utils.testing import MockAPIAdapter

mock_api = MockAPIAdapter()

# 设置自定义响应
mock_api.set_response("/send_group_msg", {
    "retcode": 0,
    "data": {"message_id": "12345"}
})

# 模拟 API 调用
async def test_api_call():
    response = await mock_api.mock_callback("/send_group_msg", {
        "group_id": "123456789",
        "message": "测试消息"
    })
    print(f"API 响应: {response}")
    # 调用信息会通过 LOG.info 输出
    # LOG: API 调用: /send_group_msg
    # LOG: 调用参数: {'group_id': '123456789', 'message': '测试消息'}

# 检查调用历史
history = mock_api.get_call_history()
group_calls = mock_api.get_calls_for_endpoint("/send_group_msg")
call_count = mock_api.get_call_count("/send_group_msg")

# 断言调用
mock_api.assert_called_with("/send_group_msg", {"group_id": "123456789"})
```

## 完整测试示例

### 插件测试示例

```python
import asyncio
import unittest
from ncatbot.core.client import BotClient
from ncatbot.utils.testing import EventFactory, ClientMixin, TestHelper
from ncatbot.plugin_system.event import EventBus

class TestBotClient(ClientMixin, BotClient):
    def __init__(self, *args, **kwargs):
        self.event_bus = EventBus()
        super().__init__(*args, **kwargs)

class PluginTest(unittest.TestCase):
    def setUp(self):
        self.client = TestBotClient(only_private=True)
        self.client.enable_mock_mode()
        self.helper = TestHelper(self.client)
        
        # 注册你的插件处理器
        # self.client.add_private_message_handler(your_plugin_handler)
    
    def tearDown(self):
        self.helper.clear_history()
    
    def test_plugin_command(self):
        """测试插件命令响应"""
        async def run_test():
            # 发送命令
            await self.helper.send_private_message("!help", user_id="123456")
            
            # 验证响应
            self.helper.assert_reply_sent("帮助信息")
            
            # 检查 API 调用
            calls = self.helper.get_api_calls()
            self.assertTrue(len(calls) > 0)
        
        asyncio.run(run_test())
    
    def test_no_response_to_invalid_command(self):
        """测试无效命令不响应"""
        async def run_test():
            await self.helper.send_private_message("无效命令", user_id="123456")
            self.helper.assert_no_reply()
        
        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
```

### 群聊插件测试示例

```python
class GroupPluginTest(unittest.TestCase):
    def setUp(self):
        self.client = TestBotClient()
        self.client.enable_mock_mode()
        self.helper = TestHelper(self.client)
    
    def test_group_command_with_permission(self):
        """测试需要权限的群聊命令"""
        async def run_test():
            # 测试管理员权限
            await self.helper.send_group_message(
                message="!kick @某人",
                group_id="123456789",
                user_id="admin_user",
                role="admin"
            )
            
            self.helper.assert_reply_sent("已执行踢人操作")
            
            # 测试普通成员无权限
            await self.helper.send_group_message(
                message="!kick @某人",
                group_id="123456789",
                user_id="normal_user",
                role="member"
            )
            
            self.helper.assert_reply_sent("权限不足")
        
        asyncio.run(run_test())
```

## 高级功能

### 自定义 API 响应

```python
# 模拟 API 失败
helper.set_api_response("/send_group_msg", {"retcode": -1, "msg": "发送失败"})

# 使用函数生成动态响应
def dynamic_response(endpoint, data):
    return {
        "retcode": 0,
        "data": {"message_id": f"msg_{data.get('group_id', 'unknown')}"}
    }

helper.mock_api.set_response("/send_group_msg", dynamic_response)

# API 调用监控
async def test_api_monitoring():
    await helper.send_group_message("测试消息", group_id="123456789")
    
    # 检查 API 调用历史
    api_calls = helper.get_api_calls()
    print(f"共调用了 {len(api_calls)} 次 API")
    
    # 检查特定端点调用
    group_msg_calls = helper.mock_api.get_calls_for_endpoint("/send_group_msg")
    for call in group_msg_calls:
        print(f"群消息调用参数: {call}")
```

### 复杂事件测试

```python
# 测试消息撤回
async def test_message_recall():
    # 先发送消息
    await helper.send_group_message("要被撤回的消息", group_id="123456789")
    
    # 创建撤回事件
    recall_event = EventFactory.create_notice_event(
        notice_type="group_recall",
        group_id="123456789",
        user_id="987654321",
        message_id="12345"
    )
    
    await client.inject_event(recall_event)
    
    # 验证插件对撤回的处理
    helper.assert_reply_sent("检测到消息撤回")
```

## 测试最佳实践

### 1. 测试隔离

每个测试用例都应该是独立的：

```python
def setUp(self):
    self.client = TestBotClient()
    self.client.enable_mock_mode()
    self.helper = TestHelper(self.client)

def tearDown(self):
    self.helper.clear_history()
```

### 2. 异步测试处理

```python
def test_async_function(self):
    async def run_test():
        # 你的异步测试代码
        pass
    
    asyncio.run(run_test())
```

### 3. 模拟真实场景

```python
# 模拟用户加群
join_event = EventFactory.create_notice_event(
    notice_type="group_increase",
    group_id="123456789",
    user_id="new_user",
    sub_type="approve"
)

await client.inject_event(join_event)
```

### 4. 权限测试

```python
# 测试不同权限级别
test_cases = [
    ("owner", "群主", True),
    ("admin", "管理员", True),
    ("member", "普通成员", False)
]

for role, desc, should_succeed in test_cases:
    with self.subTest(role=role):
        await helper.send_group_message(
            "!sensitive_command",
            role=role
        )
        
        if should_succeed:
            helper.assert_reply_sent("操作成功")
        else:
            helper.assert_reply_sent("权限不足")
```

## 运行测试

将测试文件放在 `test/unitest/` 目录下，然后运行：

```bash
# 运行单个测试文件
python test/unitest/your_test.py

# 使用 unittest 模块运行
python -m unittest test.unitest.your_test

# 运行所有测试
python -m unittest discover test/unitest/
```

## 故障排除

### 常见问题

1. **ImportError**: 确保项目根目录在 Python 路径中
2. **事件不被处理**: 检查是否启用了 Mock 模式
3. **API 调用失败**: 确认 TestHelper 正确替换了 API 回调
4. **异步问题**: 确保所有异步操作都在事件循环中运行

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查事件历史
print("事件历史:", client.get_event_history())

# 检查 API 调用
print("API 调用:", helper.get_api_calls())
```

## 扩展测试模块

如果需要扩展测试功能，可以：

1. **继承现有类**:
```python
class CustomTestHelper(TestHelper):
    def assert_image_sent(self):
        # 自定义断言逻辑
        pass
```

2. **添加新的事件类型**:
```python
class CustomEventFactory(EventFactory):
    @staticmethod
    def create_custom_event(**kwargs):
        # 创建自定义事件
        pass
```

3. **扩展 MockAPI**:
```python
class ExtendedMockAPI(MockAPIAdapter):
    def simulate_network_delay(self, delay_ms):
        # 模拟网络延迟
        pass
```

通过这个测试模块，您可以全面测试 NcatBot 插件的各种功能，确保代码质量和稳定性。
