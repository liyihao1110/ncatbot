"""
快速上手指南中的测试示例
来源: docs/testing/quick-start.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
import asyncio

# 导入通用插件
from .sleep.sleep import SleepPlugin
from .status.status import StatusPlugin


async def test_hello_plugin():
    """测试 HelloPlugin 的基本功能"""

    # 1. 创建测试客户端
    client = TestClient()
    helper = TestHelper(client)

    # 2. 启动客户端（Mock 模式默认开启）
    client.start()

    # 3. 注册要测试的插件
    client.register_plugin(SleepPlugin)
    client.register_plugin(StatusPlugin)

    # 4. 测试 sleep 命令
    await helper.send_private_message("/sleep", user_id="test_user")
    await asyncio.sleep(1)  # 等待一段时间以确保命令被处理
    
    # 5. 验证回复
    helper.assert_reply_sent("正在进入睡眠状态...")

    # 6. 检测是否阻塞
    await helper.send_private_message("/status", user_id="test_user")
    await asyncio.sleep(1)  # 等待一段时间以确保命令被处理
    helper.assert_reply_sent("NcatBot 正在运行中...")

    # 7. 测试 asleep 命令
    await helper.send_private_message("/asleep", user_id="test_user")
    await asyncio.sleep(1)  # 等待一段时间以确保命令被处理
    helper.assert_reply_sent("正在异步进入睡眠状态...")
    
    # 8. 测试阻塞
    await helper.send_private_message("/status", user_id="test_user")
    await asyncio.sleep(1)  # 等待一段时间以确保命令被
    helper.assert_reply_sent("NcatBot 正在运行中...")
    
    # 9. 汇报结果
    print("所有测试通过！")


# 运行测试
if __name__ == "__main__":
    asyncio.run(test_hello_plugin())
