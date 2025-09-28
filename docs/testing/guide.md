# NcatBot 测试框架完整指南

## 概述

NcatBot 提供了一套完整的测试框架，位于 `ncatbot.utils.testing` 模块中。该框架允许您在不启动真实 QQ 客户端的情况下测试插件功能。

## 核心组件

### 1. TestClient - 测试客户端

`TestClient` 是专门为测试设计的客户端，继承自 `BotClient` 并添加了测试功能。

**⚠️ 注意：一次运行只允许启动一次 TestClient，插件加载也必须在最开始进行，测试过程中禁止重新启动 TestClient 或操作插件**

```python
from ncatbot.utils.testing import TestClient

# 创建测试客户端
client = TestClient(load_plugin=False)  # 默认不加载任何插件

# 启动客户端（Mock 模式默认开启）
client.start()

# 注册需要测试的插件
from my_plugin import MyPlugin
client.register_plugin(MyPlugin)

# 获取已注册的插件
plugins = client.get_registered_plugins()

# 卸载插件
plugin_instance = plugins[0]
client.unregister_plugin(plugin_instance)
```

#### 主要特性：

- 自动启用 Mock 模式，跳过 WebSocket 连接
- 支持按需加载插件
- 提供插件管理功能

#### 错误示例

```python
from ncatbot.utils.testing import TestClient
from my_plugin import MyPlugin

def test_1():
    client = TestClient()
    client.start()
    client.register_plugin(MyPlugin)
    # Do something 1

def test_2():
    client = TestClient()
    client.start()
    client.register_plugin(MyPlugin)
    # Do something 2

if __name__ == "__main__":
    test_1()
    test_2()
```

一次运行中，进行了两次 TestClient 的启动，两次注册了插件，违反了 TestClient 的单例原则。

### 2. TestHelper - 测试辅助类

`TestHelper` 简化了测试中的常见操作。

```python
from ncatbot.utils.testing import TestHelper

# 创建辅助类实例
helper = TestHelper(client)

# 发送消息
await helper.send_private_message("你好", user_id="123456")
await helper.send_group_message("大家好", group_id="789012", user_id="123456")

# 获取回复
latest_reply = helper.get_latest_reply()  # 获取最新回复
second_reply = helper.get_latest_reply(-2)  # 获取倒数第二个回复

# 断言方法
helper.assert_reply_sent("期望的文本")  # 断言发送了包含指定文本的回复
helper.assert_no_reply()  # 断言没有发送任何回复

# 清理历史记录
helper.clear_history()

# 设置 API 响应
helper.set_api_response("/get_group_info", {
    "retcode": 0,
    "data": {
        "group_id": "789012",
        "group_name": "测试群",
        "member_count": 100
    }
})
```

### 3. EventFactory - 事件工厂

`EventFactory` 用于创建标准化的测试事件。

```python
from ncatbot.utils.testing import EventFactory
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image

# 创建纯文本消息事件
event = EventFactory.create_group_message(
    message="Hello World",
    group_id="123456789",
    user_id="987654321",
    nickname="TestUser",
    role="member"  # member, admin, owner
)

# 创建复杂消息事件
msg_array = MessageArray(
    Text("你好 "),
    At("123456"),
    Text(" 这是一张图片："),
    Image("http://example.com/image.jpg")
)
event = EventFactory.create_group_message(message=msg_array)

# 创建私聊消息事件
event = EventFactory.create_private_message(
    message="私聊消息",
    user_id="123456",
    sub_type="friend"  # friend, group, other
)

# 创建通知事件
event = EventFactory.create_notice_event(
    notice_type="group_increase",
    user_id="123456",
    group_id="789012",
    sub_type="approve"
)

# 创建请求事件
event = EventFactory.create_request_event(
    request_type="friend",
    user_id="123456",
    flag="unique_flag",
    comment="请加我为好友"
)
```

### 4. MockAPIAdapter - API 模拟器

`MockAPIAdapter` 拦截并模拟 API 调用。

```python
# 通过 helper 访问 mock_api
mock_api = helper.mock_api

# 获取 API 调用历史
all_calls = mock_api.get_call_history()
group_msg_calls = mock_api.get_calls_for_endpoint("/send_group_msg")

# 断言 API 调用
mock_api.assert_called_with("/send_private_msg", {
    "user_id": "123456",
    "message": [{"type": "text", "data": {"text": "Hello"}}]
})

# 获取调用次数
count = mock_api.get_call_count("/send_group_msg")

# 设置自定义响应
mock_api.set_response("/custom_api", {
    "retcode": 0,
    "data": {"custom": "response"}
})

# 设置动态响应
def dynamic_response(endpoint, data):
    if data.get("user_id") == "123456":
        return {"retcode": 0, "data": {"vip": True}}
    return {"retcode": 0, "data": {"vip": False}}

mock_api.set_response("/get_user_info", dynamic_response)
```

## 高级用法

### 1. 测试事件处理器

```python
async def test_event_handlers():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    # 注册自定义事件处理器
    handled_events = []
    
    @client.on_group_message()
    async def handle_group_msg(event):
        handled_events.append(event)
        # 提取纯文本
        text = ''.join(seg.text for seg in event.message.filter_text())
        if "ping" in text:
            await event.reply("pong")
    
    # 发送测试消息
    await helper.send_group_message("ping")
    
    # 验证处理器被调用
    assert len(handled_events) == 1
    assert handled_events[0].message.filter_text()[0].text == "ping"
    
    # 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None
    assert "pong" in str(reply["message"])
```

### 2. 测试权限系统

```python
from ncatbot.plugin_system import admin_filter

async def test_permissions():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    # 创建需要权限的插件
    class AdminPlugin(BasePlugin):
        name = "AdminPlugin"
        version = "1.0.0"
        
        async def on_load(self):
            pass

        @admin_filter
        async def admin_cmd(self, event: BaseMessageEvent):
            await event.reply("管理员命令执行成功")
    
    client.register_plugin(AdminPlugin)
    
    # 普通用户测试
    await helper.send_private_message("admin_cmd", user_id="normal_user")
    helper.assert_no_reply()  # 应该没有回复
    
    # 设置管理员权限
    rbac = client.plugin_loader.rbac_manager
    rbac.assign_role_to_user("admin_user", "admin")
    
    # 管理员测试
    helper.clear_history()
    await helper.send_private_message("admin_cmd", user_id="admin_user")
    helper.assert_reply_sent("管理员命令执行成功")
```

### 3. 测试插件间交互

```python
async def test_plugin_interaction():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    # 插件 A：提供服务
    class PluginA(NcatBotPlugin):
        name = "PluginA"
        version = "1.0.0"
        
        async def on_load(self):
            self.data = {"key": "value"}
            
        def get_data(self):
            return self.data
    
    # 插件 B：使用服务
    class PluginB(NcatBotPlugin):
        name = "PluginB"
        version = "1.0.0"
        dependencies = {"PluginA": ">=1.0.0"}
        
        async def on_load(self):
            pass

        @self.on_command("get_data")
        async def get_data_cmd(event):
            plugin_a = self.get_plugin("PluginA")
            if plugin_a:
                data = plugin_a.get_data()
                return f"获取到数据：{data}"
            return "PluginA 未找到"
    
    # 注册插件
    client.register_plugin(PluginA)
    client.register_plugin(PluginB)
    
    # 测试交互
    await helper.send_private_message("/get_data")
    helper.assert_reply_sent("获取到数据：{'key': 'value'}")
```

## 最佳实践

1. **隔离测试**: 每个测试应该独立运行，使用 `helper.clear_history()` 清理状态
2. **Mock 外部依赖**: 使用 `MockAPIAdapter` 模拟外部 API 调用
3. **异步测试**: 确保正确处理异步操作
4. **资源清理**: 测试结束后清理注册的插件和事件处理器
5. **有意义的断言**: 不仅检查是否有回复，还要验证回复内容

## 调试技巧

1. **查看日志输出**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查 API 调用**
```python
# 打印所有 API 调用
for endpoint, data in helper.get_api_calls():
    print(f"API: {endpoint}")
    print(f"Data: {data}")
```

3. **调试事件内容**
```python
# 使用 client 的事件历史
for event_type, event_data in client.event_history:
    print(f"Event: {event_type}")
    print(f"Data: {event_data}")
```

## 下一步

- 查看[标准化测试最佳实践](./best-practice-unittest.md)了解如何使用 unittest 框架
- 查看[简单函数式测试最佳实践](./best-practice-simple.md)了解快速测试方法
- 查看[API 参考文档](./api-reference.md)了解所有可用的测试 API
