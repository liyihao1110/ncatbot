"""帮助信息构建模块"""

import inspect
from typing import List


def _get_example_value(param_type, param_name: str) -> str:
    """根据参数类型生成示例值"""
    if param_type == str:
        lower = param_name.lower()
        if 'name' in lower:
            return "小明"
        if 'user' in lower:
            return "用户名"
        if 'title' in lower:
            return "标题"
        return "文本"
    if param_type == int:
        lower = param_name.lower()
        if 'age' in lower:
            return "25"
        if 'count' in lower:
            return "10"
        return "123"
    if param_type == float:
        lower = param_name.lower()
        if 'price' in lower:
            return "99.99"
        if 'rate' in lower:
            return "0.85"
        return "3.14"
    if param_type == bool:
        return "true"

    if hasattr(param_type, '__name__') and param_type.__name__ == 'Sentence':
        return "这是一句包含 空格的完整句子"

    if hasattr(param_type, '__name__'):
        type_name = param_type.__name__
        if type_name == 'At':
            return "@某人"
        if type_name == 'Image':
            return "[图片]"
        if type_name == 'Face':
            return "[表情]"
        if type_name == 'Video':
            return "[视频]"
        if type_name == 'Record':
            return "[语音]"
        if type_name == 'Reply':
            return "[回复消息]"
        if type_name in ['Text', 'PlainText']:
            return "纯文本"
        return f"[{type_name}]"

    return "参数"


def _build_parameter_signature(command_path: str, actual_params: List[inspect.Parameter]) -> str:
    help_info = command_path
    for param in actual_params:
        param_name = param.name
        param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
        if param.default != inspect.Parameter.empty:
            default_value = param.default
            if isinstance(default_value, str):
                help_info += f" [{param_name}: {param_type}=\"{default_value}\"]"
            else:
                help_info += f" [{param_name}: {param_type}={default_value}]"
        else:
            help_info += f" <{param_name}: {param_type}>"
    return help_info


def _generate_single_example(command_path: str, params: List[inspect.Parameter]) -> str | None:
    example_parts = [command_path]
    for param in params:
        param_type = param.annotation
        example_value = _get_example_value(param_type, param.name)
        if example_value:
            example_parts.append(example_value)
    return " ".join(example_parts) if len(example_parts) > 1 else None


def _generate_usage_examples(command_path: str, actual_params: List[inspect.Parameter]) -> str:
    if not actual_params:
        return f"示例: {command_path}"

    examples: list[str] = []
    full_example = _generate_single_example(command_path, actual_params)
    if full_example:
        examples.append(full_example)

    required_only = [p for p in actual_params if p.default == inspect.Parameter.empty]
    if required_only and len(required_only) < len(actual_params):
        minimal_example = _generate_single_example(command_path, required_only)
        if minimal_example and minimal_example != full_example:
            examples.append(minimal_example)

    if not examples:
        return f"示例: {command_path}"
    return "\n".join(f"示例: {example}" for example in examples)


def build_command_help(command_path: str, actual_params: List[inspect.Parameter], simple: bool = False) -> str:
    if simple:
        return _generate_usage_examples(command_path, actual_params)
    signature = _build_parameter_signature(command_path, actual_params)
    examples = _generate_usage_examples(command_path, actual_params)
    if examples:
        signature += "\n" + examples
    return signature


