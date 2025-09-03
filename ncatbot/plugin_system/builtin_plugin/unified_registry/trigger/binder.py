"""参数绑定器（简化版）

复用旧 FuncAnalyser 的规则：
- 函数签名：self, event, <typed params...>
- 支持默认值；支持 Sentence 吞剩余文本；支持基础类型与 MessageSegment 子类
实现方式：直接调用现有 FuncAnalyser(convert_args) 能力，传入 ignore 前缀数。
"""

from dataclasses import dataclass
from typing import Callable, Tuple, List

from ncatbot.utils import get_log
from ..command_system.analyzer.func_analyzer import FuncAnalyser

LOG = get_log(__name__)


@dataclass
class BindResult:
    ok: bool
    args: Tuple
    message: str = ""


class ArgumentBinder:
    def bind(self, func: Callable, event, path_words: Tuple[str, ...]) -> BindResult:
        try:
            analyser = FuncAnalyser(func, ignore=path_words)
            ok, args = analyser.convert_args(event)
            if ok:
                return BindResult(True, args)
            else:
                return BindResult(False, tuple(), message="参数不匹配或缺失")
        except Exception as e:
            LOG.debug(f"绑定异常: {e}")
            return BindResult(False, tuple(), message=str(e))


