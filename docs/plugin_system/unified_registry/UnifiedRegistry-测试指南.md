# UnifiedRegistry 测试指南

## 🚀 快速开始

### 基础测试模板

```python
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

async def test_plugin():
    # 1. 创建测试环境
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    # 2. 注册插件
    client.register_plugin(YourPlugin)
    
    # 3. 发送测试命令
    await helper.send_private_message("/hello")
    
    # 4. 验证结果
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"
    
    text = extract_text(reply["message"])
    assert "你好" in text, "回复应包含问候语"
    
    print("✅ 测试通过")

def extract_text(message_segments):
    """提取消息文本"""
    return "".join(seg.get("data", {}).get("text", "") 
                   for seg in message_segments 
                   if seg.get("type") == "text")

if __name__ == "__main__":
    asyncio.run(test_plugin())
```

## 📋 核心测试场景

### 1. 命令功能测试

```python
# 测试插件示例
class TestPlugin(NcatBotPlugin):
    name = "TestPlugin"
    version = "1.0.0"
    
    async def on_load(self):
        pass

    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply("你好！")
    
    @command_registry.command("echo")
    async def echo_cmd(self, event: BaseMessageEvent, text: str):
        await event.reply(f"回声: {text}")
    
    @command_registry.command("calc")
    async def calc_cmd(self, event: BaseMessageEvent, a: int, b: int, op: str = "add"):
        if op == "add":
            await event.reply(f"结果: {a + b}")
        else:
            await event.reply(f"不支持的操作: {op}")

async def test_commands():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    # 测试基础命令
    await helper.send_private_message("/hello")
    assert_reply_contains(helper, "你好")
    
    # 测试带参数命令
    await helper.send_private_message("/echo 测试文本")
    assert_reply_contains(helper, "测试文本")
    
    # 测试复杂参数
    await helper.send_private_message("/calc 5 3")
    assert_reply_contains(helper, "8")
    
    print("✅ 命令测试通过")

def assert_reply_contains(helper, expected_text):
    """断言回复包含指定文本"""
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"
    text = extract_text(reply["message"])
    assert expected_text in text, f"期望包含: '{expected_text}', 实际: '{text}'"
    helper.clear_history()
```

### 2. 过滤器测试

```python
from ncatbot.plugin_system import group_filter, admin_filter

class FilterTestPlugin(NcatBotPlugin):
    name = "FilterTestPlugin"
    version = "1.0.0"
    
    async def on_load(self):
        @group_filter
        @command_registry.command("group_cmd")
        async def group_cmd(self, event: BaseMessageEvent):
            await event.reply("这是群聊命令")
        
        @admin_filter
        @command_registry.command("admin_cmd")
        async def admin_cmd(self, event: BaseMessageEvent):
            await event.reply("管理员命令")

async def test_filters():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(FilterTestPlugin)
    
    # 测试群聊过滤器 - 私聊中应该被拒绝
    await helper.send_private_message("/group_cmd")
    reply = helper.get_latest_reply()
    assert reply is None, "群聊命令在私聊中应该被过滤"
    
    # 测试群聊过滤器 - 群聊中应该通过
    await helper.send_group_message("/group_cmd", group_id="test_group")
    reply = helper.get_latest_reply()
    assert reply is not None, "群聊命令在群聊中应该有回复"
    
    print("✅ 过滤器测试通过")
```

### 3. 错误处理测试

```python
async def test_error_handling():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    # 测试参数不足
    await helper.send_private_message("/calc 5")  # 缺少参数
    reply = helper.get_latest_reply()
    assert reply is not None, "应该返回错误提示"
    text = extract_text(reply["message"])
    assert "错误" in text or "参数" in text, "应该包含错误信息"
    
    # 测试类型错误
    await helper.send_private_message("/calc abc def")  # 类型错误
    reply = helper.get_latest_reply()
    assert reply is not None, "应该返回类型错误提示"
    
    print("✅ 错误处理测试通过")
```

## 🔧 实用工具函数

```python
# 通用测试辅助函数
async def test_command_with_assertion(helper, command, expected_response):
    """通用命令测试"""
    await helper.send_private_message(command)
    assert_reply_contains(helper, expected_response)

def assert_no_reply(helper):
    """断言没有回复"""
    reply = helper.get_latest_reply()
    assert reply is None, "不应该有回复"

async def test_multiple_commands(helper, test_cases):
    """批量测试命令"""
    for command, expected in test_cases:
        await test_command_with_assertion(helper, command, expected)
    print(f"✅ 批量测试通过 ({len(test_cases)} 个用例)")

# 使用示例
async def batch_test():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    test_cases = [
        ("/hello", "你好"),
        ("/echo 测试", "测试"),
        ("/calc 2 3", "5"),
    ]
    
    await test_multiple_commands(helper, test_cases)
```

## 📊 测试组织

### 完整测试套件

```python
class PluginTestSuite:
    def __init__(self, plugin_class):
        self.plugin_class = plugin_class
        self.results = {"passed": 0, "failed": 0, "errors": []}
    
    async def run_all_tests(self):
        """运行所有测试"""
        tests = [
            ("基础命令", self.test_basic_commands),
            ("参数处理", self.test_parameters),
            ("过滤器", self.test_filters),
            ("错误处理", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            try:
                await test_func()
                self.results["passed"] += 1
                print(f"✅ {test_name} 通过")
            except Exception as e:
                self.results["failed"] += 1
                self.results["errors"].append(f"{test_name}: {e}")
                print(f"❌ {test_name} 失败: {e}")
        
        self.print_summary()
    
    async def test_basic_commands(self):
        """基础命令测试"""
        client = TestClient()
        helper = TestHelper(client)
        client.start()
        client.register_plugin(self.plugin_class)
        
        # 在这里添加具体测试逻辑
        await helper.send_private_message("/hello")
        assert helper.get_latest_reply() is not None
    
    async def test_parameters(self):
        """参数测试"""
        # 实现参数相关测试
        pass
    
    async def test_filters(self):
        """过滤器测试"""
        # 实现过滤器相关测试
        pass
    
    async def test_error_handling(self):
        """错误处理测试"""
        # 实现错误处理相关测试
        pass
    
    def print_summary(self):
        """打印测试摘要"""
        total = self.results["passed"] + self.results["failed"]
        print(f"\n📊 测试摘要: {self.results['passed']}/{total} 通过")
        if self.results["errors"]:
            print("❌ 失败详情:")
            for error in self.results["errors"]:
                print(f"  - {error}")

# 使用测试套件
async def run_test_suite():
    suite = PluginTestSuite(TestPlugin)
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_test_suite())
```

## 🎯 测试最佳实践

### 1. 测试隔离
```python
async def isolated_test():
    """每个测试使用独立环境"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    try:
        client.register_plugin(TestPlugin)
        # 执行测试
        await helper.send_private_message("/test")
        # 断言结果
    finally:
        helper.clear_history()  # 清理历史
```

### 2. 数据驱动测试
```python
async def data_driven_test():
    """使用测试数据驱动"""
    test_data = [
        {"input": "/calc 1 2", "expected": "3"},
        {"input": "/calc 10 5", "expected": "15"},
        {"input": "/hello", "expected": "你好"},
    ]
    
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    for case in test_data:
        await helper.send_private_message(case["input"])
        assert_reply_contains(helper, case["expected"])
```

### 3. 测试装饰器
```python
from functools import wraps

def plugin_test(plugin_class):
    """测试装饰器"""
    def decorator(test_func):
        @wraps(test_func)
        async def wrapper():
            client = TestClient()
            helper = TestHelper(client)
            client.start()
            client.register_plugin(plugin_class)
            
            try:
                await test_func(client, helper)
                print(f"✅ {test_func.__name__} 通过")
            except Exception as e:
                print(f"❌ {test_func.__name__} 失败: {e}")
                raise
        return wrapper
    return decorator

@plugin_test(TestPlugin)
async def test_with_decorator(client, helper):
    """使用装饰器的测试"""
    await helper.send_private_message("/hello")
    assert helper.get_latest_reply() is not None
```

## 📝 调试技巧

### 1. 交互式测试
```python
async def interactive_debug():
    """交互式调试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    print("输入命令测试，输入 'exit' 退出")
    while True:
        cmd = input("> ")
        if cmd == 'exit':
            break
        
        helper.clear_history()
        await helper.send_private_message(cmd)
        
        reply = helper.get_latest_reply()
        if reply:
            print(f"回复: {extract_text(reply['message'])}")
        else:
            print("无回复")
```

### 2. 详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)

async def debug_test():
    """带详细日志的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)
    
    await helper.send_private_message("/debug_cmd")
    
    # 查看 API 调用
    for endpoint, data in helper.get_api_calls():
        print(f"API: {endpoint} -> {data}")
```

## 💡 关键要点

1. **测试三要素**: 创建环境 → 执行操作 → 验证结果
2. **必备清理**: 使用 `helper.clear_history()` 避免测试间干扰
3. **断言明确**: 提供清晰的错误信息，便于调试
4. **隔离测试**: 每个测试使用独立的插件实例
5. **辅助函数**: 封装常用操作，提高测试代码复用性

---

**🎯 下一步**: 
- 查看 [实战案例](./UnifiedRegistry-实战案例.md) 了解复杂场景
- 参考 [最佳实践](./UnifiedRegistry-最佳实践.md) 提升代码质量
