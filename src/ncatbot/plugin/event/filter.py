import re
from typing import Callable, Optional

from ncatbot.plugin.event.event import Event


class Filter:
    """消息过滤器基类"""

    def __init__(self):
        self.next_filter: Optional[Filter] = None

    def set_next(self, filter: "Filter") -> "Filter":
        """设置下一个过滤器，实现责任链模式"""
        self.next_filter = filter
        return filter

    def check(self, event: Event) -> bool:
        """检查事件是否通过过滤器"""
        if self._check(event):
            return True
        if self.next_filter:
            return self.next_filter.check(event)
        return False

    def _check(self, event: Event) -> bool:
        """具体的过滤逻辑，由子类实现"""
        raise NotImplementedError


class PrefixFilter(Filter):
    """前缀匹配过滤器"""

    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix

    def _check(self, event: Event) -> bool:
        message = event.data.raw_message
        if not message:
            return False
        return message.startswith(self.prefix)


class RegexFilter(Filter):
    """正则匹配过滤器"""

    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = re.compile(pattern)

    def _check(self, event: Event) -> bool:
        message = event.data.raw_message
        if not message:
            return False
        return bool(self.pattern.match(message))


class CustomFilter(Filter):
    """自定义过滤器"""

    def __init__(self, filter_func: Callable[[Event], bool]):
        super().__init__()
        self.filter_func = filter_func

    def _check(self, event: Event) -> bool:
        return self.filter_func(event.data)


def create_filter(
    prefix: Optional[str] = None,
    regex: Optional[str] = None,
    custom_filter: Optional[Callable[[Event], bool]] = None,
) -> Optional[Filter]:
    """创建过滤器链

    Args:
        prefix: 前缀匹配
        regex: 正则匹配
        custom_filter: 自定义过滤函数

    Returns:
        过滤器链的头部，如果所有参数都为None则返回None
    """
    filters = []

    if custom_filter:
        filters.append(CustomFilter(custom_filter))

    if prefix:
        filters.append(PrefixFilter(prefix))

    if regex:
        filters.append(RegexFilter(regex))

    if not filters:
        return None

    # 构建过滤器链
    for i in range(len(filters) - 1):
        filters[i].set_next(filters[i + 1])

    return filters[0]
