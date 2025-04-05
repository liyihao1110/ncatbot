from typing import Any, Callable, List, final
from uuid import UUID

from ncatbot.plugin.event import Event, EventBus


class EventHandlerMixin:
    """事件处理混入类，提供事件发布和订阅功能。

    # 描述
    该混入类实现了完整的事件处理系统，包括事件的同步/异步发布以及处理器的管理功能。
    作为一个Mixin类，它需要与具有 `_event_bus` 实例的类配合使用。

    # 属性
    - `_event_bus` (EventBus): 事件总线实例，用于处理事件的发布与订阅
    - `_event_handlers` (List[UUID]): 当前已注册的事件处理器ID列表

    # 使用示例
    ```python
    class MyClass(EventHandlerMixin):
        def __init__(self):
            self._event_bus = EventBus()
            self._event_handlers = []
    ```
    """

    _event_bus: EventBus
    _event_handlers: List[UUID]

    @final
    def publish_sync(self, event: Event) -> List[Any]:
        """同步发布事件。

        Args:
            event (Event): 要发布的事件对象。

        Returns:
            List[Any]: 所有事件处理器的返回值列表。
        """
        return self._event_bus.publish_sync(event)

    @final
    def publish_async(self, event: Event):
        """异步发布事件。

        Args:
            event (Event): 要发布的事件对象。

        Returns:
            None: 这个方法不返回任何值。
        """
        return self._event_bus.publish_async(event)

    @final
    def register_handler(
        self, event_type: str, handler: Callable[[Event], Any], priority: int = 0
    ) -> UUID:
        """注册一个事件处理器。

        Args:
            event_type (str): 事件类型标识符。
            handler (Callable[[Event], Any]): 事件处理器函数。
            priority (int, optional): 处理器优先级，默认为0。优先级越高，越先执行。

        Returns:
            UUID: 处理器的唯一标识符。
        """
        handler_id = self._event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)
        return handler_id

    @final
    def unregister_handler(self, handler_id: UUID) -> bool:
        """注销一个事件处理器。

        Args:
            handler_id (UUID): 要注销的事件处理器的唯一标识符。

        Returns:
            bool: 如果注销成功返回True，否则返回False。
        """
        if handler_id in self._event_handlers:
            rest = self._event_bus.unsubscribe(handler_id)
            if rest:
                self._event_handlers.remove(handler_id)
                return True
        return False

    @final
    def unregister_handlers(self):
        """注销所有事件处理器。

        Returns:
            None: 这个方法不返回任何值。
        """
        for handler_id in self._event_handlers:
            self._event_bus.unsubscribe(handler_id)
