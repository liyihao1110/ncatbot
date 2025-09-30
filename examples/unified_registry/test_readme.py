import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import group_filter, admin_filter
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent


class ReadmeDemoPlugin(NcatBotPlugin):
    name = "ReadmeDemoPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply("Hello, World!")

    @group_filter
    @command_registry.command("kick")
    async def kick_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"踢出用户: {user_id}")

    @admin_filter
    @command_registry.command("deploy")
    @option(short_name="v", long_name="verbose", help="详细输出")
    @param(name="env", default="dev", help="部署环境")
    async def deploy_cmd(
        self,
        event: BaseMessageEvent,
        app_name: str,
        env: str = "dev",
        verbose: bool = False,
    ):
        result = f"部署 {app_name} 到 {env} 环境"
        if verbose:
            result += " (详细模式)"
        await event.reply(result)


async def run_readme_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(ReadmeDemoPlugin)

    # hello
    await helper.send_private_message("/hello")
    helper.assert_reply_sent("Hello, World!")
    helper.clear_history()

    # kick 群聊可用，私聊不可
    await helper.send_group_message("/kick 12345")
    helper.assert_reply_sent("踢出用户: 12345")
    helper.clear_history()
    await helper.send_private_message("/kick 12345")
    helper.assert_no_reply()
    helper.clear_history()

    # deploy 仅管理员
    original_manager = status.global_access_manager

    class _MockManager:
        def user_has_role(self, user_id, role):
            return False

    status.global_access_manager = _MockManager()
    try:
        await helper.send_private_message("/deploy app --env=prod -v")
        helper.assert_no_reply()
        helper.clear_history()

        class _AdminManager:
            def user_has_role(self, user_id, role):
                return True

        status.global_access_manager = _AdminManager()

        await helper.send_private_message("/deploy app --env=prod -v")
        helper.assert_reply_sent("部署 app 到 prod 环境")
        helper.assert_reply_sent("(详细模式)")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    print("\n🎉 README 相关示例全部验证通过！")


if __name__ == "__main__":
    asyncio.run(run_readme_tests())
