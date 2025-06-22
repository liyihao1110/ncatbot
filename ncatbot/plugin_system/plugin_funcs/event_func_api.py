# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-29 15:36:57
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-24 17:00:30
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from typing import Any, Dict, List, Callable

from uuid import UUID

from ...utils import get_log
from ..event import EventBus, Event
from ..abc_api import AbstractPluginApi


LOG = get_log('BasePlugin')

class PluginFunctionMixin(AbstractPluginApi):
    """
    插件功能自动管理器混入类，用于快速添加、移除、禁用、启用和查询插件功能，并自动生成帮助信息。

    插件功能是指通过监听特定事件并触发特定逻辑来实现的功能。该混入类提供了一系列便捷的方法来管理插件功能，
    同时自动管理功能的注册和帮助信息。

    # 属性
    - `_event_bus` (EventBus): 事件总线实例，用于处理事件的发布与订阅。
    - `_event_handlers` (List[UUID]): 当前已注册的事件处理器ID列表。
    - `meta_data` (Dict): 插件元数据，包含功能相关信息。

    # 注意
    - 权限检查接口目前为预留功能，尚未实现。
    """

    _event_bus: EventBus
    _event_handlers: List[UUID]
    meta_data: dict

    def register_function(
        self,
        name: str,  # 功能名称
        event_type: str,  # 监听的事件类型
        trigger: Callable[[Event], bool],  # 事件触发条件函数
        func: Callable[[Event], Any],  # 功能逻辑函数
        priority: int = 0,  # 事件处理器优先级
        docs: str = "这是个神秘的功能",  # 功能描述
        permission: str = None,  # 权限要求（预留）
    ):
        """
        注册一个新的插件功能。

        功能通过监听特定事件并触发特定逻辑来实现。该方法会将功能注册到事件总线中，并记录功能的元数据。

        Args:
            name (str): 功能名称，必须唯一。
            event_type (str): 监听的事件类型。
            trigger (Callable[[Event], bool]): 事件触发条件函数，返回 `True` 时触发功能。
            func (Callable[[Event], Any]): 功能逻辑函数，当事件触发时执行。
            priority (int, optional): 事件处理器优先级，默认为 0。优先级越高，越先执行。
            docs (str, optional): 功能描述，默认为 "这是个神秘的功能"。
            permission (str, optional): 权限要求（预留），默认为空。

        Raises:
            RuntimeError: 如果功能名称已存在，会引发此错误。
        """

        if 'functions' not in self.meta_data:
            self.meta_data['functions'] = {}

        if name in self.meta_data['functions']:
            raise RuntimeError(f"你不能添加同名功能: '{name}' 已经添加过了")

        def pack(event: Event):
            """包装函数，用于判断是否触发功能并执行功能逻辑"""
            if not self.meta_data['functions'][name]['enabled']:
                return
            if trigger and not trigger(event):
                return
            if permission and not True:  # 权限检查接口（预留）
                return
            func(event)

        handler_id = self._event_bus.subscribe(event_type, pack, priority)
        
        self.meta_data['functions'][name] = {
            "enabled": True,
            "docs": docs,
            "permission": permission,
            "handler_id": handler_id
        }
        
        self._event_handlers.append(handler_id)

    def removefunc(self, name: str) -> bool:
        """
        移除一个已注册的插件功能。

        Args:
            name (str): 要移除的功能名称。

        Returns:
            bool: 如果移除成功返回 `True`，否则返回 `False`。
        """
        if name not in self.meta_data['functions']:
            return False
        handler_id = self.meta_data['functions'][name]['handler_id']
        self._event_bus.unsubscribe(handler_id)
        self._event_handlers.remove(handler_id)
        del self.meta_data['functions'][name]
        return True

    def enablefunc(self, name: str) -> bool:
        """
        启用一个插件功能。

        Args:
            name (str): 要启用的功能名称。

        Returns:
            bool: 如果启用成功返回 `True`，否则返回 `False`。
        """
        if name not in self.meta_data['functions']:
            return False
        self.meta_data['functions'][name]['enabled'] = True
        return True

    def disablefunc(self, name: str) -> bool:
        """
        禁用一个插件功能。

        Args:
            name (str): 要禁用的功能名称。

        Returns:
            bool: 如果禁用成功返回 `True`，否则返回 `False`。
        """
        if name not in self.meta_data['functions']:
            return False
        self.meta_data['functions'][name]['enabled'] = False
        return True

    def updatefuncdocs(self, name: str, docs: str) -> bool:
        """
        更新一个插件功能的描述信息。

        Args:
            name (str): 功能名称。
            docs (str): 新的功能描述。

        Returns:
            bool: 如果更新成功返回 `True`，否则返回 `False`。
        """
        if name not in self.meta_data['functions']:
            return False
        self.meta_data['functions'][name]['docs'] = docs
        return True

    def listfuncs(self) -> Dict[str, Dict[str, Any]]:
        """
        查询当前已注册的插件功能及其状态。

        Returns:
            Dict[str, Dict[str, Any]]: 一个字典，包含所有已注册的功能及其描述、启用状态和权限要求。
        """
        return {
            name: {
                "docs": info["docs"],
                "enabled": info["enabled"],
                "permission": info["permission"],
            }
            for name, info in self.meta_data['functions'].items()
        }

    def generate_help(self, template: str = "{name}: {docs} (状态: {enabled}, 权限: {permission})") -> str:
        """
        自动生成帮助信息，支持自定义模板。

        Args:
            filter (str, optional): 过滤条件，用于筛选帮助信息。默认为空字符串。
            template (str, optional): 自定义模板字符串，用于定义帮助信息的格式。默认为 "{name}: {docs} (状态: {enabled}, 权限: {permission})"。

        Returns:
            str: 生成的帮助信息文本。
        """
        help_lines = []
        help_lines.append("帮助信息列表：")
        help_lines.append("-" * 40)  # 添加分隔符

        for name, info in self.meta_data['functions'].items():
            enabled_status = "启用" if info['enabled'] else "禁用"
            help_lines.append(
                template.format(
                    name=name,
                    docs=info['docs'],
                    enabled=enabled_status,
                    permission=info['permission']
                )
            )

        if len(help_lines) == 2:  # 只有标题和分隔符
            return "没有找到匹配的帮助信息。"
        return "\n".join(help_lines)