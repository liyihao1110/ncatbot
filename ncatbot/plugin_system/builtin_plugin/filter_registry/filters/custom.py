"""自定义过滤器模块"""

from typing import Protocol, Union, TYPE_CHECKING
import inspect
from .base import BaseFilter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ..filter_registry import FilterRegistryPlugin

LOG = get_log(__name__)


class SimpleFilterProtocol(Protocol):
    """简单过滤器函数协议 - 只接收 event 参数"""
    def __call__(self, event: "BaseMessageEvent") -> bool: ...


class AdvancedFilterProtocol(Protocol):
    """高级过滤器函数协议 - 接收 manager 和 event 参数"""
    def __call__(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool: ...


# 自定义过滤器函数联合类型
CustomFilterFunc = Union[SimpleFilterProtocol, AdvancedFilterProtocol]


class CustomFilter(BaseFilter):
    """自定义过滤器类
    
    支持两种函数签名：
    1. SimpleFilterFunc: (event: BaseMessageEvent) -> bool
    2. AdvancedFilterFunc: (manager: FilterRegistryPlugin, event: BaseMessageEvent) -> bool
    """
    
    def __init__(self, func: CustomFilterFunc):
        self.func = func
        self.func_name = getattr(func, '__name__', str(func))
        
        # 预处理函数签名，避免运行时重复检查
        self._analyze_signature()
        
    def _analyze_signature(self):
        """分析并验证函数签名，只在构造时执行一次"""
        try:
            sig = inspect.signature(self.func)
            params = list(sig.parameters.values())
            param_count = len(params)
            
            if param_count == 1:
                # SimpleFilterFunc: (event: BaseMessageEvent) -> bool
                self.call_mode = "simple"
                self.event_param = params[0]
                self._validate_event_param(self.event_param)
                LOG.debug(f"CustomFilter {self.func_name}: 简单模式 (event)")
                
            elif param_count == 2:
                # AdvancedFilterFunc: (manager: FilterRegistryPlugin, event: BaseMessageEvent) -> bool
                self.call_mode = "advanced"
                self.manager_param = params[0]
                self.event_param = params[1]
                self._validate_manager_param(self.manager_param)
                self._validate_event_param(self.event_param)
                LOG.debug(f"CustomFilter {self.func_name}: 高级模式 (manager, event)")
                
            else:
                raise ValueError(f"CustomFilter 函数 {self.func_name} 参数数量错误: "
                               f"期望 1 或 2 个参数，实际 {param_count} 个")
                
            # 验证返回类型注解（可选）
            self._validate_return_annotation(sig.return_annotation)
                
        except Exception as e:
            LOG.error(f"CustomFilter 函数 {self.func_name} 签名分析失败: {e}")
            raise ValueError(f"CustomFilter 函数签名无效: {self.func_name}") from e
    
    def _validate_event_param(self, param: inspect.Parameter):
        """验证 event 参数的类型注解"""
        if param.annotation == inspect.Parameter.empty:
            LOG.warning(f"CustomFilter 函数 {self.func_name} 的 event 参数缺少类型注解，"
                       f"建议添加 BaseMessageEvent 注解")
            return
            
        if not self._is_base_message_event_type(param.annotation):
            LOG.warning(f"CustomFilter 函数 {self.func_name} 的 event 参数类型注解 "
                       f"{param.annotation} 不是 BaseMessageEvent 或其子类，可能导致类型检查问题")
    
    def _validate_manager_param(self, param: inspect.Parameter):
        """验证 manager 参数的类型注解"""
        if param.annotation == inspect.Parameter.empty:
            LOG.warning(f"CustomFilter 函数 {self.func_name} 的 manager 参数缺少类型注解，"
                       f"建议添加 FilterRegistryPlugin 注解")
            return
            
        # 由于循环导入问题，这里只做基本检查
        param_name = getattr(param.annotation, '__name__', str(param.annotation))
        if 'FilterRegistryPlugin' not in param_name and param_name != 'str':
            LOG.warning(f"CustomFilter 函数 {self.func_name} 的 manager 参数类型注解 "
                       f"{param.annotation} 可能不正确，建议使用 FilterRegistryPlugin")
    
    def _validate_return_annotation(self, return_annotation):
        """验证返回类型注解"""
        if return_annotation == inspect.Parameter.empty:
            LOG.warning(f"CustomFilter 函数 {self.func_name} 缺少返回类型注解，建议添加 -> bool")
        elif return_annotation != bool:
            LOG.warning(f"CustomFilter 函数 {self.func_name} 返回类型注解为 {return_annotation}，"
                       f"建议使用 -> bool")
    
    def _is_base_message_event_type(self, annotation) -> bool:
        """检查类型注解是否为 BaseMessageEvent 或其子类"""
        try:
            # 避免循环导入
            from ncatbot.core.event import BaseMessageEvent
            
            if isinstance(annotation, type):
                return issubclass(annotation, BaseMessageEvent)
            # 处理字符串注解的情况
            if isinstance(annotation, str):
                return 'BaseMessageEvent' in annotation
            return False
        except (TypeError, ImportError):
            return False
        
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """执行过滤器检查
        
        Args:
            manager: FilterRegistryPlugin 实例
            event: 消息事件
            
        Returns:
            bool: 过滤器检查结果
        """
        try:
            if self.call_mode == "simple":
                # SimpleFilterFunc: (event: BaseMessageEvent) -> bool
                result = self.func(event)
            elif self.call_mode == "advanced":
                # AdvancedFilterFunc: (manager: FilterRegistryPlugin, event: BaseMessageEvent) -> bool
                result = self.func(manager, event)
            else:
                # 这种情况理论上不应该出现，因为在构造时已经验证
                LOG.error(f"CustomFilter 函数 {self.func_name} 调用模式未知: {self.call_mode}")
                return False
            
            # 验证返回值类型
            if not isinstance(result, bool):
                LOG.warning(f"CustomFilter 函数 {self.func_name} 返回值不是 bool 类型: {type(result)}")
                return bool(result)  # 强制转换为 bool
            
            return result
            
        except Exception as e:
            # 分类处理不同类型的异常
            if isinstance(e, (TypeError, AttributeError)):
                LOG.error(f"CustomFilter 函数 {self.func_name} 调用失败（参数或属性错误）: {e}")
            elif isinstance(e, (ValueError, KeyError)):
                LOG.error(f"CustomFilter 函数 {self.func_name} 执行失败（逻辑错误）: {e}")
            else:
                LOG.error(f"CustomFilter 函数 {self.func_name} 执行失败（未知错误）: {e}")
            
            # 过滤器执行失败时返回 False，确保系统稳定性
            return False
