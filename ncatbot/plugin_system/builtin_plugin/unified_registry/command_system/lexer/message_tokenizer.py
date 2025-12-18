"""消息级别分词器

处理 MessageArray，将其转换为 Token 序列，支持文本和非文本元素混合处理。
"""

from typing import List
from .tokenizer import (
    StringTokenizer,
    Token,
    TokenType,
    NonTextToken,
    AdvancedCommandParser,
    ParsedCommand,
)


class MessageTokenizer:
    """消息级别分词器

    将 MessageArray 转换为 Token 序列，支持：
    - PlainText 及其子类：使用 StringTokenizer 分析
    - 其他 MessageSegment：转换为 NonTextToken
    """

    def __init__(self):
        self.command_parser = AdvancedCommandParser()

    def tokenize(self, message_array) -> List[Token]:
        """将 MessageArray 转换为 Token 序列

        Args:
            message_array: MessageArray 对象

        Returns:
            Token 序列，包含文本 Token 和 NonTextToken
        """
        tokens = []

        for segment in message_array.messages:
            if self._is_text_segment(segment):
                # 文本段：使用 StringTokenizer 分析
                text_tokenizer = StringTokenizer(segment.text)
                text_tokens = text_tokenizer.tokenize()

                # 过滤 EOF，添加到结果中
                for token in text_tokens:
                    if token.type != TokenType.EOF:
                        # 调整 token 位置为全局位置
                        token.position = len(tokens)
                        tokens.append(token)
            else:
                # 非文本段：创建 NonTextToken
                non_text_token = NonTextToken(segment, len(tokens))
                tokens.append(non_text_token)

        # 添加最终的 EOF
        tokens.append(Token(TokenType.EOF, "", len(tokens)))
        return tokens

    def parse_message(self, message_array) -> ParsedCommand:
        """直接从 MessageArray 解析到 ParsedCommand

        Args:
            message_array: MessageArray 对象

        Returns:
            ParsedCommand 解析结果
        """
        # 1. 分词
        tokens = self.tokenize(message_array)

        # 2. 解析
        result = self.command_parser.parse(tokens)

        return result

    def _is_text_segment(self, segment) -> bool:
        """判断是否为文本段

        Args:
            segment: MessageSegment 对象

        Returns:
            是否为文本段
        """
        # 检查是否有 text 属性且 msg_seg_type 为 text 或其子类
        return (
            hasattr(segment, "text")
            and hasattr(segment, "msg_seg_type")
            and segment.msg_seg_type in ["text", "plain_text"]
        )


# 便捷函数
def parse_message_command(message_array) -> ParsedCommand:
    """便捷函数：直接解析 MessageArray

    Args:
        message_array: MessageArray 对象

    Returns:
        ParsedCommand 解析结果
    """
    tokenizer = MessageTokenizer()
    return tokenizer.parse_message(message_array)
