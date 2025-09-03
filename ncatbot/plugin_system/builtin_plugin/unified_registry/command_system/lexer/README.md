# 词法分析器文档

现代化的命令行参数词法分析器，支持文本和非文本元素混合处理。

## 核心组件

### StringTokenizer - 字符串分词器
将输入字符串分解为 Token 序列。

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import StringTokenizer

tokenizer = StringTokenizer('deploy --env=prod -xvf "my app"')
tokens = tokenizer.tokenize()
```

**支持语法：**
- 短选项：`-v`, `-xvf` (组合)
- 长选项：`--verbose`, `--help`
- 参数赋值：`-p=1234`, `--config=file.json`
- 引用字符串：`"hello world"`
- 转义序列：`\"`, `\\`, `\n`, `\t`, `\r`, `/`

### AdvancedCommandParser - 高级命令解析器
从 Token 序列解析出结构化的命令数据。

```python
parser = AdvancedCommandParser()
result = parser.parse(tokens)

print(result.options)        # {'v': True, 'x': True, 'f': True}
print(result.named_params)   # {'env': 'prod'}
print(result.elements)       # [Element('text', 'deploy', 0), ...]
```

### MessageTokenizer - 消息级别分词器
处理 MessageArray，支持文本和非文本元素混合解析。

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import MessageTokenizer

tokenizer = MessageTokenizer()
result = tokenizer.parse_message(message_array)

# 支持组合参数：backup --preview=[图片] --dest=/backup
print(result.get_text_params())     # {'dest': '/backup'}
print(result.get_segment_params())  # {'preview': Image(...)}
```

## 数据结构

### ParsedCommand - 解析结果
```python
@dataclass
class ParsedCommand:
    options: Dict[str, bool]        # 选项表 {'verbose': True}
    named_params: Dict[str, Any]    # 命名参数表，支持 MessageSegment
    elements: List[Element]         # 元素列表
    raw_tokens: List[Token]         # 原始 Token 序列
    
    def get_text_params() -> Dict[str, str]     # 获取文本参数
    def get_segment_params() -> Dict[str, Any]  # 获取非文本参数
```

### NonTextToken - 非文本元素Token
```python
@dataclass
class NonTextToken(Token):
    segment: MessageSegment  # 原始 MessageSegment
    element_type: str        # 元素类型 'image', 'at' 等
```

## 用法示例

### 字符串级别解析
```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
    StringTokenizer, AdvancedCommandParser
)

tokenizer = StringTokenizer('backup "my files" --dest=/backup -xvf')
tokens = tokenizer.tokenize()
result = AdvancedCommandParser().parse(tokens)

print(f"选项: {result.options}")                    # {'x': True, 'v': True, 'f': True}
print(f"命名参数: {result.named_params}")            # {'dest': '/backup'}
print(f"元素: {[e.content for e in result.elements]}")  # ['backup', 'my files']
```

### 消息级别解析（推荐）
```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import parse_message_command

# 一行解析复杂消息
result = parse_message_command(message_array)

# 分别处理不同类型的参数
text_params = result.get_text_params()      # 文本参数
segment_params = result.get_segment_params()  # MessageSegment 参数

print(f"选项: {result.options}")
print(f"文本参数: {text_params}")
print(f"非文本参数数量: {len(segment_params)}")
```

### 组合参数示例
支持 `--param=[非文本元素]` 语法：

```python
# 消息内容：backup --preview=[图片] --notify=[At用户] --dest=/backup -v
result = parse_message_command(message_array)

print(result.options)  # {'v': True}
print(result.get_text_params())  # {'dest': '/backup'}
print(result.get_segment_params())  # {'preview': Image(...), 'notify': At(...)}
```

## 高级特性

### 混合命令处理
```python
# 处理包含文本、图片、@用户的复杂命令
# 消息：process "input.txt" [图片] @admin --format=json --verbose
result = parse_message_command(message_array)

# 结果自动分类
text_elements = [e for e in result.elements if e.type == 'text']      # ['process', 'input.txt']
image_elements = [e for e in result.elements if e.type == 'image']    # [Image(...)]
at_elements = [e for e in result.elements if e.type == 'at']          # [At(admin)]
```

### 类型安全访问
```python
# 安全访问不同类型的参数
for name, segment in result.get_segment_params().items():
    if hasattr(segment, 'file'):  # Image/Video
        print(f"文件参数 {name}: {segment.file}")
    elif hasattr(segment, 'qq'):  # At
        print(f"用户参数 {name}: @{segment.qq}")
```

## 错误处理

```python
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
    QuoteMismatchError, InvalidEscapeSequenceError
)

try:
    result = parse_message_command(message_array)
except QuoteMismatchError as e:
    print(f"引号不匹配: {e}")
except InvalidEscapeSequenceError as e:
    print(f"无效转义: {e}")
```

## 注意事项

1. **选项vs参数**: 选项是布尔状态，命名参数有值
2. **类型区分**: `get_text_params()` 返回字符串，`get_segment_params()` 返回 MessageSegment
3. **位置保持**: Element 保持原始顺序
4. **Unicode支持**: 完全支持中文和特殊字符
5. **便捷函数**: 推荐使用 `parse_message_command()` 直接解析
