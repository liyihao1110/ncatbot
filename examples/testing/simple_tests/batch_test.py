"""
批量测试函数示例
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


async def run_all_tests():
    """运行所有测试"""
    # 共享的测试环境
    client = TestClient()
    helper = TestHelper(client)
    client.start(mock_mode=True)
    client.register_plugin(HelloPlugin)
    
    # 测试结果统计
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # 测试1：基本命令
    try:
        helper.clear_history()
        await helper.send_private_message("/hello")
        reply = helper.get_latest_reply()
        assert reply is not None
        results["passed"] += 1
        print("✅ Hello 命令测试通过")
    except AssertionError as e:
        results["failed"] += 1
        results["errors"].append(f"Hello 命令测试失败: {e}")
    
    # 测试2：带参数命令
    try:
        helper.clear_history()
        await helper.send_private_message("/echo 测试文本")
        reply = helper.get_latest_reply()
        assert reply is not None
        text = extract_text(reply["message"])
        assert "测试文本" in text
        results["passed"] += 1
        print("✅ Echo 命令测试通过")
    except AssertionError as e:
        results["failed"] += 1
        results["errors"].append(f"Echo 命令测试失败: {e}")
    
    # 测试3：命令别名
    try:
        helper.clear_history()
        await helper.send_private_message("/hi")
        reply = helper.get_latest_reply()
        assert reply is not None
        results["passed"] += 1
        print("✅ 命令别名测试通过")
    except AssertionError as e:
        results["failed"] += 1
        results["errors"].append(f"命令别名测试失败: {e}")
    
    # 打印测试报告
    print("\n" + "="*50)
    print(f"测试完成: {results['passed']} 通过, {results['failed']} 失败")
    if results["errors"]:
        print("\n失败详情:")
        for error in results["errors"]:
            print(f"  - {error}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
