"""
实战案例节选的可运行演示：来自 docs/plugin_system/UnifiedRegistry-实战案例.md

运行：python -m examples.unified_registry.real_world_cases_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class QABotPlugin(NcatBotPlugin):
    name = "QABotPlugin"
    version = "1.0.0"
    description = "简单的问答机器人"

    def __init__(self):
        super().__init__()
        self.qa_database = {
            "你好": "你好！我是问答机器人，有什么可以帮助你的吗？",
            "天气": "抱歉，我还不能查询天气。请使用天气应用或网站。",
            "帮助": "可用命令：/ask <问题>、/add_qa <问题> <答案>、/list_qa",
        }

    async def on_load(self):
        pass

    @command_registry.command("ask", description="询问问题")
    def ask_cmd(self, event: BaseMessageEvent, question: str):
        for keyword, answer in self.qa_database.items():
            if keyword in question:
                return f"💡 {answer}"
        return "❓ 抱歉，我不知道这个问题的答案。你可以使用 /add_qa 添加新的问答。"

    @command_registry.command("add_qa", description="添加问答")
    def add_qa_cmd(self, event: BaseMessageEvent, question: str, answer: str):
        if len(question) > 100 or len(answer) > 500:
            return "❌ 问题或答案太长了"
        self.qa_database[question] = answer
        return f"✅ 已添加问答：\n❓ {question}\n💡 {answer}"

    @command_registry.command("list_qa", description="列出所有问答")
    def list_qa_cmd(self, event: BaseMessageEvent):
        if not self.qa_database:
            return "📝 问答库为空"
        qa_list = []
        for i, (q, a) in enumerate(self.qa_database.items(), 1):
            qa_list.append(f"{i}. ❓ {q}\n   💡 {a[:50]}{'...' if len(a) > 50 else ''}")
        return "📚 问答库：\n" + "\n\n".join(qa_list)


def extract_text(message_segments):
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text


async def main():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(QABotPlugin)

    await helper.send_private_message("/ask 今天天气怎么样？")
    print("/ask ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/add_qa 1+1=2 是不是 对")
    print("/add_qa ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/list_qa")
    print("/list_qa ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    print("✅ real_world 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


