# FilterRegistry 测试指南

## 🧪 测试框架概述

NCatBot 提供了完整的测试框架，支持单元测试和集成测试，确保你的插件质量和稳定性。

## 快速开始

### 1. 基础测试环境

```python
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# 导入测试工具
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import get_log

LOG = get_log("TestMyPlugin")

def setup_test_environment():
    """设置测试环境"""
    client = TestClient()
    helper = TestHelper(client)
    
    # 启动 Mock 模式（不需要真实的 QQ 连接）
    client.start(mock_mode=True)
    
    return client, helper
```

### 2. 第一个测试

```python
async def test_basic_command():
    """测试基础命令"""
    LOG.info("🧪 测试基础命令...")
    
    client, helper = setup_test_environment()
    
    # 发送私聊消息
    await helper.send_private_message("hello", user_id="test_user")
    
    # 验证回复
    helper.assert_reply_sent("你好！我是机器人 🤖")
    
    # 清理测试数据
    helper.clear_history()
    
    LOG.info("✅ 基础命令测试通过")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_basic_command())
```

## 完整测试类设计

### 测试类结构

```python
class MyPluginTest:
    """我的插件测试类"""
    
    def __init__(self):
        self.client = None
        self.helper = None
        self.log = get_log("MyPluginTest")
    
    def setup_test_environment(self):
        """设置测试环境"""
        self.client = TestClient()
        self.helper = TestHelper(self.client)
        self.client.start(mock_mode=True)
        return self.client, self.helper
    
    def extract_text(self, message_segments):
        """从消息段中提取纯文本"""
        text = ""
        for seg in message_segments:
            if isinstance(seg, dict) and seg.get("type") == "text":
                text += seg.get("data", {}).get("text", "")
        return text
    
    async def test_basic_commands(self):
        """测试基础命令"""
        self.log.info("🧪 测试基础命令...")
        
        client, helper = self.setup_test_environment()
        
        test_cases = [
            {
                "command": "hello",
                "expected": "你好！我是机器人 🤖",
                "description": "问候命令"
            },
            {
                "command": "ping",
                "expected": "pong! 🏓",
                "description": "ping命令"
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            try:
                await helper.send_private_message(test_case["command"], user_id="test_user")
                helper.assert_reply_sent(test_case["expected"])
                self.log.info(f"  ✅ {test_case['description']}")
                passed += 1
            except AssertionError as e:
                self.log.error(f"  ❌ {test_case['description']}: {e}")
            except Exception as e:
                self.log.error(f"  💥 {test_case['description']}: 异常 {e}")
            finally:
                helper.clear_history()
        
        self.log.info(f"🏁 基础命令测试完成: {passed}/{total} 通过")
        return passed == total
```

## 测试不同类型的功能

### 1. 参数解析测试

```python
async def test_parameter_parsing(self):
    """测试参数解析"""
    self.log.info("🧪 测试参数解析...")
    
    client, helper = self.setup_test_environment()
    
    test_cases = [
        {
            "command": "计算 5 3",
            "expected": "5 + 3 = 8",
            "description": "整数参数"
        },
        {
            "command": "echo Hello World",
            "expected": "你说: Hello World",
            "description": "字符串参数"
        },
        {
            "command": "设置 debug true",
            "expected": "设置成功: debug = True",
            "description": "布尔参数"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        try:
            await helper.send_private_message(test_case["command"], user_id="test_user")
            
            # 获取实际回复内容
            latest = helper.get_latest_reply()
            if latest:
                actual_text = self.extract_text(latest["message"])
                if test_case["expected"] in actual_text:
                    self.log.info(f"  ✅ {test_case['description']}")
                    passed += 1
                else:
                    self.log.error(f"  ❌ {test_case['description']}: 期望 '{test_case['expected']}', 实际 '{actual_text}'")
            else:
                self.log.error(f"  ❌ {test_case['description']}: 没有收到回复")
                
        except Exception as e:
            self.log.error(f"  💥 {test_case['description']}: 异常 {e}")
        finally:
            helper.clear_history()
    
    self.log.info(f"🏁 参数解析测试完成: {passed}/{total} 通过")
    return passed == total
```

### 2. 权限系统测试

```python
async def test_permission_system(self):
    """测试权限系统"""
    self.log.info("🧪 测试权限系统...")
    
    client, helper = self.setup_test_environment()
    rbac_manager = client.plugin_loader.rbac_manager
    
    # 测试普通用户无法执行管理员命令
    try:
        await helper.send_private_message("admin_command", user_id="normal_user")
        helper.assert_no_reply()  # 应该没有回复
        self.log.info("  ✅ 普通用户权限限制正常")
        normal_user_test = True
    except Exception as e:
        self.log.error(f"  ❌ 普通用户权限测试失败: {e}")
        normal_user_test = False
    finally:
        helper.clear_history()
    
    # 设置管理员权限并测试
    try:
        rbac_manager.assign_role_to_user("admin_user", "admin")
        await helper.send_private_message("admin_command", user_id="admin_user")
        helper.assert_reply_sent("管理员功能执行成功")
        self.log.info("  ✅ 管理员权限测试通过")
        admin_test = True
    except Exception as e:
        self.log.error(f"  ❌ 管理员权限测试失败: {e}")
        admin_test = False
    finally:
        helper.clear_history()
    
    passed = normal_user_test + admin_test
    self.log.info(f"🏁 权限系统测试完成: {passed}/2 通过")
    return passed == 2
```

### 3. 消息类型过滤器测试

```python
async def test_message_type_filters(self):
    """测试消息类型过滤器"""
    self.log.info("🧪 测试消息类型过滤器...")
    
    client, helper = self.setup_test_environment()
    
    # 群聊过滤器测试
    try:
        await helper.send_group_message("群聊功能", group_id="test_group", user_id="test_user")
        helper.assert_reply_sent("这是群聊专用功能")
        self.log.info("  ✅ 群聊过滤器测试通过")
        group_test = True
    except Exception as e:
        self.log.error(f"  ❌ 群聊过滤器测试失败: {e}")
        group_test = False
    finally:
        helper.clear_history()
    
    # 私聊过滤器测试
    try:
        await helper.send_private_message("私聊功能", user_id="test_user")
        helper.assert_reply_sent("这是私聊专用功能")
        self.log.info("  ✅ 私聊过滤器测试通过")
        private_test = True
    except Exception as e:
        self.log.error(f"  ❌ 私聊过滤器测试失败: {e}")
        private_test = False
    finally:
        helper.clear_history()
    
    # 跨类型测试（群聊命令在私聊中不应响应）
    try:
        await helper.send_private_message("群聊功能", user_id="test_user")
        helper.assert_no_reply()  # 群聊专用功能在私聊中不应响应
        self.log.info("  ✅ 跨类型过滤测试通过")
        cross_test = True
    except Exception as e:
        self.log.error(f"  ❌ 跨类型过滤测试失败: {e}")
        cross_test = False
    finally:
        helper.clear_history()
    
    passed = group_test + private_test + cross_test
    self.log.info(f"🏁 消息类型过滤器测试完成: {passed}/3 通过")
    return passed == 3
```

### 4. 自定义过滤器测试

```python
async def test_custom_filters(self):
    """测试自定义过滤器"""
    self.log.info("🧪 测试自定义过滤器...")
    
    client, helper = self.setup_test_environment()
    
    test_cases = [
        {
            "message": "这里包含关键词测试",
            "expected": "检测到关键词！",
            "description": "关键词过滤器"
        },
        {
            "message": "这是一条非常非常非常长的消息，用来测试长度过滤器功能是否正常工作",
            "expected": "这是一条很长的消息",
            "description": "长度过滤器"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        try:
            await helper.send_private_message(test_case["message"], user_id="test_user")
            helper.assert_reply_sent(test_case["expected"])
            self.log.info(f"  ✅ {test_case['description']}")
            passed += 1
        except Exception as e:
            self.log.error(f"  ❌ {test_case['description']}: {e}")
        finally:
            helper.clear_history()
    
    self.log.info(f"🏁 自定义过滤器测试完成: {passed}/{total} 通过")
    return passed == total
```

### 5. 错误处理测试

```python
async def test_error_handling(self):
    """测试错误处理"""
    self.log.info("🧪 测试错误处理...")
    
    client, helper = self.setup_test_environment()
    
    # 测试参数类型转换错误
    error_cases = [
        {
            "command": "计算 abc 123",  # 无效的整数参数
            "description": "整数参数转换错误"
        },
        {
            "command": "设置温度 xyz",  # 无效的浮点数参数
            "description": "浮点数参数转换错误"
        }
    ]
    
    passed = 0
    total = len(error_cases)
    
    for test_case in error_cases:
        try:
            await helper.send_private_message(test_case["command"], user_id="test_user")
            
            # 检查是否有回复
            api_calls = helper.get_api_calls()
            if len(api_calls) == 0:
                # 参数转换失败，没有回复（正常行为）
                self.log.info(f"  ✅ {test_case['description']} (正确处理，无回复)")
                passed += 1
            else:
                # 有回复，检查是否是错误提示
                latest = helper.get_latest_reply()
                if latest:
                    text = self.extract_text(latest["message"])
                    if "错误" in text or "失败" in text:
                        self.log.info(f"  ✅ {test_case['description']} (错误提示: {text[:30]}...)")
                        passed += 1
                    else:
                        self.log.warning(f"  ⚠️ {test_case['description']} (意外回复: {text[:30]}...)")
                        
        except Exception as e:
            self.log.error(f"  💥 {test_case['description']}: 异常 {e}")
        finally:
            helper.clear_history()
    
    self.log.info(f"🏁 错误处理测试完成: {passed}/{total} 通过")
    return passed == total
```

## 高级测试技巧

### 1. 并发测试

```python
async def test_concurrent_requests(self):
    """测试并发请求处理"""
    self.log.info("🧪 测试并发请求...")
    
    client, helper = self.setup_test_environment()
    
    # 创建多个并发任务
    tasks = []
    for i in range(5):
        task = helper.send_private_message(f"echo test_{i}", user_id=f"user_{i}")
        tasks.append(task)
    
    # 并发执行
    await asyncio.gather(*tasks)
    
    # 检查所有回复
    api_calls = helper.get_api_calls()
    if len(api_calls) >= 5:
        self.log.info("  ✅ 并发请求处理正常")
        return True
    else:
        self.log.error(f"  ❌ 并发请求处理异常: 期望5个回复，实际{len(api_calls)}个")
        return False
```

### 2. 性能测试

```python
async def test_response_time(self):
    """测试响应时间"""
    self.log.info("🧪 测试响应时间...")
    
    client, helper = self.setup_test_environment()
    
    import time
    
    # 测试响应时间
    start_time = time.time()
    await helper.send_private_message("hello", user_id="test_user")
    helper.assert_reply_sent("你好！我是机器人 🤖")
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000  # 转换为毫秒
    
    if response_time < 100:  # 100ms 以内
        self.log.info(f"  ✅ 响应时间测试通过: {response_time:.2f}ms")
        return True
    else:
        self.log.warning(f"  ⚠️ 响应时间较慢: {response_time:.2f}ms")
        return False
```

### 3. 数据持久化测试

```python
async def test_data_persistence(self):
    """测试数据持久化"""
    self.log.info("🧪 测试数据持久化...")
    
    client, helper = self.setup_test_environment()
    
    # 设置用户数据
    await helper.send_private_message("设置昵称 TestUser", user_id="test_user")
    helper.assert_reply_sent("昵称设置成功")
    helper.clear_history()
    
    # 重新创建环境（模拟重启）
    client, helper = self.setup_test_environment()
    
    # 检查数据是否持久化
    await helper.send_private_message("我的昵称", user_id="test_user")
    
    latest = helper.get_latest_reply()
    if latest:
        text = self.extract_text(latest["message"])
        if "TestUser" in text:
            self.log.info("  ✅ 数据持久化测试通过")
            return True
        else:
            self.log.error(f"  ❌ 数据持久化失败: {text}")
            return False
    else:
        self.log.error("  ❌ 数据持久化测试失败: 无回复")
        return False
```

## 完整测试套件

### 主测试运行器

```python
class ComprehensivePluginTest:
    """完整的插件测试套件"""
    
    def __init__(self):
        self.log = get_log("ComprehensiveTest")
        self.test_results = {}
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.log.info("🚀 开始完整插件测试")
        self.log.info("=" * 60)
        
        test_modules = [
            ("基础命令", self.test_basic_commands),
            ("参数解析", self.test_parameter_parsing),
            ("权限系统", self.test_permission_system),
            ("消息类型过滤", self.test_message_type_filters),
            ("自定义过滤器", self.test_custom_filters),
            ("错误处理", self.test_error_handling),
            ("并发处理", self.test_concurrent_requests),
            ("响应时间", self.test_response_time)
        ]
        
        passed_count = 0
        total_count = len(test_modules)
        
        for test_name, test_func in test_modules:
            self.log.info(f"\n📋 开始 {test_name} 测试...")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                if result:
                    passed_count += 1
                    self.log.info(f"✅ {test_name} 测试通过")
                else:
                    self.log.error(f"❌ {test_name} 测试失败")
            except Exception as e:
                self.log.error(f"💥 {test_name} 测试异常: {e}")
                self.test_results[test_name] = False
            
            await asyncio.sleep(0.5)  # 短暂延迟
        
        # 生成测试报告
        self.generate_test_report(passed_count, total_count)
        
        return passed_count == total_count
    
    def generate_test_report(self, passed: int, total: int):
        """生成测试报告"""
        self.log.info("=" * 60)
        self.log.info("📊 测试报告")
        self.log.info("=" * 60)
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        self.log.info(f"总测试数: {total}")
        self.log.info(f"通过测试: {passed}")
        self.log.info(f"失败测试: {total - passed}")
        self.log.info(f"成功率: {success_rate:.1f}%")
        
        self.log.info("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            self.log.info(f"  {test_name}: {status}")
        
        if passed == total:
            self.log.info("\n🎉 所有测试通过！插件质量良好")
        else:
            self.log.warning(f"\n⚠️ 有 {total - passed} 个测试失败，需要修复")

# 运行完整测试
if __name__ == "__main__":
    async def main():
        test_suite = ComprehensivePluginTest()
        success = await test_suite.run_all_tests()
        return success
    
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"💥 测试异常: {e}")
        exit(1)
```

## 最佳实践总结

### 1. 测试组织
- 按功能模块组织测试
- 使用描述性的测试名称
- 每个测试保持独立性

### 2. 测试数据管理
- 使用 `helper.clear_history()` 清理测试数据
- 为每个测试准备独立的测试数据
- 避免测试之间的数据污染

### 3. 异常处理
- 使用 try-catch 捕获异常
- 记录详细的错误信息
- 确保测试失败时有明确的原因

### 4. 性能考虑
- 添加适当的延迟避免过快请求
- 测试并发处理能力
- 监控响应时间

通过遵循这些测试最佳实践，你可以确保插件的质量和稳定性！
