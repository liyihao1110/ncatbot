# UnifiedRegistry 实战案例

## 🎯 概述

本文档提供了 UnifiedRegistry 的实际应用案例，从简单的功能插件到复杂的管理系统，帮助您了解如何在真实场景中使用 UnifiedRegistry。

## 🚀 基础应用案例

### 1. 简单问答机器人

```python
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log

LOG = get_log(__name__)

class QABotPlugin(NcatBotPlugin):
    name = "QABotPlugin"
    version = "1.0.0"
    author = "示例作者"
    description = "简单的问答机器人"
    
    async def on_load(self):
        # 预设问答库
        self.qa_database = {
            "你好": "你好！我是问答机器人，有什么可以帮助你的吗？",
            "天气": "抱歉，我还不能查询天气。请使用天气应用或网站。",
            "时间": "请检查你的设备时间，或者使用 /time 命令。",
            "帮助": "可用命令：/ask <问题>、/add_qa <问题> <答案>、/list_qa"
        }

    @command_registry.command("ask", description="询问问题")
    async def ask_cmd(self, event: BaseMessageEvent, question: str):
        """询问问题"""
        # 简单的关键词匹配
        for keyword, answer in self.qa_database.items():
            if keyword in question:
                LOG.info(f"用户 {event.user_id} 询问: {question}")
                await event.reply(f"💡 {answer}")
                return
        
        await event.reply("❓ 抱歉，我不知道这个问题的答案。你可以使用 /add_qa 添加新的问答。")
    
    @command_registry.command("add_qa", description="添加问答")
    async def add_qa_cmd(self, event: BaseMessageEvent, question: str, answer: str):
        """添加新的问答"""
        if len(question) > 100 or len(answer) > 500:
            await event.reply("❌ 问题或答案太长了")
            return
        
        self.qa_database[question] = answer
        LOG.info(f"用户 {event.user_id} 添加问答: {question} -> {answer}")
        await event.reply(f"✅ 已添加问答：\n❓ {question}\n💡 {answer}")
    
    @command_registry.command("list_qa", description="列出所有问答")
    async def list_qa_cmd(self, event: BaseMessageEvent):
        """列出所有问答"""
        if not self.qa_database:
            await event.reply("📝 问答库为空")
            return
        
        qa_list = []
        for i, (q, a) in enumerate(self.qa_database.items(), 1):
            qa_list.append(f"{i}. ❓ {q}\n   💡 {a[:50]}{'...' if len(a) > 50 else ''}")
        
        await event.reply("📚 问答库：\n" + "\n\n".join(qa_list))
    
    @command_registry.command("time", description="获取当前时间")
    async def time_cmd(self, event: BaseMessageEvent):
        """获取当前时间"""
        import datetime
        now = datetime.datetime.now()
        await event.reply(f"🕐 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
```

### 2. 群管理功能插件

```python
from ncatbot.plugin_system import group_only, admin_only

class GroupManagementPlugin(NcatBotPlugin):
    name = "GroupManagementPlugin"
    version = "1.0.0"
    description = "群聊管理功能"

    async def on_load(self):
        self.muted_users = set()
        self.group_settings = {
            "g1": {
                "mute_users": set(),
                "settings": {}
            }
        }

    @group_only
    @admin_only
    @command_registry.command("mute", description="禁言用户")
    @param(name="duration", default=60, help="禁言时长（秒）")
    async def mute_cmd(self, event: BaseMessageEvent, user_id: str, duration: int = 60):
        """禁言指定用户"""
        if duration < 1 or duration > 86400:  # 最多24小时
            await event.reply("❌ 禁言时长必须在1秒到24小时之间")
            return
        
        self.muted_users.add(user_id)
        LOG.info(f"管理员 {event.user_id} 禁言用户 {user_id} {duration}秒")
        
        # 这里应该调用真实的禁言API
        await event.reply(f"🔇 已禁言用户 {user_id}，时长 {duration} 秒")
    
    @group_only
    @admin_only
    @command_registry.command("unmute", description="解除禁言")
    async def unmute_cmd(self, event: BaseMessageEvent, user_id: str):
        """解除用户禁言"""
        if user_id in self.muted_users:
            self.muted_users.remove(user_id)
            LOG.info(f"管理员 {event.user_id} 解除用户 {user_id} 禁言")
            await event.reply(f"🔊 已解除用户 {user_id} 的禁言")
        else:
            await event.reply("❌ 该用户未被禁言")
    
    @group_only
    @admin_only
    @command_registry.command("kick", description="踢出用户")
    @option(short_name="b", long_name="ban", help="同时拉黑用户")
    async def kick_cmd(self, event: BaseMessageEvent, user_id: str, ban: bool = False):
        """踢出群成员"""
        action = "踢出并拉黑" if ban else "踢出"
        LOG.info(f"管理员 {event.user_id} {action}用户 {user_id}")
        
        # 这里应该调用真实的踢人API
        await event.reply(f"👢 已{action}用户 {user_id}")
    
    @group_only
    @command_registry.command("group_info", description="查看群信息")
    async def group_info_cmd(self, event: BaseMessageEvent):
        """查看群信息"""
        group_id = event.group_id
        settings = self.group_settings.get(group_id, {})
        
        info = f"📊 群信息 (ID: {group_id})\n"
        info += f"🔇 禁言用户数: {len(self.muted_users)}\n"
        info += f"⚙️ 特殊设置: {len(settings)} 项"
        
        await event.reply(info)
```

### 3. 信息查询插件

```python
import json
import aiohttp

class InfoQueryPlugin(NcatBotPlugin):
    name = "InfoQueryPlugin"
    version = "1.0.0"
    description = "信息查询服务"
    
    async def on_load(self):
        self.cache = {}

    @command_registry.command("weather", description="查询天气")
    @param(name="units", default="metric", help="温度单位")
    async def weather_cmd(self, event: BaseMessageEvent, city: str, units: str = "metric"):
        """查询城市天气（模拟）"""
        # 检查缓存
        cache_key = f"weather_{city}_{units}"
        if cache_key in self.cache:
            await event.reply(f"🌤️ {city} 天气：{self.cache[cache_key]} (来自缓存)")
            return
        
        # 模拟天气数据
        weather_data = {
            "北京": "晴天，25°C",
            "上海": "多云，22°C", 
            "广州": "小雨，28°C",
            "深圳": "晴天，30°C"
        }
        
        result = weather_data.get(city, "暂无该城市天气数据")
        
        # 存入缓存
        self.cache[cache_key] = result
        
        await event.reply(f"🌤️ {city} 天气：{result}")
    
    @command_registry.command("translate", description="翻译文本")
    @param(name="target", default="en", help="目标语言")
    async def translate_cmd(self, event: BaseMessageEvent, text: str, target: str = "en"):
        """翻译文本（模拟）"""
        # 简单的翻译映射
        translations = {
            "en": {
                "你好": "Hello",
                "谢谢": "Thank you",
                "再见": "Goodbye"
            },
            "ja": {
                "你好": "こんにちは",
                "谢谢": "ありがとう",
                "再见": "さようなら"
            }
        }
        
        if target not in translations:
            await event.reply(f"❌ 不支持的目标语言: {target}\n支持的语言: en, ja")
            return
        
        translated = translations[target].get(text, f"[无法翻译: {text}]")
        await event.reply(f"🌐 翻译结果：\n原文: {text}\n{target.upper()}: {translated}")
    
    @command_registry.command("search", description="搜索信息")
    @option(short_name="l", long_name="limit", help="限制结果数量")
    async def search_cmd(self, event: BaseMessageEvent, query: str, limit: bool = False):
        """搜索信息（模拟）"""
        # 模拟搜索结果
        search_results = [
            f"📄 关于 '{query}' 的搜索结果1",
            f"📄 关于 '{query}' 的搜索结果2", 
            f"📄 关于 '{query}' 的搜索结果3",
            f"📄 关于 '{query}' 的搜索结果4",
            f"📄 关于 '{query}' 的搜索结果5"
        ]
        
        if limit:
            search_results = search_results[:3]
        
        await event.reply(f"🔍 搜索 '{query}' 的结果：\n" + "\n".join(search_results))
```

## 🎮 复杂应用案例

### 1. 数据处理插件

```python
class DataProcessingPlugin(NcatBotPlugin):
    name = "DataProcessingPlugin"
    version = "1.0.0"
    description = "数据处理和分析工具"
    
    async def on_load(self):
        self.datasets = {}
    
    @command_registry.command("text_stats", description="文本统计")
    async def text_stats_cmd(self, event: BaseMessageEvent, text: str):
        """统计文本信息"""
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
```

## 🔗 简单外部API集成

### Web API 集成示例

```python
import aiohttp
import asyncio

class WebAPIPlugin(NcatBotPlugin):
    name = "WebAPIPlugin"
    version = "1.0.0"
    description = "Web API集成示例"
    
    async def on_load(self):
        self.cache = {}

    @command_registry.command("random_quote", description="获取随机名言")
    async def random_quote_cmd(self, event: BaseMessageEvent):
        """获取随机名言（模拟API调用）"""
        # 模拟API响应
        quotes = [
            "生活就像一盒巧克力，你永远不知道下一颗是什么味道。",
            "做你自己，因为其他人都已经被占用了。",
            "昨天是历史，明天是谜团，今天是礼物。",
            "不要因为结束而哭泣，要因为发生过而微笑。"
        ]
        
        import random
        quote = random.choice(quotes)
        await event.reply(f"💭 今日名言：\n{quote}")
    
    @command_registry.command("mock_api", description="模拟API调用")
    @param(name="endpoint", default="users", help="API端点")
    async def mock_api_cmd(self, event: BaseMessageEvent, endpoint: str = "users"):
        """模拟API调用"""
        # 模拟不同的API响应
        mock_responses = {
            "users": {"total": 100, "active": 85},
            "posts": {"total": 500, "today": 12},
            "stats": {"cpu": "45%", "memory": "60%"}
        }
        
        if endpoint not in mock_responses:
            await event.reply(f"❌ 未知的API端点: {endpoint}\n可用端点: {', '.join(mock_responses.keys())}")
            return
        
        data = mock_responses[endpoint]
        await event.reply(f"🌐 API响应 ({endpoint}):\n" + "\n".join([f"{k}: {v}" for k, v in data.items()]))
```

## 🚦 下一步

现在您已经看到了 UnifiedRegistry 的实际应用！接下来可以：

1. **学习测试**: 查看 [测试指南](./UnifiedRegistry-测试指南.md) 确保代码质量
2. **解决问题**: 参考 [常见问题](./UnifiedRegistry-FAQ.md) 处理开发疑问
3. **改进代码**: 回顾 [最佳实践](./UnifiedRegistry-最佳实践.md) 优化实现

---

**💡 提示**: 这些案例展示了 UnifiedRegistry 的灵活性和强大功能。您可以根据自己的需求组合和修改这些模式。
