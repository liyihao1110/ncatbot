"""
完整的插件单元测试示例
来源: docs/testing/best-practice-unittest.md
运行方式：python -m unittest test_calculator_plugin.py
"""
import unittest
import asyncio
from typing import List, Type

from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.plugin_system import BasePlugin
from ncatbot.utils import get_log
from ..common.calculator_plugin import CalculatorPlugin

LOG = get_log("PluginTest")


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
    
    def get_plugin(self, plugin_class):
        """获取已加载的插件实例"""
        for plugin in self.client.get_registered_plugins():
            if isinstance(plugin, plugin_class):
                return plugin
        raise ValueError(f"插件 {plugin_class.__name__} 未找到")


class TestCalculatorPlugin(NcatBotTestCase):
    """计算器插件的测试类"""
    
    test_plugins = [CalculatorPlugin]
    
    def setUp(self):
        super().setUp()
        self.plugin = self.get_plugin(CalculatorPlugin)
    
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
