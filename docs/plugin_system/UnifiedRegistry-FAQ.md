# UnifiedRegistry 常见问题解答

## ❓ 基础使用问题

### Q1: 为什么我的命令函数参数必须有类型注解？

**A:** UnifiedRegistry 的命令系统依赖类型注解来进行自动类型转换和参数验证。除了 `self` 参数外，所有其他参数都必须有类型注解。

```python
# ❌ 错误：缺少类型注解

@command_registry.command("bad")
def bad_cmd(self, event, text):  # 缺少类型注解
    return text

# ✅ 正确：完整的类型注解
@command_registry.command("good")
def good_cmd(self, event: BaseMessageEvent, text: str):
    return text
```

### Q2: 装饰器的顺序有什么要求？

**A:** 装饰器必须按特定顺序使用：

1. 过滤器装饰器（如 `@admin_only`, `@group_only`）
2. 命令注册装饰器（`@command_registry.command()`）
3. 参数装饰器（`@option`, `@param`）

```python
# ✅ 正确的顺序
@admin_only                    # 1. 过滤器
@command_registry.command("deploy")  # 2. 命令注册
@option("v", "verbose")        # 3. 参数装饰器
def deploy_cmd(self, event: BaseMessageEvent, verbose: bool = False):
    return "部署完成"

# ❌ 错误的顺序
@command_registry.command("wrong")
@admin_only  # 过滤器应该在命令注册之前
def wrong_cmd(self, event: BaseMessageEvent):
    return "错误"
```

### Q3: 如何在命令中访问插件的属性和方法？

**A:** 使用 `self` 参数可以访问插件实例的所有属性和方法：

```python
class MyPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.config = {"max_users": 100}
    
    async def on_load(self):
        @command_registry.command("count")
        def count_cmd(self, event: BaseMessageEvent):
            self.counter += 1  # 访问插件属性
            return f"计数: {self.counter}"
        
        @command_registry.command("reset")
        def reset_cmd(self, event: BaseMessageEvent):
            self._reset_counter()  # 调用插件方法
            return "计数已重置"
    
    def _reset_counter(self):
        """插件的私有方法"""
        self.counter = 0
```

## 🔧 命令注册问题

### Q4: 为什么我的命令没有被注册？

**A:** 检查以下几个常见原因：

1. **函数没有标记为命令**：确保添加了 `__is_command__` 标记
```python
@command_registry.command("test")
def test_cmd(self, event: BaseMessageEvent):
    return "测试"
# 装饰器会自动添加 test_cmd.__is_command__ = True
```

2. **插件没有正确加载**：确保插件在 `on_load` 中注册命令
```python
async def on_load(self):
    # 保持轻量
    pass

@command_registry.command("hello")
def hello_cmd(self, event: BaseMessageEvent):
    return "Hello"
```

3. **命令名称冲突**：检查是否有重复的命令名或别名

### Q5: 如何处理命令参数的默认值？

**A:** 在函数签名中直接设置默认值：

```python
@command_registry.command("greet")
def greet_cmd(self, event: BaseMessageEvent, name: str = "朋友"):
    return f"你好，{name}！"

# 使用方式：
# /greet          -> "你好，朋友！"
# /greet 小明     -> "你好，小明！"
```

对于命名参数，使用 `@param` 装饰器：

```python
@command_registry.command("deploy")
@param(name="env", default="dev", help="部署环境")
def deploy_cmd(self, event: BaseMessageEvent, app: str, env: str = "dev"):
    return f"部署 {app} 到 {env} 环境"

# 使用方式：
# /deploy myapp              -> "部署 myapp 到 dev 环境"
# /deploy myapp --env=prod   -> "部署 myapp 到 prod 环境"
```

### Q6: 命令别名不工作怎么办？

**A:** 确保别名格式正确：

```python
# ✅ 正确的别名设置
@command_registry.command("status", aliases=["stat", "st"])
def status_cmd(self, event: BaseMessageEvent):
    return "状态正常"

# ❌ 常见错误
@command_registry.command("status", aliases="stat")  # 应该是列表
```

## 🛡️ 过滤器问题

### Q7: 过滤器不生效怎么办？

**A:** 检查以下几点：

1. **装饰器顺序**：过滤器装饰器必须在命令装饰器之前
2. **权限配置**：确保权限管理系统已正确配置
3. **过滤器逻辑**：检查自定义过滤器的返回值

```python
# 调试过滤器
def debug_filter(event: BaseMessageEvent) -> bool:
    result = your_filter_logic(event)
    LOG.debug(f"过滤器结果: {result} for user {event.user_id}")
    return result
```

### Q8: 如何创建复杂的权限控制？

**A:** 组合多个过滤器或创建自定义过滤器：

```python
# 方法1: 组合现有过滤器
@admin_only
@group_only
@command_registry.command("admin_group_cmd")
def admin_group_cmd(self, event: BaseMessageEvent):
    return "管理员群聊命令"

# 方法2: 自定义过滤器
class VipFilter(BaseFilter):
    def __init__(self, min_level: int = 5):
        super().__init__(f"vip_level_{min_level}")
        self.min_level = min_level
    
    def check(self, event: BaseMessageEvent) -> bool:
        user_level = self.get_user_level(event.user_id)
        return user_level >= self.min_level

@command_registry.command("vip_cmd")
def vip_cmd(self, event: BaseMessageEvent):
    return "VIP功能"

# 添加自定义过滤器
filter_registry.add_filter_to_function(vip_cmd, VipFilter(min_level=10))
```

### Q9: 过滤器错误如何调试？

**A:** 启用调试日志并检查过滤器执行：

```python
from ncatbot.utils import get_log
LOG = get_log(__name__)

def my_filter(event: BaseMessageEvent) -> bool:
    try:
        result = complex_check(event)
        LOG.debug(f"过滤器检查结果: {result}")
        return result
    except Exception as e:
        LOG.error(f"过滤器执行错误: {e}")
        return False  # 出错时的默认行为
```

## 🔄 参数解析问题

### Q10: 参数类型转换失败怎么办？

**A:** 提供错误处理和用户友好的提示：

```python
@command_registry.command("safe_calc")
def safe_calc_cmd(self, event: BaseMessageEvent, a: str, b: str):
    """安全的计算命令，手动处理类型转换"""
    try:
        num_a = float(a)
        num_b = float(b)
        result = num_a + num_b
        return f"结果: {result}"
    except ValueError:
        return f"❌ 参数错误: '{a}' 或 '{b}' 不是有效数字\n💡 请输入数字，例如: /safe_calc 1.5 2.3"
```

### Q11: 如何处理包含空格的参数？

**A:** 使用引号包围参数：

```python
@command_registry.command("say")
def say_cmd(self, event: BaseMessageEvent, message: str):
    return f"机器人说: {message}"

# 使用方式：
# /say "hello world"           -> "机器人说: hello world"
# /say '包含 空格 的 消息'      -> "机器人说: 包含 空格 的 消息"
```

### Q12: 选项和参数的区别是什么？

**A:** 

- **选项** (`@option`): 布尔标志，开启或关闭某个功能
- **参数** (`@param`): 有具体值的配置项

```python
@command_registry.command("backup")
@option(short_name="v", long_name="verbose", help="详细输出")  # 布尔选项
@param(name="path", default="/backup", help="备份路径")        # 有值的参数
def backup_cmd(self, event: BaseMessageEvent, 
               path: str = "/backup", verbose: bool = False):
    result = f"备份到 {path}"
    if verbose:
        result += " (详细模式)"
    return result

# 使用方式：
# /backup                      -> "备份到 /backup"
# /backup --verbose            -> "备份到 /backup (详细模式)"
# /backup --path=/data         -> "备份到 /data"
# /backup --path=/data -v      -> "备份到 /data (详细模式)"
```

## 🐛 错误处理问题

### Q13: 如何提供用户友好的错误信息？

**A:** 使用清晰的错误格式和建议：

```python
@command_registry.command("divide")
def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
    # 参数验证
    if b == 0:
        return "❌ 错误: 除数不能为0\n💡 请确保第二个数字不是0"
    
    try:
        result = a / b
        return f"✅ {a} ÷ {b} = {result}"
    except Exception as e:
        return f"❌ 计算失败\n🔧 详细错误: {e}\n💡 请检查输入的数字格式"
```

### Q14: 如何记录和调试错误？

**A:** 使用日志系统记录详细信息：

```python
from ncatbot.utils import get_log
LOG = get_log(__name__)

@command_registry.command("complex_operation")
def complex_operation_cmd(self, event: BaseMessageEvent, data: str):
    user_id = event.user_id
    LOG.info(f"用户 {user_id} 开始复杂操作: {data}")
    
    try:
        result = self.process_complex_data(data)
        LOG.info(f"用户 {user_id} 操作成功: {result}")
        return f"✅ 操作完成: {result}"
    
    except ValueError as e:
        LOG.warning(f"用户 {user_id} 输入错误: {e}")
        return f"❌ 输入错误: {e}\n💡 请检查输入格式"
    
    except Exception as e:
        LOG.error(f"用户 {user_id} 操作失败: {e}", exc_info=True)
        return "❌ 系统错误，请稍后重试"
```

## 🔧 开发和调试

### Q15: 如何调试插件的命令注册？

**A:** 查看注册状态和冲突：

```python
async def on_load(self):
    # 注册命令
    @command_registry.command("debug_test")
    def debug_test_cmd(self, event: BaseMessageEvent):
        return "调试测试"
    
    # 检查注册状态
    all_commands = command_registry.get_all_commands()
    LOG.debug(f"已注册的命令: {list(all_commands.keys())}")
    
    # 检查是否成功注册
    if ("debug_test",) in all_commands:
        LOG.info("debug_test 命令注册成功")
    else:
        LOG.error("debug_test 命令注册失败")
```

### Q16: 插件间如何共享数据？

**A:** 使用插件系统的依赖机制：

```python
class DataProviderPlugin(NcatBotPlugin):
    name = "DataProviderPlugin"
    
    def __init__(self):
        super().__init__()
        self.shared_data = {"global_count": 0}
    
    def get_data(self, key: str):
        return self.shared_data.get(key)
    
    def set_data(self, key: str, value):
        self.shared_data[key] = value

class DataConsumerPlugin(NcatBotPlugin):
    name = "DataConsumerPlugin"
    dependencies = {"DataProviderPlugin": ">=1.0.0"}
    
    async def on_load(self):
        @command_registry.command("get_global")
        def get_global_cmd(self, event: BaseMessageEvent):
            provider = self.get_plugin("DataProviderPlugin")
            if provider:
                count = provider.get_data("global_count")
                return f"全局计数: {count}"
            return "数据提供插件未找到"
```

### Q17: 如何实现命令的条件启用？

**A:** 使用动态过滤器或配置检查：

```python
class ConditionalPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.features_enabled = {
            "advanced_mode": False,
            "debug_mode": True
        }
    
    async def on_load(self):
        pass

    # 条件性注册命令（加载期仅根据配置决定是否声明命令）
    if self.features_enabled.get("advanced_mode"):
        @command_registry.command("advanced_cmd")
        def advanced_cmd(self, event: BaseMessageEvent):
            return "高级功能已启用"
    
    # 运行时条件检查
    @command_registry.command("debug_info")
    def debug_info_cmd(self, event: BaseMessageEvent):
        if not self.features_enabled.get("debug_mode"):
            return "❌ 调试模式未启用"
        return "🔧 调试信息: ..."
```

## ⚠️ 常见陷阱

### Q18: 为什么修改代码后命令没有更新？

**A:** 可能的原因：

1. **插件缓存**：重启机器人或重新加载插件
2. **注册顺序**：确保命令在 `on_load` 中注册
3. **代码错误**：检查控制台的错误信息

### Q19: 内存泄漏和性能问题

**A:** 注意以下几点：

```python
class PerformantPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.max_cache_size = 1000
    
    async def on_load(self):
        @command_registry.command("cached_operation")
        def cached_operation_cmd(self, event: BaseMessageEvent, key: str):
            # 缓存大小控制
            if len(self.cache) > self.max_cache_size:
                # 清理一半缓存
                items = list(self.cache.items())
                self.cache = dict(items[len(items)//2:])
            
            # 使用缓存
            if key in self.cache:
                return f"缓存结果: {self.cache[key]}"
            
            result = self.expensive_operation(key)
            self.cache[key] = result
            return f"新结果: {result}"
```

### Q20: 如何处理插件的配置更新？

**A:** 实现配置热重载：

```python
class ConfigurablePlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置（可以从文件、数据库等）"""
        return {
            "max_users": 100,
            "timeout": 30,
            "features": ["basic", "advanced"]
        }
    
    async def on_load(self):
        @admin_only
        @command_registry.command("reload_config")
        def reload_config_cmd(self, event: BaseMessageEvent):
            try:
                old_config = self.config.copy()
                self.config = self.load_config()
                
                # 比较配置变化
                changes = []
                for key, value in self.config.items():
                    if key not in old_config or old_config[key] != value:
                        changes.append(f"{key}: {old_config.get(key, '无')} -> {value}")
                
                if changes:
                    return f"✅ 配置已重载\n变更:\n" + "\n".join(changes)
                else:
                    return "✅ 配置已重载（无变更）"
                    
            except Exception as e:
                return f"❌ 配置重载失败: {e}"
```

---

## 🆘 获取更多帮助

如果您的问题没有在此FAQ中找到答案：

1. **检查日志**: 查看机器人的日志输出，通常包含有用的错误信息
2. **参考文档**: 回顾相关的指南文档
3. **简化测试**: 创建最小的测试案例来重现问题
4. **社区支持**: 在项目的GitHub或社区论坛寻求帮助

**💡 记住**: 大多数问题都与装饰器顺序、类型注解或权限配置有关。仔细检查这些基础设置通常能解决问题。
