from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    BaseFilter,
    filter_registry,
)
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
import time


class LevelFilter(BaseFilter):
    def __init__(self, min_level: int):
        super().__init__(f"level_{min_level}")
        self.min_level = min_level

    def check(self, event: BaseMessageEvent) -> bool:
        return self.get_user_level(event.user_id) >= self.min_level

    def get_user_level(self, user_id: str) -> int:
        # 演示：固定返回 1，可按需扩展
        return 1


class LevelAndCooldownPlugin(NcatBotPlugin):
    name = "LevelAndCooldownPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    def _is_command(self, event: BaseMessageEvent) -> bool:
        raw = getattr(event, "raw_message", None) or ""
        return isinstance(raw, str) and (raw.startswith("/") or raw.startswith("!"))

    @LevelFilter(min_level=1)
    async def high_level_message(self, event: BaseMessageEvent):
        if "高等级" in event.raw_message:
            await event.reply("收到一条高等级用户的消息")

    # 冷却时间过滤器注册
    @filter_registry.register("cooldown")
    def cooldown_filter(event: BaseMessageEvent) -> bool:
        # 注意：此处访问 self 仅为示例，真实实现建议外移或用闭包
        user_id = event.user_id
        current_time = time.time()
        store = LevelAndCooldownPlugin._cooldown_store
        if user_id in store and current_time - store[user_id] < 1:
            return False
        store[user_id] = current_time
        return True

    # 用于演示存储（避免实例问题）
    _cooldown_store = {}

    @filter_registry.filters("cooldown")
    @command_registry.command("limited")
    async def limited_command(self, event: BaseMessageEvent):
        await event.reply("有冷却限制的命令")
