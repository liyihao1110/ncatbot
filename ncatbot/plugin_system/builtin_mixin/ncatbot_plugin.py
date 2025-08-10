from ncatbot.plugin_system.base_plugin import BasePlugin
from .config_mixin import ConfigMixin
from .time_task_mixin import TimeTaskMixin
from ncatbot.utils import get_log

LOG = get_log("ncatbot.plugin_system")

class NcatBotPlugin(BasePlugin, ConfigMixin, TimeTaskMixin):
    async def on_load(self) -> None:
        LOG.info(f"插件 {self.name} 加载成功")

    async def on_reload(self) -> None:
        LOG.info(f"插件 {self.name} 重载成功")
    
    async def on_close(self) -> None:
        LOG.info(f"插件 {self.name} 卸载成功")