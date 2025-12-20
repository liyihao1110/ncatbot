"""过滤器注册器 v2.0"""

from typing import Dict, List, Callable, Optional, Union, Any
from dataclasses import dataclass
from .base import BaseFilter
from .builtin import CustomFilter
from ncatbot.utils import get_log
from ..utils import get_func_plugin_name

LOG = get_log(__name__)


@dataclass
class FilterEntry:
    """过滤器条目"""

    name: str
    filter_instance: BaseFilter
    metadata: Dict[str, Any]


class FilterRegistry:
    """统一过滤器注册器
    可以用字符串索引 filter 实例
    支持两种注册方式：
    1. filter_registry.register_filter(name, filter_instance)
    2. filter_registry.register(func) 或 @filter_registry 装饰器
    """

    def __init__(self):
        self._filters: Dict[str, FilterEntry] = {}
        self._function_filters: Dict[str, Callable] = {}
        from .decorators import admin_filter, root_filter, private_filter, group_filter

        self.admin_filter = admin_filter
        self.root_filter = root_filter
        self.private_filter = private_filter
        self.group_filter = group_filter
        self.admin_only = admin_filter
        self.root_only = root_filter
        self.private_only = private_filter
        self.group_only = group_filter

    def _validate_filter_function(self, func: Callable) -> None:
        # TODO: 验证（自定义）过滤器函数
        pass

    # 方式1：实例注册
    def register_filter(
        self,
        name: str,
        filter_instance: BaseFilter,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """注册过滤器实例

        Args:
            name: 过滤器名称
            filter_instance: 过滤器实例
            metadata: 元数据
        """
        if name in self._filters:
            LOG.warning(f"过滤器 {name} 已存在，将被覆盖")

        self._filters[name] = FilterEntry(
            name=name, filter_instance=filter_instance, metadata=metadata or {}
        )
        LOG.debug(f"注册过滤器实例: {name} -> {filter_instance}")

    # 方式2：函数注册
    def register(self, func_or_name=None, name: str = None):
        """注册过滤器函数或用作装饰器

        Args:
            func_or_name: 过滤器函数或过滤器名称
            name: 过滤器名称（当第一个参数是函数时使用）

        Returns:
            装饰器或注册的函数
        """

        def _register(f: Callable) -> Callable:
            # 确定过滤器名称
            if isinstance(func_or_name, str):
                filter_name = func_or_name  # 装饰器模式：@register("name")
            else:
                filter_name = name or f.__name__  # 直接调用模式或无名称装饰器

            custom_filter = CustomFilter(f, filter_name)
            self.register_filter(filter_name, custom_filter)

            return f

        if func_or_name is None or isinstance(func_or_name, str):
            # 用作装饰器: @filter_registry.register() 或 @filter_registry.register("name")
            return _register
        else:
            # 直接调用: filter_registry.register(func)
            return _register(func_or_name)

    def __call__(self, func: Callable = None, name: str = None):
        """使注册器实例可调用，等同于 register 方法"""
        return self.register(func, name)

    # 为函数添加过滤器
    def add_filter_to_function(
        self, func: Callable, *filters: Union[BaseFilter, str]
    ) -> Callable:
        """为函数添加过滤器

        Args:
            func: 目标函数
            *filters: 过滤器实例或名称

        Returns:
            修改后的函数
        """
        if not hasattr(func, "__filters__"):
            setattr(func, "__filters__", [])
            function_name = f"{get_func_plugin_name(func)}::{func.__name__}"
            self._function_filters[function_name] = func

        filter_list: List[BaseFilter] = getattr(func, "__filters__")

        for filter_item in filters:
            if isinstance(filter_item, str):
                # 按名称查找过滤器
                if filter_item in self._filters:
                    filter_list.append(self._filters[filter_item].filter_instance)
                else:
                    LOG.error(f"未找到名为 {filter_item} 的过滤器")
            elif isinstance(filter_item, BaseFilter):
                filter_list.append(filter_item)
            else:
                LOG.error(f"不支持的过滤器类型: {type(filter_item)}")

        LOG.debug(f"为函数 {func.__name__} 添加了 {len(filters)} 个过滤器")
        return func

    # 查询方法
    def get_filter(self, name: str) -> Optional[FilterEntry]:
        """获取过滤器条目"""
        return self._filters.get(name)

    def get_filter_instance(self, name: str) -> Optional[BaseFilter]:
        """获取过滤器实例"""
        entry = self.get_filter(name)
        return entry.filter_instance if entry else None

    def filters(self, *filters: Union[BaseFilter, str]):
        """为函数添加多个过滤器"""

        def wrapper(func: Callable):
            self.add_filter_to_function(func, *filters)
            return func

        return wrapper

    def clear(self):
        """清除所有注册的过滤器"""
        self._filters.clear()
        self._function_filters.clear()

    def revoke_plugin(self, plugin_name: str):
        """撤销插件的过滤器"""
        deleted_filters = [
            name for name in self._function_filters.keys() if name.split("::")[0] == plugin_name
        ]
        for name in deleted_filters:
            del self._function_filters[name]


# 全局单例
filter_registry = FilterRegistry()
