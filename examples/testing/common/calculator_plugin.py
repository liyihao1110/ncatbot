"""
CalculatorPlugin - 用于演示 unittest 测试的计算器插件
来源: docs/testing/best-practice-unittest.md
"""

from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import on_message
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core.event.message_segment import MessageArray


class CalculatorPlugin(NcatBotPlugin):
    """简单计算器插件 - 用于演示测试"""

    name = "CalculatorPlugin"
    version = "1.0.0"
    description = "提供基本数学计算功能的演示插件"

    async def on_load(self):
        self.calculation_count = 0

    @on_message
    async def handle_message(self, event: BaseMessageEvent):
        """处理消息事件"""
        message_text = self.extract_text(event.message)

        # 处理问候命令
        if message_text.strip() == "/hello":
            await event.reply("你好！我是计算器插件 🧮")
            return

        # 处理计算命令
        if message_text.startswith("/calc "):
            expression = message_text[6:].strip()
            await self._handle_calculation(event, expression)
            return

        # 处理统计命令
        if message_text.strip() == "/stats":
            await event.reply(f"已进行 {self.calculation_count} 次计算")
            return

    async def _handle_calculation(self, event: BaseMessageEvent, expression: str):
        """处理数学计算"""
        try:
            # 简单的安全计算（仅支持基本运算符）
            allowed_chars = set("0123456789+-*/() .")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("包含不支持的字符")

            result = eval(expression)
            self.calculation_count += 1
            await event.reply(f"计算结果：{expression} = {result}")
            return

        except Exception as e:
            await event.reply(f"计算错误：{str(e)}")

    def extract_text(self, message_array: MessageArray):
        """提取消息中的文本内容"""
        return "".join([seg.text for seg in message_array.filter_text()])
