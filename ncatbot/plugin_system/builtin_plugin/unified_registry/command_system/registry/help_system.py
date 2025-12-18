"""帮助系统

自动生成命令帮助文档和使用说明。
"""

from typing import List, Optional
from ..utils.specs import ParameterSpec, OptionSpec, OptionGroupSpec
from .registry import CommandSpec, CommandGroup


class HelpGenerator:
    """帮助文档生成器"""

    def __init__(self):
        self.max_width = 80
        self.indent = "  "

    def generate_command_help(self, cmd_def: CommandSpec) -> str:
        """生成单个命令的帮助文档"""
        lines = []

        # 命令头部
        lines.append(f"📋 命令: {cmd_def.name}")
        if cmd_def.aliases:
            lines.append(f"📋 别名: {', '.join(cmd_def.aliases)}")

        # 描述
        if cmd_def.description:
            lines.append("")
            lines.append("📝 描述:")
            lines.append(f"{self.indent}{cmd_def.description}")

        # 用法
        usage = self._generate_usage(cmd_def)
        lines.append("")
        lines.append("💡 用法:")
        lines.append(f"{self.indent}{usage}")

        # 位置参数
        positional_params = cmd_def.get_positional_parameters()
        if positional_params:
            lines.append("")
            lines.append("📍 位置参数:")
            for param in positional_params:
                lines.extend(self._format_parameter(param))

        # 命名参数
        named_params = cmd_def.get_named_parameters()
        if named_params:
            lines.append("")
            lines.append("🏷️ 命名参数:")
            for param in named_params:
                lines.extend(self._format_named_parameter(param))

        # 选项
        if cmd_def.options:
            lines.append("")
            lines.append("⚙️ 选项:")
            for option in cmd_def.options:
                lines.extend(self._format_option(option))

        # 选项组
        if cmd_def.option_groups:
            lines.append("")
            lines.append("📦 选项组:")
            for group in cmd_def.option_groups:
                lines.extend(self._format_option_group(group, cmd_def.options))

        # 示例
        examples = self._generate_examples(cmd_def)
        if examples:
            lines.append("")
            lines.append("🌰 示例:")
            for example in examples:
                lines.append(f"{self.indent}{example}")

        return "\n".join(lines)

    def generate_group_help(self, group: CommandGroup) -> str:
        """生成命令组的帮助文档"""
        lines = []

        # 组头部
        lines.append(f"📁 命令组: {group.name}")
        if group.description:
            lines.append(f"📝 描述: {group.description}")

        # 子命令
        if group.commands:
            lines.append("")
            lines.append("🔧 可用命令:")
            for name, cmd_def in group.commands.items():
                if name == cmd_def.name:  # 避免显示别名
                    desc = cmd_def.description or "无描述"
                    lines.append(f"{self.indent}{name:<20} {desc}")

        # 子组
        if group.subgroups:
            lines.append("")
            lines.append("📁 子命令组:")
            for name, subgroup in group.subgroups.items():
                desc = subgroup.description or "无描述"
                lines.append(f"{self.indent}{name:<20} {desc}")

        return "\n".join(lines)

    def generate_command_list(self, commands: List[CommandSpec]) -> str:
        """生成命令列表"""
        lines = ["📋 所有可用命令:"]
        lines.append("")

        # 按名称排序
        sorted_commands = sorted(commands, key=lambda x: x.name)

        for cmd_def in sorted_commands:
            desc = cmd_def.description or "无描述"
            # 截断过长的描述
            if len(desc) > 50:
                desc = desc[:47] + "..."
            lines.append(f"{self.indent}{cmd_def.name:<20} {desc}")

        lines.append("")
        lines.append("💡 使用 /<命令名> --help 查看详细帮助")

        return "\n".join(lines)

    def _generate_usage(self, cmd_def: CommandSpec) -> str:
        """生成用法字符串"""
        parts = [f"/{cmd_def.name}"]

        # 位置参数
        for param in cmd_def.get_positional_parameters():
            if param.required:
                parts.append(f"<{param.name}>")
            else:
                parts.append(f"[{param.name}]")

        # 命名参数
        named_params = cmd_def.get_named_parameters()
        if named_params:
            parts.append("[命名参数...]")

        # 选项
        if cmd_def.options:
            parts.append("[选项...]")

        return " ".join(parts)

    def _format_parameter(self, param: ParameterSpec) -> List[str]:
        """格式化位置参数"""
        lines = []

        # 参数名和类型
        type_name = param.get_friendly_type_name()
        param_line = f"{self.indent}{param.name}"
        if not param.required:
            param_line += " (可选)"
        param_line += f" - {type_name}"
        lines.append(param_line)

        # 描述
        if param.description:
            lines.append(f"{self.indent}{self.indent}{param.description}")

        # 默认值
        if not param.required and param.default is not None:
            lines.append(f"{self.indent}{self.indent}默认值: {param.default}")

        # 选择值
        if param.choices:
            choices_str = ", ".join(str(c) for c in param.choices)
            lines.append(f"{self.indent}{self.indent}可选值: {choices_str}")

        # 多类型示例
        if param.is_multi_type():
            union_type = param.get_union_type()
            for type_obj in union_type.types:
                examples = param.get_examples_for_type(type_obj)
                if examples:
                    type_name = type_obj.__name__
                    examples_str = ", ".join(examples[:3])
                    lines.append(
                        f"{self.indent}{self.indent}{type_name}示例: {examples_str}"
                    )

        return lines

    def _format_named_parameter(self, param: ParameterSpec) -> List[str]:
        """格式化命名参数"""
        lines = []

        # 参数名和类型
        type_name = param.get_friendly_type_name()
        param_line = f"{self.indent}--{param.name}"
        if not param.required:
            param_line += " (可选)"
        param_line += f" - {type_name}"
        lines.append(param_line)

        # 描述和其他信息同位置参数
        lines.extend(self._format_parameter(param)[1:])  # 跳过第一行

        return lines

    def _format_option(self, option: OptionSpec) -> List[str]:
        """格式化选项"""
        lines = []

        # 选项名
        names = option.get_option_names()
        option_line = f"{self.indent}{', '.join(names)}"

        if option.needs_value():
            type_name = (
                option.value_type.__name__
                if hasattr(option.value_type, "__name__")
                else str(option.value_type)
            )
            option_line += f" <{type_name}>"

        lines.append(option_line)

        # 描述
        if option.description:
            lines.append(f"{self.indent}{self.indent}{option.description}")

        # 默认值
        if option.default_value is not None and not option.is_flag():
            lines.append(f"{self.indent}{self.indent}默认值: {option.default_value}")

        # 选择值
        if option.choices:
            choices_str = ", ".join(str(c) for c in option.choices)
            lines.append(f"{self.indent}{self.indent}可选值: {choices_str}")

        return lines

    def _format_option_group(
        self, group: OptionGroupSpec, all_options: List[OptionSpec]
    ) -> List[str]:
        """格式化选项组"""
        lines = []

        # 组名
        group_line = f"{self.indent}{group.name}"
        if group.is_required:
            group_line += " (必选)"
        lines.append(group_line)

        # 组描述
        if group.description:
            lines.append(f"{self.indent}{self.indent}{group.description}")

        # 组内选项 - 显示所有可选项
        for choice in group.choices:
            choice_line = f"{self.indent}--{choice}"
            if choice == group.default:
                choice_line += " (默认)"
            lines.append(choice_line)

        return lines

    def _generate_examples(self, cmd_def: CommandSpec) -> List[str]:
        """生成使用示例"""
        examples = []

        # 基本示例
        basic_example = f"/{cmd_def.name}"

        # 添加必需的位置参数
        required_pos = [p for p in cmd_def.get_positional_parameters() if p.required]
        for param in required_pos:
            examples_for_type = param.get_examples_for_type(param.get_type_list()[0])
            if examples_for_type:
                basic_example += f" {examples_for_type[0]}"
            else:
                basic_example += f" <{param.name}>"

        examples.append(basic_example)

        # 带选项的示例
        if cmd_def.options:
            with_options = basic_example
            flag_options = [opt for opt in cmd_def.options if opt.is_flag()]
            if flag_options:
                opt = flag_options[0]
                if opt.short_name:
                    with_options += f" {opt.short_name}"
                elif opt.long_name:
                    with_options += f" {opt.long_name}"

            value_options = [opt for opt in cmd_def.options if opt.needs_value()]
            if value_options:
                opt = value_options[0]
                option_name = opt.long_name or opt.short_name
                if opt.choices:
                    value = opt.choices[0]
                elif opt.default_value is not None:
                    value = opt.default_value
                else:
                    value = "value"
                with_options += f" {option_name}={value}"

            if with_options != basic_example:
                examples.append(with_options)

        return examples


def format_error_with_help(
    error_msg: str, cmd_def: Optional[CommandSpec] = None
) -> str:
    """格式化错误信息并附加帮助提示"""
    lines = [f"❌ {error_msg}"]

    if cmd_def:
        lines.append("")
        lines.append("💡 正确用法:")

        # 生成简化的用法提示
        help_gen = HelpGenerator()
        usage = help_gen._generate_usage(cmd_def)
        lines.append(f"   {usage}")

        lines.append("")
        lines.append(f"📖 详细帮助: /{cmd_def.name} --help")

    return "\n".join(lines)
