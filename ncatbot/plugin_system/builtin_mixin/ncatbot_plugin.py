from typing import final, Any
from ncatbot.plugin_system.base_plugin import BasePlugin
from ..builtin_mixin.command_mixin import CommandMixin
from .config_mixin import ConfigMixin
from .time_task_mixin import TimeTaskMixin
from ncatbot.utils import get_log

LOG = get_log("ncatbot.plugin_system")


class NcatBotPlugin(BasePlugin, ConfigMixin, TimeTaskMixin, CommandMixin):
    def __init__(self, *args, **kwargs):
        BasePlugin.__init__(self, *args, **kwargs)

    async def on_load(self) -> None:
        LOG.info(f"插件 {self.name} 加载成功")

    async def on_reload(self) -> None:
        LOG.info(f"插件 {self.name} 重载成功")

    async def on_close(self) -> None:
        LOG.info(f"插件 {self.name} 卸载成功")

    @final
    async def __unload__(self, *a: Any, **kw: Any) -> None:
        if hasattr(self, "_time_task_jobs"):
            for name in self._time_task_jobs:
                self.remove_scheduled_task(name)
        await super().__unload__(*a, **kw)

    @final
    async def __onload__(self) -> None:
        await super().__onload__()
