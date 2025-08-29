# NcatBot 测试模块 - 快速参考 (函数版)

## 三步开始测试 (无需 unittest)

### 1️⃣ 导入和设置
```python
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

def setup_test():
    client = TestClient()  # 开箱即用的测试客户端
    helper = TestHelper(client)
    return client, helper
```

### 2️⃣ 注册插件
```python
client, helper = setup_test()
client.register_plugin(your_plugin_instance)
```

### 3️⃣ 测试命令
```python
async def test_hello():
    client, helper = setup_test()
    
    await helper.send_private_message("hello", user_id="123")
    helper.assert_reply_sent("Hello, World!")
    
    print("✅ hello 命令测试通过")

# 运行测试
asyncio.run(test_hello())
```

## 常用方法速查

### 发送消息
```python
# 私聊
await helper.send_private_message("消息", user_id="123456")

# 群聊  
await helper.send_group_message("消息", group_id="789", user_id="456")
```

### 验证回复
```python
helper.assert_reply_sent()              # 有回复
helper.assert_reply_sent("预期内容")     # 有包含特定内容的回复
helper.assert_no_reply()                # 没有回复
```

### 手动验证 (不用 assert)
```python
# 获取API调用
api_calls = helper.get_api_calls()
print(f"API调用次数: {len(api_calls)}")

# 获取最新回复
latest = helper.get_latest_reply()
if latest:
    message_text = extract_text(latest["message"])
    print(f"最新回复: {message_text}")
    
# 提取消息文本的辅助函数
def extract_text(message_segments):
    text = ""
    for seg in message_segments:
        if seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text
```

### 自定义响应
```python
helper.set_api_response("/endpoint", {"retcode": 0, "data": {}})
```

## 完整测试脚本模板

```python
#!/usr/bin/env python3
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
# from your_plugin import YourPlugin  # 导入你的插件

def extract_text(message_segments):
    """提取消息文本"""
    text = ""
    for seg in message_segments:
        if seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text

def setup_test():
    """设置测试环境"""
    client = TestClient()
    helper = TestHelper(client)
    
    # 注册插件
    # plugin = YourPlugin(event_bus=client.event_bus, plugin_loader=None)
    # client.register_plugin(plugin)
    
    return client, helper

async def test_basic_hello():
    """测试基础问候"""
    print("🧪 测试基础问候...")
    
    client, helper = setup_test()
    
    # 发送 hello 命令
    await helper.send_private_message("hello", user_id="test123")
    
    # 验证回复
    try:
        helper.assert_reply_sent("Hello, World!")
        print("✅ 基础问候测试通过")
    except AssertionError as e:
        print(f"❌ 基础问候测试失败: {e}")
    
    # 清理
    helper.clear_history()

async def test_personalized_hello():
    """测试个性化问候"""
    print("🧪 测试个性化问候...")
    
    client, helper = setup_test()
    
    # 发送带名字的 hello 命令
    await helper.send_group_message("hello Alice", group_id="group123", user_id="user456")
    
    # 手动检查回复
    latest = helper.get_latest_reply()
    if latest:
        message_text = extract_text(latest["message"])
        if "Hello, Alice!" in message_text:
            print("✅ 个性化问候测试通过")
        else:
            print(f"❌ 个性化问候测试失败，实际回复: {message_text}")
    else:
        print("❌ 个性化问候测试失败: 没有收到回复")
    
    helper.clear_history()

async def test_help_command():
    """测试帮助命令"""
    print("🧪 测试帮助命令...")
    
    client, helper = setup_test()
    
    await helper.send_private_message("help", user_id="test123")
    
    # 检查是否有回复
    api_calls = helper.get_api_calls()
    if len(api_calls) > 0:
        latest = helper.get_latest_reply()
        message_text = extract_text(latest["message"])
        if "帮助" in message_text or "help" in message_text.lower():
            print("✅ 帮助命令测试通过")
        else:
            print(f"❌ 帮助命令测试失败，回复内容: {message_text[:100]}...")
    else:
        print("❌ 帮助命令测试失败: 没有API调用")
    
    helper.clear_history()

async def test_no_response():
    """测试无效命令不响应"""
    print("🧪 测试无效命令...")
    
    client, helper = setup_test()
    
    await helper.send_private_message("invalid_command_xyz", user_id="test123")
    
    try:
        helper.assert_no_reply()
        print("✅ 无效命令测试通过")
    except AssertionError:
        print("❌ 无效命令测试失败: 不应该有回复")
    
    helper.clear_history()

async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行插件测试...")
    print("=" * 50)
    
    # 运行各个测试
    await test_basic_hello()
    await test_personalized_hello()
    await test_help_command()
    await test_no_response()
    
    print("=" * 50)
    print("🎉 所有测试完成!")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_all_tests())
```

## 简单的单个测试

```python
#!/usr/bin/env python3
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
# from your_plugin import YourPlugin

async def quick_test():
    # 设置
    client = TestClient()
    helper = TestHelper(client)
    
    # 注册插件
    # plugin = YourPlugin(event_bus=client.event_bus, plugin_loader=None)
    # client.register_plugin(plugin)
    
    # 测试
    await helper.send_private_message("hello", user_id="123")
    
    # 检查结果
    calls = helper.get_api_calls()
    print(f"API调用次数: {len(calls)}")
    
    if len(calls) > 0:
        latest = helper.get_latest_reply()
        print(f"最新回复: {latest}")

# 运行
asyncio.run(quick_test())
```

## 交互式测试

```python
#!/usr/bin/env python3
import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

async def interactive_test():
    client = TestClient()
    helper = TestHelper(client)
    
    # 注册你的插件
    # client.register_plugin(your_plugin)
    
    print("🤖 交互式插件测试器")
    print("输入消息进行测试，输入 'quit' 退出")
    
    while True:
        message = input("\n💬 输入测试消息: ").strip()
        if message.lower() == 'quit':
            break
            
        # 发送消息
        await helper.send_private_message(message, user_id="interactive_test")
        
        # 显示结果
        api_calls = helper.get_api_calls()
        if len(api_calls) > 0:
            latest = helper.get_latest_reply()
            if latest:
                # 提取文本
                text = ""
                for seg in latest["message"]:
                    if seg.get("type") == "text":
                        text += seg.get("data", {}).get("text", "")
                print(f"🤖 机器人回复: {text}")
            else:
                print("🤖 机器人无回复")
        else:
            print("🤖 没有触发任何响应")
        
        # 清空历史，准备下次测试
        helper.clear_history()

if __name__ == "__main__":
    asyncio.run(interactive_test())
```

就是这么简单，无需复杂的测试框架！ 🎉
