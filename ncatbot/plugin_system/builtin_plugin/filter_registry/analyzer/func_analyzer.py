"""函数分析器模块"""

from typing import Callable, Union, List, Tuple
import inspect
from ncatbot.core.event import BaseMessageEvent, Text, MessageSegment
from ncatbot.core.event.message_segment.message_segment import PlainText
from ncatbot.core.event.message_segment.sentence import Sentence
from ncatbot.utils import get_log

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
        
        # 验证函数签名
        self._validate_signature()
    
    def _validate_signature(self):
        """验证函数签名是否符合要求"""
        if len(self.param_list) < 2:
            LOG.error(f"函数参数不足: {self.func_qualname} 需要至少两个参数")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"函数参数不足: {self.func_qualname} 需要至少两个参数")
        
        # 检查第一个参数名必须是 self
        first_param = self.param_list[0]
        if first_param.name != "self":
            LOG.error(f"第一个参数名必须是 'self': {self.func_qualname} 的第一个参数是 '{first_param.name}'")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第一个参数名必须是 'self': {self.func_qualname} 的第一个参数是 '{first_param.name}'")
        
        # 检查第二个参数必须被注解为 BaseMessageEvent 的子类
        second_param = self.param_list[1]
        if second_param.annotation == inspect.Parameter.empty:
            LOG.error(f"第二个参数缺少类型注解: {self.func_qualname} 的参数 '{second_param.name}' 需要 BaseMessageEvent 或其子类注解")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第二个参数缺少类型注解: {self.func_qualname} 的参数 '{second_param.name}' 需要 BaseMessageEvent 或其子类注解")
        
        # 检查第二个参数是否为 BaseMessageEvent 或其子类
        if not (isinstance(second_param.annotation, type) and issubclass(second_param.annotation, BaseMessageEvent)):
            LOG.error(f"第二个参数类型注解错误: {self.func_qualname} 的参数 '{second_param.name}' 注解为 {second_param.annotation}，需要 BaseMessageEvent 或其子类")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第二个参数类型注解错误: {self.func_qualname} 的参数 '{second_param.name}' 注解为 {second_param.annotation}，需要 BaseMessageEvent 或其子类")
    
    def build_help_info(self) -> str:
        """构建帮助信息
        
        Returns:
            str: 函数的帮助信息
        """
        # 生成一行帮助
        pass
    
    def detect_args_type(self) -> List[type]:
        """探测参数表类型
        
        跳过第一二个参数，其余参数如果没写注解直接报错。
        前两个参数的验证已经在 _validate_signature 中完成。
        如果有 ignore 项，会在参数类型列表开头添加对应的 str 类型。
        
        Returns:
            List[type]: 参数类型列表（包含 ignore 对应的 str 类型）
            
        Raises:
            ValueError: 当参数缺少类型注解或类型不支持时
        """
        param_list = self.param_list[2:]  # 跳过前两个参数
        LOG.debug(param_list)
        args_types = []
        
        # 在参数类型列表开头添加 ignore 对应的 str 类型
        if self.ignore is not None:
            for _ in self.ignore:
                args_types.append(str)
        
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
                args_types.append(annotation)
            elif isinstance(annotation, type) and issubclass(annotation, MessageSegment):
                args_types.append(annotation)
            else:
                LOG.error(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                LOG.info(f"支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类")
                raise ValueError(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持，"
                               f"支持的类型: str, int, float, bool, Sentence 或 MessageSegment 的子类")
        
        return args_types
    
    def convert_args(self, event: BaseMessageEvent) -> Tuple[bool, Tuple[...]]:
        """将事件中的参数转换为函数参数
        
        需要保证参数类型正确，否则异常。
        现在 ignore 项也作为正常的 str 参数进行匹配，返回时会排除前面的 ignore 参数。
        
        Args:
            event: 消息事件
            
        Returns:
            Tuple[bool, Tuple[...]]: (是否成功, 转换后的参数元组，不包含 ignore 参数)
        """
        def add_arg(arg: Union[str, MessageSegment]) -> bool:
            if self.cur_index >= len(args_type):
                return False
            
            try:
                if args_type[self.cur_index] in (str, int, float, bool):
                    # 添加类型转换错误处理
                    if args_type[self.cur_index] == str:
                        converted_arg = str(arg)
                    elif args_type[self.cur_index] == int:
                        converted_arg = int(arg)
                    elif args_type[self.cur_index] == float:
                        converted_arg = float(arg)
                    elif args_type[self.cur_index] == bool:
                        if arg.lower() == "false" or arg == '0':
                            converted_arg = False
                        else:
                            converted_arg = True
                    
                    self.args_list.append(converted_arg)
                    self.cur_index += 1
                elif args_type[self.cur_index] == Sentence:  # Sentence 类型处理
                    # Sentence 类型：直接创建 Sentence 对象
                    sentence = Sentence(arg)
                    self.args_list.append(sentence)
                    self.cur_index += 1
                elif issubclass(args_type[self.cur_index], MessageSegment):
                    if not isinstance(arg, MessageSegment):
                        return False  # 类型不匹配
                    self.args_list.append(arg)
                    self.cur_index += 1
                return True
            except (ValueError, TypeError) as e:
                LOG.warning(f"参数类型转换失败: {arg} -> {args_type[self.cur_index]}, 错误: {e}")
                return False
            
        def process_text_segment(text_content: str) -> bool:
            """处理 Text 消息段，支持部分匹配后剩余内容给 Sentence"""

            # 按空格分割处理
            cur_str_list = [s.strip() for s in text_content.split(" ") if s.strip()]

            for i, str_arg in enumerate(cur_str_list):
                # 在处理每个单词前，检查当前参数是否需要 Sentence
                if (self.cur_index < len(args_type) and 
                    args_type[self.cur_index] == Sentence):
                    # 如果当前参数需要 Sentence，将剩余的所有单词组合起来
                    remaining_text = " ".join(cur_str_list[i:])
                    return add_arg(remaining_text)
                
                # 否则正常处理单个单词
                if not add_arg(str_arg):
                    return False
            
            return True
            
        args_type = self.detect_args_type()
        LOG.debug(args_type)
        self.args_list = []
        self.cur_index = 0
        ignore_count = len(self.ignore) if self.ignore is not None else 0
        
        
        for arg in event.message.messages:
            if isinstance(arg, PlainText):
                if not process_text_segment(arg.text):
                    return (False, tuple(self.args_list))
            else:
                if not add_arg(arg):
                    return (False, tuple(self.args_list))
        
        # 最后检查是否所有必需参数都已填充
        if self.cur_index < len(args_type):
            LOG.debug(f"参数数量不足: 需要 {len(args_type)} 个，实际获得 {self.cur_index} 个")
            return (False, tuple(self.args_list))
        
        # 返回时排除前面的 ignore 参数
        actual_args = tuple(self.args_list[ignore_count:])
        return (True, actual_args)
