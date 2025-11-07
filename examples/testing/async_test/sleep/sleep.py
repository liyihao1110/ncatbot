import time
import asyncio
from ncatbot.plugin_system import NcatBotPlugin, command_registry
from ncatbot.core.event import BaseMessageEvent

class SleepPlugin(NcatBotPlugin):
    name = "SleepPlugin"
    version = "1.0.0"
    description = "一个简单的状态插件，用于让bot睡觉"
    author = "Cline"

    async def on_load(self):
        # 插件加载时可以执行一些初始化操作
        pass

    @command_registry.command("sleep", description="让bot进入睡眠状态")
    def sleep_cmd(self, event: BaseMessageEvent):
        """处理 /sleep 命令"""
        event.reply_sync("正在进入睡眠状态...")
        time.sleep(9)  # 模拟睡眠99秒
        event.reply_sync("睡眠结束，bot 已唤醒。")

    @command_registry.command("asleep", description="让bot进入睡眠状态")
    async def asleep_cmd(self, event: BaseMessageEvent):
        """处理 /sleep 命令"""
        await event.reply("正在异步进入睡眠状态...")
        await asyncio.sleep(9)  # 模拟睡眠99秒
        await event.reply("异步睡眠结束，bot 已唤醒。")
    