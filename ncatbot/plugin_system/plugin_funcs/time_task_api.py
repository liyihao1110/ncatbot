# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-15 19:08:20
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-15 19:16:58
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from typing import Any, Dict, List, Callable, Optional, Tuple, Union, final
from ...utils import TimeTaskScheduler
from ..abc_api import AbstractPluginApi

class TimeTaskMixin(AbstractPluginApi):
    """定时任务调度混入类，提供定时任务的管理功能
    
    # 描述
    该混入类提供了定时任务的添加、移除等管理功能支持灵活的任务调度配置，
    包括固定间隔执行、条件触发、参数动态生成等特性

    # 属性
    - `_time_task_scheduler` (TimeTaskScheduler): 时间任务调度器实例

    # 特性
    - 支持固定时间间隔的任务调度
    - 支持条件触发机制
    - 支持最大执行次数限制
    - 支持动态参数生成
    """
    _time_task_scheduler: TimeTaskScheduler
    meta_data: dict
    
    def init_api(self):
        self._time_task_scheduler = TimeTaskScheduler()
    
    @final
    def add_scheduled_task(self,
                job_func: Callable,
                name: str,
                interval: Union[str, int, float],
                conditions: Optional[List[Callable[[], bool]]] = None,
                max_runs: Optional[int] = None,
                args: Optional[Tuple] = None,
                kwargs: Optional[Dict] = None,
                args_provider: Optional[Callable[[], Tuple]] = None,
                kwargs_provider: Optional[Callable[[], Dict[str, Any]]] = None) -> bool:
        """添加一个定时任务

        Args:
            job_func (Callable): 要执行的任务函数
            name (str): 任务名称
            interval (Union[str, int, float]): 任务执行的时间间隔
            conditions (Optional[List[Callable[[], bool]]], optional): 任务执行的条件列表默认为None
            max_runs (Optional[int], optional): 任务的最大执行次数默认为None
            args (Optional[Tuple], optional): 任务函数的位置参数默认为None
            kwargs (Optional[Dict], optional): 任务函数的关键字参数默认为None
            args_provider (Optional[Callable[[], Tuple]], optional): 提供任务函数位置参数的函数默认为None
            kwargs_provider (Optional[Callable[[], Dict[str, Any]]], optional): 提供任务函数关键字参数的函数默认为None

        Returns:
            bool: 如果任务添加成功返回True，否则返回False
        """
        if 'time_task' not in self.meta_data:
            self.meta_data['time_task'] = {}
        if name in self.meta_data['time_task']:
            raise RuntimeError(f"你不能添加同任务: '{name}' 已经添加过了")
        job_info = {
            'name': name,
            'job_func': job_func,
            'interval': interval,
            'max_runs': max_runs,
            'conditions': conditions or [],
            'args': args,
            'kwargs': kwargs or {},
            'args_provider': args_provider,
            'kwargs_provider': kwargs_provider
        }
        self.meta_data['time_task'][name] = job_info
        return self._time_task_scheduler.add_job(**job_info)

    @final
    def remove_scheduled_task(self, task_name: str):
        """移除一个定时任务

        Args:
            task_name (str): 要移除的任务名称

        Returns:
            bool: 如果任务移除成功返回True，否则返回False
        """
        if self._time_task_scheduler.remove_job(name=task_name):
            del self.meta_data['time_task'][task_name]
            return True
        return False