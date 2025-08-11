import re
import asyncio
from typing import Callable, Optional, List, Dict, Any
from typing import final
from ncatbot.core.event import BaseMessageEvent
from ncatbot.plugin_system.event import NcatBotEvent
from ncatbot.utils.assets.literals import PermissionGroup
from ncatbot.utils import get_log
from functools import partial

LOG = get_log("FunctionMixin")

class Filter:
    """消息过滤器基类"""

    def __init__(self):
        self.next_filter: Optional[Filter] = None

    def set_next(self, filter: "Filter") -> "Filter":
        """设置下一个过滤器，实现责任链模式"""
        self.next_filter = filter
        return filter

    def check(self, event: BaseMessageEvent) -> bool:
        """检查事件是否通过过滤器"""
        if self._check(event):
            return True
        if self.next_filter:
            return self.next_filter.check(event)
        return False

    def _check(self, event: BaseMessageEvent) -> bool:
        """具体的过滤逻辑，由子类实现"""
        raise NotImplementedError


class PrefixFilter(Filter):
    """前缀匹配过滤器"""

    def __init__(self, prefix: str):
        super().__init__()
        self.prefix = prefix

    def _check(self, event: BaseMessageEvent) -> bool:
        message = event.raw_message
        if not message:
            return False
        return message.startswith(self.prefix)


class RegexFilter(Filter):
    """正则匹配过滤器"""

    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = re.compile(pattern)

    def _check(self, event: BaseMessageEvent) -> bool:
        message = event.raw_message
        if not message:
            return False
        return bool(self.pattern.match(message))


class CustomFilter(Filter):
    """自定义过滤器"""

    def __init__(self, filter_func: Callable[[BaseMessageEvent], bool]):
        super().__init__()
        self.filter_func = filter_func

    def _check(self, event: BaseMessageEvent) -> bool:
        return self.filter_func(event)


def create_filter(
    prefix: Optional[str] = None,
    regex: Optional[str] = None,
    custom_filter: Optional[Callable[[BaseMessageEvent], bool]] = None,
) -> Filter:
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
        raise ValueError("至少需要一个过滤器")

    # 构建过滤器链
    for i in range(len(filters) - 1):
        filters[i].set_next(filters[i + 1])

    return filters[0]


class Func:
    def __init__(self, data: dict):
        self.name = data['name']
        self.permission = data['permission']
        self.description = data['description']
        self.usage = data['usage']
        self.examples = data['examples']
        self.tags = data['tags']
        self.metadata = data['metadata']
        self.handlder_id = data['handlder_id']
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Func):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False


class FunctionMixin:
    def _warn_permission_raise_deprecated(self):
        if not hasattr(FunctionMixin, '_permission_raise_deprecated_warned'):
            FunctionMixin._permission_raise_deprecated_warned = True
            LOG.warning("提权参数已经弃用, 请删掉该参数")

    @final
    def get_registered_funcs(self) -> List[Func]:
        if not hasattr(self, '_registered_funcs'):
            self._registered_funcs = []
        return [Func(func) for func in self._registered_funcs]
    
    @final
    def unregister_func(self, name: str):
        if not hasattr(self, '_registered_funcs'):
            self._registered_funcs = []
        for func in self._registered_funcs:
            if func.name == name:
                self.unregister_handler(func.handlder_id)
                self._registered_funcs.remove(func)
                break
        else:
            raise ValueError(f"插件 {self.name} 不存在功能 {name}")

    @final
    def _create_func_handler(self, name: str, handler: Callable, filter_chain) -> Callable:
        is_coroutine = asyncio.iscoroutinefunction(handler)

        async def wrapped_handler(
            event: NcatBotEvent,
            current_name: str = name,
            current_handler: Callable = handler,
            current_filter: Any = filter_chain,
        ):
            data = event.data
            
            if not isinstance(data, BaseMessageEvent):
                LOG.error(f"事件数据类型错误，预期 BaseMessageEvent，实际得到 {type(data)}")
                return None
            try:
                permission = f"{self.name}.{current_name}"
                if not self._rbac_manager.check_permission(data.user_id, permission):
                    # TODO: 权限不足反馈
                    return None
                
                if not current_filter.check(data):
                    return None
                
                LOG.debug(f"插件 {self.name} 功能 {current_name} 正在执行")
                if is_coroutine:
                    return await current_handler(data)
                else:
                    return current_handler(data)
                    
            except Exception as e:
                LOG.error(f"插件 {self.name} 功能 {current_name} 执行失败: {e}", exc_info=True)
                return None
        wrapped_handler.__name__ = name
        return wrapped_handler
    
    @final
    def _register_func(
        self,
        name: str,
        handler: Callable[[BaseMessageEvent], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission: PermissionGroup = PermissionGroup.USER.value,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        timeout: float = None,
    ) -> Func:
        # 默认权限路径: 插件名.功能名
        self._rbac_manager.assign_permissions_to_role(permission, f"{self.name}.{name}", 'white')
        # 注册功能
        if not hasattr(self, '_registered_funcs'):
            self._registered_funcs: List[Func] = []
        if name not in self._registered_funcs:        
            if filter is None and prefix is None and regex is None:
                prefix = f"/{self.name}.{name}"
            
            filter_chain = create_filter(prefix, regex, filter)
            warpped_handler = self._create_func_handler(name, handler, filter_chain)
            func = Func({
                'name': name,
                'permission': permission,
                'description': description,
                'usage': usage,
                'examples': examples,
                'tags': tags,
                'metadata': metadata,
                'handlder_id': self.register_handler("re:ncatbot.group_message_event|ncatbot.private_message_event", warpped_handler, timeout=timeout)
            })
            self._registered_funcs.append(func)
            return func
        else:
            raise ValueError(f"插件 {self.name} 已存在功能 {name}")

    def register_user_func(
        self,
        name: str,
        handler: Callable[[BaseMessageEvent], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission_raise: bool = None,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        timeout: float = None,
    ) -> Func:
        """注册普通用户功能

        Args:
            name: 功能名
            handler: 处理函数
            filter: 自定义过滤器
            prefix: 前缀匹配
            regex: 正则匹配
            permission_raise: 是否提权
            description: 功能描述
            usage: 使用说明
            examples: 使用示例
            tags: 功能标签
            metadata: 额外元数据
        """
        if permission_raise is not None:
            self._warn_permission_raise_deprecated()
        return self._register_func(
            name,
            handler,
            filter,
            prefix,
            regex,
            PermissionGroup.USER.value,
            description,
            usage,
            examples,
            tags,
            metadata,
            timeout,
        )

    def register_admin_func(
        self,
        name: str,
        handler: Callable[[BaseMessageEvent], Any],
        filter: Callable = None,
        prefix: str = None,
        regex: str = None,
        permission_raise: bool = None,
        description: str = "",
        usage: str = "",
        examples: List[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        timeout: float = None,
    ) -> Func:
        if permission_raise is not None:
            self._warn_permission_raise_deprecated()
        return self._register_func(
            name,
            handler,
            filter,
            prefix,
            regex,
            PermissionGroup.ADMIN.value,
            description,
            usage,
            examples,
            tags,
            metadata,
            timeout,
        )