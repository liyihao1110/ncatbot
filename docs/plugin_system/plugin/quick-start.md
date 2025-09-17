# 插件快速开始指南

本指南将帮助您快速了解 ncatbot 插件系统的基本结构，并创建一个简单的插件示例。

## 插件系统概述

ncatbot 插件系统基于事件驱动架构，提供以下核心功能：

- **生命周期管理**：自动处理插件的加载、重载和卸载
- **命令注册系统**：支持参数、选项、别名等高级命令功能
- **事件处理**：响应各种 QQ 消息事件
- **权限控制**：内置管理员、群组等权限过滤器
- **配置管理**：支持 YAML 格式的插件配置

## 最小插件示例

### 1. 插件文件结构

```
plugins/
└── your_plugin/
    ├── __init__.py          # 插件入口文件
    └── main.py       # 插件主文件
```

#### main.py

```python
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

class HelloPlugin(NcatBotPlugin):
    """简单的问候插件"""
    
    # 必需的插件元数据
    name = "HelloPlugin"
    version = "1.0.0"
    description = "一个简单的问候插件"
    
    async def on_load(self):
        """插件加载时的初始化"""
        pass
    
    @command_registry.command("hello", aliases=["hi"], description="问候命令")
    async def hello_command(self, event: BaseMessageEvent):
        """处理 /hello 命令"""
        await event.reply("你好！这是来自 HelloPlugin 的问候。")
```

#### __init__.py

```python
from .main import HelloPlugin # 导入插件类

__all__ = ["HelloPlugin"] # 导出插件类，供插件系统识别
```

### 2. 插件必需属性

每个插件都必须定义以下属性：

- `name` (str): 插件名称，必须唯一
- `version` (str): 插件版本号
- `description` (str): 插件描述（可选）
- `author` (str): 插件作者（可选，默认为 "Unknown"）

### 3. 生命周期方法

插件可以重写以下生命周期方法：

**`on_load`**: 插件加载时调用，用于初始化资源，必须定义为**异步方法**。
**`on_close`**: 插件卸载时调用，用于清理资源，必须定义为**异步方法**。

```python
class MyPlugin(NcatBotPlugin):
    async def on_load(self):
        """插件加载时调用，用于初始化资源"""
        pass
    
    async def on_close(self):
        """插件卸载时调用，用于清理资源"""
        pass
```

## 插件类的一些属性

- `self.api`：用于调用 NcatBot API，[API 参考](../../api/README.md)
- `self._time_task_scheduler`：定时任务调度器，[定时任务](./time_task_mixin.md)
- `self.config`：用于存放插件的一些配置数据，[配置](./config_mixin.md)

