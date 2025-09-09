# 标准化测试最佳实践 - 使用 unittest 框架

本文档介绍如何使用 Python 标准库 `unittest` 框架编写规范的 NcatBot 插件测试。

## 基础测试类设置

### 1. 创建基础测试类

```python
import unittest
import asyncio
from typing import Optional
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import get_log

LOG = get_log("PluginTest")

class AsyncTestCase(unittest.TestCase):
    """支持异步测试的基础类"""
    
    def setUp(self):
        """每个测试方法执行前的设置"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
    
    def run_async(self, coro):
        """运行异步协程的辅助方法"""
        return self.loop.run_until_complete(coro)
    
    def tearDown(self):
        """每个测试方法执行后的清理"""
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
    
    @classmethod
    def setUpClass(cls):
        """类级别的一次性设置"""
        LOG.info(f"开始测试类: {cls.__name__}")
    
    def setUp(self):
        """测试方法级别的设置"""
        super().setUp()
        self.client = TestClient()
        self.helper = TestHelper(self.client)
        self.client.start()
        LOG.info(f"开始测试: {self._testMethodName}")
    
    def tearDown(self):
        """测试方法级别的清理"""
        self.helper.clear_history()
        LOG.info(f"完成测试: {self._testMethodName}")
        super().tearDown()
    
    def extract_text(self, message_segments):
        """从消息段中提取纯文本"""
        text = ""
        for seg in message_segments:
            if isinstance(seg, dict) and seg.get("type") == "text":
                text += seg.get("data", {}).get("text", "")
        return text
```

### 2. 创建专用测试类

```python
from my_plugin import MyPlugin

class TestMyPlugin(NcatBotTestCase):
    """MyPlugin 的测试类"""
    
    def setUp(self):
        """设置测试环境"""
        super().setUp()
        # 注册要测试的插件
        self.client.register_plugin(MyPlugin)
        self.plugin = self.client.get_registered_plugins()[0]
    
    def test_plugin_metadata(self):
        """测试插件元数据"""
        self.assertEqual(self.plugin.name, "MyPlugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertIsNotNone(self.plugin.description)
    
    def test_basic_command(self):
        """测试基本命令功能"""
        async def _test():
            await self.helper.send_private_message("/hello")
            
            reply = self.helper.get_latest_reply()
            self.assertIsNotNone(reply, "应该收到回复")
            
            text = self.extract_text(reply["message"])
            self.assertIn("你好", text, "回复应包含问候语")
        
        self.run_async(_test())
    
    def test_command_with_parameters(self):
        """测试带参数的命令"""
        async def _test():
            # 测试有效参数
            await self.helper.send_private_message("/calc 10 + 20")
            reply = self.helper.get_latest_reply()
            self.assertIsNotNone(reply)
            
            text = self.extract_text(reply["message"])
            self.assertIn("30", text, "计算结果应该是30")
            
            self.helper.clear_history()
            
            # 测试无效参数
            await self.helper.send_private_message("/calc invalid")
            reply = self.helper.get_latest_reply()
            self.assertIsNotNone(reply)
            
            text = self.extract_text(reply["message"])
            self.assertIn("错误", text, "应该返回错误信息")
        
        self.run_async(_test())
```

## 高级测试模式

### 1. 使用 Mock 和 Patch

```python
from unittest.mock import Mock, patch, AsyncMock

class TestAdvancedFeatures(NcatBotTestCase):
    """高级功能测试"""
    
    @patch('my_plugin.external_api.fetch_data')
    def test_external_api_integration(self, mock_fetch):
        """测试外部 API 集成"""
        # 设置 mock 返回值
        mock_fetch.return_value = {"status": "success", "data": "test_data"}
        
        async def _test():
            await self.helper.send_private_message("/fetch_data")
            reply = self.helper.get_latest_reply()
            
            text = self.extract_text(reply["message"])
            self.assertIn("test_data", text)
            
            # 验证 mock 被调用
            mock_fetch.assert_called_once()
        
        self.run_async(_test())
    
    def test_async_operation_with_mock(self):
        """测试异步操作"""
        async def _test():
            # Mock 异步方法
            self.plugin.async_method = AsyncMock(return_value="async_result")
            
            await self.helper.send_private_message("/async_command")
            reply = self.helper.get_latest_reply()
            
            text = self.extract_text(reply["message"])
            self.assertIn("async_result", text)
            
            # 验证异步方法被调用
            self.plugin.async_method.assert_awaited_once()
        
        self.run_async(_test())
```

### 2. 参数化测试

```python
import unittest
from parameterized import parameterized

class TestParameterized(NcatBotTestCase):
    """参数化测试示例"""
    
    @parameterized.expand([
        ("hello", "你好"),
        ("goodbye", "再见"),
        ("thanks", "谢谢"),
    ])
    def test_greetings(self, command, expected_response):
        """测试不同的问候命令"""
        async def _test():
            await self.helper.send_private_message(f"/{command}")
            reply = self.helper.get_latest_reply()
            
            self.assertIsNotNone(reply)
            text = self.extract_text(reply["message"])
            self.assertIn(expected_response, text)
        
        self.run_async(_test())
    
    @parameterized.expand([
        ("user123", "user", False),  # 普通用户，应该被拒绝
        ("admin456", "admin", True),  # 管理员，应该成功
        ("root789", "root", True),    # Root用户，应该成功
    ])
    def test_permission_levels(self, user_id, role, should_succeed):
        """测试不同权限级别"""
        async def _test():
            # 设置用户角色
            rbac = self.client.plugin_loader.rbac_manager
            rbac.assign_role_to_user(user_id, role)
            
            # 发送需要权限的命令
            await self.helper.send_private_message(
                "/admin_command", 
                user_id=user_id
            )
            
            reply = self.helper.get_latest_reply()
            if should_succeed:
                self.assertIsNotNone(reply, f"{role} 应该能执行命令")
            else:
                self.assertIsNone(reply, f"{role} 不应该能执行命令")
        
        self.run_async(_test())
```

### 3. 测试套件组织

```python
# test_suite.py
import unittest
from test_basic_features import TestBasicFeatures
from test_advanced_features import TestAdvancedFeatures
from test_permissions import TestPermissions

def create_test_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestBasicFeatures,
        TestAdvancedFeatures,
        TestPermissions,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite

def run_specific_tests():
    """运行特定测试"""
    suite = unittest.TestSuite()
    
    # 只运行特定的测试方法
    suite.addTest(TestBasicFeatures('test_hello_command'))
    suite.addTest(TestPermissions('test_admin_permission'))
    
    return suite

if __name__ == '__main__':
    # 运行所有测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(create_test_suite())
    
    # 或者运行特定测试
    # runner.run(run_specific_tests())
```

### 4. 自定义断言方法

```python
class CustomAssertionsMixin:
    """自定义断言混入类"""
    
    def assertReplyContains(self, expected_text: str, msg: str = None):
        """断言最新回复包含指定文本"""
        reply = self.helper.get_latest_reply()
        self.assertIsNotNone(reply, msg or "没有收到任何回复")
        
        text = self.extract_text(reply["message"])
        self.assertIn(
            expected_text, 
            text, 
            msg or f"回复中不包含期望文本: {expected_text}"
        )
    
    def assertNoReply(self, msg: str = None):
        """断言没有回复"""
        reply = self.helper.get_latest_reply()
        self.assertIsNone(reply, msg or "不应该有回复")
    
    def assertReplyMatches(self, pattern: str, msg: str = None):
        """断言回复匹配正则表达式"""
        import re
        reply = self.helper.get_latest_reply()
        self.assertIsNotNone(reply, msg or "没有收到任何回复")
        
        text = self.extract_text(reply["message"])
        self.assertRegex(
            text, 
            pattern, 
            msg or f"回复不匹配模式: {pattern}"
        )
    
    def assertApiCalled(self, endpoint: str, times: int = None, msg: str = None):
        """断言 API 被调用"""
        count = self.helper.mock_api.get_call_count(endpoint)
        if times is None:
            self.assertGreater(
                count, 
                0, 
                msg or f"API {endpoint} 未被调用"
            )
        else:
            self.assertEqual(
                count, 
                times, 
                msg or f"API {endpoint} 调用次数不正确"
            )

class EnhancedTestCase(NcatBotTestCase, CustomAssertionsMixin):
    """增强的测试基类"""
    pass

class TestWithCustomAssertions(EnhancedTestCase):
    """使用自定义断言的测试"""
    
    def test_reply_assertions(self):
        """测试回复断言"""
        async def _test():
            await self.helper.send_private_message("/hello")
            self.assertReplyContains("你好")
            
            self.helper.clear_history()
            
            await self.helper.send_private_message("/invalid")
            self.assertNoReply()
        
        self.run_async(_test())
    
    def test_api_assertions(self):
        """测试 API 断言"""
        async def _test():
            await self.helper.send_group_message(
                "测试消息",
                group_id="123456"
            )
            self.assertApiCalled("/send_group_msg", times=1)
        
        self.run_async(_test())
```

## 测试覆盖率

### 使用 coverage.py 分析测试覆盖率

```bash
# 安装 coverage
pip install coverage

# 运行测试并收集覆盖率数据
coverage run -m unittest discover -s tests -p "test_*.py"

# 生成覆盖率报告
coverage report -m

# 生成 HTML 报告
coverage html
```

## 持续集成配置

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests with coverage
      run: |
        coverage run -m unittest discover -s tests
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 最佳实践总结

1. **测试隔离**: 每个测试方法应该独立，不依赖其他测试的状态
2. **有意义的测试名称**: 使用描述性的测试方法名，如 `test_admin_command_requires_permission`
3. **适当的断言**: 不仅检查是否有响应，还要验证响应内容的正确性
4. **Mock 外部依赖**: 使用 Mock 隔离外部服务，确保测试的可靠性
5. **测试边界情况**: 包括正常情况、错误情况和边界情况
6. **保持测试简洁**: 每个测试只验证一个功能点
7. **使用 setUp 和 tearDown**: 正确初始化和清理测试环境
8. **文档化测试**: 为复杂的测试添加注释说明测试目的

## 下一步

- 查看[简单函数式测试最佳实践](./best-practice-simple.md)了解更灵活的测试方法
- 查看[API 参考文档](./api-reference.md)了解所有测试相关的 API
