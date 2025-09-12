from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option
from ncatbot.core.event import BaseMessageEvent


class DataProcessingPlugin(NcatBotPlugin):
    name = "DataProcessingPlugin"
    version = "1.0.0"
    description = "数据处理和分析工具"
    
    async def on_load(self):
        self.datasets = {}
    
    @command_registry.command("text_stats", description="文本统计")
    async def text_stats_cmd(self, event: BaseMessageEvent, text: str):
        import re
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        sentence_count = len(re.findall(r'[.!?]+', text))
        stats = f"📝 文本统计:\n"
        stats += f"🔤 字符数: {char_count}\n"
        stats += f"📝 单词数: {word_count}\n"
        stats += f"📄 行数: {line_count}\n"
        stats += f"📋 句子数: {sentence_count}"
        await event.reply(stats)


