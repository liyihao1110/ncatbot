"""函数分析器模块"""

from typing import Callable, Union, List, Tuple
import inspect
from ncatbot.core.event import BaseMessageEvent, Text, MessageSegment
from ncatbot.core.event.message_segment.message_segment import PlainText
from ncatbot.core.event.message_segment.sentence import Sentence
from ncatbot.utils import get_log
from .help_builder import build_command_help

LOG = get_log(__name__)


def get_subclass_recursive(cls: type) -> List[type]:
    """递归获取类的所有子类
    
    Args:
        cls: 要获取子类的类
        
    Returns:
        List[type]: 包含该类及其所有子类的列表
    """
    return [cls] + [subcls for subcls in cls.__subclasses__() for subcls in get_subclass_recursive(subcls)]


class FuncAnalyser:
    """函数分析器
    
    分析函数签名，验证参数类型，并提供参数转换功能。
    支持的参数类型：str, int, float, bool, Sentence, MessageSegment 的子类。
    """
    
    def __init__(self, func: Callable, ignore=None):
        self.func = func
        self.alias = getattr(func, "__alias__", [])
        self.ignore = ignore  # 转换时的忽略项（通常是命令匹配的前缀）
        
        # 生成 metadata 以便代码更易于理解
        self.func_name = func.__name__
        self.func_module = func.__module__
        self.func_qualname = func.__qualname__
        self.signature = inspect.signature(func)
        self.param_list = list(self.signature.parameters.values())
        self.param_names = [param.name for param in self.param_list]
        self.param_annotations = [param.annotation for param in self.param_list]
        
        # 新增：分析参数默认值
        self.param_defaults = {}  # 存储参数默认值 {相对索引: 默认值}
        self.required_param_count = 0  # 必需参数数量（不包括 self 和 event）
        
        self._analyze_signature()

    def _analyze_signature(self):
        self._validate_signature()
        self._analyze_defaults()
        self.args_type, self.is_required_list = self._detect_args_type()

    def _validate_signature(self):
        # TODO: 提示对方法签名的严格要求
        """验证函数签名是否符合要求，并确定 event 与实际参数起始索引"""
        if len(self.param_list) < 1:
            LOG.error(f"函数参数不足: {self.func_qualname} 需要至少包含 event 参数")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"函数参数不足: {self.func_qualname} 需要至少包含 event 参数")

        first_param = self.param_list[0]

        # 形态一：实例方法，要求参数形如 (self, event: BaseMessageEvent, ...)
        if first_param.name == "self":
            if len(self.param_list) < 2:
                LOG.error(f"函数参数不足: {self.func_qualname} 需要包含 event 参数")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"函数参数不足: {self.func_qualname} 需要包含 event 参数")
            event_param = self.param_list[1]
            if event_param.annotation == inspect.Parameter.empty:
                LOG.error(f"event 参数缺少类型注解: {self.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"event 参数缺少类型注解: {self.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解")
            if not (isinstance(event_param.annotation, type) and issubclass(event_param.annotation, BaseMessageEvent)):
                LOG.error(f"event 参数类型注解错误: {self.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"event 参数类型注解错误: {self.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类")
            self.event_param_index = 1
        else:
            # 形态二：普通/静态方法，要求(event: BaseMessageEvent, ...)
            event_param = first_param
            if event_param.annotation == inspect.Parameter.empty:
                LOG.error(f"event 参数缺少类型注解: {self.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"event 参数缺少类型注解: {self.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解")
            if not (isinstance(event_param.annotation, type) and issubclass(event_param.annotation, BaseMessageEvent)):
                LOG.error(f"event 参数类型注解错误: {self.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"event 参数类型注解错误: {self.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类")
            self.event_param_index = 0

        # 计算实际参数的起始索引与切片
        self.actual_args_start_index = self.event_param_index + 1
        self.actual_params = self.param_list[self.actual_args_start_index:]
    
    def _analyze_defaults(self):
        """分析函数参数的默认值"""
        # 分析实际的命令参数（跳过 self/cls 与 event）
        actual_params = self.actual_params
        
        for i, param in enumerate(actual_params):
            if param.default != inspect.Parameter.empty:
                # 存储默认值，使用相对于实际参数的索引
                self.param_defaults[i] = param.default
                LOG.debug(f"发现默认参数: {param.name} = {param.default}")
            else:
                # 统计必需参数数量
                self.required_param_count += 1
        
        # 验证默认参数的位置（默认参数必须在必需参数之后）
        has_default = False
        for param in actual_params:
            if param.default != inspect.Parameter.empty:
                has_default = True
            elif has_default:
                # 发现默认参数后又有必需参数，这是不允许的
                LOG.error(f"参数顺序错误: {self.func_qualname} 中默认参数 '{param.name}' 后不能有必需参数")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"参数顺序错误: {self.func_qualname} 中默认参数后不能有必需参数 '{param.name}'")
        
        LOG.debug(f"函数 {self.func_name}: 必需参数={self.required_param_count}, 默认参数={len(self.param_defaults)}")
    
    def build_help_info(self, path, simple: bool = False) -> str:
        """构建命令的帮助信息
        
        Args:
            path: 命令路径（元组形式）
            simple: 如果为 True，只显示示例用法
        
        Returns:
            str: 帮助信息，包含参数解释和/或示例用法
            
        Examples:
            完整格式: greet <name: str> [age: int=18] [title: str="朋友"]
                     示例: greet 小明 25 同学
            简化格式: greet 小明 25 同学
        """
        # 构建命令路径
        if isinstance(path, tuple):
            command_path = " ".join(path)
        else:
            command_path = str(path)
        
        # 处理实际的命令参数并委托给帮助构建器
        actual_params = self.actual_params
        return build_command_help(command_path, actual_params, simple)
    
    def _detect_args_type(self) -> Tuple[List[type], List[bool]]:
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
        
        # 在参数类型列表开头添加 ignore 对应的 str 类型
        if self.ignore is not None:
            for _ in self.ignore:
                args_types.append(str)
                is_required_list.append(True)  # ignore 参数总是必需的
        
        for param in param_list:
            annotation = param.annotation
            # 检查是否有注解
            if annotation == inspect.Parameter.empty:
                LOG.error(f"函数参数缺少类型注解: {self.func_qualname} 的参数 '{param.name}' 缺少类型注解")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"函数参数缺少类型注解: {self.func_qualname} 的参数 '{param.name}' 缺少类型注解")
            
            # 检查注解是否为支持的类型
            if annotation in (str, int, float, bool):
                args_types.append(annotation)
            elif annotation == Sentence:  # 新增：支持 Sentence 类型
                # TODO: 稳定 Sentence 类型
                args_types.append(annotation)
            elif isinstance(annotation, type) and issubclass(annotation, MessageSegment):
                args_types.append(annotation)
            else:
                LOG.error(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                LOG.info(f"支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类")
                raise ValueError(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持，"
                               f"支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类")
            
            # 标记该参数是否为必需参数
            is_required_list.append(param.default == inspect.Parameter.empty)
        
        return args_types, is_required_list

    def detect_args_type(self) -> Tuple[List[type], List[bool]]:
        return self.args_type, self.is_required_list
    