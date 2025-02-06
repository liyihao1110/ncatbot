import importlib
import os

from ncatbot.logger import get_log
from ncatbot.message import GroupMessage, PrivateMessage
from ncatbot.plugins_base import PluginBase

_log = get_log()


class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def load_plugins(self):
        """加载插件目录中的插件"""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                module_name = filename[:-3]  # 去掉 .py 后缀
                if module_name == "__init__":
                    continue
                module = importlib.import_module(f"plugins.{module_name}")
                plugin_class = getattr(module, module_name)
                plugin_instance = plugin_class()  # 实例化插件类
                self.plugins.append(plugin_instance)

        _log.info(f"Loaded {len(self.plugins)} plugins")
        _log.info(f"Plugins: {self.plugins}")

    def register_plugin(self, plugin: PluginBase):
        """注册插件"""
        self.plugins.append(plugin)

    async def handle_group_message(self, msg: GroupMessage):
        """调用所有插件的 on_group_message"""
        for plugin in self.plugins:
            if hasattr(plugin, "on_group_message"):
                await plugin.on_group_message(msg)

    async def handle_private_message(self, msg: PrivateMessage):
        """调用所有插件的 on_private_message"""
        _log.info(f"Handling private message: {msg}")
        for plugin in self.plugins:
            if hasattr(plugin, "on_private_message"):
                _log.info(f"Calling plugin {plugin} on_private_message")
                await plugin.on_private_message(msg)

    async def handle_notice(self, msg):
        """调用所有插件的 on_notice"""
        for plugin in self.plugins:
            if hasattr(plugin, "on_notice"):
                await plugin.on_notice(msg)

    async def handle_request(self, msg):
        """调用所有插件的 on_request"""
        for plugin in self.plugins:
            if hasattr(plugin, "on_request"):
                await plugin.on_request(msg)
