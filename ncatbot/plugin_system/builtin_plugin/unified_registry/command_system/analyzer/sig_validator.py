from ncatbot.utils import get_log
from ..utils import FuncSpec
from ncatbot.core.event import BaseMessageEvent
import inspect

LOG = get_log(__name__)


class SigValidator:
    def __init__(self, descriptor: "FuncSpec"):
        self.descriptor = descriptor

    def analyze_signature(self):
        """分析函数签名，获取实际参数列表。"""
        # TODO: 提示对方法签名的严格要求
        """验证函数签名是否符合要求，并确定 event 与实际参数起始索引"""
        if len(self.descriptor.param_list) < 1:
            LOG.error(
                f"函数参数不足: {self.descriptor.func_qualname} 需要至少包含 event 参数"
            )
            LOG.info(
                f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
            )
            raise ValueError(
                f"函数参数不足: {self.descriptor.func_qualname} 需要至少包含 event 参数"
            )

        first_param = self.descriptor.param_list[0]

        # 形态一：实例方法，要求参数形如 (self, event: BaseMessageEvent, ...)
        if first_param.name == "self":
            if len(self.descriptor.param_list) < 2:
                LOG.error(
                    f"函数参数不足: {self.descriptor.func_qualname} 需要包含 event 参数"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"函数参数不足: {self.descriptor.func_qualname} 需要包含 event 参数"
                )
            event_param = self.descriptor.param_list[1]
            if event_param.annotation == inspect.Parameter.empty:
                LOG.error(
                    f"event 参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"event 参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解"
                )
            if not (
                isinstance(event_param.annotation, type)
                and issubclass(event_param.annotation, BaseMessageEvent)
            ):
                LOG.error(
                    f"event 参数类型注解错误: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"event 参数类型注解错误: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类"
                )
            self.event_param_index = 1
        else:
            # 形态二：普通/静态方法，要求(event: BaseMessageEvent, ...)
            event_param = first_param
            if event_param.annotation == inspect.Parameter.empty:
                LOG.error(
                    f"event 参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"event 参数缺少类型注解: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 需要 BaseMessageEvent 或其子类注解"
                )
            if not (
                isinstance(event_param.annotation, type)
                and issubclass(event_param.annotation, BaseMessageEvent)
            ):
                LOG.error(
                    f"event 参数类型注解错误: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类"
                )
                LOG.info(
                    f"函数来自 {self.descriptor.func_module}.{self.descriptor.func_qualname}"
                )
                raise ValueError(
                    f"event 参数类型注解错误: {self.descriptor.func_qualname} 的参数 '{event_param.name}' 注解为 {event_param.annotation}，需要 BaseMessageEvent 或其子类"
                )
            self.event_param_index = 0

        # 计算实际参数的起始索引与切片
        return (
            self.event_param_index + 1,
            self.descriptor.param_list[self.event_param_index + 1 :],
        )
