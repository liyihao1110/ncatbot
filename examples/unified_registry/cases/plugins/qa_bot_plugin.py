from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log


LOG = get_log(__name__)


class QABotPlugin(NcatBotPlugin):
    name = "QABotPlugin"
    version = "1.0.0"
    author = "示例作者"
    description = "简单的问答机器人"

    async def on_load(self):
        self.qa_database = {
            "你好": "你好！我是问答机器人，有什么可以帮助你的吗？",
            "天气": "抱歉，我还不能查询天气。请使用天气应用或网站。",
            "时间": "请检查你的设备时间，或者使用 /time 命令。",
            "帮助": "可用命令：/ask <问题>、/add_qa <问题> <答案>、/list_qa",
        }

    @command_registry.command("ask", description="询问问题")
    async def ask_cmd(self, event: BaseMessageEvent, question: str):
        for keyword, answer in self.qa_database.items():
            if keyword in question:
                LOG.info(f"用户 {event.user_id} 询问: {question}")
                await event.reply(f"💡 {answer}")
                return
        await event.reply(
            "❓ 抱歉，我不知道这个问题的答案。你可以使用 /add_qa 添加新的问答。"
        )

    @command_registry.command("add_qa", description="添加问答")
    async def add_qa_cmd(self, event: BaseMessageEvent, question: str, answer: str):
        if len(question) > 100 or len(answer) > 500:
            await event.reply("❌ 问题或答案太长了")
            return
        self.qa_database[question] = answer
        LOG.info(f"用户 {event.user_id} 添加问答: {question} -> {answer}")
        await event.reply(f"✅ 已添加问答：\n❓ {question}\n💡 {answer}")

    @command_registry.command("list_qa", description="列出所有问答")
    async def list_qa_cmd(self, event: BaseMessageEvent):
        if not self.qa_database:
            await event.reply("📝 问答库为空")
            return
        qa_list = []
        for i, (q, a) in enumerate(self.qa_database.items(), 1):
            qa_list.append(f"{i}. ❓ {q}\n   💡 {a[:50]}{'...' if len(a) > 50 else ''}")
        await event.reply("📚 问答库：\n" + "\n\n".join(qa_list))

    @command_registry.command("time", description="获取当前时间")
    async def time_cmd(self, event: BaseMessageEvent):
        import datetime

        now = datetime.datetime.now()
        await event.reply(f"🕐 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
