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
        
        # 新增：分析参数默认值
        self.param_defaults = {}  # 存储参数默认值 {相对索引: 默认值}
        self.required_param_count = 0  # 必需参数数量（不包括 self 和 event）
        
        # 验证函数签名
        self._validate_signature()
        
        # 分析默认值（在验证签名之后）
        self._analyze_defaults()
    
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
    
    def _analyze_defaults(self):
        """分析函数参数的默认值"""
        # 跳过前两个参数（self 和 event），分析实际的命令参数
        actual_params = self.param_list[2:]
        
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
        
        # 跳过 self 和 event 参数，处理实际的命令参数
        actual_params = self.param_list[2:]
        
        if simple:
            # 简化模式：只显示示例用法
            return self._generate_usage_examples(command_path, actual_params)
        else:
            # 完整模式：显示参数解释 + 示例用法
            help_info = self._build_parameter_signature(command_path, actual_params)
            examples = self._generate_usage_examples(command_path, actual_params)
            if examples:
                help_info += "\n" + examples
            return help_info
    
    def _build_parameter_signature(self, command_path: str, actual_params: list) -> str:
        """构建参数签名描述"""
        help_info = command_path
        
        for i, param in enumerate(actual_params):
            param_name = param.name
            param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
            
            # 检查是否有默认值
            if param.default != inspect.Parameter.empty:
                # 可选参数：用方括号包围，显示默认值
                default_value = param.default
                if isinstance(default_value, str):
                    help_info += f" [{param_name}: {param_type}=\"{default_value}\"]"
                else:
                    help_info += f" [{param_name}: {param_type}={default_value}]"
            else:
                # 必需参数：用尖括号包围
                help_info += f" <{param_name}: {param_type}>"
        
        return help_info
    
    def _generate_usage_examples(self, command_path: str, actual_params: list) -> str:
        """生成使用示例"""
        if not actual_params:
            return f"示例: {command_path}"
        
        examples = []
        
        # 生成完整示例（包含所有参数）
        full_example = self._generate_single_example(command_path, actual_params, include_all=True)
        if full_example:
            examples.append(full_example)
        
        # 生成最简示例（只包含必需参数）
        required_only = [p for p in actual_params if p.default == inspect.Parameter.empty]
        if required_only and len(required_only) < len(actual_params):
            minimal_example = self._generate_single_example(command_path, required_only, include_all=True)
            if minimal_example and minimal_example != full_example:
                examples.append(minimal_example)
        
        if not examples:
            return f"示例: {command_path}"
        
        return "\n".join(f"示例: {example}" for example in examples)
    
    def _generate_single_example(self, command_path: str, params: list, include_all: bool = False) -> str:
        """生成单个示例"""
        example_parts = [command_path]
        
        for param in params:
            param_type = param.annotation
            example_value = self._get_example_value(param_type, param.name)
            if example_value:
                example_parts.append(example_value)
        
        return " ".join(example_parts) if len(example_parts) > 1 else None
    
    def _get_example_value(self, param_type, param_name: str) -> str:
        """根据参数类型生成示例值"""
        # 处理基础类型
        if param_type == str:
            # 根据参数名生成合适的示例
            if 'name' in param_name.lower():
                return "小明"
            elif 'user' in param_name.lower():
                return "用户名"
            elif 'title' in param_name.lower():
                return "标题"
            else:
                return "文本"
        elif param_type == int:
            if 'age' in param_name.lower():
                return "25"
            elif 'count' in param_name.lower():
                return "10"
            else:
                return "123"
        elif param_type == float:
            if 'price' in param_name.lower():
                return "99.99"
            elif 'rate' in param_name.lower():
                return "0.85"
            else:
                return "3.14"
        elif param_type == bool:
            return "true"
        elif hasattr(param_type, '__name__') and param_type.__name__ == 'Sentence':
            return "这是一句包含 空格的完整句子"
        
        # 处理 MessageSegment 子类
        if hasattr(param_type, '__name__'):
            type_name = param_type.__name__
            if type_name == 'At':
                return "@某人"
            elif type_name == 'Image':
                return "[图片]"
            elif type_name == 'Face':
                return "[表情]"
            elif type_name == 'Video':
                return "[视频]"
            elif type_name == 'Record':
                return "[语音]"
            elif type_name == 'Reply':
                return "[回复消息]"
            elif type_name in ['Text', 'PlainText']:
                return "纯文本"
            else:
                return f"[{type_name}]"
        
        return "参数"
    
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
        param_list = self.param_list[2:]  # 跳过前两个参数
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
    
    def convert_args(self, event: BaseMessageEvent) -> Tuple[bool, Tuple[...]]:
        """将事件中的参数转换为函数参数
        
        支持默认值的参数转换。当提供的参数不足时，会使用函数定义的默认值进行补全。
        ignore 项也作为正常的 str 参数进行匹配，返回时会排除前面的 ignore 参数。
        
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
            
        args_type, is_required_list = self.detect_args_type()
        LOG.debug(f"参数类型: {args_type}, 必需标记: {is_required_list}")
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
        
        # 处理参数不足的情况（支持默认值）
        if self.cur_index < len(args_type):
            # 检查剩余的参数是否都有默认值
            missing_required_count = 0
            for i in range(self.cur_index, len(args_type)):
                if is_required_list[i]:
                    missing_required_count += 1
            
            if missing_required_count > 0:
                LOG.debug(f"必需参数缺失: 还需要 {missing_required_count} 个必需参数")
                return (False, tuple(self.args_list))
            
            # 所有剩余参数都有默认值，进行补全
            for i in range(self.cur_index, len(args_type)):
                # 计算在实际参数中的相对索引（排除 ignore 参数）
                relative_index = i - ignore_count
                if relative_index in self.param_defaults:
                    default_value = self.param_defaults[relative_index]
                    self.args_list.append(default_value)
                    LOG.debug(f"使用默认值: 索引 {relative_index} = {default_value}")
                else:
                    # 这种情况理论上不应该发生，因为我们已经检查过必需参数
                    LOG.error(f"内部错误: 参数索引 {relative_index} 既不是必需的也没有默认值")
                    return (False, tuple(self.args_list))
        
        # 返回时排除前面的 ignore 参数
        actual_args = tuple(self.args_list[ignore_count:])
        LOG.debug(f"参数转换成功: {actual_args}")
        return (True, actual_args)
