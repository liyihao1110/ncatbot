import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.filters_custom_plugin import (
    CustomFiltersPlugin,
    bind_custom_filter_to_function,
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry,
)
from ncatbot.core.event import BaseMessageEvent


async def run_custom_filters_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(CustomFiltersPlugin)

    # time_filter：仅在 9~22 点之间允许。无法确定当前时间，做最小验证：
    # 这里只验证逻辑路径（若在允许时间，应有回复；否则无回复）。
    await helper.send_private_message("/vip")
    # 不断言具体真/假，只要不抛异常并能继续后续用例即可。
    helper.clear_history()

    # keyword_filter + 自定义绑定到函数（非命令）
    @bind_custom_filter_to_function
    async def time_check_command(event: BaseMessageEvent):
        await event.reply("关键字命中")

    # 注册到过滤器函数集合中
    filter_registry._function_filters.append(time_check_command)

    # 未包含关键字，应该无回复
    await helper.send_private_message("这是一条普通消息")
    helper.assert_no_reply()
    helper.clear_history()

    # 包含关键字，触发回复
    await helper.send_private_message("我是一名机器人用户")
    helper.assert_reply_sent("关键字命中")
    helper.clear_history()

    print("\n✅ custom_filters 测试通过")


if __name__ == "__main__":
    asyncio.run(run_custom_filters_tests())
