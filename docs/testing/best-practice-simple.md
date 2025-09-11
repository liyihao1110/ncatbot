# 简单函数式测试最佳实践

本文档介绍如何使用简单的函数方式快速编写 NcatBot 插件测试，适合快速验证、调试和原型开发。

## 基本模式

### 1. 最简单的测试函数

```python
from ncatbot.utils.testing import TestClient, TestHelper
from my_plugin import MyPlugin
import asyncio

async def test_hello():
    """测试 hello 命令"""
    # 创建客户端和辅助器
    client = TestClient()
    helper = TestHelper(client)
    
    # 启动并注册插件
    client.start()
    client.register_plugin(MyPlugin)
    
    # 发送测试消息
    await helper.send_private_message("/hello")
    
    # 验证回复
    reply = helper.get_latest_reply()
    if reply:
        print("✅ 测试通过：收到回复")
        print(f"回复内容：{reply['message']}")
    else:
        print("❌ 测试失败：没有收到回复")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_hello())
```

### 2. 带断言的测试函数

```python
async def test_with_assertions():
    """带断言的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 测试正常情况
    await helper.send_private_message("/echo 测试文本")
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"
    
    # 提取文本内容
    text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            text += seg["data"]["text"]
    
    assert "测试文本" in text, f"回复应包含输入文本，实际：{text}"
    print("✅ Echo 命令测试通过")
    
    # 测试错误情况
    helper.clear_history()
    await helper.send_private_message("/echo")  # 没有参数
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到错误提示"
    print("✅ 错误处理测试通过")

asyncio.run(test_with_assertions())
```

## 实用测试模式

### 1. 批量测试函数

```python
async def run_all_tests():
    """运行所有测试"""
    # 共享的测试环境
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 测试结果统计
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # 测试1：基本命令
    try:
        helper.clear_history()
        await helper.send_private_message("/status")
        reply = helper.get_latest_reply()
        assert reply is not None
        results["passed"] += 1
        print("✅ 状态命令测试通过")
    except AssertionError as e:
        results["failed"] += 1
        results["errors"].append(f"状态命令测试失败: {e}")
    
    # 测试2：带参数命令
    try:
        helper.clear_history()
        await helper.send_private_message("/calc 1 + 1")
        reply = helper.get_latest_reply()
        assert reply is not None
        text = extract_text(reply["message"])
        assert "2" in text
        results["passed"] += 1
        print("✅ 计算命令测试通过")
    except AssertionError as e:
        results["failed"] += 1
        results["errors"].append(f"计算命令测试失败: {e}")
    
    # 打印测试报告
    print("\n" + "="*50)
    print(f"测试完成: {results['passed']} 通过, {results['failed']} 失败")
    if results["errors"]:
        print("\n失败详情:")
        for error in results["errors"]:
            print(f"  - {error}")
    print("="*50)

def extract_text(message_segments):
    """辅助函数：提取消息文本"""
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text

asyncio.run(run_all_tests())
```

### 2. 交互式测试函数

```python
async def interactive_test():
    """交互式测试模式"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    print("🎮 交互式测试模式")
    print("输入命令进行测试，输入 'exit' 退出")
    print("-" * 50)
    
    while True:
        command = input("\n> ")
        if command.lower() == 'exit':
            break
        
        # 清理历史
        helper.clear_history()
        
        # 发送命令
        await helper.send_private_message(command)
        
        # 获取回复
        reply = helper.get_latest_reply()
        if reply:
            text = extract_text(reply["message"])
            print(f"📨 回复: {text}")
        else:
            print("❌ 没有回复")
        
        # 显示 API 调用
        api_calls = helper.get_api_calls()
        if api_calls:
            print(f"📡 API 调用: {len(api_calls)} 次")
            for endpoint, data in api_calls[-3:]:  # 只显示最后3个
                print(f"   - {endpoint}")

asyncio.run(interactive_test())
```

### 3. 性能测试函数

```python
import time

async def performance_test():
    """性能测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 测试参数
    num_messages = 100
    command = "/hello"
    
    print(f"🏃 开始性能测试: 发送 {num_messages} 条消息")
    
    # 记录开始时间
    start_time = time.time()
    
    # 发送多条消息
    for i in range(num_messages):
        await helper.send_private_message(command)
        helper.clear_history()  # 避免内存累积
    
    # 计算耗时
    elapsed = time.time() - start_time
    avg_time = elapsed / num_messages * 1000  # 转换为毫秒
    
    print(f"✅ 完成测试")
    print(f"总耗时: {elapsed:.2f} 秒")
    print(f"平均响应时间: {avg_time:.2f} 毫秒")
    print(f"QPS: {num_messages / elapsed:.2f}")

asyncio.run(performance_test())
```

## 高级技巧

### 1. 测试装饰器

```python
from functools import wraps
import traceback

def plugin_test(plugin_class):
    """测试装饰器，自动设置测试环境"""
    def decorator(test_func):
        @wraps(test_func)
        async def wrapper():
            # 设置测试环境
            client = TestClient()
            helper = TestHelper(client)
            client.start()
            client.register_plugin(plugin_class)
            
            try:
                # 运行测试
                await test_func(client, helper)
                print(f"✅ {test_func.__name__} 通过")
            except Exception as e:
                print(f"❌ {test_func.__name__} 失败: {e}")
                traceback.print_exc()
        
        return wrapper
    return decorator

# 使用装饰器
@plugin_test(MyPlugin)
async def test_decorated(client, helper):
    """使用装饰器的测试"""
    await helper.send_private_message("/hello")
    reply = helper.get_latest_reply()
    assert reply is not None

asyncio.run(test_decorated())
```

### 2. 数据驱动测试

```python
async def data_driven_test():
    """数据驱动的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 测试数据
    test_cases = [
        {
            "name": "基本加法",
            "input": "/calc 1 + 1",
            "expected": "2",
        },
        {
            "name": "减法",
            "input": "/calc 10 - 5",
            "expected": "5",
        },
        {
            "name": "乘法",
            "input": "/calc 3 * 4",
            "expected": "12",
        },
        {
            "name": "除法",
            "input": "/calc 20 / 4",
            "expected": "5",
        },
        {
            "name": "错误输入",
            "input": "/calc invalid",
            "expected": "错误",
        },
    ]
    
    # 运行测试
    for case in test_cases:
        helper.clear_history()
        await helper.send_private_message(case["input"])
        reply = helper.get_latest_reply()
        
        if reply:
            text = extract_text(reply["message"])
            if case["expected"] in text:
                print(f"✅ {case['name']}: 通过")
            else:
                print(f"❌ {case['name']}: 失败 (期望 '{case['expected']}', 实际 '{text}')")
        else:
            print(f"❌ {case['name']}: 失败 (没有回复)")

asyncio.run(data_driven_test())
```

### 3. Mock 集成测试

```python
async def test_with_mock():
    """使用 Mock 的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    
    # 创建带 Mock 的插件
    class WeatherPlugin(BasePlugin):
        name = "WeatherPlugin"
        version = "1.0.0"
        
        async def on_load(self):
            @self.on_command("weather")
            async def weather_cmd(event, city: str = "北京"):
                # 假设这里会调用外部 API
                weather_data = await self.get_weather(city)
                return f"{city}的天气：{weather_data}"
        
        async def get_weather(self, city):
            # 实际会调用天气 API
            return "晴天"
    
    # 注册插件
    client.register_plugin(WeatherPlugin)
    plugin = client.get_registered_plugins()[0]
    
    # Mock 外部调用
    async def mock_weather(city):
        return {"北京": "晴天", "上海": "多云"}.get(city, "未知")
    
    plugin.get_weather = mock_weather
    
    # 测试不同城市
    for city in ["北京", "上海", "深圳"]:
        helper.clear_history()
        await helper.send_private_message(f"/weather {city}")
        reply = helper.get_latest_reply()
        
        if reply:
            text = extract_text(reply["message"])
            print(f"✅ {city}: {text}")
        else:
            print(f"❌ {city}: 没有回复")

asyncio.run(test_with_mock())
```

## 调试技巧

### 1. 详细日志输出

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_with_logging():
    """带详细日志的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 测试并查看日志
    await helper.send_private_message("/debug")
    
    # 打印所有 API 调用
    print("\n📡 API 调用记录:")
    for endpoint, data in helper.get_api_calls():
        print(f"Endpoint: {endpoint}")
        print(f"Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
        print("-" * 50)
```

### 2. 断点调试辅助

```python
async def debug_test():
    """方便断点调试的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(MyPlugin)
    
    # 在这里设置断点
    await helper.send_private_message("/test")
    
    # 检查状态
    reply = helper.get_latest_reply()
    plugins = client.get_registered_plugins()
    api_calls = helper.get_api_calls()
    
    # 使用 IPython 进行交互式调试（如果安装了）
    try:
        from IPython import embed
        embed()  # 进入交互式环境
    except ImportError:
        # 手动检查变量
        print(f"Reply: {reply}")
        print(f"Plugins: {[p.name for p in plugins]}")
        print(f"API Calls: {len(api_calls)}")
```

## 最佳实践总结

1. **保持简单**: 函数式测试适合快速验证，不要过度复杂化
2. **快速反馈**: 立即打印结果，方便调试
3. **重用代码**: 提取公共函数，如 `extract_text()`
4. **逐步构建**: 从简单测试开始，逐步添加复杂性
5. **交互式探索**: 使用交互式测试快速了解插件行为
6. **适时转换**: 当测试变复杂时，考虑转为标准化测试

## 何时使用函数式测试

✅ **适合场景**:
- 快速验证新功能
- 调试具体问题
- 探索性测试
- 演示和文档示例
- 一次性测试脚本

❌ **不适合场景**:
- 需要持续集成的项目
- 复杂的测试场景
- 需要测试覆盖率报告
- 团队协作的大型项目

## 下一步

- 查看[标准化测试最佳实践](./best-practice-unittest.md)了解更规范的测试方法
- 查看[API 参考文档](./api-reference.md)了解所有可用的测试 API
