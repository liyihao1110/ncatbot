from typing import Callable, List
from ..utils import CommandRegistrationError, OptionSpec, OptionGroupSpec, ParameterSpec


class DecoratorValidator:
    """装饰器验证器

    验证装饰器的合理性和一致性。
    """

    @staticmethod
    def validate_function_decorators(func: Callable):
        """验证函数上的装饰器

        验证内容包括：
        1. 选项名冲突检查（短选项和长选项）
        2. 参数名冲突检查
        3. 选项组验证
        4. 装饰器之间的兼容性检查
        5. 选项名格式验证
        6. 选项组值冲突检查（与其他选项组值、选项名、参数名）
        """
        errors = []
        warnings = []

        # 获取装饰器信息 (Spec 对象列表)
        options: List[OptionSpec] = getattr(
            func, "__command_options__", []
        )  # List[OptionSpec]
        params: List[ParameterSpec] = getattr(
            func, "__command_params__", []
        )  # List[ParameterSpec]
        groups: List[OptionGroupSpec] = getattr(
            func, "__command_option_groups__", []
        )  # List[OptionGroupSpec]

        # 1. 验证选项名冲突和格式
        short_options = {}  # 短选项名 -> 选项信息
        long_options = {}  # 长选项名 -> 选项信息
        all_option_names = set()  # 所有选项名（用于冲突检测）

        for i, option in enumerate(options):
            option_info = f"选项 #{i + 1}"

            # 验证短选项
            if option.short_name:
                short_name = option.short_name

                # 格式验证
                if not short_name.isalnum() or len(short_name) != 1:
                    errors.append(
                        f"{option_info}: 短选项名 '{short_name}' 必须是单个字母或数字"
                    )

                # 冲突检查
                if short_name in short_options:
                    errors.append(
                        f"{option_info}: 短选项名 '{short_name}' 与选项 #{short_options[short_name]['index'] + 1} 冲突"
                    )
                else:
                    short_options[short_name] = {"index": i, "option": option}
                    all_option_names.add(short_name)

            # 验证长选项
            if option.long_name:
                long_name = option.long_name

                # 格式验证
                if not long_name.replace("-", "").replace("_", "").isalnum():
                    errors.append(
                        f"{option_info}: 长选项名 '{long_name}' 只能包含字母、数字、连字符和下划线"
                    )

                if long_name.startswith("--"):
                    errors.append(
                        f"{option_info}: 长选项名 '{long_name}' 不应包含 '--' 前缀"
                    )
                    warnings.append(
                        f"{option_info}: 建议将 '{long_name}' 改为 '{long_name.lstrip('-')}'"
                    )

                if len(long_name) < 2:
                    errors.append(
                        f"{option_info}: 长选项名 '{long_name}' 至少需要两个字符"
                    )

                # 冲突检查
                if long_name in long_options:
                    errors.append(
                        f"{option_info}: 长选项名 '{long_name}' 与选项 #{long_options[long_name]['index'] + 1} 冲突"
                    )
                else:
                    long_options[long_name] = {"index": i, "option": option}
                    all_option_names.add(long_name)

            # 检查选项是否为空
            if not option.short_name and not option.long_name:
                errors.append(f"{option_info}: 选项必须至少指定一个短选项名或长选项名")

        # 2. 验证参数名冲突和格式
        param_names = {}  # 参数名 -> 参数信息

        for i, param in enumerate(params):
            param_info = f"参数 #{i + 1}"
            name = param.name

            # 格式验证
            if not name.replace("_", "").replace("-", "").isalnum():
                errors.append(
                    f"{param_info}: 参数名 '{name}' 只能包含字母、数字、连字符和下划线"
                )

            # 冲突检查
            if name in param_names:
                errors.append(
                    f"{param_info}: 参数名 '{name}' 与参数 #{param_names[name]['index'] + 1} 冲突"
                )
            else:
                param_names[name] = {"index": i, "param": param}

            # 与选项名冲突检查
            if name in all_option_names:
                errors.append(f"{param_info}: 参数名 '{name}' 与选项名冲突")

        # 3. 验证选项组
        group_names = {}  # 组名 -> 组信息
        all_group_choices = set()  # 所有选项组的值（用于冲突检测）

        for i, group in enumerate(groups):
            group_info = f"选项组 #{i + 1}"
            name = group.name

            if not name:
                errors.append(f"{group_info}: 选项组必须指定名称")
                continue

            # 组名冲突检查
            if name in group_names:
                errors.append(
                    f"{group_info}: 选项组名 '{name}' 与选项组 #{group_names[name]['index'] + 1} 冲突"
                )
            else:
                group_names[name] = {"index": i, "group": group}

            # 组名和选项名冲突检查
            if name in all_option_names:
                errors.append(f"{group_info}: 选项组名 '{name}' 与选项名冲突")

            # 组名和参数名冲突检查
            if name in param_names:
                errors.append(f"{group_info}: 选项组名 '{name}' 与参数名冲突")

            # 验证选项组配置
            choices = group.choices
            if not choices:
                errors.append(f"{group_info}: 选项组 '{name}' 必须指定选项列表")
            else:
                # 检查选项是否重复
                if len(choices) != len(set(choices)):
                    errors.append(f"{group_info}: 选项组 '{name}' 的选项列表包含重复项")

                # 检查默认值是否在选项中
                default = group.default
                if default and default not in choices:
                    errors.append(
                        f"{group_info}: 选项组 '{name}' 的默认值 '{default}' 不在选项列表中"
                    )

                # 检查选项组的值与其他选项组的值冲突
                for choice in choices:
                    if choice in all_group_choices:
                        # 找到冲突的选项组
                        conflicting_group = None
                        for other_group_name, other_group_info in group_names.items():
                            if choice in other_group_info["group"].choices:
                                conflicting_group = f"选项组 '{other_group_name}'"
                                break
                        if conflicting_group:
                            errors.append(
                                f"{group_info}: 选项组 '{name}' 的值 '{choice}' 与 {conflicting_group} 的值冲突"
                            )
                        else:
                            errors.append(
                                f"{group_info}: 选项组 '{name}' 的值 '{choice}' 与其他选项组的值冲突"
                            )
                    all_group_choices.add(choice)

                # 检查选项组的值与短选项名冲突
                for choice in choices:
                    if choice in short_options:
                        conflicting_option = short_options[choice]
                        errors.append(
                            f"{group_info}: 选项组 '{name}' 的值 '{choice}' 与短选项 '{choice}' (选项 #{conflicting_option['index'] + 1}) 冲突"
                        )

                # 检查选项组的值与长选项名冲突
                for choice in choices:
                    if choice in long_options:
                        conflicting_option = long_options[choice]
                        errors.append(
                            f"{group_info}: 选项组 '{name}' 的值 '{choice}' 与长选项 '{choice}' (选项 #{conflicting_option['index'] + 1}) 冲突"
                        )

                # 检查选项组的值与参数名冲突
                for choice in choices:
                    if choice in param_names:
                        conflicting_param = param_names[choice]
                        errors.append(
                            f"{group_info}: 选项组 '{name}' 的值 '{choice}' 与参数 '{choice}' (参数 #{conflicting_param['index'] + 1}) 冲突"
                        )

        # 5. 生成详细的错误信息和建议
        if errors:
            error_details = []
            suggestions = []

            for error in errors:
                error_details.append(f"  • {error}")

            # 生成建议
            if "选项名冲突" in "; ".join(errors):
                suggestions.append("检查是否有重复的选项名，确保每个选项名都是唯一的")

            if "参数名冲突" in "; ".join(errors):
                suggestions.append("检查是否有重复的参数名，确保每个参数名都是唯一的")

            if "格式" in "; ".join(errors):
                suggestions.append(
                    "确保选项名和参数名符合命名规范：字母、数字、连字符和下划线"
                )

            if "选项组" in "; ".join(errors):
                suggestions.append("检查选项组配置，确保名称唯一且选项列表正确")

            if "选项组值" in "; ".join(errors) and "冲突" in "; ".join(errors):
                suggestions.append(
                    "检查选项组的值是否与其他选项组的值、选项名或参数名冲突，确保所有名称都是唯一的"
                )

            raise CommandRegistrationError(
                func.__name__,
                f"装饰器验证失败，发现 {len(errors)} 个错误",
                details="\n".join(error_details),
                suggestions=suggestions,
            )

        # 6. 输出警告（如果有）
        if warnings:
            import warnings as warnings_module

            for warning in warnings:
                warnings_module.warn(f"命令 '{func.__name__}': {warning}", UserWarning)
