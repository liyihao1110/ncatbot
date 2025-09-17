# TimeTaskMixin 时间任务混入类使用指南

## 概述

`TimeTaskMixin` 是一个强大的定时任务调度混入类，为插件提供了灵活的定时任务管理功能。支持多种时间格式、条件触发、参数动态生成等高级特性。

## 基本用法

### 支持的时间格式

#### 间隔任务

- 基础单位：`"30s"`, `"5m"`, `"2h"`, `"1d"`
- 组合格式：`"2h30m"`, `"1d12h"`
- 冒号分隔：`"00:05:30"` (时:分:秒)
- 自然语言：`"2天3小时5秒"`

#### 每日定点任务

- 格式：`"09:30"`, `"23:59"`

#### 一次性任务

- 标准格式：`"2025-12-31 23:59:59"`
- GitHub格式：`"2025:12:31-23:59:59"`

### 2. 高级功能

#### 条件执行

```python
def is_working_time():
    return 9 <= datetime.now().hour <= 18

self.add_scheduled_task(
    self.work_task, 
    "work_task", 
    "1h",
    conditions=[is_working_time]
)
```

#### 限制执行次数

```python
# 只执行5次
self.add_scheduled_task(
    self.limited_task, 
    "limited_task", 
    "10s",
    max_runs=5
)
```

#### 动态参数生成

```python
def get_current_data():
    return {"timestamp": time.time()}

self.add_scheduled_task(
    self.data_task,
    "data_task", 
    "30s",
    kwargs_provider=get_current_data
)
```

## 完整示例

```python
class TimeTaskDemo(NcatBotPlugin):
    name = "TimeTaskDemo"
    
    async def on_load(self):
        # 每5秒执行一次
        self.add_scheduled_task(self.heartbeat, "heartbeat", "5s")
        
        # 每天上午9点执行
        self.add_scheduled_task(self.daily_report, "daily", "09:00")
        
        # 带条件的任务
        self.add_scheduled_task(
            self.conditional_task, 
            "conditional", 
            "1m",
            conditions=[self.is_active]
        )
    
    async def heartbeat(self):
        print("💓 心跳检测")
    
    async def daily_report(self):
        print("📊 生成日报")
    
    async def conditional_task(self):
        print("✅ 条件满足，执行任务")
    
    def is_active(self):
        return True  # 你的条件逻辑
```

## 任务管理

### 移除任务

```python
# 移除指定任务
self.remove_scheduled_task("task_name")
```

## 注意事项

1. **任务名称唯一性**：每个任务必须有唯一的名称标识
2. **异步支持**：支持异步和同步函数
3. **资源清理**：插件卸载时会自动清理相关任务
