from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.plugin_system import command_registry, NcatBotPlugin
from ncatbot.core import BaseMessageEvent


class ConfigTestPlugin(NcatBotPlugin):
    name = "ConfigTestPlugin"
    author = "TestAuthor"
    version = "1.0.0"

    async def on_load(self) -> None:
        self.register_config(
            "counter", default_value=0, description="A simple counter", value_type=int
        )

    @command_registry.command("get_counter", aliases=["gc"])
    async def get_counter(self, event: BaseMessageEvent) -> int:
        print(self.config["counter"])

    @command_registry.command("increment_counter", aliases=["ic"])
    async def increment_counter(self, event: BaseMessageEvent) -> int:
        self.config["counter"] += 1


# 测试配置功能
bot = TestClient()
helper = TestHelper(bot)
bot.run_backend()
bot.register_plugin(ConfigTestPlugin)
helper.send_private_message_sync("/ic")
helper.send_private_message_sync("/gc")  # 应该输出 1
helper.send_private_message_sync("/ic")
helper.send_private_message_sync(
    "/cfg ConfigTestPlugin counter 2", user_id="123456"
)  # 应该输出 2
helper.assert_reply_sent("插件 ConfigTestPlugin 配置 counter 更新为 2")
bot.bot_exit()
