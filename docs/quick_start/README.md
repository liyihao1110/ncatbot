## 最小可运行示例（插件 / run_backend / run_frontend）

本页提供三种快速起步方式的“最小示例”代码：
- 插件最小示例（基于 UnifiedRegistry 命令注册/过滤器）
- 后端最小示例（run_backend：同步环境主动调用 API）
- 前端最小示例（run_frontend：注册处理器/命令，事件驱动）

> 环境准备：请先正确配置 NapCat（见项目 README 或 `ncatbot.core.adapter.nc.launch` 相关文档），并设置 websocket 与 token。

---

### 1) 插件最小示例（plugins/hello_plugin.py）

文件结构（默认插件目录 `./plugins`）：
```
plugins/
    hello_plugin/
        hello_plugin.py
        __init__.py
```

hello_plugin/hello_plugin.py：
```python
from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

class HelloPlugin(NcatBotPlugin):
    name = "HelloPlugin"
    version = "1.0.0"

    async def on_load(self):
        # 可留空，保持轻量
        pass

    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply("你好！我是插件 HelloPlugin。")

```

hello_plugin/\_\_init\_\_.py：
```python
from .hello_plugin import HelloPlugin

__all__ = ["HelloPlugin"]
```

运行（前端模式）：
```python
from ncatbot.core import BotClient
from ncatbot.utils import config

# 基础配置（示例）
config.set_bot_uin("123456")

bot = BotClient()
bot.run_frontend()
```
- 进入任意群/私聊发送：`/hello` 即可收到回复。
- 命令函数参数（除 `self`）必须有类型注解，详见 UnifiedRegistry 文档。

---

### 2) run_backend 最小示例（同步主动发送）

适用：从同步主线程启动机器人并“主动”发送一些消息，随后继续执行主线程（守护线程连接 NapCat）。

```python
from ncatbot.core import BotClient
from ncatbot.utils import config

# 基础配置（示例）
config.set_bot_uin("123456")

bot = BotClient()
api = bot.run_backend(debug=True)  # 后台线程启动，返回全局 API（同步友好）

# 同步接口主动发消息（示例群号/QQ 号请替换）
api.send_group_text_sync(123456789, "后端已启动：Hello from backend")
api.send_private_text_sync(987654321, "后端问候：Hi")

print("后台已运行，继续做其他同步任务……")
# ... 你的其他逻辑 ...
```

要点：
- `run_backend(...)` 阻塞等待启动成功并返回 `BotAPI`；之后可直接使用 `*_sync` 同步方法。
- 启动参数可传 `bt_uin/root/ws_uri/webui_uri/ws_token/webui_token/remote_mode/enable_webui_interaction/debug` 等（见 `StartArgs`）。

---

### 3) run_frontend 最小示例（事件驱动处理器）

适用：使用装饰器注册事件处理器（或使用 UnifiedRegistry 插件系统），异步流式处理消息。

```python
from ncatbot.core import BotClient
from ncatbot.utils import config
from ncatbot.core.event import GroupMessageEvent, PrivateMessageEvent

# 基础配置（示例）
bot = BotClient()

@bot.on_group_message
async def greet_group(event: GroupMessageEvent):
    if "测试" in "".join(seg.text for seg in event.message.filter_text()):
        await event.reply("前端：测试成功")

@bot.on_private_message
def greet_private(event: PrivateMessageEvent):
    # 同步处理器也可用：
    event.reply_sync("收到私聊（同步回复）")

bot.run_frontend(debug=True, bt_uin="123456")
```

要点：
- 处理器可异步/同步混用；群处理器 `event.reply(..., at=True)` 默认@并引用；私聊使用 `event.reply(...)`。
- 如需使用 UnifiedRegistry 的命令/过滤器，请参考 `docs/plugin_system/unified_registry/*`。

---

### 延伸阅读
- 事件快速上手：`docs/api/QuickStart_Events.md`
- 事件 API 参考：`docs/api/reference/Events.md`
- 消息发送与获取：`docs/api/reference/MessageAPI.md`
- UnifiedRegistry：`docs/plugin_system/unified_registry/UnifiedRegistry-快速开始.md`
