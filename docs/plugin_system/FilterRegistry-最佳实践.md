# FilterRegistry 最佳实践指南

## 🎯 编程最佳实践

### 1. 插件结构设计

#### 推荐的文件结构

```
plugins/
└── MyPlugin/
    ├── __init__.py
    ├── main.py           # 主插件文件
    ├── config.py         # 配置管理
    ├── utils.py          # 工具函数
    ├── filters.py        # 自定义过滤器
    └── handlers/         # 处理器模块
        ├── __init__.py
        ├── admin.py      # 管理功能
        ├── user.py       # 用户功能
        └── system.py     # 系统功能
```

#### 主插件类设计

```python
from ncatbot.plugin import BasePlugin
from ncatbot.plugin_system.builtin_plugin.filter_registry import filter
from ncatbot.utils import get_log
from .config import PluginConfig
from .filters import *

class MyPlugin(BasePlugin):
    """插件主类 - 遵循单一职责原则"""
    
    name = "MyPlugin"
    version = "1.0.0"
    author = "YourName"
    description = "插件功能描述"
    
    def __init__(self):
        super().__init__()
        self.config = PluginConfig()
        self.log = get_log(self.name)
    
    async def on_load(self):
        """插件加载时的初始化"""
        self.log.info(f"{self.name} v{self.version} 加载成功")
        await super().on_load()
```

### 2. 过滤器设计模式

#### 单一职责过滤器

```python
# ✅ 好的做法 - 每个过滤器只负责一个条件
def is_weekend(event: BaseMessageEvent) -> bool:
    """检查是否是周末"""
    import datetime
    return datetime.datetime.now().weekday() >= 5

def contains_keyword(keyword: str):
    """返回关键词检查过滤器"""
    def filter_func(event: BaseMessageEvent) -> bool:
        return keyword.lower() in event.raw_message.lower()
    return filter_func

# ❌ 避免这样 - 过滤器功能过于复杂
def complex_filter(event: BaseMessageEvent) -> bool:
    """不推荐：功能过于复杂的过滤器"""
    import datetime
    is_weekend = datetime.datetime.now().weekday() >= 5
    has_keyword = 'special' in event.raw_message
    is_long_message = len(event.raw_message) > 50
    user_active = check_user_activity(event.user_id)  # 复杂逻辑
    return is_weekend and has_keyword and is_long_message and user_active
```

#### 可复用过滤器库

```python
# filters.py
"""可复用的过滤器库"""

def time_range_filter(start_hour: int, end_hour: int):
    """时间范围过滤器工厂"""
    def filter_func(event: BaseMessageEvent) -> bool:
        import datetime
        hour = datetime.datetime.now().hour
        return start_hour <= hour <= end_hour
    return filter_func

def message_length_filter(min_length: int = 0, max_length: int = float('inf')):
    """消息长度过滤器工厂"""
    def filter_func(event: BaseMessageEvent) -> bool:
        length = len(event.raw_message)
        return min_length <= length <= max_length
    return filter_func

def regex_filter(pattern: str):
    """正则表达式过滤器工厂"""
    import re
    compiled_pattern = re.compile(pattern)
    
    def filter_func(event: BaseMessageEvent) -> bool:
        return bool(compiled_pattern.search(event.raw_message))
    return filter_func

# 使用示例
@filter.custom(time_range_filter(9, 17))  # 工作时间
@filter.custom(message_length_filter(min_length=10))  # 最少10字符
async def work_hour_handler(self, event: BaseMessageEvent):
    await event.reply("工作时间功能")
```

### 3. 命令设计模式

#### 命令分组策略

```python
class AdminPlugin(BasePlugin):
    """管理功能插件"""
    
    # 创建管理命令组
    admin = filter.command_group("admin")
    
    @admin.command("user")
    async def admin_user(self, event: BaseMessageEvent, action: str, user_id: str):
        """用户管理: admin user ban 123456"""
        if action == "ban":
            await self.ban_user(user_id)
            await event.reply(f"用户 {user_id} 已被封禁")
        elif action == "unban":
            await self.unban_user(user_id)
            await event.reply(f"用户 {user_id} 已解封")
    
    @admin.command("config")
    async def admin_config(self, event: BaseMessageEvent, key: str, value: str = None):
        """配置管理: admin config show / admin config set key value"""
        if value is None:
            # 显示配置
            config_value = await self.get_config(key)
            await event.reply(f"{key} = {config_value}")
        else:
            # 设置配置
            await self.set_config(key, value)
            await event.reply(f"配置已更新: {key} = {value}")
```

#### 参数验证模式

```python
@filter.command("transfer")
async def transfer_money(self, event: BaseMessageEvent, 
                        target_user: str, 
                        amount: float):
    """转账功能 - 包含参数验证"""
    
    # 参数验证
    if amount <= 0:
        await event.reply("❌ 转账金额必须大于0")
        return
    
    if amount > 10000:
        await event.reply("❌ 单次转账不能超过10000")
        return
    
    if target_user == str(event.user_id):
        await event.reply("❌ 不能给自己转账")
        return
    
    # 业务逻辑
    try:
        result = await self.perform_transfer(event.user_id, target_user, amount)
        await event.reply(f"✅ 转账成功！交易ID: {result['transaction_id']}")
    except InsufficientFundsError:
        await event.reply("❌ 余额不足")
    except UserNotFoundError:
        await event.reply("❌ 目标用户不存在")
    except Exception as e:
        self.log.error(f"转账失败: {e}")
        await event.reply("❌ 转账失败，请稍后重试")
```

### 4. 错误处理最佳实践

#### 优雅的异常处理

```python
from ncatbot.utils import get_log

class RobustPlugin(BasePlugin):
    """具有健壮错误处理的插件"""
    
    def __init__(self):
        super().__init__()
        self.log = get_log(self.name)
    
    @filter.command("查询")
    async def query_data(self, event: BaseMessageEvent, query_type: str, query_id: str):
        """数据查询 - 完整错误处理"""
        
        try:
            # 参数验证
            if not query_type in ['user', 'order', 'product']:
                await event.reply("❌ 查询类型错误，支持: user, order, product")
                return
            
            # 业务逻辑
            result = await self.fetch_data(query_type, query_id)
            
            if result is None:
                await event.reply(f"❌ 未找到 {query_type} ID: {query_id}")
                return
            
            # 格式化输出
            formatted_result = self.format_result(result)
            await event.reply(f"✅ 查询结果:\n{formatted_result}")
            
        except NetworkError as e:
            self.log.warning(f"网络错误: {e}")
            await event.reply("❌ 网络连接失败，请稍后重试")
            
        except DatabaseError as e:
            self.log.error(f"数据库错误: {e}")
            await event.reply("❌ 数据服务暂时不可用")
            
        except Exception as e:
            self.log.error(f"查询异常: {e}", exc_info=True)
            await event.reply("❌ 查询失败，已记录错误信息")
```

#### 过滤器异常处理

```python
def safe_database_filter(event: BaseMessageEvent) -> bool:
    """安全的数据库过滤器"""
    try:
        # 可能失败的数据库查询
        user_data = database.get_user(event.user_id)
        return user_data and user_data.is_vip
    except DatabaseConnectionError:
        # 数据库连接失败时，默认不通过过滤器
        LOG.warning(f"数据库连接失败，用户 {event.user_id} 过滤器检查跳过")
        return False
    except Exception as e:
        LOG.error(f"过滤器异常: {e}")
        return False

@filter.custom(safe_database_filter)
async def vip_feature(self, event: BaseMessageEvent):
    """VIP专用功能"""
    await event.reply("欢迎使用VIP功能！✨")
```

### 5. 性能优化建议

#### 缓存机制

```python
from functools import lru_cache
import asyncio

class PerformantPlugin(BasePlugin):
    """高性能插件示例"""
    
    def __init__(self):
        super().__init__()
        self._user_cache = {}
        self._cache_ttl = 300  # 5分钟缓存
    
    @lru_cache(maxsize=1000)
    def get_user_level(self, user_id: str) -> int:
        """缓存用户等级查询"""
        # 模拟数据库查询
        return database.get_user_level(user_id)
    
    async def get_user_data_with_cache(self, user_id: str):
        """带缓存的用户数据获取"""
        import time
        current_time = time.time()
        
        # 检查缓存
        if user_id in self._user_cache:
            cache_data, cache_time = self._user_cache[user_id]
            if current_time - cache_time < self._cache_ttl:
                return cache_data
        
        # 获取新数据
        user_data = await self.fetch_user_data(user_id)
        self._user_cache[user_id] = (user_data, current_time)
        
        return user_data
```

#### 异步操作优化

```python
@filter.command("批量查询")
async def batch_query(self, event: BaseMessageEvent, *user_ids):
    """批量查询用户信息 - 并发优化"""
    
    if len(user_ids) > 10:
        await event.reply("❌ 一次最多查询10个用户")
        return
    
    # 并发查询，而不是串行
    tasks = [self.get_user_info(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    success_results = []
    failed_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_count += 1
            self.log.warning(f"查询用户 {user_ids[i]} 失败: {result}")
        else:
            success_results.append(f"{user_ids[i]}: {result}")
    
    # 回复结果
    if success_results:
        reply = "✅ 查询结果:\n" + "\n".join(success_results)
        if failed_count > 0:
            reply += f"\n\n⚠️ {failed_count} 个查询失败"
    else:
        reply = "❌ 所有查询都失败了"
    
    await event.reply(reply)
```

### 6. 配置管理最佳实践

#### 配置类设计

```python
# config.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml
import os

@dataclass
class PluginConfig:
    """插件配置类"""
    
    # 基础配置
    enabled: bool = True
    debug_mode: bool = False
    
    # 功能配置
    max_query_results: int = 50
    cache_ttl: int = 300
    rate_limit: int = 10  # 每分钟最大请求数
    
    # 权限配置
    admin_users: List[str] = None
    vip_users: List[str] = None
    
    # API配置
    api_endpoints: Dict[str, str] = None
    timeout: int = 30
    
    def __post_init__(self):
        if self.admin_users is None:
            self.admin_users = []
        if self.vip_users is None:
            self.vip_users = []
        if self.api_endpoints is None:
            self.api_endpoints = {}
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'PluginConfig':
        """从文件加载配置"""
        if not os.path.exists(config_path):
            return cls()  # 返回默认配置
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self), f, default_flow_style=False, allow_unicode=True)
```

#### 配置验证

```python
class ConfigurablePlugin(BasePlugin):
    """支持配置的插件"""
    
    def __init__(self):
        super().__init__()
        self.config = PluginConfig.load_from_file("data/MyPlugin/config.yaml")
        self._validate_config()
    
    def _validate_config(self):
        """验证配置的有效性"""
        if self.config.rate_limit <= 0:
            raise ValueError("rate_limit 必须大于 0")
        
        if self.config.cache_ttl < 0:
            raise ValueError("cache_ttl 不能为负数")
        
        # 验证API端点
        for name, endpoint in self.config.api_endpoints.items():
            if not endpoint.startswith(('http://', 'https://')):
                raise ValueError(f"无效的API端点: {name} -> {endpoint}")
    
    @filter.admin_only()
    @filter.command("config")
    async def config_command(self, event: BaseMessageEvent, 
                           action: str, key: str = None, value: str = None):
        """配置管理命令"""
        
        if action == "show":
            if key:
                # 显示特定配置
                if hasattr(self.config, key):
                    val = getattr(self.config, key)
                    await event.reply(f"{key} = {val}")
                else:
                    await event.reply(f"❌ 配置项 {key} 不存在")
            else:
                # 显示所有配置
                config_text = self._format_config()
                await event.reply(f"当前配置:\n{config_text}")
        
        elif action == "set":
            if not key or value is None:
                await event.reply("❌ 用法: config set <key> <value>")
                return
            
            try:
                await self._set_config(key, value)
                await event.reply(f"✅ 配置已更新: {key} = {value}")
            except Exception as e:
                await event.reply(f"❌ 配置更新失败: {e}")
```

### 7. 测试最佳实践

#### 单元测试

```python
import unittest
from unittest.mock import AsyncMock, Mock
from your_plugin import MyPlugin

class TestMyPlugin(unittest.IsolatedAsyncioTestCase):
    """插件单元测试"""
    
    async def asyncSetUp(self):
        """测试设置"""
        self.plugin = MyPlugin()
        self.mock_event = Mock()
        self.mock_event.reply = AsyncMock()
        self.mock_event.user_id = "test_user"
        self.mock_event.raw_message = "test message"
    
    async def test_hello_command(self):
        """测试hello命令"""
        await self.plugin.hello_command(self.mock_event)
        self.mock_event.reply.assert_called_once_with("你好！我是机器人 🤖")
    
    async def test_parameter_parsing(self):
        """测试参数解析"""
        await self.plugin.calculate(self.mock_event, 5, 3)
        self.mock_event.reply.assert_called_once_with("5 + 3 = 8")
    
    def test_custom_filter(self):
        """测试自定义过滤器"""
        from your_plugin.filters import contains_keyword
        
        # 测试匹配情况
        self.mock_event.raw_message = "这是一个测试关键词"
        result = contains_keyword("关键词")(self.mock_event)
        self.assertTrue(result)
        
        # 测试不匹配情况
        self.mock_event.raw_message = "这是一个普通消息"
        result = contains_keyword("关键词")(self.mock_event)
        self.assertFalse(result)
```

#### 集成测试

```python
# 使用项目提供的测试框架
from ncatbot.utils.testing import TestClient, TestHelper

async def test_plugin_integration():
    """插件集成测试"""
    
    client = TestClient()
    helper = TestHelper(client)
    
    # 启动测试环境
    client.start(mock_mode=True)
    
    # 测试命令
    await helper.send_private_message("hello", user_id="test_user")
    helper.assert_reply_sent("你好！我是机器人 🤖")
    
    # 测试权限
    await helper.send_private_message("admin command", user_id="normal_user")
    helper.assert_no_reply()  # 普通用户无权限
    
    # 设置管理员权限
    rbac_manager = client.plugin_loader.rbac_manager
    rbac_manager.assign_role_to_user("admin_user", "admin")
    
    await helper.send_private_message("admin command", user_id="admin_user")
    helper.assert_reply_sent("管理员功能")
```

### 8. 文档和注释规范

#### 函数文档

```python
@filter.command("查询用户")
async def query_user(self, event: BaseMessageEvent, user_id: str, info_type: str = "basic"):
    """查询用户信息
    
    Args:
        event: 消息事件对象
        user_id: 要查询的用户ID
        info_type: 信息类型，可选值: basic, detailed, stats
    
    Returns:
        None: 直接回复消息给用户
    
    Raises:
        UserNotFoundError: 用户不存在时抛出
        PermissionError: 无权限查询时抛出
    
    Examples:
        查询用户 123456          # 查询基础信息
        查询用户 123456 detailed  # 查询详细信息
        查询用户 123456 stats     # 查询统计信息
    """
    # 实现代码...
```

#### 过滤器文档

```python
def business_hours_filter(start: int = 9, end: int = 17):
    """营业时间过滤器工厂函数
    
    创建一个只在指定时间范围内通过的过滤器。
    
    Args:
        start: 开始时间（24小时制）
        end: 结束时间（24小时制）
    
    Returns:
        function: 过滤器函数
    
    Example:
        @filter.custom(business_hours_filter(9, 18))
        async def business_feature(self, event):
            # 只在9:00-18:00之间响应
            pass
    """
    def filter_func(event: BaseMessageEvent) -> bool:
        import datetime
        hour = datetime.datetime.now().hour
        return start <= hour <= end
    
    return filter_func
```

遵循这些最佳实践，可以创建出高质量、可维护、性能优良的机器人插件！
