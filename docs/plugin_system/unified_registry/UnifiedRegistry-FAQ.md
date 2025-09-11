# UnifiedRegistry 常见问题解答

## ❓ 基础使用问题

### Q1: 为什么我的命令函数参数必须有类型注解？

**A:** UnifiedRegistry 的命令系统依赖类型注解来进行自动类型转换和参数验证。除了 `self` 参数外，所有其他参数都必须有类型注解。命令函数推荐为 `async def`，且通过 `await event.reply(...)` 进行异步回复，不再通过 return 返回文本。

```python
# ❌ 错误：缺少类型注解

@command_registry.command("bad")
async def bad_cmd(self, event, text):  # 缺少类型注解
    await event.reply(text)

# ✅ 正确：完整的类型注解，并使用异步回复
@command_registry.command("good")
async def good_cmd(self, event: BaseMessageEvent, text: str):
    await event.reply(text)
```

### Q2: 装饰器的顺序有什么要求？

**A:** 装饰器必须按特定顺序使用：

1. 过滤器装饰器（如 `@admin_only`, `@group_only`）
2. 命令注册装饰器（`@command_registry.command()`）
3. 参数装饰器（`@option`, `@param`）
4. 函数体内通过 `await event.reply(...)` 进行异步回复

```python
# ✅ 正确的顺序
@admin_only                    # 1. 过滤器
@command_registry.command("deploy")  # 2. 命令注册
@option("v", "verbose")        # 3. 参数装饰器
async def deploy_cmd(self, event: BaseMessageEvent, verbose: bool = False):
    await event.reply("部署完成")

# ❌ 错误的顺序
@command_registry.command("wrong")
@admin_only  # 过滤器应该在命令注册之前
async def wrong_cmd(self, event: BaseMessageEvent):
    await event.reply("错误")
```

### Q3: 如何在命令中访问插件的属性和方法？

**A:** 功能函数被定义为类方法时，使用 `self` 参数可以访问插件实例的所有属性和方法：

```python
class MyPlugin(NcatBotPlugin):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.config = {"max_users": 100}
    
    async def on_load(self):
        pass

    @command_registry.command("count")
    async def count_cmd(self, event: BaseMessageEvent):
        self.counter += 1  # 访问插件属性
        await event.reply(f"计数: {self.counter}")
    
    @command_registry.command("reset")
    async def reset_cmd(self, event: BaseMessageEvent):
        self._reset_counter()  # 调用插件方法
        await event.reply("计数已重置")
    
    def _reset_counter(self):
        """插件的私有方法"""
        self.counter = 0
```

## 🔧 命令注册问题

### Q4: 为什么我的命令没有被注册？

**A:** 检查以下几个常见原因：

1. **插件没有正确加载**：确保注册命令的代码被执行，一般来说，注册代码会在定义函数时执行。
```python
async def on_load(self):
    # 保持轻量
    pass

@command_registry.command("hello")
def hello_cmd(self, event: BaseMessageEvent):
    return "Hello"
```

2. **命令名称冲突**：检查是否有重复的命令名或别名，报错信息往往会给出提示。

### Q5: 如何处理命令参数的默认值？

**A:** 在函数签名中直接设置默认值：

```python
@command_registry.command("greet")
async def greet_cmd(self, event: BaseMessageEvent, name: str = "朋友"):
    await event.reply(f"你好，{name}！")

# 使用方式：
# /greet          -> "你好，朋友！"
# /greet 小明     -> "你好，小明！"
```

对于命名参数，使用 `@param` 装饰器：

```python
@command_registry.command("deploy")
@param(name="env", default="dev", help="部署环境")
async def deploy_cmd(self, event: BaseMessageEvent, app: str, env: str = "dev"):
    await event.reply(f"部署 {app} 到 {env} 环境")

# 使用方式：
# /deploy myapp              -> "部署 myapp 到 dev 环境"
# /deploy myapp --env=prod   -> "部署 myapp 到 prod 环境"
```

### Q6: 命令别名不工作怎么办？

**A:** 确保别名格式正确：

```python
# ✅ 正确的别名设置
@command_registry.command("status", aliases=["stat", "st"])
async def status_cmd(self, event: BaseMessageEvent):
    await event.reply("状态正常")

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

## 🔄 参数解析问题

### Q8: 参数类型转换失败怎么办？

**A:** 提供错误处理和用户友好的提示：

```python
@command_registry.command("safe_calc")
async def safe_calc_cmd(self, event: BaseMessageEvent, a: str, b: str):
    """安全的计算命令，手动处理类型转换"""
    try:
        num_a = float(a)
        num_b = float(b)
        result = num_a + num_b
        await event.reply(f"结果: {result}")
    except ValueError:
        await event.reply(f"❌ 参数错误: '{a}' 或 '{b}' 不是有效数字\n💡 请输入数字，例如: /safe_calc 1.5 2.3")
```

### Q9: 如何处理包含空格的参数？

**A:** 使用引号包围参数：

```python
@command_registry.command("say")
async def say_cmd(self, event: BaseMessageEvent, message: str):
    await event.reply(f"机器人说: {message}")

# 使用方式：
# /say "hello world"           -> "机器人说: hello world"
# /say "包含 空格 的 消息"      -> "机器人说: 包含 空格 的 消息"
```

### Q10: 选项和参数的区别是什么？

**A:** 

- **选项** (`@option`): 布尔标志，开启或关闭某个功能
- **参数** (`@param`): 有具体值的配置项

```python
@command_registry.command("backup")
@option(short_name="v", long_name="verbose", help="详细输出")  # 布尔选项
@param(name="path", default="/backup", help="备份路径")        # 有值的参数
async def backup_cmd(self, event: BaseMessageEvent, 
               path: str = "/backup", verbose: bool = False):
    result = f"备份到 {path}"
    if verbose:
        result += " (详细模式)"
    await event.reply(result)

# 使用方式：
# /backup                      -> "备份到 /backup"
# /backup --verbose            -> "备份到 /backup (详细模式)"
# /backup --path=/data         -> "备份到 /data"
# /backup --path=/data -v      -> "备份到 /data (详细模式)"
```

## 🐛 错误处理问题

### Q11: 如何提供用户友好的错误信息？

**A:** 使用清晰的错误格式和建议：

```python
@command_registry.command("divide")
async def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
    # 参数验证
    if b == 0:
        await event.reply("❌ 错误: 除数不能为0\n💡 请确保第二个数字不是0")
    
    try:
        result = a / b
        await event.reply(f"✅ {a} ÷ {b} = {result}")
    except Exception as e:
        await event.reply(f"❌ 计算失败\n🔧 详细错误: {e}\n💡 请检查输入的数字格式")
```

### Q14: 如何记录和调试错误？

**A:** 使用日志系统记录详细信息：

```python
from ncatbot.utils import get_log
LOG = get_log(__name__)

@command_registry.command("complex_operation")
async def complex_operation_cmd(self, event: BaseMessageEvent, data: str):
    user_id = event.user_id
    LOG.info(f"用户 {user_id} 开始复杂操作: {data}")
    
    try:
        result = self.process_complex_data(data)
        LOG.info(f"用户 {user_id} 操作成功: {result}")
        await event.reply(f"✅ 操作完成: {result}")
    
    except ValueError as e:
        LOG.warning(f"用户 {user_id} 输入错误: {e}")
        await event.reply(f"❌ 输入错误: {e}\n💡 请检查输入格式")
    
    except Exception as e:
        LOG.error(f"用户 {user_id} 操作失败: {e}", exc_info=True)
        await event.reply("❌ 系统错误，请稍后重试")
```

## ⚠️ 常见陷阱

### Q18: 为什么修改代码后命令没有更新？

**A:** 不支持热重载，需要重启机器人或重新加载插件。

## 🆘 获取更多帮助

如果您的问题没有在此FAQ中找到答案：

1. **检查日志**: 查看机器人的日志输出，通常包含有用的错误信息
2. **参考文档**: 回顾相关的指南文档
3. **简化测试**: 创建最小的测试案例来重现问题
4. **社区支持**: 在项目的GitHub或社区论坛寻求帮助

**💡 记住**: 大多数问题都与装饰器顺序、类型注解或权限配置有关。仔细检查这些基础设置通常能解决问题。
