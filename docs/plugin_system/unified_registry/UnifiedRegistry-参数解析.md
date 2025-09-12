# UnifiedRegistry 参数解析指南

## 🔧 参数解析系统概述

UnifiedRegistry 的参数解析系统是一个强大的现代化命令行参数处理引擎，支持复杂的命令行语法、智能的类型转换和灵活的非文本元素处理。

## 🎯 核心特性

### 支持的语法格式

- **短选项**: `-v`, `-xvf` (组合选项)
- **长选项**: `--verbose`, `--help`
- **参数赋值**: `-p=1234`, `--env=prod`
- **引用字符串**: `"包含空 格的文本"`
- **转义序列**: `\"`, `\\`, `\n`, `\t`
- **非文本元素**: 图片、@用户、表情等消息元素

### 核心组件

- **词法分析器** (`StringTokenizer`): 解析字符串为Token序列
- **消息分词器** (`MessageTokenizer`): 处理混合消息元素
- **参数绑定器** (`ArgumentBinder`): 将解析结果绑定到函数参数
- **类型转换器**: 自动进行类型转换和验证

## 📝 基础语法示例

### 1. 简单参数

```python
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("echo")
    async def echo_cmd(self, event: BaseMessageEvent, text: str):
        await event.reply(f"你说的是: {text}")
```

**使用示例**:
- `/echo hello` → "你说的是: hello"
- `/echo 这是一段文本` → "你说的是: 这是一段文本"

### 2. 多个参数

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass
    
    @command_registry.command("calc")
    async def calc_cmd(self, event: BaseMessageEvent, a: int, op: str, b: int):
        if op == "add":
            await event.reply(f"{a} + {b} = {a + b}")
        elif op == "sub":
            await event.reply(f"{a} - {b} = {a - b}")
        else:
            await event.reply("支持的操作: add, sub")
```

**使用示例**:
- `/calc 10 add 20` → "10 + 20 = 30"
- `/calc 100 sub 50` → "100 - 50 = 50"

### 3. 引用字符串

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("say")
    async def say_cmd(self, event: BaseMessageEvent, message: str):
        await event.reply(f"机器人说: {message}")
```

**使用示例**:
- `/say "hello world"` → "机器人说: hello world"
- `/say "包含 空格 的 消息"` → "机器人说: 包含 空格 的 消息"

## 🎛️ 选项和参数语法

### 1. 短选项

```python
from ncatbot.plugin_system import option

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("list")
    @option(short_name="l", help="长格式显示")
    @option(short_name="a", help="显示隐藏文件")
    @option(short_name="h", help="人类可读格式")
    async def list_cmd(self, event: BaseMessageEvent, path: str = ".", 
                    l: bool = False, a: bool = False, h: bool = False):
        result = f"列出目录: {path}"
        
        options = []
        if l:
            options.append("长格式")
        if a:
            options.append("显示隐藏")
        if h:
            options.append("人类可读")
        
        if options:
            result += f" ({', '.join(options)})"
        
        await event.reply(result)
```

**使用示例**:
- `/list` → "列出目录: ."
- `/list -l` → "列出目录: . (长格式)"
- `/list -la` → "列出目录: . (长格式, 显示隐藏)"
- `/list -lah /home` → "列出目录: /home (长格式, 显示隐藏, 人类可读)"（这里 /home 是一个位置参数，传递给 path 参数）

### 2. 长选项

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("backup")
    @option(long_name="compress", help="压缩备份文件")
    @option(long_name="encrypt", help="加密备份文件")
    @option(long_name="verify", help="验证备份完整性")
    async def backup_cmd(self, event: BaseMessageEvent, source: str,
                    compress: bool = False, encrypt: bool = False, verify: bool = False):
        result = f"备份 {source}"
        
        features = []
        if compress:
            features.append("压缩")
        if encrypt:
            features.append("加密")
        if verify:
            features.append("验证")
        
        if features:
            result += f" [{', '.join(features)}]"
        
        await event.reply(result)
```

**使用示例**:
- `/backup /data` → "备份 /data"
- `/backup /data --compress` → "备份 /data [压缩]"
- `/backup /data --compress --encrypt` → "备份 /data [压缩, 加密]"

### 3. 参数赋值

```python
from ncatbot.plugin_system import param

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("deploy")
    @param(name="env", default="dev", help="部署环境")
    @param(name="port", default=8080, help="端口号")
    @param(name="workers", default=4, help="工作进程数")
    async def deploy_cmd(self, event: BaseMessageEvent, app: str,
                    env: str = "dev", port: int = 8080, workers: int = 4):
        await event.reply(f"部署 {app}: 环境={env}, 端口={port}, 进程={workers}")
```

**使用示例**:
- `/deploy myapp` → "部署 myapp: 环境=dev, 端口=8080, 进程=4"
- `/deploy myapp --env=prod` → "部署 myapp: 环境=prod, 端口=8080, 进程=4"
- `/deploy myapp --env=prod --port=9000 --workers=8` → "部署 myapp: 环境=prod, 端口=9000, 进程=8"

### 4. 复杂组合语法

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("process")
    @option(short_name="v", long_name="verbose", help="详细输出")
    @option(short_name="f", long_name="force", help="强制执行")
    @param(name="output", default="result.txt", help="输出文件")
    @param(name="format", default="json", help="输出格式")
    async def process_cmd(self, event: BaseMessageEvent, input_file: str,
                    output: str = "result.txt", format: str = "json",
                    verbose: bool = False, force: bool = False):
        result = f"处理文件: {input_file} → {output} ({format}格式)"
        
        if verbose:
            result += " [详细模式]"
        if force:
            result += " [强制模式]"
        
        await event.reply(result)
```

**使用示例**:
- `/process data.csv` → "处理文件: data.csv → result.txt (json格式)"
- `/process data.csv -v --output=output.xml --format=xml` → "处理文件: data.csv → output.xml (xml格式) [详细模式]"
- `/process "my file.txt" --force -v` → "处理文件: my file.txt → result.txt (json格式) [详细模式] [强制模式]"

## 🔄 类型转换系统

### 1. 自动类型转换

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("math")
    async def math_cmd(self, event: BaseMessageEvent, a: int, b: float, c: bool):
        """演示不同类型的自动转换"""
        result = f"整数: {a} (类型: {type(a).__name__})\n"
        result += f"浮点数: {b} (类型: {type(b).__name__})\n"
        result += f"布尔值: {c} (类型: {type(c).__name__})"
        await event.reply(result)
```

**使用示例**:
- `/math 42 3.14 true` → "整数: 42 (类型: int)\n浮点数: 3.14 (类型: float)\n布尔值: True (类型: bool)"
- `/math 100 2.5 false` → "整数: 100 (类型: int)\n浮点数: 2.5 (类型: float)\n布尔值: False (类型: bool)"

### 2. 布尔值处理

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("toggle")
    async def toggle_cmd(self, event: BaseMessageEvent, feature: str, enabled: bool):
        status = "启用" if enabled else "禁用"
        await event.reply(f"功能 '{feature}' 已{status}")
```

**布尔值识别规则**:
- **True**: any other value
- **False**: `false`, `False`, `0`

**使用示例**:
- `/toggle logging true` → "功能 'logging' 已启用"
- `/toggle debug false` → "功能 'debug' 已禁用"
- `/toggle cache 1` → "功能 'cache' 已启用"

### 3. 错误处理

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("divide")
    async def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
        """带错误处理的数学运算"""
        try:
            if b == 0:
                await event.reply("❌ 错误: 除数不能为0")
                return
            result = a / b
            await event.reply(f"✅ {a} ÷ {b} = {result}")
        except Exception as e:
            await event.reply(f"❌ 计算错误: {e}")
```

## 🖼️ 非文本元素处理

### 1. 图片参数

```python
from ncatbot.core.event.message_segment import Image

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("analyze")
    async def analyze_cmd(self, event: BaseMessageEvent, description: str, image: Image):
        """分析图片（示例，实际需要图片处理逻辑）"""
        await event.reply(f"分析图片: {description}\n图片信息: {image.file}")
```

**使用方式**: `/analyze "这是一张风景图" [图片]`

### 2. @用户参数

```python
from ncatbot.core.event.message_segment import At

class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("mention")
    async def mention_cmd(self, event: BaseMessageEvent, message: str, user: At):
        """提及用户"""
        await event.reply(f"发送消息给 @{user.qq}: {message}")
```

**使用方式**: `/mention "你好" @某用户`

## 🔧 高级语法特性

### 1. 转义字符支持

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("format")
    async def format_cmd(self, event: BaseMessageEvent, text: str):
        """支持转义字符的格式化"""
        # 处理常见转义字符
        formatted = text.replace('\\n', '\n').replace('\\t', '\t')
        await event.reply(f"格式化结果:\n{formatted}")
```

**使用示例**:
- `/format "第一行\n第二行"`
- `/format "名称\t值"`

### 2. 引号嵌套

TODO: 支持性存疑

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("quote")
    async def quote_cmd(self, event: BaseMessageEvent, text: str):
        """处理引号嵌套"""
        await event.reply(f"引用内容: {text}")
```

**使用示例**:
- `/quote "他说: \"你好\""` → "引用内容: 他说: "你好""
- `/quote "包含\"双引号\"的文本"` → "引用内容: 包含"双引号"的文本"

### 3. 复杂命令行

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        pass

    @command_registry.command("build")
    @option(short_name="v", long_name="verbose")
    @option(short_name="c", long_name="clean")
    @param(name="output", default="dist")
    @param(name="target", default="all")
    async def build_cmd(self, event: BaseMessageEvent, project: str,
                  output: str = "dist", target: str = "all",
                  verbose: bool = False, clean: bool = False):
        """复杂的构建命令"""
        result = f"构建项目: {project}"
        result += f"\n目标: {target}"
        result += f"\n输出: {output}"
        
        if clean:
            result += "\n🧹 执行清理"
        if verbose:
            result += "\n📝 详细输出模式"
        
        await event.reply(result)
```

**使用示例**:
- `/build myproject` → 基础构建
- `/build myproject --output="build/release" --target=production -vc` → 完整构建
- `/build "My Project" --clean -v --output="/path/to/build"` → 带引号的项目名

## 📊 语法总结表

| 语法类型 | 格式 | 示例 | 说明 |
|----------|------|------|------|
| 短选项 | `-x` | `-v`, `-f` | 单字符选项 |
| 组合短选项 | `-xyz` | `-vfq` | 多个短选项组合 |
| 长选项 | `--option` | `--verbose` | 完整单词选项 |
| 短选项赋值 | `-x=value` | `-p=8080` | 短选项带值 |
| 长选项赋值 | `--option=value` | `--env=prod` | 长选项带值 |
| 双引号字符串 | `"text"` | `"hello world"` | 包含空格的文本 |
| 转义字符 | `\"`, `\\` | `"say \"hi\""` | 转义特殊字符 |
| 非文本元素 | `[图片]`, `@用户` | `analyze [图片]` | 消息中的媒体元素 |

## 🔍 未来期望特性

- 通过类型注解而非装饰器来定义参数
- 支持可变参数和额外命名参数

## 🚦 下一步

掌握参数解析系统后，您可以：

1. **应用实践**: 查看 [实战案例](./UnifiedRegistry-实战案例.md) 学习复杂应用
2. **提升质量**: 阅读 [最佳实践](./UnifiedRegistry-最佳实践.md) 优化代码
3. **测试验证**: 参考 [测试指南](./UnifiedRegistry-测试指南.md) 确保功能正确

---

**💡 提示**: 参数解析系统的强大之处在于它能够处理复杂的命令行语法，同时保持代码的简洁性。充分利用类型注解可以获得更好的开发体验。
