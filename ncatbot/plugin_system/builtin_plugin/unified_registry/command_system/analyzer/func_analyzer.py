"""函数分析器模块"""

from typing import Callable, List
from ncatbot.utils import get_log
from .sig_validator import SigValidator
from .param_validator import ParamsValidator
from ..utils import CommandSpec, FuncSpec
from ...utils import get_func_plugin_name

LOG = get_log(__name__)


def get_subclass_recursive(cls: type) -> List[type]:
    """递归获取类的所有子类

    Args:
        cls: 要获取子类的类

    Returns:
        List[type]: 包含该类及其所有子类的列表
    """
    return [cls] + [
        subcls
        for subcls in cls.__subclasses__()
        for subcls in get_subclass_recursive(subcls)
    ]


class FuncAnalyser:
    """函数分析器

    分析函数签名，验证参数类型，并提供参数转换功能。
    支持的参数类型：str, int, float, bool, Sentence, MessageSegment 的子类。
    """

    def __init__(self, func: Callable):
        self.func_descriptor = FuncSpec(func)

    def analyze(self) -> CommandSpec:
        self.sig_validator = SigValidator(self.func_descriptor)
        self.actual_args_start_index, self.actual_params = (
            self.sig_validator.analyze_signature()
        )
        self.params_validator = ParamsValidator(
            self.func_descriptor, self.actual_params
        )
        spec = self.params_validator.analyze_params()
        spec.plugin_name = get_func_plugin_name(self.func_descriptor.func)
        return spec
