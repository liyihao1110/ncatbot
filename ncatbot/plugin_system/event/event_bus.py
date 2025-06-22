# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-11 17:31:16
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-12 18:29:00
# @Description  : 事件总线类,用于管理和分发事件
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from typing import List, Any, Callable, Dict
from ..pluginsys_err import EventHandlerError
from .event import Event
import re
import asyncio
import uuid

class EventBus:
    """
    事件总线类,用于管理和分发事件
    """
    def __init__(self):
        """
        初始化事件总线
        """
        self._exact_handlers = {}
        self._regex_handlers = []
        # 钩子存储-按事件类型
        self._type_hooks: Dict[str, Dict[str, List[Callable]]] = {}
        # 钩子存储-按处理器UUID
        self._uuid_hooks: Dict[uuid.UUID, Dict[str, List[Callable]]] = {}
        # 钩子类型列表
        self._hook_types = [
            'before_publish',  # 发布事件前
            'after_publish',   # 发布事件后 
            'before_handler',  # 处理器执行前
            'after_handler',   # 处理器执行后
            'on_error'        # 发生错误时
        ]

    def subscribe(self, event_type: str, handler: Callable[[Event], Any], priority: int = 0) -> uuid.UUID:
        """
        订阅事件处理器,并返回处理器的唯一 ID

        Args
            event_type: str - 事件类型或正则模式（以 're:' 开头表示正则匹配）
            handler: Callable[[Event], Any] - 事件处理器函数
            priority: int - 处理器的优先级（数字越大,优先级越高）

        return:
            UUID - 处理器的唯一 ID
        """
        handler_id = uuid.uuid4()
        pattern = None
        if event_type.startswith("re:"):
            try:
                pattern = re.compile(event_type[3:])
            except re.error as e:
                raise ValueError(f"无效正则表达式: {event_type[3:]}") from e
            self._regex_handlers.append((pattern, priority, handler, handler_id))
        else:
            self._exact_handlers.setdefault(event_type, []).append(
                (pattern, priority, handler, handler_id)
            )
        return handler_id

    def unsubscribe(self, handler_id: uuid.UUID) -> bool:
        """
        取消订阅事件处理器

        Args
            handler_id: UUID - 处理器的唯一 ID

        return:
            bool - 是否成功取消订阅
        """
        # 取消精确匹配处理器
        for event_type in list(self._exact_handlers.keys()):
            self._exact_handlers[event_type] = [
                (patt, pr, h, hid) for (patt, pr, h, hid) in self._exact_handlers[event_type] if hid != handler_id
            ]
            if not self._exact_handlers[event_type]:
                del self._exact_handlers[event_type]
        # 取消正则匹配处理器
        self._regex_handlers = [
            (patt, pr, h, hid) for (patt, pr, h, hid) in self._regex_handlers if hid != handler_id
        ]
        # 移除UUID关联的钩子
        if handler_id in self._uuid_hooks:
            del self._uuid_hooks[handler_id]
        
        return True

    def add_hook(self, hook_type: str, func: Callable, event_type: str = None, handler_id: uuid.UUID = None) -> None:
        """添加钩子函数
        
        Args:
            hook_type: 钩子类型
            func: 钩子函数
            event_type: 事件类型,用于关联特定事件类型
            handler_id: 处理器ID,用于关联特定处理器
        """
        if hook_type not in self._hook_types:
            raise ValueError(f"无效的钩子类型: {hook_type}")
            
        if handler_id:
            # UUID关联
            if handler_id not in self._uuid_hooks:
                self._uuid_hooks[handler_id] = {t:[] for t in self._hook_types}
            self._uuid_hooks[handler_id][hook_type].append(func)
        elif event_type:
            # 事件类型关联
            if event_type not in self._type_hooks:
                self._type_hooks[event_type] = {t:[] for t in self._hook_types}
            self._type_hooks[event_type][hook_type].append(func)
        else:
            raise ValueError("必须指定event_type或handler_id之一")

    async def _run_hooks(self, hook_type: str, event: Event, handler=None, *args, **kwargs) -> None:
        """运行指定类型的钩子函数"""
        hooks_to_run = []
        
        # 获取事件类型关联的钩子
        if event.type in self._type_hooks:
            hooks_to_run.extend(self._type_hooks[event.type][hook_type])
            
        # 获取处理器UUID关联的钩子
        if handler and hasattr(handler, 'id'):
            handler_id = handler.id
            if handler_id in self._uuid_hooks:
                hooks_to_run.extend(self._uuid_hooks[handler_id][hook_type])

        # 执行钩子
        for hook in hooks_to_run:
            if asyncio.iscoroutinefunction(hook):
                await hook(event, *args, **kwargs)
            else:
                await asyncio.get_running_loop().run_in_executor(
                    None, hook, event, *args, **kwargs
                )

    async def publish_async(self, event: Event) -> List[Any]:
        """
        异步发布事件

        Args
            event: Event - 要发布的事件

        return:
            List[Any] - 所有处理器返回的结果的列表
        """
        # 发布前钩子
        await self._run_hooks('before_publish', event)
        
        if event.intercepted:
            await self._run_hooks('after_publish', event)
            return event.results

        handlers = []
        if event.type in self._exact_handlers:
            # 处理精确匹配处理器
            for (pattern, priority, handler, handler_id) in self._exact_handlers[event.type]:
                handlers.append((handler, priority, handler_id))
        else:
            # 处理正则匹配处理器
            for (pattern, priority, handler, handler_id) in self._regex_handlers:
                if pattern and pattern.match(event.type):
                    handlers.append((handler, priority, handler_id))
        
        # 按优先级排序
        sorted_handlers = sorted(handlers, key=lambda x: (-x[1], x[0].__name__))
        
        results = []
        # 按优先级顺序调用处理器
        for handler, priority, handler_id in sorted_handlers:
            if event._propagation_stopped:
                break

            # 处理器执行前钩子
            await self._run_hooks('before_handler', event, handler)
            
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    # 将同步函数包装为异步任务
                    await asyncio.get_running_loop().run_in_executor(None, handler, event)
                # 处理器执行后钩子
                await self._run_hooks('after_handler', event, handler)
            except Exception as e:
                # 错误钩子
                await self._run_hooks('on_error', event, handler, e)
                raise EventHandlerError(e,handler)
            # 收集结果
            results.extend(event._results)
        
        # 发布后钩子
        await self._run_hooks('after_publish', event)
        return results

    def publish_sync(self, event: Event) -> List[Any]:
        """
        同步发布事件

        Args
            event: Event - 要发布的事件

        return:
            List[Any] - 所有处理器返回的结果的列表
        """
        loop = asyncio.new_event_loop()  # 创建新的事件循环
        try:
            asyncio.set_event_loop(loop)  # 设置为当前事件循环
            return loop.run_until_complete(self.publish_async(event))
        finally:
            loop.close()  # 关闭事件循环