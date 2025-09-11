"""
性能测试函数示例
来源: docs/testing/best-practice-simple.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio
import time


async def performance_test():
    """性能测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start(mock_mode=True)
    client.register_plugin(HelloPlugin)
    
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


if __name__ == "__main__":
    asyncio.run(performance_test())
