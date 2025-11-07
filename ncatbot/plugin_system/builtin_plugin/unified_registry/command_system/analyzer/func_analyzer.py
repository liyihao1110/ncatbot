"""函数分析器模块"""

from typing import Callable, List
from ncatbot.utils import get_log
from .sig_validator import SigValidator
from .param_validator import ParamsValidator
from ..utils import CommandSpec, FuncSpec
from ncatbot.utils import ncatbot_config
from pathlib import Path
import inspect

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
        plugin_dir = Path(ncatbot_config.plugin.plugins_dir).resolve()
        file = inspect.getsourcefile(self.func_descriptor.func)
        spec.plugin_name = "ncatbot"
        if file:
            file_path = Path(file).resolve()            
            try:
                relative_path = file_path.relative_to(plugin_dir)
                if relative_path.parts:
                    spec.plugin_name = relative_path.parts[0]
            except ValueError:
                pass
        return spec