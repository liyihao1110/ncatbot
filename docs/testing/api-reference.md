# NcatBot 测试框架 API 参考

本文档提供 `ncatbot.utils.testing` 模块中所有测试相关类和方法的详细参考。

## TestClient

测试专用客户端，继承自 `BotClient` 和 `ClientMixin`。

### 类定义

```python
class TestClient(ClientMixin, BotClient):
    def __init__(self, load_plugin: bool = False, *args, **kwargs)
```

### 构造函数参数

- `load_plugin` (bool, 可选): 是否自动加载插件，默认为 `False`
- `*args, **kwargs`: 传递给父类的其他参数

### 方法

#### `start(mock_mode: bool = True)`

启动测试客户端。

**参数:**
- `mock_mode` (bool): 是否使用 Mock 模式，默认为 `True`

**示例:**
```python
client = TestClient()
client.start()
```

#### `register_plugin(plugin_class: Type[BasePlugin])`

注册插件到测试客户端。

**参数:**
- `plugin_class` (Type[BasePlugin]): 插件类（不是实例）

**示例:**
```python
from my_plugin import MyPlugin
client.register_plugin(MyPlugin)
```

#### `get_registered_plugins() -> List[BasePlugin]`

获取所有已注册的插件实例列表。

**返回:**
- List[BasePlugin]: 插件实例列表

**示例:**
```python
plugins = client.get_registered_plugins()
for plugin in plugins:
    print(f"插件: {plugin.name} v{plugin.version}")
```

#### `get_plugin(type: Type[T]) -> T`

获取已注册的插件实例。

**参数:**
- `type` (Type[T]): 插件类型

**返回:**
- T: 插件实例（有类型注解）

**示例:**
```python
plugin = client.get_plugin(CalculatorPlugin)
```

#### `unregister_plugin(plugin: BasePlugin)`

从测试客户端卸载插件。（**通过装饰器等注册的命令无法被卸载**）

**参数:**
- `plugin` (BasePlugin): 要卸载的插件实例

**示例:**
```python
plugin = client.get_registered_plugins()[0]
client.unregister_plugin(plugin)
```

## TestHelper

测试辅助类，提供便捷的测试操作方法。

### 类定义

```python
class TestHelper:
    def __init__(self, client_with_mixin)
```

### 构造函数参数

- `client_with_mixin`: 带有 ClientMixin 的客户端实例（通常是 TestClient）

### 方法

#### `async send_private_message(...)`

发送私聊消息事件。

**参数:**
- `message` (str): 消息内容
- `user_id` (str, 可选): 发送者 ID，默认 "987654321"
- `nickname` (str, 可选): 发送者昵称，默认 "TestUser"
- `**kwargs`: 其他事件参数

**示例:**
```python
await helper.send_private_message(
    "/hello",
    user_id="123456",
    nickname="测试用户"
)
```

#### `async send_group_message(...)`

发送群聊消息事件。

**参数:**
- `message` (str): 消息内容
- `group_id` (str, 可选): 群组 ID，默认 "123456789"
- `user_id` (str, 可选): 发送者 ID，默认 "987654321"
- `nickname` (str, 可选): 发送者昵称，默认 "TestUser"
- `**kwargs`: 其他事件参数

**示例:**
```python
await helper.send_group_message(
    "大家好",
    group_id="888888",
    user_id="123456",
    nickname="测试用户",
    role="member"
)
```

#### `get_latest_reply(index: int = -1) -> Optional[Dict]`

获取最新的回复消息。

**参数:**
- `index` (int, 可选): 回复索引，默认 -1（最新的）

**返回:**
- Optional[Dict]: 回复数据字典，如果没有回复则返回 None

**示例:**
```python
# 获取最新回复
latest = helper.get_latest_reply()

# 获取倒数第二个回复
second_last = helper.get_latest_reply(-2)
```

#### `assert_reply_sent(expected_text: Optional[str] = None)`

断言发送了回复（可选：包含特定文本）。

**参数:**
- `expected_text` (str, 可选): 期望包含的文本

**抛出:**
- AssertionError: 如果没有回复或文本不匹配

**示例:**
```python
helper.assert_reply_sent("操作成功")
```

#### `assert_no_reply()`

断言没有发送任何回复。

**抛出:**
- AssertionError: 如果有回复

**示例:**
```python
helper.assert_no_reply()
```

#### `get_api_calls() -> List[Tuple[str, Dict]]`

获取所有 API 调用记录。

**返回:**
- List[Tuple[str, Dict]]: (endpoint, data) 元组列表

**示例:**
```python
calls = helper.get_api_calls()
for endpoint, data in calls:
    print(f"API: {endpoint}")
```

#### `clear_history()`

清空所有历史记录（事件和 API 调用）。

**示例:**
```python
helper.clear_history()
```

#### `set_api_response(endpoint: str, response: Dict)`

设置特定 API 端点的响应。

**参数:**
- `endpoint` (str): API 端点路径
- `response` (Dict): 响应数据

**示例:**
```python
helper.set_api_response("/get_user_info", {
    "retcode": 0,
    "data": {
        "user_id": "123456",
        "nickname": "测试用户",
        "level": 10
    }
})
```

## EventFactory

事件工厂类，用于创建标准化的测试事件。

### 静态方法

#### `create_group_message(...) -> GroupMessageEvent`

创建群聊消息事件。

**参数:**
- `message` (Union[str, MessageArray]): 消息内容
- `group_id` (str, 可选): 群组 ID，默认 "123456789"
- `user_id` (str, 可选): 发送者 ID，默认 "987654321"
- `nickname` (str, 可选): 发送者昵称，默认 "TestUser"
- `card` (str, 可选): 群名片
- `role` (str, 可选): 群角色 ("member", "admin", "owner")，默认 "member"
- `self_id` (str, 可选): 机器人 ID，默认 "123456789"
- `message_id` (str, 可选): 消息 ID，自动生成
- `**kwargs`: 其他事件数据

**返回:**
- GroupMessageEvent: 群消息事件实例

**示例:**
```python
# 纯文本消息
event = EventFactory.create_group_message("Hello")

# 复杂消息
from ncatbot.core.event.message_segment import MessageArray, Text, At
msg = MessageArray(Text("你好 "), At("123456"))
event = EventFactory.create_group_message(msg, role="admin")
```

#### `create_private_message(...) -> PrivateMessageEvent`

创建私聊消息事件。

**参数:**
- `message` (Union[str, MessageArray]): 消息内容
- `user_id` (str, 可选): 发送者 ID，默认 "987654321"
- `nickname` (str, 可选): 发送者昵称，默认 "TestUser"
- `self_id` (str, 可选): 机器人 ID，默认 "123456789"
- `message_id` (str, 可选): 消息 ID，自动生成
- `sub_type` (str, 可选): 子类型 ("friend", "group", "other")，默认 "friend"
- `**kwargs`: 其他事件数据

**返回:**
- PrivateMessageEvent: 私聊消息事件实例

#### `create_notice_event(...) -> NoticeEvent`

创建通知事件。

**参数:**
- `notice_type` (str): 通知类型
- `user_id` (str, 可选): 用户 ID，默认 "987654321"
- `group_id` (str, 可选): 群组 ID
- `self_id` (str, 可选): 机器人 ID，默认 "123456789"
- `sub_type` (str, 可选): 子类型
- `**kwargs`: 其他事件数据

**返回:**
- NoticeEvent: 通知事件实例

**示例:**
```python
# 群成员增加通知
event = EventFactory.create_notice_event(
    notice_type="group_increase",
    user_id="123456",
    group_id="789012",
    sub_type="approve"
)
```

#### `create_request_event(...) -> RequestEvent`

创建请求事件。

**参数:**
- `request_type` (str): 请求类型
- `user_id` (str, 可选): 用户 ID，默认 "987654321"
- `flag` (str, 可选): 请求标志，默认 "test_flag"
- `self_id` (str, 可选): 机器人 ID，默认 "123456789"
- `sub_type` (str, 可选): 子类型
- `**kwargs`: 其他事件数据

**返回:**
- RequestEvent: 请求事件实例

## MockAPIAdapter

模拟 API 适配器，用于拦截和模拟 API 调用。

### 类定义

```python
class MockAPIAdapter:
    def __init__(self)
```

### 方法

#### `async mock_callback(endpoint: str, data: Dict) -> Dict`

模拟 API 回调（内部使用）。

#### `set_response(endpoint: str, response: Union[Dict, Callable])`

设置特定端点的响应。

**参数:**
- `endpoint` (str): API 端点
- `response` (Union[Dict, Callable]): 响应数据或生成响应的函数

**示例:**
```python
# 静态响应
mock_api.set_response("/get_status", {
    "retcode": 0,
    "data": {"status": "online"}
})

# 动态响应
def dynamic_response(endpoint, data):
    user_id = data.get("user_id")
    return {
        "retcode": 0,
        "data": {"vip": user_id == "123456"}
    }

mock_api.set_response("/check_vip", dynamic_response)
```

#### `get_call_history() -> List[Tuple[str, Dict]]`

获取所有调用历史。

**返回:**
- List[Tuple[str, Dict]]: (endpoint, data) 元组列表

#### `get_calls_for_endpoint(endpoint: str) -> List[Dict]`

获取特定端点的调用记录。

**参数:**
- `endpoint` (str): API 端点

**返回:**
- List[Dict]: 调用数据列表

#### `clear_call_history()`

清空调用历史。

#### `assert_called_with(endpoint: str, expected_data: Dict)`

断言特定端点被调用且数据匹配。

**参数:**
- `endpoint` (str): API 端点
- `expected_data` (Dict): 期望的调用数据

**抛出:**
- AssertionError: 如果端点未被调用或数据不匹配

#### `get_call_count(endpoint: str) -> int`

获取特定端点的调用次数。

**参数:**
- `endpoint` (str): API 端点

**返回:**
- int: 调用次数

## ClientMixin

为 BotClient 添加测试功能的混入类。

### 方法

#### `enable_mock_mode()`

启用 Mock 模式。

#### `disable_mock_mode()`

禁用 Mock 模式。

#### `mock_start()`

Mock 模式下的启动方法（跳过真实连接）。

#### `async inject_event(event: BaseEventData)`

注入事件到事件处理系统。

**参数:**
- `event` (BaseEventData): 要注入的事件

**示例:**
```python
event = EventFactory.create_private_message("测试消息")
await client.inject_event(event)
```

#### `clear_event_history()`

清空事件历史记录。

## 常用模式示例

### 完整测试流程

```python
from ncatbot.utils.testing import TestClient, TestHelper, EventFactory
from my_plugin import MyPlugin
import asyncio

async def complete_test_example():
    # 1. 初始化
    client = TestClient()
    helper = TestHelper(client)
    
    # 2. 启动客户端
    client.start()
    
    # 3. 注册插件
    client.register_plugin(MyPlugin)
    
    # 4. 设置 Mock 响应
    helper.set_api_response("/get_user_info", {
        "retcode": 0,
        "data": {"nickname": "测试用户", "level": 10}
    })
    
    # 5. 发送测试消息
    await helper.send_private_message("/info")
    
    # 6. 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None
    
    # 7. 检查 API 调用
    api_calls = helper.mock_api.get_calls_for_endpoint("/get_user_info")
    assert len(api_calls) == 1
    
    # 8. 清理
    helper.clear_history()
    
    print("✅ 测试完成")

asyncio.run(complete_test_example())
```

### 提取消息文本的辅助函数

```python
def extract_text(message_segments):
    """从消息段列表中提取纯文本"""
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text

# 使用示例
reply = helper.get_latest_reply()
if reply:
    text = extract_text(reply["message"])
    print(f"回复文本: {text}")
```
