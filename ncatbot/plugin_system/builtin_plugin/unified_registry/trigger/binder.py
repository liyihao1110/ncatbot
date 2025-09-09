"""参数绑定器（基于 message_tokenizer 结果）

策略：
- 使用 MessageTokenizer.parse_message(event.message) 获取 ParsedCommand
- 使用 FuncAnalyser 仅做签名与类型约束（detect_args_type、默认值收集）
- 位置参数绑定来源：ParsedCommand.elements（已剔除选项与命名参数）
- Sentence 类型吞剩余文本元素；MessageSegment 子类按元素匹配；基础类型从文本元素解析
"""

from dataclasses import dataclass
from typing import Callable, Tuple, List, Any, Dict

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils.specs import CommandSpec
from ncatbot.utils import get_log
from ..command_system.analyzer.func_analyzer import FuncAnalyser
from ..command_system.lexer.message_tokenizer import MessageTokenizer
from ncatbot.core.event import BaseMessageEvent

LOG = get_log(__name__)


@dataclass
class BindResult:
    ok: bool
    args: Tuple # 位置参数
    named_args: Dict[str, Any] # 命名参数
    message: str = ""


class ArgumentBinder:
    def bind(self, spec: CommandSpec, event: BaseMessageEvent, path_words: Tuple[str, ...], prefixes: List[str]) -> BindResult:
        try:
            # TODO: 绑定错误回报提示
            # 解析消息为 ParsedCommand（elements 已去除选项/命名参数）
            tokenizer = MessageTokenizer()
            parsed = tokenizer.parse_message(event.message)
            elements = list(parsed.elements)  # copy
            LOG.debug(f"解析后的元素: {elements}, 命名参数: {parsed.named_params}, 选项: {parsed.options}")
            LOG.debug(f"路径词: {path_words}")
            # 跳过命令词（仅匹配前置的 text 元素）
            skip_idx = 0
            pw = list(path_words)
            pw_idx = 0
            while skip_idx < len(elements) and pw_idx < len(pw):
                el = elements[skip_idx]
                if el.type == "text" and (str(el.content) == pw[pw_idx] or (el.content[0] in prefixes) and el.content[1:].startswith(pw[pw_idx])):
                    skip_idx += 1
                    pw_idx += 1
                else:
                    break

            LOG.debug(f"跳过索引: {skip_idx}")
            idx = skip_idx
            bound_args: List[Any] = []
            bound_kwargs: Dict[str, Any] = {}

            for k, v in parsed.named_params.items():
                bound_kwargs[k] = v
            
            for o in parsed.options:
                bound_kwargs.update(spec.get_kw_binding(o))

            for element in elements[skip_idx:]:
                bound_args.append(element.content)

            return BindResult(True, tuple(bound_args), bound_kwargs, "")
        except Exception as e:
            LOG.debug(f"绑定异常: {e}")
            raise e

