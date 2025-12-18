"""字符串分词器

支持命令行参数解析，包括短选项、长选项、参数赋值和转义字符串处理。
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from ncatbot.utils import NcatBotError


class TokenType(Enum):
    """Token 类型枚举"""

    WORD = "word"  # 普通单词
    SHORT_OPTION = "short_option"  # 短选项 -v, -xvf
    LONG_OPTION = "long_option"  # 长选项 --verbose
    ARGUMENT = "argument"  # 参数值
    QUOTED_STRING = "quoted_string"  # 引用字符串 "content"
    SEPARATOR = "separator"  # 分隔符 =
    NON_TEXT_ELEMENT = "non_text_element"  # 非文本元素
    EOF = "eof"  # 结束标记


class QuoteState(Enum):
    """引号状态"""

    NONE = "none"  # 无引号
    DOUBLE = "double"  # 双引号状态


@dataclass
class Token:
    """词法单元"""

    type: TokenType
    value: str
    position: int

    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', pos={self.position})"

    def __repr__(self):
        return self.__str__()


@dataclass
class NonTextToken(Token):
    """非文本元素 Token"""

    segment: Any  # MessageSegment，使用 Any 避免循环导入
    element_type: str

    def __init__(self, segment, position: int):
        element_type = self._get_element_type(segment)
        super().__init__(
            type=TokenType.NON_TEXT_ELEMENT,
            value=f"[{element_type}]",
            position=position,
        )
        self.segment = segment
        self.element_type = element_type

    def _get_element_type(self, segment) -> str:
        """根据 MessageSegment 类型获取元素类型"""
        type_map = {
            "At": "at",
            "Image": "image",
            "Video": "video",
            "Face": "face",
            "Reply": "reply",
            "Node": "node",
            "Forward": "forward",
        }
        class_name = segment.__class__.__name__
        return type_map.get(class_name, class_name.lower())


class QuoteMismatchError(NcatBotError):
    """引号不匹配错误"""

    def __init__(self, position: int, quote_char: str):
        super().__init__(f"Position {position}: Unmatched quote '{quote_char}'")
        self.position = position
        self.quote_char = quote_char


class InvalidEscapeSequenceError(NcatBotError):
    """无效转义序列错误"""

    def __init__(self, position: int, sequence: str):
        super().__init__(f"Position {position}: Invalid escape sequence '\\{sequence}'")
        self.position = position
        self.sequence = sequence


class StringTokenizer:
    """字符串分词器

    将输入字符串解析为 Token 序列，支持：
    - 短选项：-v, -x, -xvf (组合)
    - 长选项：--verbose, --help
    - 参数赋值：-p=1234, --para=value
    - 转义字符串："有 空格 的 字符串"
    - 转义序列：\\", \\\\, \\n, \\t, \\r
    """

    # 支持的转义序列映射
    ESCAPE_SEQUENCES = {
        '"': '"',
        "\\": "\\",
        "n": "\n",
        "t": "\t",
        "r": "\r",
        "/": "/",
    }

    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.position = 0
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """执行分词，返回 Token 列表"""
        self.tokens = []
        self.position = 0

        while self.position < self.length:
            self._skip_whitespace()
            if self.position >= self.length:
                break

            char = self.text[self.position]

            # 检查引号字符串
            if char == '"':
                self._parse_quoted_string()
            # 检查长选项 --
            elif char == "-" and self._peek() == "-":
                self._parse_long_option()
            # 检查短选项 -
            elif char == "-" and self._peek() and self._peek() != "-":
                self._parse_short_option()
            # 检查分隔符 =
            elif char == "=":
                self._add_token(TokenType.SEPARATOR, char)
                self.position += 1
            # 普通单词
            else:
                self._parse_word()

        # 添加 EOF 标记
        self._add_token(TokenType.EOF, "")
        return self.tokens

    def _peek(self, offset: int = 1) -> Optional[str]:
        """查看后续字符，不移动位置"""
        peek_pos = self.position + offset
        if peek_pos < self.length:
            return self.text[peek_pos]
        return None

    def _skip_whitespace(self):
        """跳过空白字符"""
        while self.position < self.length and self.text[self.position].isspace():
            self.position += 1

    def _add_token(self, token_type: TokenType, value: str):
        """添加 Token"""
        token = Token(token_type, value, self.position - len(value))
        self.tokens.append(token)

    def _parse_quoted_string(self):
        """解析引用字符串 "content" """
        start_pos = self.position
        self.position += 1  # 跳过开始引号

        value = ""
        while self.position < self.length:
            char = self.text[self.position]

            if char == '"':
                # 结束引号
                self.position += 1
                self._add_token(TokenType.QUOTED_STRING, value)
                return
            elif char == "\\":
                # 转义序列
                self.position += 1
                if self.position >= self.length:
                    raise InvalidEscapeSequenceError(self.position - 1, "EOF")

                escape_char = self.text[self.position]
                if escape_char in self.ESCAPE_SEQUENCES:
                    value += self.ESCAPE_SEQUENCES[escape_char]
                else:
                    raise InvalidEscapeSequenceError(self.position - 1, escape_char)
                self.position += 1
            else:
                value += char
                self.position += 1

        # 到达字符串末尾但没有找到结束引号
        self._add_token(TokenType.WORD, self.text[start_pos : self.position])
        return

    def _parse_long_option(self):
        """解析长选项 --option 或 --option=value"""
        start_pos = self.position
        self.position += 2  # 跳过 --

        # 读取选项名
        option_name = ""
        while (
            self.position < self.length
            and not self.text[self.position].isspace()
            and self.text[self.position] != "="
        ):
            option_name += self.text[self.position]
            self.position += 1

        if not option_name:
            while (
                self.position < self.length and not self.text[self.position].isspace()
            ):
                self.position += 1
            self._add_token(TokenType.WORD, self.text[start_pos : self.position])
            return

        # 检查是否有参数赋值
        if self.position < self.length and self.text[self.position] == "=":
            # 有赋值，解析为 LONG_OPTION=value
            self._add_token(TokenType.LONG_OPTION, option_name)
            # 分隔符会在下一次循环中处理
        else:
            # 无赋值，纯选项
            self._add_token(TokenType.LONG_OPTION, option_name)

    def _parse_short_option(self):
        """解析短选项 -v 或 -xvf 或 -p=value"""
        start_pos = self.position
        self.position += 1  # 跳过 -

        # 读取选项字符
        options = ""
        while self.position < self.length and self.text[self.position].isalpha():
            options += self.text[self.position]
            self.position += 1

        if not options:
            while (
                self.position < self.length and not self.text[self.position].isspace()
            ):
                self.position += 1
            self._add_token(TokenType.WORD, self.text[start_pos : self.position])
            return

        # 检查是否有参数赋值（只对单个选项）
        if (
            len(options) == 1
            and self.position < self.length
            and self.text[self.position] == "="
        ):
            # 单个选项有赋值
            self._add_token(TokenType.SHORT_OPTION, options)
            # 分隔符会在下一次循环中处理
        else:
            # 多个选项组合或无赋值
            self._add_token(TokenType.SHORT_OPTION, options)

    def _parse_word(self):
        """解析普通单词"""
        value = ""
        while (
            self.position < self.length
            and not self.text[self.position].isspace()
            and self.text[self.position] not in '="'
        ):
            value += self.text[self.position]
            self.position += 1

        if value:
            self._add_token(TokenType.WORD, value)


@dataclass
class Element:
    """命令元素 - 未解析的原始部分"""

    type: str  # "text", "image", "at", etc.
    content: Any  # 原始内容
    position: int  # 在原始序列中的位置

    def __str__(self):
        return f"Element({self.type}, '{self.content}', pos={self.position})"

    def __repr__(self):
        return self.__str__()


@dataclass
class ParsedCommand:
    """解析后的命令结构"""

    options: Dict[str, bool]  # 选项表 {选项名: True}
    named_params: Dict[str, Any]  # 命名参数表 {参数名: 值}，支持 MessageSegment
    elements: List[Element]  # 未解析的元素（按位置顺序）
    raw_tokens: List[Token]  # 原始token序列

    def __str__(self):
        return (
            f"ParsedCommand(options={self.options}, "
            f"named_params={self.named_params}, "
            f"elements={self.elements})"
        )

    def __repr__(self):
        return self.__str__()

    def get_text_params(self) -> Dict[str, str]:
        """获取文本类型的命名参数"""
        return {k: v for k, v in self.named_params.items() if isinstance(v, str)}

    def get_segment_params(self) -> Dict[str, Any]:
        """获取 MessageSegment 类型的命名参数"""
        return {
            k: v for k, v in self.named_params.items() if hasattr(v, "msg_seg_type")
        }


class AdvancedCommandParser:
    """高级命令解析器

    从 Token 序列解析出：
    - options: 选项表（布尔状态）
    - named_params: 命名参数表（键值对）
    - elements: 未解析的元素（保持原始位置）
    """

    def parse(self, tokens: List[Token]) -> ParsedCommand:
        """解析 Token 序列

        Args:
            tokens: Token 序列

        Returns:
            ParsedCommand: 解析结果
        """
        options = {}  # 选项表：{选项名: True}
        named_params = {}  # 命名参数表：{参数名: 值}
        elements = []  # 未解析元素

        i = 0
        while i < len(tokens) and tokens[i].type != TokenType.EOF:
            token = tokens[i]

            if token.type == TokenType.SHORT_OPTION:
                if self._has_assignment(tokens, i):
                    # -p=value 形式 → named_params
                    name, value = self._parse_assignment(tokens, i)
                    named_params[name] = value
                    i += 3  # 跳过 option + separator + value
                else:
                    # -v 或 -xvf 形式 → options
                    for char in token.value:
                        options[char] = True  # 只记录选中状态
                    i += 1

            elif token.type == TokenType.LONG_OPTION:
                if self._has_assignment(tokens, i):
                    # --name=value 形式 → named_params
                    name, value = self._parse_assignment(tokens, i)
                    named_params[name] = value
                    i += 3
                else:
                    # --verbose 形式 → options
                    options[token.value] = True  # 只记录选中状态
                    i += 1

            elif token.type in [TokenType.WORD, TokenType.QUOTED_STRING]:
                # 转换为 Element
                element = Element(
                    type="text", content=token.value, position=len(elements)
                )
                elements.append(element)
                i += 1

            elif token.type == TokenType.NON_TEXT_ELEMENT:
                # 处理非文本元素
                non_text_token = token  # 应该是 NonTextToken 类型
                element = Element(
                    type=non_text_token.element_type,
                    content=non_text_token.segment,
                    position=len(elements),
                )
                elements.append(element)
                i += 1

            else:
                # 跳过 SEPARATOR, EOF 等
                i += 1

        return ParsedCommand(
            options=options,
            named_params=named_params,
            elements=elements,
            raw_tokens=tokens,
        )

    def _has_assignment(self, tokens: List[Token], index: int) -> bool:
        """检查选项是否有赋值"""
        return (
            index + 1 < len(tokens)
            and tokens[index + 1].type == TokenType.SEPARATOR
            and index + 2 < len(tokens)
            and tokens[index + 2].type
            in [TokenType.WORD, TokenType.QUOTED_STRING, TokenType.NON_TEXT_ELEMENT]
        )

    def _parse_assignment(self, tokens: List[Token], index: int) -> Tuple[str, Any]:
        """解析选项赋值，支持非文本值"""
        option_name = tokens[index].value
        value_token = tokens[index + 2]

        if value_token.type == TokenType.NON_TEXT_ELEMENT:
            # 非文本值：返回原始 MessageSegment
            return option_name, value_token.segment
        else:
            # 文本值：返回字符串
            return option_name, value_token.value
