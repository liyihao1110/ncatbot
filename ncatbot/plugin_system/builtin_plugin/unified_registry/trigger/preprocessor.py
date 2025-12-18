"""消息前置处理器

负责：
- 命令前缀判断
- 大小写归一
- 提取首段文本（用于 tokenizer）
"""

from dataclasses import dataclass
from typing import Optional, List

from ncatbot.utils import get_log
from ncatbot.core.event import BaseMessageEvent

LOG = get_log(__name__)


@dataclass
class PreprocessResult:
    command_text: str


class MessagePreprocessor:
    def __init__(
        self, *, prefixes: List[str], require_prefix: bool, case_sensitive: bool
    ) -> None:
        self.prefixes = prefixes
        self.require_prefix = require_prefix
        self.case_sensitive = case_sensitive

    def _normalize(self, s: str) -> str:
        return s if self.case_sensitive else s.lower()

    def precheck(self, event: BaseMessageEvent) -> Optional[PreprocessResult]:
        """提取首段文本，并根据配置判断是否进入命令解析流程。"""
        if not event.message.messages:
            return None

        first = event.message.messages[0]
        if getattr(first, "msg_seg_type", None) != "text":
            # 没有首段文本，不进入命令解析
            return None

        text: str = getattr(first, "text", "") or ""
        raw = text
        norm = self._normalize(text).lstrip()

        if self.require_prefix:
            matched = None
            for p in self.prefixes:
                p_norm = self._normalize(p)
                if norm.startswith(p_norm):
                    matched = p
                    break
            if matched is None:
                return None
            # 去除前缀，原样切除与大小写无关
            cut_len = len(matched)
            return PreprocessResult(command_text=raw[cut_len:].lstrip())
        else:
            return PreprocessResult(command_text=raw)
