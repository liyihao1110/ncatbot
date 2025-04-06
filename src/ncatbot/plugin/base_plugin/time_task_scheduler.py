from typing import Any, Callable, Dict, List, Optional, Tuple, Union, final

from ncatbot.utils import TimeTaskScheduler


class SchedulerMixin:
    """定时任务调度混入类，提供定时任务的管理功能。

    # 描述
    该混入类提供了定时任务的添加、移除等管理功能。支持灵活的任务调度配置，
    包括固定间隔执行、条件触发、参数动态生成等特性。

    # 属性
    - `_time_task_scheduler` (TimeTaskScheduler): 时间任务调度器实例

    # 特性
    - 支持固定时间间隔的任务调度
    - 支持条件触发机制
    - 支持最大执行次数限制
    - 支持动态参数生成
    """

    _time_task_scheduler: TimeTaskScheduler

    @final
    def add_scheduled_task(
        self,
        job_func: Callable,
        name: str,
        interval: Union[str, int, float],
        conditions: Optional[List[Callable[[], bool]]] = None,
        max_runs: Optional[int] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict] = None,
        args_provider: Optional[Callable[[], Tuple]] = None,
        kwargs_provider: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> bool:
        """添加一个定时任务。

        Args:
            job_func (Callable): 要执行的任务函数。
            name (str): 任务名称。
            interval (Union[str, int, float]): 任务执行的时间间隔。
            conditions (Optional[List[Callable[[], bool]]], optional): 任务执行的条件列表。默认为None。
            max_runs (Optional[int], optional): 任务的最大执行次数。默认为None。
            args (Optional[Tuple], optional): 任务函数的位置参数。默认为None。
            kwargs (Optional[Dict], optional): 任务函数的关键字参数。默认为None。
            args_provider (Optional[Callable[[], Tuple]], optional): 提供任务函数位置参数的函数。默认为None。
            kwargs_provider (Optional[Callable[[], Dict[str, Any]]], optional): 提供任务函数关键字参数的函数。默认为None。

        Returns:
            bool: 如果任务添加成功返回True，否则返回False。
        """
        job_info = {
            "name": name,
            "job_func": job_func,
            "interval": interval,
            "max_runs": max_runs,
            "conditions": conditions or [],
            "args": args,
            "kwargs": kwargs or {},
            "args_provider": args_provider,
            "kwargs_provider": kwargs_provider,
        }
        return self._time_task_scheduler.add_job(**job_info)

    @final
    def remove_scheduled_task(self, task_name: str):
        """移除一个定时任务。

        Args:
            task_name (str): 要移除的任务名称。

        Returns:
            bool: 如果任务移除成功返回True，否则返回False。
        """
        return self._time_task_scheduler.remove_job(name=task_name)
