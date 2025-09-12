# UnifiedRegistry 最佳实践指南

## 🎯 概述

本指南汇集了 UnifiedRegistry 开发中的最佳实践和经验技巧，帮助您编写高质量、可维护的插件代码。

## 🏗️ 代码组织最佳实践

### 1. 插件结构设计

#### ✅ 推荐的插件结构

```python
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import group_only, admin_only
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log

LOG = get_log(__name__)

class WellOrganizedPlugin(NcatBotPlugin):
    name = "WellOrganizedPlugin"
    version = "1.0.0"
    author = "你的名字"
    description = "结构良好的插件示例"
    
    async def on_load(self):
        """插件加载保持轻量"""
        # 初始化插件状态
        self.stats = {"command_count": 0}
        self.config = {"max_users": 100}
        LOG.info(f"正在加载 {self.name} v{self.version}")
        LOG.info(f"{self.name} 加载完成")
    
    @command_registry.command("hello", description="基础问候命令")
    async def hello_cmd(self, event: BaseMessageEvent):
        self.stats["command_count"] += 1
        await event.reply("你好！")
    
    @admin_only
    @command_registry.command("stats", description="查看统计信息")
    async def stats_cmd(self, event: BaseMessageEvent):
        await event.reply(f"命令使用次数: {self.stats['command_count']}")
    
    @command_registry.command("calc", description="简单计算器")
    async def calc_cmd(self, event: BaseMessageEvent, a: int, b: int):
        await event.reply(f"结果: {a + b}")
```

#### ❌ 避免的组织方式

```python
# 不推荐：所有代码挤在 on_load 中
class PoorlyOrganizedPlugin(NcatBotPlugin):
    async def on_load(self):
        
        @command_registry.command("cmd1")
        def cmd1(self, event: BaseMessageEvent):
            # 复杂逻辑直接写在这里
            pass
        
        @command_registry.command("cmd2") 
        def cmd2(self, event: BaseMessageEvent):
            # 更多复杂逻辑
            pass
        
        # ... 50个命令都挤在这里
```

### 2. 命令命名规范

#### ✅ 清晰的命名方式

```python
class NamingBestPractices(NcatBotPlugin):
    async def on_load(self):
        pass

    # 动词+名词格式，语义清晰
    @command_registry.command("create_user", description="创建新用户")
    async def create_user_cmd(self, event: BaseMessageEvent, username: str):
        await event.reply(f"创建用户: {username}")
    
    @command_registry.command("delete_user", description="删除用户")
    async def delete_user_cmd(self, event: BaseMessageEvent, username: str):
        await event.reply(f"删除用户: {username}")
    
    @command_registry.command("list_users", description="列出所有用户")
    async def list_users_cmd(self, event: BaseMessageEvent):
        await event.reply("用户列表: ...")
    
    # 使用别名提供简短版本
    @command_registry.command("get_info", aliases=["info", "i"], description="获取信息")
    async def get_info_cmd(self, event: BaseMessageEvent):
        await event.reply("系统信息: ...")
```

#### ❌ 避免的命名方式

```python
# 不推荐：模糊、缩写、无意义的命名
@command_registry.command("usr")  # 不清楚是什么操作
@command_registry.command("do_something")  # 太泛泛
@command_registry.command("cmd1")  # 无意义
```

### 3. 过滤器复用策略

#### ✅ 智能的过滤器组合

```python
class FilterReuseExample(NcatBotPlugin):
    async def on_load(self):
        # 为相关命令使用相同的过滤器组合
        self._register_user_management()
        self._register_system_management()
    
    def _register_user_management(self):
        # 注意这里的命令属于类外命令，无法进行 self 传参
        """用户管理命令（管理员+群聊）"""
        @admin_only
        @group_only
        @command_registry.command("ban_user")
        async def ban_user_cmd(event: BaseMessageEvent, user_id: str):
            await event.reply(f"封禁用户: {user_id}")
            
        
        @admin_only
        @group_only
        @command_registry.command("unban_user")
        async def unban_user_cmd(event: BaseMessageEvent, user_id: str):
            await event.reply(f"解封用户: {user_id}")
    
    def _register_system_management(self):
        """系统管理命令（仅管理员）"""
        @admin_only
        @command_registry.command("system_status")
        async def system_status_cmd(event: BaseMessageEvent):
            await event.reply("系统状态正常")
        
        @admin_only
        @command_registry.command("restart_service")
        async def restart_service_cmd(event: BaseMessageEvent, service: str):
            await event.reply(f"重启服务: {service}")
```

## 📝 代码质量提升

### 1. 函数设计原则

#### ✅ 单一职责原则

```python
class SingleResponsibilityExample(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("user_info")
    async def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
        """获取用户信息（职责单一）"""
        user_data = self._get_user_data(user_id)
        if not user_data:
            await event.reply("❌ 用户不存在")
        
        formatted_info = self._format_user_info(user_data)
        await event.reply(formatted_info)
    
    def _get_user_data(self, user_id: str) -> dict:
        """获取用户数据（单一职责）"""
        # 只负责数据获取
        return {"id": user_id, "name": "测试用户", "level": 5}
    
    def _format_user_info(self, user_data: dict) -> str:
        """格式化用户信息（单一职责）"""
        # 只负责格式化显示
        return f"用户信息:\n👤 ID: {user_data['id']}\n📝 名称: {user_data['name']}\n⭐ 等级: {user_data['level']}"
```

### 2. 状态管理

#### ✅ 良好的状态管理

```python
class StateManagementExample(NcatBotPlugin):
        
    
    async def on_load(self):
        self.user_sessions = {}
        self.command_stats = {}
        self.config = {
            "max_session_time": 3600,
            "rate_limit": 10
        }

    @command_registry.command("start_session")
    async def start_session_cmd(self, event: BaseMessageEvent):
        """开始用户会话"""
        user_id = event.user_id
        
        # 检查现有会话
        if user_id in self.user_sessions:
            await event.reply("❌ 您已有活跃会话，请先结束当前会话")
        
        # 创建新会话
        import time
        self.user_sessions[user_id] = {
            "start_time": time.time(),
            "operations": 0
        }
        
        await event.reply("✅ 会话已开始")
    
    @command_registry.command("end_session")
    async def end_session_cmd(self, event: BaseMessageEvent):
        """结束用户会话"""
        user_id = event.user_id
        
        if user_id not in self.user_sessions:
            await event.reply("❌ 您没有活跃的会话")
        
        # 清理会话
        session = self.user_sessions.pop(user_id)
        import time
        duration = time.time() - session["start_time"]
        
        await event.reply(f"✅ 会话已结束\n⏱️ 持续时间: {duration:.1f}秒\n📊 操作次数: {session['operations']}")
```

## 📋 装饰器使用规范

### 1. 装饰器顺序

#### ✅ 正确的装饰器顺序

```python
class DecoratorOrderExample(NcatBotPlugin):
    async def on_load(self):
        pass

    # 正确顺序：过滤器 → 命令注册 → 参数装饰器
    @admin_only                           # 1. 过滤器在最上面
    @group_only                          # 2. 多个过滤器可以堆叠
    @command_registry.command("deploy")  # 3. 命令注册器
    @option("v", "verbose")              # 4. 选项装饰器
    @param("env", default="dev")         # 5. 参数装饰器
    def deploy_cmd(self, event: BaseMessageEvent, app: str, 
                    env: str = "dev", verbose: bool = False):
        await event.reply(f"部署 {app} 到 {env}")
```

### 2. 参数命名一致性

#### ✅ 一致的参数命名

```python
class ConsistentNamingExample(NcatBotPlugin):
    async def on_load(self):
        pass

    # 在整个插件中保持一致的参数命名，否则会报错
    @command_registry.command("create_item")
    @param("category", default="default", help="物品分类")
    async def create_item_cmd(self, event: BaseMessageEvent, name: str, category: str = "default"):
        await event.reply(f"创建物品: {name} (分类: {category})")
    
    @command_registry.command("delete_item")
    @param("category", default="default", help="物品分类")  # 相同参数使用相同名称
    async def delete_item_cmd(self, event: BaseMessageEvent, name: str, category: str = "default"):
        await event.reply(f"删除物品: {name} (分类: {category})")
```

## 🚦 下一步

掌握最佳实践后，您可以：

1. **查看实例**: 阅读 [实战案例](./UnifiedRegistry-实战案例.md) 看到这些实践的应用
2. **测试代码**: 参考 [测试指南](./UnifiedRegistry-测试指南.md) 确保代码质量
3. **解决问题**: 查看 [常见问题](./UnifiedRegistry-FAQ.md) 处理开发中的疑问

---

**💡 总结**: 好的代码不仅要功能正确，还要易读、易维护、易扩展。遵循这些最佳实践可以显著提升代码质量和开发效率。
