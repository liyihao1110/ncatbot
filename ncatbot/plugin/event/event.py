# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-06 20:41:46
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from typing import Any, List, Union


class EventType:
    def __init__(self, plugin_name: str, event_name: str):
        self.plugin_name = plugin_name
        self.event_name = event_name

    def __str__(self):
        return f"{self.plugin_name}.{self.event_name}"


class EventSource:
    def __init__(self, user_id: Union[str, int], group_id: Union[str, int]):
        self.user_id = str(user_id)
        self.group_id = str(group_id)


class Event:
    """
    事件类，用于封装事件的类型和数据
    """

    def __init__(self, type: EventType, data: Any, source: EventSource = None):
        """
        初始化事件

        参数:
            type: str - 事件的类型
            data: Any - 事件携带的数据
        """
        self.type = type
        self.data = data
        self.source = source  # 事件源
        self._results: List[Any] = []
        self._propagation_stopped = False

    def stop_propagation(self):
        """
        停止事件的传播
        当调用此方法后，后续的处理器将不会被执行
        """
        self._propagation_stopped = True

    def add_result(self, result: Any):
        """
        添加事件处理结果

        参数:
            result: Any - 处理器返回的结果
        """
        self._results.append(result)

    def __repr__(self):
        return f'Event(type="{self.type}",data={self.data})'
