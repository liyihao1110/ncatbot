"""命令解析器（Resolver）

职责：
- 从注册器构建命令索引
- 严格冲突检测（默认禁止前缀重叠）
- 基于 token 的命令匹配（首段文本 tokens）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Union, Tuple

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils.specs import (
    CommandSpec,
)
from ncatbot.utils import get_log
from ..command_system.lexer.tokenizer import Token, TokenType

LOG = get_log(__name__)


@dataclass
class CommandEntry:
    path_words: Tuple[str, ...]
    command: CommandSpec


class CommandResolver:
    def __init__(
        self, *, case_sensitive: bool, prefixes: List[str], allow_hierarchical: bool
    ) -> None:
        self.case_sensitive = case_sensitive
        self.allow_hierarchical = allow_hierarchical
        self.prefixes_tuple = tuple(prefix for prefix in prefixes)
        # 哈希索引：规范化路径字符串 → CommandEntry
        self._index: Dict[Tuple[str, ...], CommandEntry] = {}

    def clear(self):
        """清除索引"""
        self._index.clear()

    def _normalize(self, s: str) -> str:
        return s if self.case_sensitive else s.lower()

    def _path_to_norm(self, path: Tuple[str, ...]) -> Tuple[str, ...]:
        return tuple(self._normalize(p) for p in path)

    def build_index(
        self,
        commands: Dict[Tuple[str, ...], CommandSpec],
        aliases: Dict[Tuple[str, ...], CommandSpec],
    ) -> None:
        """构建索引并进行严格冲突检测。"""
        entries: Dict[Tuple[str, ...], CommandEntry] = {}

        def add_entry(path: Tuple[str, ...], command: CommandSpec):
            norm_path = self._path_to_norm(path)
            if norm_path in entries:
                raise ValueError(f"命令重复: {' '.join(norm_path)}")
            entries[norm_path] = CommandEntry(path_words=norm_path, command=command)

        for path, command in commands.items():
            add_entry(path, command)
        for path, command in aliases.items():
            add_entry(path, command)

        # 严格：不允许任意两条路径存在前缀关系
        paths = list(entries.keys())
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                a, b = paths[i], paths[j]
                min_len = min(len(a), len(b))
                if a[:min_len] == b[:min_len] and a != b:
                    if not self.allow_hierarchical:
                        raise ValueError(
                            f"命令前缀冲突: {' '.join(a)} vs {' '.join(b)}"
                        )

        self._index = entries
        LOG.debug(f"Resolver 索引构建完成: {len(self._index)}")

    def resolve_from_tokens(
        self, tokens: List[Token]
    ) -> Union[Tuple[str, CommandEntry], Tuple[None, None]]:
        """从首段 tokens 解析命令。

        策略：仅接收 TokenType.WORD/QUOTED_STRING 序列作为命令词；
        遇到第一个非上述类型 token 即停止命令词聚合。
        在严格模式下，应当保证不会出现“多匹配”。
        """
        words: List[str] = []
        for t in tokens:
            if t.type in (TokenType.WORD, TokenType.QUOTED_STRING):
                words.append(t.value)
            else:
                break

        if not words:
            return None, None
        # 尝试从最长到最短匹配（兼容 allow_hierarchical=true 的场景）
        for k in range(len(words), 0, -1):
            candidate = tuple(self._normalize(w) for w in words[:k])
            if candidate in self._index:
                return "", self._index[candidate]

        if words[0].startswith(self.prefixes_tuple):
            prefix = words[0][0]
            words[0] = words[0][1:]
            for k in range(len(words), 0, -1):
                candidate = tuple(self._normalize(w) for w in words[:k])
                if candidate in self._index:
                    return prefix, self._index[candidate]
        return None, None

    def get_commands(self) -> List[CommandEntry]:
        """获取所有已注册的命令条目。"""
        return list(self._index.values())
