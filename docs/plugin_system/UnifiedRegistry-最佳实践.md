# UnifiedRegistry 最佳实践指南

## 🎯 概述

本指南汇集了 UnifiedRegistry 开发中的最佳实践和经验技巧，帮助您编写高质量、可维护的插件代码。

## 🏗️ 代码组织最佳实践

### 1. 插件结构设计

#### ✅ 推荐的插件结构

```python
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only, admin_only
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log

LOG = get_log(__name__)

class WellOrganizedPlugin(NcatBotPlugin):
    name = "WellOrganizedPlugin"
    version = "1.0.0"
    author = "你的名字"
    description = "结构良好的插件示例"
    
    def __init__(self):
        super().__init__()
        # 初始化插件状态
        self.stats = {"command_count": 0}
        self.config = {"max_users": 100}
    
    async def on_load(self):
        """插件加载保持轻量"""
        LOG.info(f"正在加载 {self.name} v{self.version}")
        LOG.info(f"{self.name} 加载完成")
    
    @command_registry.command("hello", description="基础问候命令")
    def hello_cmd(self, event: BaseMessageEvent):
        self.stats["command_count"] += 1
        return "你好！"
    
    @admin_only
    @command_registry.command("stats", description="查看统计信息")
    def stats_cmd(self, event: BaseMessageEvent):
        return f"命令使用次数: {self.stats['command_count']}"
    
    @command_registry.command("calc", description="简单计算器")
    def calc_cmd(self, event: BaseMessageEvent, a: int, b: int):
        return f"结果: {a + b}"
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
        # 动词+名词格式，语义清晰
        @command_registry.command("create_user", description="创建新用户")
        def create_user_cmd(self, event: BaseMessageEvent, username: str):
            return f"创建用户: {username}"
        
        @command_registry.command("delete_user", description="删除用户")
        def delete_user_cmd(self, event: BaseMessageEvent, username: str):
            return f"删除用户: {username}"
        
        @command_registry.command("list_users", description="列出所有用户")
        def list_users_cmd(self, event: BaseMessageEvent):
            return "用户列表: ..."
        
        # 使用别名提供简短版本
        @command_registry.command("get_info", aliases=["info", "i"], description="获取信息")
        def get_info_cmd(self, event: BaseMessageEvent):
            return "系统信息: ..."
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
        """用户管理命令（管理员+群聊）"""
        @admin_only
        @group_only
        @command_registry.command("ban_user")
        def ban_user_cmd(self, event: BaseMessageEvent, user_id: str):
            return f"封禁用户: {user_id}"
        
        @admin_only
        @group_only
        @command_registry.command("unban_user")
        def unban_user_cmd(self, event: BaseMessageEvent, user_id: str):
            return f"解封用户: {user_id}"
    
    def _register_system_management(self):
        """系统管理命令（仅管理员）"""
        @admin_only
        @command_registry.command("system_status")
        def system_status_cmd(self, event: BaseMessageEvent):
            return "系统状态正常"
        
        @admin_only
        @command_registry.command("restart_service")
        def restart_service_cmd(self, event: BaseMessageEvent, service: str):
            return f"重启服务: {service}"
```

## 🛡️ 错误处理模式

### 1. 参数验证

#### ✅ 完善的参数验证

```python
class ParameterValidationExample(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("set_age")
        def set_age_cmd(self, event: BaseMessageEvent, age: int):
            """设置年龄（带验证）"""
            # 输入验证
            if age < 0:
                return "❌ 年龄不能为负数"
            if age > 150:
                return "❌ 年龄不能超过150岁"
            
            # 业务逻辑
            return f"✅ 年龄设置为: {age}"
        
        @command_registry.command("divide")
        def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
            """除法运算（带错误处理）"""
            if b == 0:
                return "❌ 错误: 除数不能为0"
            
            result = a / b
            return f"✅ {a} ÷ {b} = {result}"
        
        @command_registry.command("create_group")
        def create_group_cmd(self, event: BaseMessageEvent, name: str):
            """创建群组（带输入验证）"""
            # 清理和验证输入
            name = name.strip()
            if not name:
                return "❌ 群组名称不能为空"
            if len(name) > 50:
                return "❌ 群组名称不能超过50个字符"
            if any(char in name for char in ['<', '>', '&', '"']):
                return "❌ 群组名称包含非法字符"
            
            return f"✅ 创建群组: {name}"
```

### 2. 异常处理模式

#### ✅ 优雅的异常处理

```python
class ExceptionHandlingExample(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("safe_operation")
        def safe_operation_cmd(self, event: BaseMessageEvent, data: str):
            """安全操作示例"""
            try:
                # 可能出错的操作
                result = self.process_data(data)
                return f"✅ 处理成功: {result}"
            
            except ValueError as e:
                LOG.warning(f"参数错误: {e}")
                return f"❌ 参数错误: 请检查输入格式"
            
            except FileNotFoundError:
                LOG.error(f"文件未找到: {data}")
                return "❌ 找不到指定的文件"
            
            except Exception as e:
                LOG.error(f"未知错误: {e}")
                return "❌ 操作失败，请稍后重试"
    
    def process_data(self, data: str):
        """模拟可能出错的数据处理"""
        if data == "error":
            raise ValueError("测试错误")
        return f"processed_{data}"
```

### 3. 用户友好的错误提示

#### ✅ 清晰的错误信息

```python
class UserFriendlyErrorsExample(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("transfer")
        @param(name="amount", help="转账金额")
        def transfer_cmd(self, event: BaseMessageEvent, to_user: str, amount: float):
            """转账命令（用户友好的错误提示）"""
            # 验证金额
            if amount <= 0:
                return "❌ 转账金额必须大于0\n💡 示例: /transfer @用户 100.5"
            
            if amount > 10000:
                return "❌ 单次转账不能超过10,000\n💡 如需大额转账，请联系管理员"
            
            # 验证目标用户
            if to_user == event.user_id:
                return "❌ 不能向自己转账\n💡 请选择其他用户"
            
            # 模拟余额检查
            user_balance = self.get_user_balance(event.user_id)
            if user_balance < amount:
                return f"❌ 余额不足\n💰 当前余额: {user_balance}\n💡 请充值后再试"
            
            return f"✅ 转账成功\n👤 收款人: {to_user}\n💰 金额: {amount}"
    
    def get_user_balance(self, user_id: str) -> float:
        """获取用户余额（示例）"""
        return 1000.0  # 模拟余额
```

## 📝 代码质量提升

### 1. 函数设计原则

#### ✅ 单一职责原则

```python
class SingleResponsibilityExample(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("user_info")
        def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
            """获取用户信息（职责单一）"""
            user_data = self._get_user_data(user_id)
            if not user_data:
                return "❌ 用户不存在"
            
            formatted_info = self._format_user_info(user_data)
            return formatted_info
    
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
    def __init__(self):
        super().__init__()
        # 在构造函数中初始化状态
        self.user_sessions = {}
        self.command_stats = {}
        self.config = {
            "max_session_time": 3600,
            "rate_limit": 10
        }
    
    async def on_load(self):
        @command_registry.command("start_session")
        def start_session_cmd(self, event: BaseMessageEvent):
            """开始用户会话"""
            user_id = event.user_id
            
            # 检查现有会话
            if user_id in self.user_sessions:
                return "❌ 您已有活跃会话，请先结束当前会话"
            
            # 创建新会话
            import time
            self.user_sessions[user_id] = {
                "start_time": time.time(),
                "operations": 0
            }
            
            return "✅ 会话已开始"
        
        @command_registry.command("end_session")
        def end_session_cmd(self, event: BaseMessageEvent):
            """结束用户会话"""
            user_id = event.user_id
            
            if user_id not in self.user_sessions:
                return "❌ 您没有活跃的会话"
            
            # 清理会话
            session = self.user_sessions.pop(user_id)
            import time
            duration = time.time() - session["start_time"]
            
            return f"✅ 会话已结束\n⏱️ 持续时间: {duration:.1f}秒\n📊 操作次数: {session['operations']}"
```

### 3. 日志记录最佳实践

#### ✅ 合理的日志记录

```python
from ncatbot.utils import get_log

LOG = get_log(__name__)

class LoggingBestPracticesExample(NcatBotPlugin):
    async def on_load(self):
        @command_registry.command("important_operation")
        def important_operation_cmd(self, event: BaseMessageEvent, action: str):
            """重要操作（带完整日志）"""
            user_id = event.user_id
            
            # 记录操作开始
            LOG.info(f"用户 {user_id} 开始执行操作: {action}")
            
            try:
                # 执行操作
                result = self._perform_operation(action)
                
                # 记录成功
                LOG.info(f"用户 {user_id} 成功执行操作 {action}: {result}")
                return f"✅ 操作成功: {result}"
                
            except Exception as e:
                # 记录错误（包含足够的上下文）
                LOG.error(f"用户 {user_id} 执行操作 {action} 失败: {e}", exc_info=True)
                return "❌ 操作失败，请稍后重试"
    
    def _perform_operation(self, action: str):
        """执行具体操作"""
        if action == "test":
            LOG.debug("执行测试操作")  # 调试信息
            return "测试完成"
        else:
            raise ValueError(f"未知操作: {action}")
```

## 📋 装饰器使用规范

### 1. 装饰器顺序

#### ✅ 正确的装饰器顺序

```python
class DecoratorOrderExample(NcatBotPlugin):
    async def on_load(self):
        # 正确顺序：过滤器 → 命令注册 → 参数装饰器
        @admin_only                           # 1. 过滤器在最上面
        @group_only                          # 2. 多个过滤器可以堆叠
        @command_registry.command("deploy")  # 3. 命令注册器
        @option("v", "verbose")              # 4. 选项装饰器
        @param("env", default="dev")         # 5. 参数装饰器
        def deploy_cmd(self, event: BaseMessageEvent, app: str, 
                       env: str = "dev", verbose: bool = False):
            return f"部署 {app} 到 {env}"
```

### 2. 参数命名一致性

#### ✅ 一致的参数命名

```python
class ConsistentNamingExample(NcatBotPlugin):
    async def on_load(self):
        # 在整个插件中保持一致的参数命名
        @command_registry.command("create_item")
        @param("category", default="default", help="物品分类")
        def create_item_cmd(self, event: BaseMessageEvent, name: str, category: str = "default"):
            return f"创建物品: {name} (分类: {category})"
        
        @command_registry.command("delete_item")
        @param("category", default="default", help="物品分类")  # 相同参数使用相同名称
        def delete_item_cmd(self, event: BaseMessageEvent, name: str, category: str = "default"):
            return f"删除物品: {name} (分类: {category})"
```

## 🔧 常用开发模式

### 1. 配置管理模式

```python
class ConfigManagementExample(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        # 集中管理配置
        self.config = {
            "max_retries": 3,
            "timeout": 30,
            "rate_limits": {
                "per_user": 10,
                "per_minute": 100
            }
        }
    
    async def on_load(self):
        @admin_only
        @command_registry.command("config")
        @param("value", help="配置值")
        def config_cmd(self, event: BaseMessageEvent, key: str, value: str = None):
            """配置管理命令"""
            if value is None:
                # 查看配置
                if key in self.config:
                    return f"配置 {key} = {self.config[key]}"
                else:
                    return f"❌ 配置项 {key} 不存在"
            else:
                # 设置配置
                old_value = self.config.get(key, "未设置")
                self.config[key] = value
                return f"✅ 配置已更新: {key} = {value} (原值: {old_value})"
```

### 2. 缓存模式

```python
class CachingPatternExample(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_ttl = 300  # 5分钟过期
    
    async def on_load(self):
        @command_registry.command("expensive_query")
        def expensive_query_cmd(self, event: BaseMessageEvent, query: str):
            """昂贵查询操作（带缓存）"""
            # 检查缓存
            cached_result = self._get_cached_result(query)
            if cached_result:
                return f"📋 缓存结果: {cached_result}"
            
            # 执行昂贵操作
            result = self._perform_expensive_operation(query)
            
            # 存入缓存
            self._cache_result(query, result)
            
            return f"🆕 新结果: {result}"
    
    def _get_cached_result(self, key: str):
        """获取缓存结果"""
        import time
        if key in self.cache:
            cached_data = self.cache[key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["result"]
            else:
                # 缓存过期，删除
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, result: str):
        """缓存结果"""
        import time
        self.cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def _perform_expensive_operation(self, query: str) -> str:
        """模拟昂贵操作"""
        import time
        time.sleep(0.1)  # 模拟耗时操作
        return f"processed_{query}"
```

## 📚 代码复用技巧

### 1. 通用工具方法

```python
class UtilityMethodsExample(NcatBotPlugin):
    def __init__(self):
        super().__init__()
    
    async def on_load(self):
        @command_registry.command("format_data")
        def format_data_cmd(self, event: BaseMessageEvent, data: str):
            """格式化数据显示"""
            formatted = self._format_with_emoji(data)
            return formatted
        
        @command_registry.command("validate_input")
        def validate_input_cmd(self, event: BaseMessageEvent, input_data: str):
            """验证输入数据"""
            if not self._is_valid_input(input_data):
                return "❌ 输入格式无效"
            return "✅ 输入格式正确"
    
    def _format_with_emoji(self, text: str) -> str:
        """通用格式化方法"""
        return f"📝 {text}"
    
    def _is_valid_input(self, data: str) -> bool:
        """通用验证方法"""
        return len(data) > 0 and len(data) < 100
    
    def _log_user_action(self, user_id: str, action: str):
        """通用日志记录"""
        LOG.info(f"用户 {user_id} 执行操作: {action}")
```

## 🚦 下一步

掌握最佳实践后，您可以：

1. **查看实例**: 阅读 [实战案例](./UnifiedRegistry-实战案例.md) 看到这些实践的应用
2. **测试代码**: 参考 [测试指南](./UnifiedRegistry-测试指南.md) 确保代码质量
3. **解决问题**: 查看 [常见问题](./UnifiedRegistry-FAQ.md) 处理开发中的疑问

---

**💡 总结**: 好的代码不仅要功能正确，还要易读、易维护、易扩展。遵循这些最佳实践可以显著提升代码质量和开发效率。
