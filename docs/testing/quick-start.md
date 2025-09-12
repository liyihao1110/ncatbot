# NcatBot 测试快速上手指南

本指南将帮助您快速了解如何为 NcatBot 插件编写测试。

## 环境准备

```python
# 导入必要的测试工具
from ncatbot.utils.testing import TestClient, TestHelper, EventFactory
from ncatbot.plugin_system import BasePlugin
from ncatbot.plugin_system import command_registry, param, option
import asyncio
```

## 最简单的测试示例

### 1. 创建一个简单插件

```python
"""
HelloPlugin - 用于测试文档验证的简单插件
"""
from ncatbot.plugin_system.builtin_mixin.ncatbot_plugin import NcatBotPlugin
from ncatbot.core.event import BaseMessageEvent
from ncatbot.plugin_system import command_registry, param, option


class HelloPlugin(NcatBotPlugin):
    """用于演示的简单插件"""
    name = "HelloPlugin"
    version = "1.0.0"
    description = "用于演示测试的简单插件"
        
    async def on_load(self):
        pass

    @command_registry.command("hello", aliases=["hi"], description="问候")
    async def hello_command(self, event: BaseMessageEvent):
        await event.reply("你好！这是来自 HelloPlugin 的问候。")

    @command_registry.command("echo", description="回显文本")
    @param(name="lang", default="zh", help="语言", choices=["zh","en"])
    @option(short_name="v", long_name="verbose", help="详细输出")
    async def echo_command(self, event: BaseMessageEvent, text: str, lang: str = "zh", verbose: bool = False):
        await event.reply(f"[{lang}] 你说的是：{text}" + (" (verbose)" if verbose else ""))

```

### 2. 编写测试代码

```python
async def test_hello_plugin():
    """测试 HelloPlugin 的基本功能"""
    
    # 1. 创建测试客户端
    client = TestClient()
    helper = TestHelper(client)
    
    # 2. 启动客户端（Mock 模式默认开启）
    client.start()
    
    # 3. 注册要测试的插件
    client.register_plugin(HelloPlugin)
    
    # 4. 测试 hello 命令
    await helper.send_private_message("/hello", user_id="test_user")
    
    # 5. 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"
    
    # 提取消息文本
    message_text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            message_text += seg["data"]["text"]
    
    assert "你好！这是来自 HelloPlugin 的问候。" in message_text
    print("✅ hello 命令测试通过")
    
    # 6. 清理历史记录，准备下一个测试
    helper.clear_history()
    
    # 7. 测试命令别名
    await helper.send_private_message("/hi", user_id="test_user")
    reply = helper.get_latest_reply()
    assert reply is not None, "别名命令应该有回复"
    print("✅ 命令别名测试通过")
    
    helper.clear_history()
    
    # 8. 测试带参数/选项/命名参数
    await helper.send_private_message("/echo 测试文本 --lang=zh -v", user_id="test_user")
    reply = helper.get_latest_reply()
    assert reply is not None
    
    message_text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            message_text += seg["data"]["text"]
    
    assert "你说的是：测试文本" in message_text
    print("✅ echo 命令测试通过")
    
    print("\n🎉 所有测试通过！")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_hello_plugin())
```

## 核心概念解释

1. **TestClient**: 测试专用的客户端，自动启用 Mock 模式
   - `register_plugin()`: 注册需要测试的插件
   - `start()`: 启动客户端，跳过真实连接

2. **TestHelper**: 简化测试操作的辅助类
   - `send_private_message()`: 模拟发送私聊消息
   - `send_group_message()`: 模拟发送群消息
   - `get_latest_reply()`: 获取最新的回复
   - `clear_history()`: 清理历史记录

3. **EventFactory**: 创建标准化的测试事件（上例中由 helper 内部使用）

## 测试文档目录

- [完整测试指南](./guide.md) - 详细了解测试框架的所有功能
- [标准化测试最佳实践](./best-practice-unittest.md) - 使用 unittest 框架的规范测试
- [简单函数式测试最佳实践](./best-practice-simple.md) - 快速编写测试函数
- [API 参考文档](./api-reference.md) - 所有测试相关 API 的详细说明
