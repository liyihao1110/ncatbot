# NcatBot 插件系统开发文档

## 重要注意事项

⚠️ **特别提醒**:

1. 系统当前未处理 Ctrl+C 中断，这意味着插件的 `on_unload`方法不会自动执行，数据也不会自动保存
2. 插件的工作路径会被重定向到 `./data/{plugin_name}/`
3. 需要手动安装 `packaging` 依赖: `pip install packaging`
4. 此文档由ai创建，仅用于参考
5. 目前处于测试阶段，接口和运行机制可能进行完全不兼容的修改

## 1. 快速开始

### 1.1 配置开发环境

```bash
# 克隆项目
git clone https://github.com/your/ncatbot.git
cd ncatbot

# 安装依赖
pip install -e .
pip install packaging
```

### 1.2 创建基础插件

```python
from .main import MyPlugin

__all__ = ['MyPlugin']
```

```python
from ncatbot.plugins_sys import BasePlugin, Event

class MyPlugin(BasePlugin):
    name = "MyPlugin"
    version = "1.0.0"

    async def on_load(self):
        print(f"元数据: {self.meta_data}")
        print(f"工作路径: {os.getcwd()}")  # 会指向 ./data/MyPlugin/
        self.register_handler("my_event", self.handle_event)

    async def handle_event(self, event: Event):
        print(f"收到事件: {event.data}")
```

## 2. 核心概念

### 2.1 事件系统

```python
@dataclass
class Event:
    type: str                   # 事件类型
    data: Dict[str, Any]       # 事件数据
    results: List[Any]         # 处理结果
    _stopped: bool = False     # 是否停止传播

    def stop_propagation(self):
        """停止事件继续传播"""
        self._stopped = True
```

### 2.2 插件生命周期

```python
class MyPlugin(BasePlugin):
    async def on_load(self):
        """插件加载时调用"""
        pass

    async def on_unload(self):
        """插件卸载时调用"""
        pass

    async def _close_(self):
        """插件关闭时自动调用(需正确退出)"""
        pass
```

### 2.3 数据持久化

```python
class MyPlugin(BasePlugin):
    def __init__(self, event_bus):
        super().__init__(event_bus)
        self.data["counter"] = 0  # 会自动保存到 data/{plugin_name}/Plugin.json

    async def on_load(self):
        print(f"计数器: {self.data['counter']}")
```

### 2.4 事件处理

```python
class MyPlugin(BasePlugin):
    async def on_load(self):
        # 支持正则匹配,re:前缀
        self.register_handler("re:test\.", self.handle_test)
        self.register_handler("exact.match", self.handle_exact)

    async def handle_test(self, event: Event):
        print(f"正则匹配处理器: {event.data}")

    async def handle_exact(self, event: Event):
        print(f"精确匹配处理器: {event.data}")
```

## 3. 插件开发指南

### 3.1 推荐的插件结构

```
my_plugin/
├── __init__.py      # 定义运行时的插件类
├── main.py          # 工具函数
├── utils.py         # 工具函数
├── LICENSE          # 开源协议
└── README.md        # 文档
```

### 3.2 插件间通信

```python
# 发布事件
event = Event("test.event", {"message": "hello"})
await self.event_bus.publish_async(event)  # 异步发布
results = await self.event_bus.publish_sync(event)  # 同步等待结果
```

### 3.3 插件依赖管理

```python
class MyPlugin(BasePlugin):
    name = "MyPlugin"
    version = "1.0.0"
    dependencies = {
        "OtherPlugin": ">=1.0.0",
        "Logger": ">=2.0.0"
    }
```

### 3.4 配置和元数据

```python
class MyPlugin(BasePlugin):
    async def on_load(self):
        # meta_data 是只读的全局配置
        api_key = self.meta_data.get("api_key")

        # data 是插件私有的可写存储
        self.data["count"] = self.data.get("count", 0) + 1
```

## 4. 最佳实践

1. **异常处理**：始终包装可能失败的操作

```python
try:
    result = await self.do_something()
except Exception as e:
    print(f"操作失败: {e}")
```

2. **资源管理**：使用 `async with` 管理异步资源

```python
async def handle_event(self, event):
    async with self.lock:  # 线程安全的资源访问
        self.data["count"] += 1
```

3. **优雅退出**：实现 `_close_` 方法清理资源

```python
async def _close_(self):
    await super()._close_()  # 调用基类清理
    await self.cleanup_resources()
```

4. **版本控制**：使用语义化版本号

```python
version = "1.0.0"  # 主版本.次版本.修订号
```
