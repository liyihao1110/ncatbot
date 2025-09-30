from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import param
from ncatbot.core.event import BaseMessageEvent
import random


class WebAPIPlugin(NcatBotPlugin):
    name = "WebAPIPlugin"
    version = "1.0.0"
    description = "Web API集成示例（模拟）"

    async def on_load(self):
        pass

    @command_registry.command("random_quote", description="获取随机名言")
    async def random_quote_cmd(self, event: BaseMessageEvent):
        quotes = [
            "生活就像一盒巧克力，你永远不知道下一颗是什么味道。",
            "做你自己，因为其他人都已经被占用了。",
            "昨天是历史，明天是谜团，今天是礼物。",
            "不要因为结束而哭泣，要因为发生过而微笑。",
        ]
        quote = random.choice(quotes)
        await event.reply(f"💭 今日名言：\n{quote}")

    @command_registry.command("mock_api", description="模拟API调用")
    @param(name="endpoint", default="users", help="API端点")
    async def mock_api_cmd(self, event: BaseMessageEvent, endpoint: str = "users"):
        mock_responses = {
            "users": {"total": 100, "active": 85},
            "posts": {"total": 500, "today": 12},
            "stats": {"cpu": "45%", "memory": "60%"},
        }
        if endpoint not in mock_responses:
            await event.reply(
                "❌ 未知的API端点: {endpoint}\n可用端点: users, posts, stats"
            )
            return
        data = mock_responses[endpoint]
        await event.reply(
            "🌐 API响应 ("
            + endpoint
            + "):\n"
            + "\n".join([f"{k}: {v}" for k, v in data.items()])
        )
