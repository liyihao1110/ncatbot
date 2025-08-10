# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-11 17:31:16
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-29 19:32:46
# @Description  : 事件类,封装事件信息
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from typing import List, Any
from copy import copy


class NcatBotEvent:
    """事件类

    用于封装事件信息,包含事件类型、数据及处理结果。

    Attributes:
        type (str): 事件类型标识符
        data (Any): 事件携带的数据
        _results (List[Any]): 事件处理的结果集合
        _propagation_stopped (bool): 事件传播是否已停止的标志
    """

    def __init__(self, type: str, data: Any):
        """初始化事件实例

        Args:
            type: 事件类型标识符
            data: 事件携带的数据
        """
        self._type: str = type
        self._data: Any = data
        self._results: List[Any] = []
        self._propagation_stopped: bool = False
        self._intercepted: bool = False
        self._exceptions: List[Exception] = []

    @property
    def data(self):
        return copy(self._data)

    @property
    def type(self):
        return copy(self._type)

    @property
    def results(self):
        return copy(self._results)

    @property 
    def intercepted(self) -> bool:
        """是否被拦截"""
        return self._intercepted

    @property
    def exceptions(self) -> List[Exception]:
        """获取事件处理过程中收集到的异常"""
        return copy(self._exceptions)

    def __eq__(self, value: str):
        return self.type == value

    def __add__(self, other):
        self.add_result(other)
        return self

    def __iadd__(self, other):
        self.add_result(other)
        return self

    def stop_propagation(self):
        """停止事件的继续传播
        
        调用此方法后,后续的事件处理器将不会被执行。
        """
        self._propagation_stopped = True

    def add_result(self, result: Any):
        """添加事件处理结果
        
        Args:
            result: 处理器返回的结果
        """
        self._results.append(result)
    
    def add_exception(self, exception: Exception):
        """添加事件处理过程中的异常
        
        Args:
            exception: 处理过程中捕获的异常
        """
        self._exceptions.append(exception)
    
    def intercept(self):
        """拦截事件,阻止事件继续处理
        同时会停止事件传播
        """
        self._propagation_stopped = True
        self._intercepted = True
    
    def __repr__(self):
        return f'Event(type="{self.type}",data={self.data},results={self.results},exceptions={self.exceptions})'
