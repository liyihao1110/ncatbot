import time
from ncatbot.plugin_system import NcatBotPlugin, command_registry
from ncatbot.core.event import BaseMessageEvent

# 记录 Bot 启动时间
start_time = time.time()


class StatusPlugin(NcatBotPlugin):
    name = "StatusPlugin"
    version = "1.0.0"
    description = "一个简单的状态插件，用于显示 Bot 运行时长"
    author = "Cline"

    async def on_load(self):
        # 插件加载时可以执行一些初始化操作
        pass

    @command_registry.command("status", description="显示 Bot 运行状态")
    async def status_cmd(self, event: BaseMessageEvent):
        """处理 /status 命令"""
        running_time = time.time() - start_time
        days = int(running_time // (24 * 3600))
        hours = int((running_time % (24 * 3600)) // 3600)
        minutes = int((running_time % 3600) // 60)
        seconds = int(running_time % 60)

        status_message = (
            f"NcatBot 正在运行中...\n"
            f"运行时长: {days}天 {hours}小时 {minutes}分钟 {seconds}秒"
        )

        await event.reply(status_message)
