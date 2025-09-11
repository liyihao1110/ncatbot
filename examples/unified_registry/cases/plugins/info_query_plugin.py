from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent


class InfoQueryPlugin(NcatBotPlugin):
    name = "InfoQueryPlugin"
    version = "1.0.0"
    description = "信息查询服务"

    async def on_load(self):
        self.cache = {}

    @command_registry.command("weather", description="查询天气")
    @param(name="units", default="metric", help="温度单位")
    async def weather_cmd(self, event: BaseMessageEvent, city: str, units: str = "metric"):
        cache_key = f"weather_{city}_{units}"
        if cache_key in self.cache:
            await event.reply(f"🌤️ {city} 天气：{self.cache[cache_key]} (来自缓存)")
            return
        weather_data = {
            "北京": "晴天，25°C",
            "上海": "多云，22°C",
            "广州": "小雨，28°C",
            "深圳": "晴天，30°C",
        }
        result = weather_data.get(city, "暂无该城市天气数据")
        self.cache[cache_key] = result
        await event.reply(f"🌤️ {city} 天气：{result}")

    @command_registry.command("translate", description="翻译文本")
    @param(name="target", default="en", help="目标语言")
    async def translate_cmd(self, event: BaseMessageEvent, text: str, target: str = "en"):
        translations = {
            "en": {"你好": "Hello", "谢谢": "Thank you", "再见": "Goodbye"},
            "ja": {"你好": "こんにちは", "谢谢": "ありがとう", "再见": "さようなら"},
        }
        if target not in translations:
            await event.reply("❌ 不支持的目标语言: {target}\n支持的语言: en, ja")
            return
        translated = translations[target].get(text, f"[无法翻译: {text}]")
        await event.reply(f"🌐 翻译结果：\n原文: {text}\n{target.upper()}: {translated}")

    @command_registry.command("search", description="搜索信息")
    @option(short_name="l", long_name="limit", help="限制结果数量")
    async def search_cmd(self, event: BaseMessageEvent, query: str, limit: bool = False):
        search_results = [
            f"📄 关于 '{query}' 的搜索结果1",
            f"📄 关于 '{query}' 的搜索结果2",
            f"📄 关于 '{query}' 的搜索结果3",
            f"📄 关于 '{query}' 的搜索结果4",
            f"📄 关于 '{query}' 的搜索结果5",
        ]
        if limit:
            search_results = search_results[:3]
        await event.reply("🔍 搜索 '" + query + "' 的结果:\n" + "\n".join(search_results))


