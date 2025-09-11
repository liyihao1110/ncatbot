"""
交互式测试函数示例
来源: docs/testing/best-practice-simple.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


def extract_text(message_segments):
    """辅助函数：提取消息文本"""
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text


async def interactive_test():
    """交互式测试模式"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)
    
    print("🎮 交互式测试模式")
    print("输入命令进行测试，输入 'exit' 退出")
    print("示例命令: /hello, /hi, /echo 测试文本")
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


if __name__ == "__main__":
    print("启动交互式测试...")
    asyncio.run(interactive_test())
