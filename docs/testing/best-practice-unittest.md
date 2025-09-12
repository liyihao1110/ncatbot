# 标准化测试最佳实践 - 使用 unittest 框架

本文档介绍如何使用 Python 标准库 `unittest` 框架编写规范的 NcatBot 插件测试。

## 基础测试类设置

## 完整可运行示例

以下是一个完整的单元测试示例，包含插件定义和测试代码：

```python
"""
完整的插件单元测试示例
运行方式：python -m unittest test_calculator_plugin.py
"""
import unittest
import asyncio
from typing import List, Type
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.utils import get_log
from ncatbot.plugin_system import on_message
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core.event.message_segment import MessageArray

LOG = get_log("PluginTest")

# ============== 插件定义部分 ==============
class CalculatorPlugin(NcatBotPlugin):
    """简单计算器插件 - 用于演示测试"""
    
    name = "CalculatorPlugin"
    version = "1.0.0"
    description = "提供基本数学计算功能的演示插件"
    
    async def on_load(self):
        self.calculation_count = 0

    @on_message
    async def handle_message(self, event: BaseMessageEvent):
        """处理消息事件"""
        message_text = self.extract_text(event.message)
        
        # 处理问候命令
        if message_text.strip() == "/hello":
            await event.reply("你好！我是计算器插件 🧮")
            return
        
        # 处理计算命令
        if message_text.startswith("/calc "):
            expression = message_text[6:].strip()
            await self._handle_calculation(event, expression)
            return
        
        # 处理统计命令
        if message_text.strip() == "/stats":
            await event.reply(f"已进行 {self.calculation_count} 次计算")
            return
    
    async def _handle_calculation(self, event: BaseMessageEvent, expression: str):
        """处理数学计算"""
        try:
            # 简单的安全计算（仅支持基本运算符）
            allowed_chars = set('0123456789+-*/() .')
            if not all(c in allowed_chars for c in expression):
                raise ValueError("包含不支持的字符")
            
            result = eval(expression)
            self.calculation_count += 1
            await event.reply(f"计算结果：{expression} = {result}")
            return
            
        except Exception as e:
            await event.reply(f"计算错误：{str(e)}")
    
    def extract_text(self, message_array: MessageArray):
        """提取消息中的文本内容"""
        return "".join([seg.text for seg in message_array.filter_text()])


# ============== 测试基类定义 ==============
class AsyncTestCase(unittest.TestCase):
    """支持异步测试的基础类"""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
    
    def run_async(self, coro):
        """运行异步协程"""
        return self.loop.run_until_complete(coro)
    
    def tearDown(self):
        # 清理未完成的任务
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        if pending:
            self.loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )

class AsyncTestCase(unittest.TestCase):
    """支持异步测试的基础类"""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
    
    def run_async(self, coro):
        """运行异步协程"""
        return self.loop.run_until_complete(coro)
    
    def tearDown(self):
        # 清理未完成的任务
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        if pending:
            self.loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )


class NcatBotTestCase(AsyncTestCase):
    """NcatBot 插件测试基类"""
    
    test_plugins: List[Type[BasePlugin]] = []
    client: TestClient = None
    helper: TestHelper = None
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化 - 启动测试客户端并加载插件"""
        LOG.info(f"开始测试类: {cls.__name__}")
        
        cls.client = TestClient()
        cls.helper = TestHelper(cls.client)
        cls.client.start()
        
        # 加载测试插件
        if cls.test_plugins:
            for plugin_class in cls.test_plugins:
                cls.client.register_plugin(plugin_class)
                LOG.info(f"已加载测试插件: {plugin_class.__name__}")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理 - 卸载插件并清理资源"""
        if cls.client:
            plugins = cls.client.get_registered_plugins()
            for plugin in plugins:
                cls.client.unregister_plugin(plugin)
            LOG.info("TestClient 资源已清理")
    
    def setUp(self):
        super().setUp()
        if self.helper:
            self.helper.clear_history()
    
    def tearDown(self):
        if self.helper:
            self.helper.clear_history()
        super().tearDown()
    
    def extract_text(self, message_segments):
        """从消息段中提取纯文本"""
        text = ""
        for seg in message_segments:
            if isinstance(seg, dict) and seg.get("type") == "text":
                text += seg.get("data", {}).get("text", "")
        return text


class TestCalculatorPlugin(NcatBotTestCase):
    """计算器插件的测试类"""
    
    test_plugins = [CalculatorPlugin]
    
    def setUp(self):
        super().setUp()
        self.plugin = self.client.get_plugin(CalculatorPlugin)
    
    def test_plugin_metadata(self):
        """测试插件元数据"""
        self.assertEqual(self.plugin.name, "CalculatorPlugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertIn("计算", self.plugin.description)
    
    def test_hello_command(self):
        """测试问候命令"""
        async def _test():
            await self.helper.send_private_message("/hello")
            reply = self.helper.get_latest_reply()
            
            self.assertIsNotNone(reply, "应该收到回复")
            text = self.extract_text(reply["message"])
            self.assertIn("你好", text)
            self.assertIn("计算器", text)
        
        self.run_async(_test())
    
    def test_basic_calculation(self):
        """测试基本计算功能"""
        async def _test():
            await self.helper.send_private_message("/calc 10 + 20")
            reply = self.helper.get_latest_reply()
            
            self.assertIsNotNone(reply)
            text = self.extract_text(reply["message"])
            self.assertIn("30", text)
            self.assertIn("10 + 20", text)
        
        self.run_async(_test())
    
    def test_calculation_error(self):
        """测试计算错误处理"""
        async def _test():
            await self.helper.send_private_message("/calc invalid_expression")
            reply = self.helper.get_latest_reply()
            
            self.assertIsNotNone(reply)
            text = self.extract_text(reply["message"])
            self.assertIn("错误", text)
        
        self.run_async(_test())
    
    def test_statistics_tracking(self):
        """测试统计功能"""
        async def _test():
            # 执行几次计算
            self.client.get_plugin(CalculatorPlugin).calculation_count = 0

            await self.helper.send_private_message("/calc 1 + 1")
            self.helper.get_latest_reply()  # 清除回复
            
            await self.helper.send_private_message("/calc 2 * 3")
            self.helper.get_latest_reply()  # 清除回复
            
            # 检查统计
            await self.helper.send_private_message("/stats")
            reply = self.helper.get_latest_reply()
            
            text = self.extract_text(reply["message"])
            self.assertIn("2", text)  # 应该显示进行了2次计算
        
        self.run_async(_test())


if __name__ == "__main__":
    unittest.main()
```

## 最佳实践总结

### 1. 生命周期管理（关键）
- **TestClient 单例原则**: 在整个测试类生命周期中，TestClient 只能启动一次
- **插件集中加载**: 所有测试插件在 `test_plugins` 类属性中声明，在 `setUpClass` 中统一加载
- **资源正确清理**: 在 `tearDownClass` 中卸载插件和清理客户端资源
- **测试方法轻量化**: `setUp` 和 `tearDown` 只进行轻量级的状态清理

### 2. 测试设计原则
- **测试隔离**: 每个测试方法应该独立，不依赖其他测试的状态
- **有意义的测试名称**: 使用描述性的测试方法名
- **适当的断言**: 不仅检查是否有响应，还要验证响应内容的正确性
- **保持测试简洁**: 每个测试只验证一个功能点

### 3. 外部依赖和组织
- **Mock 外部依赖**: 使用 Mock 隔离外部服务，确保测试的可靠性
- **恢复原始状态**: Mock 后记得在测试结束时恢复原始方法
- **使用测试会话管理器**: 确保每个测试类的资源得到正确管理
- **测试边界情况**: 包括正常情况、错误情况和边界情况

## ⚠️ 重要提醒：生命周期管理

1. **TestClient 只能启动一次**：在整个测试类的生命周期中，`client.start()` 只能被调用一次
2. **插件集中管理**：所有要测试的插件必须在 `test_plugins` 类属性中声明
3. **避免重复初始化**：不要在 `setUp` 方法中创建新的 TestClient 实例

**错误示例**：
```python
def setUp(self):
    self.client = TestClient()  # ❌ 错误：每次都创建新客户端
    self.client.start()         # ❌ 错误：重复启动
```

**正确示例**：
```python
class TestMyPlugin(NcatBotTestCase):
    test_plugins = [MyPlugin]   # ✅ 正确：在类属性中声明插件
    
    def setUp(self):
        super().setUp()         # ✅ 正确：只调用父类的轻量级初始化
```

遵循这些原则可以确保测试的稳定性和性能。

## 下一步

- 查看[简单函数式测试最佳实践](./best-practice-simple.md)了解更灵活的测试方法
- 查看[API 参考文档](./api-reference.md)了解所有测试相关的 API