"""函数分析器模块"""

from typing import Callable, List
import inspect
from ncatbot.utils import get_log
from .sig_validator import SigValidator
from .param_validator import ParamsValidator, CommonadSpec

LOG = get_log(__name__)


def get_subclass_recursive(cls: type) -> List[type]:
    """递归获取类的所有子类
    
    Args:
        cls: 要获取子类的类
        
    Returns:
        List[type]: 包含该类及其所有子类的列表
    """
    return [cls] + [subcls for subcls in cls.__subclasses__() for subcls in get_subclass_recursive(subcls)]

class FuncDesciptor:
    def __init__(self, func: Callable):
        self.func = func
        self.alias = getattr(func, "__alias__", [])
        
        # 生成 metadata 以便代码更易于理解
        self.func_name = func.__name__
        self.func_module = func.__module__
        self.func_qualname = func.__qualname__
        self.signature = inspect.signature(func)
        self.param_list = list(self.signature.parameters.values())
        self.param_names = [param.name for param in self.param_list]
        self.param_annotations = [param.annotation for param in self.param_list]

class FuncAnalyser:
    """函数分析器
    
    分析函数签名，验证参数类型，并提供参数转换功能。
    支持的参数类型：str, int, float, bool, Sentence, MessageSegment 的子类。
    """
    
    def __init__(self, func: Callable):
        self.func_descriptor = FuncDesciptor(func)

    def analyze(self) -> CommonadSpec:
        self.sig_validator = SigValidator(self.func_descriptor)
        self.params_validator = ParamsValidator(self.func_descriptor, self.actual_params)
        self.actual_args_start_index, self.actual_params = self.sig_validator.analyze_signature()
        return self.params_validator.analyze_params()
    
    
    