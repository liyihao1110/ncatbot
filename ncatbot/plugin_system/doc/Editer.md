# 插件系统功能扩展指南

## 扩展 BasePlugin

你可以通过继承 BasePlugin 创建增强版本的插件基类:

```python
class BasePluginPlus(BasePlugin):
    """增强版插件基类"""
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._storage = {}  # 添加存储空间
      
    async def save_data(self, key: str, value: Any):
        """添加数据持久化方法"""
        self._storage[key] = value
        # 保存到文件
        async with aiofiles.open(self.workspace / "data.json", "w") as f:
            await f.write(json.dumps(self._storage))
          
    async def load_data(self, key: str) -> Any:
        """添加数据加载方法"""
        if not self._storage:
            # 从文件加载
            try:
                async with aiofiles.open(self.workspace / "data.json") as f:
                    self._storage = json.loads(await f.read())
            except FileNotFoundError:
                pass
        return self._storage.get(key)
```

## 扩展装饰器系统

通过继承 CompatibleHandler 可以创建新的装饰器:

```python
class TimedHandler(CompatibleHandler):
    """定时任务装饰器"""
  
    @staticmethod 
    def check(func: Callable) -> bool:
        return hasattr(func, "_timed_task")
      
    @staticmethod
    def handle(plugin: BasePlugin, func: Callable, event_bus: EventBus) -> None:
        interval = func._timed_task["interval"]
        asyncio.create_task(TimedHandler._run_task(plugin, func, interval))
      
    @staticmethod
    async def _run_task(plugin: BasePlugin, func: Callable, interval: float):
        while True:
            await asyncio.sleep(interval)
            await func(plugin)

def timed_task(interval: float):
    """添加定时任务装饰器"""
    def wrapper(func):
        func._timed_task = {"interval": interval}
        return func
    return wrapper
```

使用示例:

```python
class MyPlugin(BasePluginPlus):
    @timed_task(interval=60)
    async def check_updates(self):
        """每60秒执行一次"""
        pass
```

## 扩展事件总线

你可以通过继承 EventBus 添加新功能:

```python
class EventBusPlus(EventBus):
    """增强版事件总线"""
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = []
      
    async def publish(self, event: Event) -> List[Any]:
        """添加事件历史记录"""
        self._history.append({
            "time": time.time(),
            "type": event.type,
            "data": event.data
        })
        return await super().publish(event)
      
    def get_history(self, limit: int = 100) -> List[dict]:
        """获取最近的事件历史"""
        return self._history[-limit:]
```
