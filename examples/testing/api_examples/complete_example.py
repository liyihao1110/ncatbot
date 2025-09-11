"""
API 参考文档中的完整测试流程示例
来源: docs/testing/api-reference.md
"""
from ncatbot.utils.testing import TestClient, TestHelper, EventFactory
from ..common.hello_plugin import HelloPlugin
import asyncio


def extract_text(message_segments):
    """从消息段列表中提取纯文本"""
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text


async def complete_test_example():
    """完整测试流程示例"""
    # 1. 初始化
    client = TestClient()
    helper = TestHelper(client)
    
    # 2. 启动客户端
    client.start()
    
    # 3. 注册插件
    client.register_plugin(HelloPlugin)
    
    # 4. 设置 Mock 响应
    helper.set_api_response("/get_user_info", {
        "retcode": 0,
        "data": {"nickname": "测试用户", "level": 10}
    })
    
    # 5. 发送测试消息
    await helper.send_private_message("/hello")
    
    # 6. 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None
    print(f"收到回复: {extract_text(reply['message'])}")
    
    # 7. 检查 API 调用
    api_calls = helper.get_api_calls()
    print(f"API 调用次数: {len(api_calls)}")
    for endpoint, data in api_calls:
        print(f"API: {endpoint}")
    
    # 8. 清理
    helper.clear_history()
    
    print("✅ 测试完成")


async def test_helper_methods():
    """测试 TestHelper 的各种方法"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)
    
    # 测试发送私聊消息
    await helper.send_private_message(
        "/hello",
        user_id="123456",
        nickname="测试用户"
    )
    
    # 测试发送群聊消息
    await helper.send_group_message(
        "大家好",
        group_id="888888",
        user_id="123456",
        nickname="测试用户",
        role="member"
    )
    
    # 获取最新回复
    latest = helper.get_latest_reply()
    print(f"最新回复: {latest}")
    
    # 获取倒数第二个回复
    second_last = helper.get_latest_reply(-2)
    print(f"倒数第二个回复: {second_last}")
    
    # 断言回复
    try:
        helper.assert_reply_sent("你好")
        print("✅ 断言通过：包含期望文本")
    except AssertionError:
        print("❌ 断言失败")
    
    # 测试 API 响应设置
    helper.set_api_response("/get_user_info", {
        "retcode": 0,
        "data": {
            "user_id": "123456",
            "nickname": "测试用户",
            "level": 10
        }
    })
    print("✅ API 响应设置完成")


async def test_event_factory_methods():
    """测试 EventFactory 的各种方法"""
    # 纯文本消息
    event = EventFactory.create_group_message("Hello")
    print(f"群消息事件: {event.message}")
    
    # 私聊消息
    event = EventFactory.create_private_message(
        message="私聊消息",
        user_id="123456",
        nickname="测试用户",
        sub_type="friend"
    )
    print(f"私聊消息事件: {event.user_id}")
    
    # 群成员增加通知
    event = EventFactory.create_notice_event(
        notice_type="group_increase",
        user_id="123456",
        group_id="789012",
        sub_type="approve"
    )
    print(f"通知事件: {event.notice_type}")
    
    # 好友请求事件
    event = EventFactory.create_request_event(
        request_type="friend",
        user_id="123456",
        flag="test_flag",
        comment="请加我为好友"
    )
    print(f"请求事件: {event.request_type}")


if __name__ == "__main__":
    print("运行完整测试流程...")
    asyncio.run(complete_test_example())
    
    print("\n测试 TestHelper 方法...")
    asyncio.run(test_helper_methods())
    
    print("\n测试 EventFactory 方法...")
    asyncio.run(test_event_factory_methods())
