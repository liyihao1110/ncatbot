# UnifiedRegistry 实战案例

## 🎯 概述

本文档提供了 UnifiedRegistry 的实际应用案例，从简单的功能插件到复杂的管理系统，帮助您了解如何在真实场景中使用 UnifiedRegistry。

## 🚀 基础应用案例

### 1. 简单问答机器人

```python
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log

LOG = get_log(__name__)

class QABotPlugin(NcatBotPlugin):
    name = "QABotPlugin"
    version = "1.0.0"
    author = "示例作者"
    description = "简单的问答机器人"
    
    def __init__(self):
        super().__init__()
        # 预设问答库
        self.qa_database = {
            "你好": "你好！我是问答机器人，有什么可以帮助你的吗？",
            "天气": "抱歉，我还不能查询天气。请使用天气应用或网站。",
            "时间": "请检查你的设备时间，或者使用 /time 命令。",
            "帮助": "可用命令：/ask <问题>、/add_qa <问题> <答案>、/list_qa"
        }
    
    async def on_load(self):
        pass

    @command_registry.command("ask", description="询问问题")
    def ask_cmd(self, event: BaseMessageEvent, question: str):
        """询问问题"""
        # 简单的关键词匹配
        for keyword, answer in self.qa_database.items():
            if keyword in question:
                LOG.info(f"用户 {event.user_id} 询问: {question}")
                return f"💡 {answer}"
        
        return "❓ 抱歉，我不知道这个问题的答案。你可以使用 /add_qa 添加新的问答。"
    
    @command_registry.command("add_qa", description="添加问答")
    def add_qa_cmd(self, event: BaseMessageEvent, question: str, answer: str):
        """添加新的问答"""
        if len(question) > 100 or len(answer) > 500:
            return "❌ 问题或答案太长了"
        
        self.qa_database[question] = answer
        LOG.info(f"用户 {event.user_id} 添加问答: {question} -> {answer}")
        return f"✅ 已添加问答：\n❓ {question}\n💡 {answer}"
    
    @command_registry.command("list_qa", description="列出所有问答")
    def list_qa_cmd(self, event: BaseMessageEvent):
        """列出所有问答"""
        if not self.qa_database:
            return "📝 问答库为空"
        
        qa_list = []
        for i, (q, a) in enumerate(self.qa_database.items(), 1):
            qa_list.append(f"{i}. ❓ {q}\n   💡 {a[:50]}{'...' if len(a) > 50 else ''}")
        
        return "📚 问答库：\n" + "\n\n".join(qa_list)
    
    @command_registry.command("time", description="获取当前时间")
    def time_cmd(self, event: BaseMessageEvent):
        """获取当前时间"""
        import datetime
        now = datetime.datetime.now()
        return f"🕐 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"
```

### 2. 群管理功能插件

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only, admin_only

class GroupManagementPlugin(NcatBotPlugin):
    name = "GroupManagementPlugin"
    version = "1.0.0"
    description = "群聊管理功能"
    
    def __init__(self):
        super().__init__()
        self.muted_users = set()  # 简单的禁言列表
        self.group_settings = {}  # 群设置
    
    async def on_load(self):
        pass

    @group_only
    @admin_only
    @command_registry.command("mute", description="禁言用户")
    @param(name="duration", default=60, help="禁言时长（秒）")
    def mute_cmd(self, event: BaseMessageEvent, user_id: str, duration: int = 60):
        """禁言指定用户"""
        if duration < 1 or duration > 86400:  # 最多24小时
            return "❌ 禁言时长必须在1秒到24小时之间"
        
        self.muted_users.add(user_id)
        LOG.info(f"管理员 {event.user_id} 禁言用户 {user_id} {duration}秒")
        
        # 这里应该调用真实的禁言API
        return f"🔇 已禁言用户 {user_id}，时长 {duration} 秒"
    
    @group_only
    @admin_only
    @command_registry.command("unmute", description="解除禁言")
    def unmute_cmd(self, event: BaseMessageEvent, user_id: str):
        """解除用户禁言"""
        if user_id in self.muted_users:
            self.muted_users.remove(user_id)
            LOG.info(f"管理员 {event.user_id} 解除用户 {user_id} 禁言")
            return f"🔊 已解除用户 {user_id} 的禁言"
        else:
            return "❌ 该用户未被禁言"
    
    @group_only
    @admin_only
    @command_registry.command("kick", description="踢出用户")
    @option(short_name="b", long_name="ban", help="同时拉黑用户")
    def kick_cmd(self, event: BaseMessageEvent, user_id: str, ban: bool = False):
        """踢出群成员"""
        action = "踢出并拉黑" if ban else "踢出"
        LOG.info(f"管理员 {event.user_id} {action}用户 {user_id}")
        
        # 这里应该调用真实的踢人API
        return f"👢 已{action}用户 {user_id}"
    
    @group_only
    @command_registry.command("group_info", description="查看群信息")
    def group_info_cmd(self, event: BaseMessageEvent):
        """查看群信息"""
        group_id = event.group_id
        settings = self.group_settings.get(group_id, {})
        
        info = f"📊 群信息 (ID: {group_id})\n"
        info += f"🔇 禁言用户数: {len(self.muted_users)}\n"
        info += f"⚙️ 特殊设置: {len(settings)} 项"
        
        return info
```

### 3. 信息查询插件

```python
import json
import aiohttp

class InfoQueryPlugin(NcatBotPlugin):
    name = "InfoQueryPlugin"
    version = "1.0.0"
    description = "信息查询服务"
    
    def __init__(self):
        super().__init__()
        self.cache = {}  # 简单缓存
    
    async def on_load(self):
        pass

    @command_registry.command("weather", description="查询天气")
    @param(name="units", default="metric", help="温度单位")
    def weather_cmd(self, event: BaseMessageEvent, city: str, units: str = "metric"):
        """查询城市天气（模拟）"""
        # 检查缓存
        cache_key = f"weather_{city}_{units}"
        if cache_key in self.cache:
            return f"🌤️ {city} 天气：{self.cache[cache_key]} (来自缓存)"
        
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
        
        return f"🌤️ {city} 天气：{result}"
    
    @command_registry.command("translate", description="翻译文本")
    @param(name="target", default="en", help="目标语言")
    def translate_cmd(self, event: BaseMessageEvent, text: str, target: str = "en"):
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
            return f"❌ 不支持的目标语言: {target}\n支持的语言: en, ja"
        
        translated = translations[target].get(text, f"[无法翻译: {text}]")
        return f"🌐 翻译结果：\n原文: {text}\n{target.upper()}: {translated}"
    
    @command_registry.command("search", description="搜索信息")
    @option(short_name="l", long_name="limit", help="限制结果数量")
    def search_cmd(self, event: BaseMessageEvent, query: str, limit: bool = False):
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
        
        return f"🔍 搜索 '{query}' 的结果：\n" + "\n".join(search_results)
```

## 🎮 复杂应用案例

### 1. 多功能管理系统（基于DemoUnified扩展）

```python
class AdvancedManagementPlugin(NcatBotPlugin):
    name = "AdvancedManagementPlugin"
    version = "2.0.0"
    description = "高级管理系统插件"
    
    def __init__(self):
        super().__init__()
        self.user_stats = {}  # 用户统计
        self.system_config = {
            "maintenance_mode": False,
            "rate_limit": 10,
            "max_file_size": 1024 * 1024  # 1MB
        }
        self.operation_history = []  # 操作历史
    
    async def on_load(self):
        # 用户管理子系统
        self._register_user_management()
        # 系统管理子系统
        self._register_system_management() 
        # 统计分析子系统
        self._register_statistics()
        # 数据处理子系统
        self._register_data_processing()
    
    def _register_user_management(self):
        """用户管理功能"""
        user_group = command_registry.group("user", description="用户管理")
        
        @admin_only
        @user_group.command("list", description="列出用户")
        @option(short_name="a", long_name="active", help="只显示活跃用户")
        @param(name="limit", default=10, help="显示数量限制")
        def user_list_cmd(self, event: BaseMessageEvent, limit: int = 10, active: bool = False):
            users = list(self.user_stats.keys())[:limit]
            if active:
                users = [u for u in users if self.user_stats.get(u, {}).get('active', False)]
            
            if not users:
                return "📝 没有找到用户"
            
            user_list = "\n".join([f"👤 {user}" for user in users])
            return f"👥 用户列表 ({len(users)}/{len(self.user_stats)}):\n{user_list}"
        
        @admin_only
        @user_group.command("info", description="查看用户详情")
        def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
            if user_id not in self.user_stats:
                return f"❌ 用户 {user_id} 不存在"
            
            stats = self.user_stats[user_id]
            info = f"👤 用户信息: {user_id}\n"
            info += f"📊 命令使用次数: {stats.get('command_count', 0)}\n"
            info += f"🕐 最后活跃: {stats.get('last_active', '未知')}\n"
            info += f"✅ 状态: {'活跃' if stats.get('active', False) else '非活跃'}"
            
            return info
        
        @admin_only
        @user_group.command("ban", description="封禁用户")
        @param(name="reason", default="违反规定", help="封禁原因")
        def user_ban_cmd(self, event: BaseMessageEvent, user_id: str, reason: str = "违反规定"):
            self._log_operation(event.user_id, f"封禁用户 {user_id}", reason)
            
            if user_id not in self.user_stats:
                self.user_stats[user_id] = {}
            
            self.user_stats[user_id]['banned'] = True
            self.user_stats[user_id]['ban_reason'] = reason
            
            return f"🚫 已封禁用户 {user_id}\n原因: {reason}"
    
    def _register_system_management(self):
        """系统管理功能"""
        system_group = command_registry.group("system", description="系统管理")
        
        @admin_only
        @system_group.command("status", description="系统状态")
        def system_status_cmd(self, event: BaseMessageEvent):
            import psutil
            import datetime
            
            # 获取系统信息
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            status = f"🖥️ 系统状态:\n"
            status += f"💾 CPU 使用率: {cpu_percent}%\n"
            status += f"🧠 内存使用率: {memory.percent}%\n"
            status += f"👥 注册用户: {len(self.user_stats)}\n"
            status += f"📋 操作历史: {len(self.operation_history)}\n"
            status += f"⚙️ 维护模式: {'开启' if self.system_config['maintenance_mode'] else '关闭'}"
            
            return status
        
        @admin_only
        @system_group.command("config", description="系统配置")
        def system_config_cmd(self, event: BaseMessageEvent, key: str, value: str = None):
            if value is None:
                # 查看配置
                if key in self.system_config:
                    return f"⚙️ {key} = {self.system_config[key]}"
                else:
                    return f"❌ 配置项 {key} 不存在"
            else:
                # 设置配置
                old_value = self.system_config.get(key, "未设置")
                
                # 类型转换
                if key in ["rate_limit", "max_file_size"]:
                    try:
                        value = int(value)
                    except ValueError:
                        return f"❌ {key} 必须是数字"
                elif key == "maintenance_mode":
                    value = value.lower() in ["true", "1", "yes", "on"]
                
                self.system_config[key] = value
                self._log_operation(event.user_id, f"修改配置 {key}", f"{old_value} -> {value}")
                
                return f"✅ 配置已更新: {key} = {value}"
        
        @admin_only
        @system_group.command("maintenance", description="维护模式")
        @option(short_name="o", long_name="on", help="开启维护模式")
        @option(short_name="f", long_name="off", help="关闭维护模式")
        def maintenance_cmd(self, event: BaseMessageEvent, on: bool = False, off: bool = False):
            if on and off:
                return "❌ 不能同时开启和关闭维护模式"
            
            if on:
                self.system_config["maintenance_mode"] = True
                self._log_operation(event.user_id, "开启维护模式", "")
                return "🔧 维护模式已开启"
            elif off:
                self.system_config["maintenance_mode"] = False
                self._log_operation(event.user_id, "关闭维护模式", "")
                return "✅ 维护模式已关闭"
            else:
                status = "开启" if self.system_config["maintenance_mode"] else "关闭"
                return f"🔧 当前维护模式: {status}"
    
    def _register_statistics(self):
        """统计分析功能"""
        stats_group = command_registry.group("stats", description="统计分析")
        
        @admin_only
        @stats_group.command("summary", description="统计摘要")
        def stats_summary_cmd(self, event: BaseMessageEvent):
            total_users = len(self.user_stats)
            active_users = sum(1 for stats in self.user_stats.values() if stats.get('active', False))
            banned_users = sum(1 for stats in self.user_stats.values() if stats.get('banned', False))
            total_commands = sum(stats.get('command_count', 0) for stats in self.user_stats.values())
            
            summary = f"📊 统计摘要:\n"
            summary += f"👥 总用户数: {total_users}\n"
            summary += f"✅ 活跃用户: {active_users}\n"
            summary += f"🚫 封禁用户: {banned_users}\n"
            summary += f"⚡ 总命令数: {total_commands}\n"
            summary += f"📝 操作记录: {len(self.operation_history)}"
            
            return summary
        
        @admin_only
        @stats_group.command("top", description="使用排行")
        @param(name="limit", default=5, help="显示数量")
        def stats_top_cmd(self, event: BaseMessageEvent, limit: int = 5):
            # 按命令使用次数排序
            sorted_users = sorted(
                self.user_stats.items(),
                key=lambda x: x[1].get('command_count', 0),
                reverse=True
            )[:limit]
            
            if not sorted_users:
                return "📊 暂无使用数据"
            
            ranking = "🏆 使用排行榜:\n"
            for i, (user_id, stats) in enumerate(sorted_users, 1):
                count = stats.get('command_count', 0)
                ranking += f"{i}. {user_id}: {count} 次\n"
            
            return ranking
    
    def _register_data_processing(self):
        """数据处理功能"""
        data_group = command_registry.group("data", description="数据处理")
        
        @admin_only
        @data_group.command("export", description="导出数据")
        @option_group(choices=["json", "csv"], name="format", default="json", help="导出格式")
        def data_export_cmd(self, event: BaseMessageEvent, data_type: str, format: str = "json"):
            if data_type == "users":
                data = self.user_stats
            elif data_type == "operations":
                data = self.operation_history
            elif data_type == "config":
                data = self.system_config
            else:
                return f"❌ 不支持的数据类型: {data_type}\n支持: users, operations, config"
            
            if format == "json":
                import json
                result = json.dumps(data, ensure_ascii=False, indent=2)
            elif format == "csv":
                # 简化的CSV格式
                if isinstance(data, dict):
                    result = "key,value\n" + "\n".join([f"{k},{v}" for k, v in data.items()])
                else:
                    result = str(data)
            
            # 实际应用中应该生成文件并返回下载链接
            return f"📄 {data_type} 数据 ({format} 格式):\n```\n{result[:500]}{'...' if len(result) > 500 else ''}\n```"
        
        @admin_only
        @data_group.command("cleanup", description="清理数据")
        @option(short_name="f", long_name="force", help="强制清理")
        def data_cleanup_cmd(self, event: BaseMessageEvent, data_type: str, force: bool = False):
            if not force:
                return f"⚠️ 确认清理 {data_type} 数据？使用 --force 参数确认"
            
            if data_type == "history":
                count = len(self.operation_history)
                self.operation_history.clear()
                self._log_operation(event.user_id, f"清理操作历史", f"清理了 {count} 条记录")
                return f"🧹 已清理 {count} 条操作历史"
            elif data_type == "cache":
                # 清理缓存（如果有的话）
                return "🧹 缓存清理完成"
            else:
                return f"❌ 不支持清理的数据类型: {data_type}"
    
    def _log_operation(self, user_id: str, operation: str, details: str):
        """记录操作日志"""
        import datetime
        self.operation_history.append({
            "user_id": user_id,
            "operation": operation,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # 限制历史记录数量
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-500:]  # 保留最新500条
```

### 2. 数据处理插件

```python
class DataProcessingPlugin(NcatBotPlugin):
    name = "DataProcessingPlugin"
    version = "1.0.0"
    description = "数据处理和分析工具"
    
    def __init__(self):
        super().__init__()
        self.datasets = {}  # 存储数据集
    
    async def on_load(self):
        @command_registry.command("csv_analyze", description="分析CSV数据")
        @option(short_name="h", long_name="header", help="包含标题行")
        def csv_analyze_cmd(self, event: BaseMessageEvent, data: str, header: bool = False):
            """分析CSV格式数据"""
            try:
                lines = data.strip().split('\n')
                if header and lines:
                    headers = lines[0].split(',')
                    data_lines = lines[1:]
                else:
                    headers = [f"列{i+1}" for i in range(len(lines[0].split(',')))] if lines else []
                    data_lines = lines
                
                if not data_lines:
                    return "❌ 没有数据行"
                
                # 基础统计
                total_rows = len(data_lines)
                total_cols = len(headers)
                
                analysis = f"📊 CSV数据分析:\n"
                analysis += f"📝 总行数: {total_rows}\n"
                analysis += f"📋 总列数: {total_cols}\n"
                analysis += f"🏷️ 列名: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}"
                
                return analysis
                
            except Exception as e:
                return f"❌ 数据分析失败: {e}"
        
        @command_registry.command("json_format", description="格式化JSON数据")
        @option(short_name="c", long_name="compact", help="紧凑格式")
        def json_format_cmd(self, event: BaseMessageEvent, json_data: str, compact: bool = False):
            """格式化JSON数据"""
            try:
                import json
                data = json.loads(json_data)
                
                if compact:
                    formatted = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                else:
                    formatted = json.dumps(data, ensure_ascii=False, indent=2)
                
                return f"✅ JSON格式化完成:\n```json\n{formatted}\n```"
                
            except json.JSONDecodeError as e:
                return f"❌ JSON格式错误: {e}"
        
        @command_registry.command("text_stats", description="文本统计")
        def text_stats_cmd(self, event: BaseMessageEvent, text: str):
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
            
            return stats
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
        @command_registry.command("random_quote", description="获取随机名言")
        def random_quote_cmd(self, event: BaseMessageEvent):
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
            return f"💭 今日名言：\n{quote}"
        
        @command_registry.command("mock_api", description="模拟API调用")
        @param(name="endpoint", default="users", help="API端点")
        def mock_api_cmd(self, event: BaseMessageEvent, endpoint: str = "users"):
            """模拟API调用"""
            # 模拟不同的API响应
            mock_responses = {
                "users": {"total": 100, "active": 85},
                "posts": {"total": 500, "today": 12},
                "stats": {"cpu": "45%", "memory": "60%"}
            }
            
            if endpoint not in mock_responses:
                return f"❌ 未知的API端点: {endpoint}\n可用端点: {', '.join(mock_responses.keys())}"
            
            data = mock_responses[endpoint]
            return f"🌐 API响应 ({endpoint}):\n" + "\n".join([f"{k}: {v}" for k, v in data.items()])
```

## 🚦 下一步

现在您已经看到了 UnifiedRegistry 的实际应用！接下来可以：

1. **学习测试**: 查看 [测试指南](./UnifiedRegistry-测试指南.md) 确保代码质量
2. **解决问题**: 参考 [常见问题](./UnifiedRegistry-FAQ.md) 处理开发疑问
3. **改进代码**: 回顾 [最佳实践](./UnifiedRegistry-最佳实践.md) 优化实现

---

**💡 提示**: 这些案例展示了 UnifiedRegistry 的灵活性和强大功能。您可以根据自己的需求组合和修改这些模式。
