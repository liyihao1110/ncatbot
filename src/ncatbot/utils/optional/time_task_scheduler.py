# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 20:40:12
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-23 15:30:12
# @Description  : 定时任务支持
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import functools
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from schedule import Scheduler


class TimeTaskScheduler:
    """
    任务调度器，支持以下特性:
    - 多模式调度: 间隔任务/每日定点任务/一次性任务
    - 动态参数生成函数/预定义静态参数传入
    - 外部循环单步执行模式/独立执行模式
    - 执行条件判断
    - 运行次数限制

    Attributes:
        _scheduler (Scheduler): 内部调度器实例
        _jobs (list): 存储所有任务信息的列表
    """

    def __init__(self):
        self._scheduler = Scheduler()
        self._jobs = []

    def _parse_time(self, time_str: str) -> dict:
        """
        解析时间参数为调度配置字典，支持格式:
        - 一次性任务: 'YYYY-MM-DD HH:MM:SS' 或 GitHub Action格式 'YYYY:MM:DD-HH:MM:SS'
        - 每日任务: 'HH:MM'
        - 间隔任务:
            * 基础单位: '120s', '2h30m', '0.5d'
            * 冒号分隔: '00:15:30' (时:分:秒)
            * 自然语言: '2天3小时5秒'

        Args:
            time_str (str): 时间参数字符串

        Returns:
            dict: 调度配置字典，包含以下键:
                - type: 调度类型 ('once'/'daily'/'interval')
                - value: 具体参数 (秒数/时间字符串)

        Raises:
            ValueError: 当时间格式无效时抛出
        """
        # 尝试解析为一次性任务
        try:
            if re.match(r"^\d{4}:\d{2}:\d{2}-\d{2}:\d{2}:\d{2}$", time_str):
                dt_str = time_str.replace(":", "-", 2).replace("-", " ", 1)
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            else:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            now = datetime.now()
            if dt < now:
                raise ValueError("指定的时间已过期")

            return {"type": "once", "value": (dt - now).total_seconds()}
        except ValueError:
            pass

        # 尝试解析为每日任务
        if re.match(r"^([0-1][0-9]|2[0-3]):([0-5][0-9])$", time_str):
            try:
                datetime.strptime(time_str, "%H:%M")
                return {"type": "daily", "value": time_str}
            except ValueError:
                pass

        # 解析为间隔任务
        try:
            return {"type": "interval", "value": self._parse_interval(time_str)}
        except ValueError as e:
            raise ValueError(f"无效的时间格式: {time_str}") from e

    def _parse_interval(self, time_str: str) -> int:
        """
        解析间隔时间参数为秒数

        Args:
            time_str (str): 间隔时间字符串，支持格式:
                * 基础单位: '120s', '2h30m', '0.5d'
                * 冒号分隔: '00:15:30' (时:分:秒)
                * 自然语言: '2天3小时5秒'

        Returns:
            int: 总秒数

        Raises:
            ValueError: 当格式无效时抛出
        """
        units = {"d": 86400, "h": 3600, "m": 60, "s": 1}

        # 单位组合格式 (如2h30m)
        unit_match = re.match(r"^([\d.]+)([dhms])?$", time_str, re.IGNORECASE)
        if unit_match:
            num, unit = unit_match.groups()
            unit = unit.lower() if unit else "s"
            return int(float(num) * units[unit])

        # 冒号分隔格式 (如01:30:00)
        if ":" in time_str:
            parts = list(map(float, time_str.split(":")))
            multipliers = [1, 60, 3600, 86400][-len(parts) :]
            return int(sum(p * m for p, m in zip(parts[::-1], multipliers)))

        # 自然语言格式 (如2天3小时5秒)
        lang_match = re.match(r"(\d+)\s*天\s*(\d+)\s*小时\s*(\d+)\s*秒", time_str)
        if lang_match:
            d, h, s = map(int, lang_match.groups())
            return d * 86400 + h * 3600 + s

        raise ValueError("无法识别的间隔时间格式")

    def add_job(
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
        """
        添加定时任务

        Args:
            job_func (Callable): 要执行的任务函数
            name (str): 任务唯一标识名称
            interval (Union[str, int, float]): 调度时间参数
            conditions (Optional[List[Callable]]): 执行条件列表
            max_runs (Optional[int]): 最大执行次数
            args (Optional[Tuple]): 静态位置参数
            kwargs (Optional[Dict]): 静态关键字参数
            args_provider (Optional[Callable]): 动态位置参数生成函数
            kwargs_provider (Optional[Callable]): 动态关键字参数生成函数

        Returns:
            bool: 是否添加成功

        Raises:
            ValueError: 当参数冲突或时间格式无效时
        """
        # 名称唯一性检查
        if any(job["name"] == name for job in self._jobs):
            print(f"任务添加失败: 名称 '{name}' 已存在")
            return False

        # 参数冲突检查
        if (args and args_provider) or (kwargs and kwargs_provider):
            raise ValueError("静态参数和动态参数生成器不能同时使用")

        try:
            # 解析时间参数
            interval_cfg = self._parse_time(str(interval))

            # 一次性任务强制设置max_runs=1
            if interval_cfg["type"] == "once":
                if max_runs and max_runs != 1:
                    raise ValueError("一次性任务必须设置 max_runs=1")
                max_runs = 1

            job_info = {
                "name": name,
                "func": job_func,
                "max_runs": max_runs,
                "run_count": 0,
                "conditions": conditions or [],
                "static_args": args,
                "static_kwargs": kwargs or {},
                "args_provider": args_provider,
                "kwargs_provider": kwargs_provider,
            }

            @functools.wraps(job_func)
            def job_wrapper():
                # 执行次数检查
                if (
                    job_info["max_runs"]
                    and job_info["run_count"] >= job_info["max_runs"]
                ):
                    self.remove_job(name)
                    return

                # 条件检查
                if not all(cond() for cond in job_info["conditions"]):
                    return

                # 参数处理
                dyn_args = (
                    job_info["args_provider"]() if job_info["args_provider"] else ()
                )
                dyn_kwargs = (
                    job_info["kwargs_provider"]() if job_info["kwargs_provider"] else {}
                )
                final_args = dyn_args or job_info["static_args"] or ()
                final_kwargs = {**job_info["static_kwargs"], **dyn_kwargs}

                # 执行任务
                try:
                    job_info["func"](*final_args, **final_kwargs)
                    job_info["run_count"] += 1
                except Exception as e:
                    print(f"任务执行失败 [{name}]: {str(e)}")

            # 创建调度任务
            if interval_cfg["type"] == "interval":
                job = self._scheduler.every(interval_cfg["value"]).seconds.do(
                    job_wrapper
                )
            elif interval_cfg["type"] == "daily":
                job = (
                    self._scheduler.every()
                    .day.at(interval_cfg["value"])
                    .do(job_wrapper)
                )
            elif interval_cfg["type"] == "once":
                job = self._scheduler.every(interval_cfg["value"]).seconds.do(
                    job_wrapper
                )

            job_info["schedule_job"] = job
            self._jobs.append(job_info)
            return True

        except Exception as e:
            print(f"任务添加失败: {str(e)}")
            return False

    def step(self) -> None:
        """单步执行"""
        self._scheduler.run_pending()

    def run(self) -> None:
        """独立运行"""
        try:
            while True:
                self.step()
                # 计算下一次任务的最早执行时间
                next_run_time = None
                for job in self._jobs:
                    if job["schedule_job"].next_run is not None:
                        if (
                            next_run_time is None
                            or job["schedule_job"].next_run < next_run_time
                        ):
                            next_run_time = job["schedule_job"].next_run
                # 如果有任务待执行，计算需要等待的时间
                if next_run_time is not None:
                    sleep_time = (next_run_time - datetime.now()).total_seconds()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        # 如果已经过了下一次执行时间，立即检查任务
                        continue
                else:
                    # 如果没有任务待执行，适当等待
                    time.sleep(0.2)  # 我觉得吧, 应该不需要等待
        except KeyboardInterrupt:
            print("\n调度器已安全停止")

    def remove_job(self, name: str) -> bool:
        """
        移除指定名称的任务

        Args:
            name (str): 要移除的任务名称

        Returns:
            bool: 是否成功找到并移除任务
        """
        for job in self._jobs:
            if job["name"] == name:
                self._scheduler.cancel_job(job["schedule_job"])
                self._jobs.remove(job)
                return True
        return False

    def get_job_status(self, name: str) -> Optional[dict]:
        """
        获取任务状态信息

        Args:
            name (str): 任务名称

        Returns:
            Optional[dict]: 包含状态信息的字典，格式:
                {
                    'name': 任务名称,
                    'next_run': 下次运行时间,
                    'run_count': 已执行次数,
                    'max_runs': 最大允许次数
                }
        """
        for job in self._jobs:
            if job["name"] == name:
                return {
                    "name": name,
                    "next_run": job["schedule_job"].next_run,
                    "run_count": job["run_count"],
                    "max_runs": job["max_runs"],
                }
        return None
