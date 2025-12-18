from typing import List, Tuple
from ncatbot.core.event import MessageSegment
from ncatbot.utils import get_log
from ..utils import CommandRegistrationError
from ..utils import CommandSpec, OptionSpec, OptionGroupSpec, ParameterSpec, FuncSpec
import inspect

LOG = get_log(__name__)


class ParamsValidator:
    def __init__(self, descriptor: "FuncSpec", actual_params: List[inspect.Parameter]):
        self.descriptor = descriptor
        self.actual_params = actual_params
        self.func = descriptor.func

    def analyze_params(self):
        # 分析非位置参数
        options: List[OptionSpec] = getattr(self.func, "__command_options__", [])
        params: List[ParameterSpec] = getattr(self.func, "__command_params__", [])
        groups: List[OptionGroupSpec] = getattr(
            self.func, "__command_option_groups__", []
        )

        # 构建实际参数名到索引的映射（跳过 self/cls 与 event）
        actual_params = self.actual_params
        name_to_index = {p.name: idx for idx, p in enumerate(actual_params)}

        analyzed_params = []
        analyzed_options = []
        analyzed_groups = []

        decorated_param_indexes = set()

        # 校验 param
        for i, spec in enumerate(params):
            name = spec.name
            if name not in name_to_index:
                raise CommandRegistrationError(
                    self.func.__name__,
                    f"装饰器参数 '{name}' 未在函数签名中找到",
                    details=f"参数列表: {', '.join([p.name for p in actual_params])}",
                    suggestions=[
                        "确保 @param(name=...) 与函数形参名一致",
                        "将命名参数放在参数列表最后",
                    ],
                )
            idx = name_to_index[name]
            spec.index = idx
            analyzed_params.append(spec)
            decorated_param_indexes.add(idx)

        # 校验 option（使用 long_name 优先，其次 short_name 作为绑定参数名）
        for i, spec in enumerate(options):
            bind_name = spec.long_name or spec.short_name
            if not bind_name:
                raise CommandRegistrationError(
                    self.func.__name__,
                    "选项未提供 long_name 或 short_name",
                    details=f"选项序号: #{i + 1}",
                    suggestions=["为选项提供 long_name 或 short_name"],
                )
            if bind_name not in name_to_index:
                raise CommandRegistrationError(
                    self.func.__name__,
                    f"选项 '{bind_name}' 未在函数签名中找到对应形参",
                    details=f"参数列表: {', '.join([p.name for p in actual_params])}",
                    suggestions=[
                        "确保选项名与绑定的函数形参名一致",
                        "将选项对应参数放在参数列表最后",
                    ],
                )
            idx = name_to_index[bind_name]
            analyzed_options.append(spec)
            decorated_param_indexes.add(idx)

        # 校验 option_group（按 name 绑定）
        for i, spec in enumerate(groups):
            group_name = spec.name
            if not group_name:
                raise CommandRegistrationError(
                    self.func.__name__,
                    "选项组缺少 name",
                    details=f"选项组序号: #{i + 1}",
                    suggestions=["为选项组指定唯一的 name"],
                )
            if group_name not in name_to_index:
                raise CommandRegistrationError(
                    self.func.__name__,
                    f"选项组 '{group_name}' 未在函数签名中找到对应形参",
                    details=f"参数列表: {', '.join([p.name for p in actual_params])}",
                    suggestions=[
                        "确保选项组名与函数形参名一致",
                        "将选项组对应参数放在参数列表最后",
                    ],
                )
            idx = name_to_index[group_name]
            analyzed_groups.append(spec)
            decorated_param_indexes.add(idx)

        # 顺序校验：所有被装饰的参数必须连续出现在末尾
        earliest = (
            min(decorated_param_indexes)
            if decorated_param_indexes
            else len(actual_params)
        )
        trailing_range = set(range(earliest, len(actual_params)))
        if decorated_param_indexes and not decorated_param_indexes.issuperset(
            trailing_range
        ):
            # 找出位于尾部却未被装饰的参数
            offending = [
                actual_params[i].name
                for i in sorted(trailing_range - decorated_param_indexes)
            ]
            raise CommandRegistrationError(
                self.func.__name__,
                "装饰器参数必须位于参数列表尾部且连续",
                details=f"非装饰参数出现在尾部: {', '.join(offending)}",
                suggestions=[
                    "将所有命名/选项/选项组对应参数移到参数列表最后",
                    "确保它们在末尾连续排列",
                ],
            )

        spec = CommandSpec(
            analyzed_options,
            analyzed_groups,
            analyzed_params,
            self.detect_args_type(),
            self.descriptor.func,
        )
        return spec

    def detect_args_type(self) -> Tuple[List[type], List[bool]]:
        """探测参数表类型

        跳过第一二个参数，其余参数如果没写注解直接报错。
        前两个参数的验证已经在 _validate_signature 中完成。
        如果有 ignore 项，会在参数类型列表开头添加对应的 str 类型。

        Returns:
            Tuple[List[type], List[bool]]: (参数类型列表, 是否必需标记列表)
            - 参数类型列表包含 ignore 对应的 str 类型
            - 是否必需标记列表对应每个参数是否为必需参数

        Raises:
            ValueError: 当参数缺少类型注解或类型不支持时
        """
        param_list = self.actual_params  # 实际的命令参数
        LOG.debug(param_list)
        args_types = []
        is_required_list = []

        for param in param_list:
            annotation = param.annotation
            # 检查是否有注解
            if annotation == inspect.Parameter.empty:
                LOG.error(
                    f"函数参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{param.name}' 缺少类型注解"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"函数参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{param.name}' 缺少类型注解"
                )

            # TODO: 支持 Sentence 类型
            # 检查注解是否为支持的类型
            if annotation in (str, int, float, bool):
                args_types.append(annotation)
            elif isinstance(annotation, type) and issubclass(
                annotation, MessageSegment
            ):
                args_types.append(annotation)
            else:
                LOG.error(
                    f"函数参数类型不支持: {self.descriptor.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                LOG.info(
                    "支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类"
                )
                raise ValueError(
                    f"函数参数类型不支持: {self.descriptor.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持，"
                    f"支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类"
                )

            # 标记该参数是否为必需参数
            is_required_list.append(param.default == inspect.Parameter.empty)

        return args_types
