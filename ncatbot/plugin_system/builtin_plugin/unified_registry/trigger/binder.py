"""参数绑定器（基于 message_tokenizer 结果）

策略：
- 使用 MessageTokenizer.parse_message(event.message) 获取 ParsedCommand
- 使用 FuncAnalyser 仅做签名与类型约束（detect_args_type、默认值收集）
- 位置参数绑定来源：ParsedCommand.elements（已剔除选项与命名参数）
- Sentence 类型吞剩余文本元素；MessageSegment 子类按元素匹配；基础类型从文本元素解析
"""

from dataclasses import dataclass
from typing import Callable, Tuple, List, Any, Dict

from ncatbot.utils import get_log
from ..command_system.analyzer.func_analyzer import FuncAnalyser
from ..command_system.lexer.message_tokenizer import MessageTokenizer

LOG = get_log(__name__)


@dataclass
class BindResult:
    ok: bool
    args: Tuple # 位置参数
    named_args: Dict[str, Any] # 命名参数
    options: Dict[str, bool] # 选项
    message: str = ""


class ArgumentBinder:
    def bind(self, func: Callable, event, path_words: Tuple[str, ...], prefixes: List[str]) -> BindResult:
        try:
            analyser = FuncAnalyser(func)
            args_types, is_required_list = analyser.detect_args_type()

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
            self.idx = skip_idx
            bound_args: List[Any] = []

            def take_text() -> Tuple[bool, str]:
                if self.idx >= len(elements):
                    return False, ""
                el = elements[self.idx]
                if el.type != "text":
                    return False, ""
                self.idx += 1
                return True, str(el.content)

            def take_segment(expected_cls) -> Tuple[bool, Any]:
                if self.idx >= len(elements):
                    return False, None
                el = elements[self.idx]
                if el.type == "text":
                    return False, None
                seg = el.content
                # 类型校验（MessageSegment 子类名匹配）
                if expected_cls is not None and not isinstance(seg, expected_cls):
                    return False, None
                self.idx += 1
                return True, seg

            # 逐个参数绑定
            for i, tp in enumerate(args_types):
                # Sentence：吞剩余文本元素
                # if getattr(tp, "__name__", None) == "Sentence":
                #     texts: List[str] = []
                #     while self.idx < len(elements) and elements[self.idx].type == "text":
                #         texts.append(str(elements[self.idx].content))
                #         self.idx += 1
                #     bound_args.append(" ".join(texts))
                #     continue

                # MessageSegment 子类：取下一个非文本元素
                if hasattr(tp, "__mro__") and any(c.__name__ == "MessageSegment" for c in getattr(tp, "__mro__", [])):
                    ok, seg = take_segment(tp)
                    if not ok:
                        if not is_required_list[i]:
                            # 可选参数缺失：使用默认值
                            default_val = analyser.param_defaults.get(i, None)
                            bound_args.append(default_val)
                            continue
                        return BindResult(False, tuple(), message="缺少非文本参数")
                    bound_args.append(seg)
                    continue

                # 基础类型（str/int/float/bool）：从文本元素读取并转换
                ok, text_val = take_text()
                if not ok:
                    if not is_required_list[i]:
                        default_val = analyser.param_defaults.get(i, None)
                        bound_args.append(default_val)
                        continue
                    return BindResult(False, tuple(), message="缺少文本参数")

                try:
                    if tp is str:
                        bound_args.append(text_val)
                    elif tp is int:
                        bound_args.append(int(text_val))
                    elif tp is float:
                        bound_args.append(float(text_val))
                    elif tp is bool:
                        bound_args.append(False if text_val.lower() in ("false", "0", "no") else True)
                    else:
                        # 未知类型（按字符串处理）
                        bound_args.append(text_val)
                except Exception:
                    return BindResult(False, tuple(), message="类型转换失败")
            LOG.debug(f"绑定成功: {bound_args}")
            return BindResult(True, tuple(bound_args))
        except Exception as e:
            LOG.debug(f"绑定异常: {e}")
            raise e

