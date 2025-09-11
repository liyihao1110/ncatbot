from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option
from ncatbot.core.event import BaseMessageEvent


class DataProcessingPlugin(NcatBotPlugin):
    name = "DataProcessingPlugin"
    version = "1.0.0"
    description = "数据处理和分析工具"
    
    async def on_load(self):
        pass

    @command_registry.command("csv_analyze", description="分析CSV数据")
    @option(short_name="h", long_name="header", help="包含标题行")
    async def csv_analyze_cmd(self, event: BaseMessageEvent, data: str, header: bool = False):
        try:
            lines = data.strip().split('\n')
            if not lines:
                await event.reply("❌ 没有数据行")
                return
            if header:
                headers = lines[0].split(',')
                data_lines = lines[1:]
            else:
                headers = [f"列{i+1}" for i in range(len(lines[0].split(',')))]
                data_lines = lines
            if not data_lines:
                await event.reply("❌ 没有数据行")
                return
            total_rows = len(data_lines)
            total_cols = len(headers)
            analysis = f"📊 CSV数据分析:\n"
            analysis += f"📝 总行数: {total_rows}\n"
            analysis += f"📋 总列数: {total_cols}\n"
            analysis += f"🏷️ 列名: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}"
            await event.reply(analysis)
        except Exception as e:
            await event.reply(f"❌ 数据分析失败: {e}")

    @command_registry.command("json_format", description="格式化JSON数据")
    @option(short_name="c", long_name="compact", help="紧凑格式")
    async def json_format_cmd(self, event: BaseMessageEvent, json_data: str, compact: bool = False):
        try:
            import json
            data = json.loads(json_data)
            if compact:
                formatted = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            else:
                formatted = json.dumps(data, ensure_ascii=False, indent=2)
            await event.reply(f"✅ JSON格式化完成:\n```json\n{formatted}\n````")
        except Exception as e:
            await event.reply(f"❌ JSON格式错误: {e}")

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


