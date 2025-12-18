"""过滤器验证器 v2.0"""

from typing import Callable, List, TYPE_CHECKING
from .base import BaseFilter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent

LOG = get_log("Validator")


class FilterValidator:
    """过滤器验证器 v2.0"""

    def validate_filters(self, func: Callable, event: "BaseMessageEvent") -> bool:
        """验证函数的所有过滤器

        Args:
            func: 要验证的函数
            event: 消息事件

        Returns:
            bool: True 表示通过所有过滤器，False 表示被拦截
        """
        filters: List[BaseFilter] = getattr(func, "__filters__", [])

        if not filters:
            # 没有过滤器的函数默认通过
            return True

        # 执行所有过滤器验证
        for filter_instance in filters:
            try:
                if not filter_instance.check(event):
                    LOG.debug(f"函数 {func.__name__} 被过滤器 {filter_instance} 拦截")
                    return False
            except Exception as e:
                LOG.error(f"过滤器验证失败: {filter_instance}, 错误: {e}")
                return False

        LOG.debug(f"函数 {func.__name__} 通过所有过滤器验证")
        return True
