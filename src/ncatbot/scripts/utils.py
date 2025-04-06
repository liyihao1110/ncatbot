import os

from ncatbot.plugin import PluginLoader
from ncatbot.utils import PLUGINS_DIR


def get_plugin_info(path: str):
    if os.path.exists(path):
        return PluginLoader(None).get_plugin_info(path)
    else:
        raise FileNotFoundError(f"dir not found: {path}")


def get_pulgin_info_by_name(name: str):
    """
    Args:
        name (str): 插件名
    Returns:
        Tuple[bool, str]: 是否存在插件, 插件版本
    """
    plugin_path = os.path.join(PLUGINS_DIR, name)
    if os.path.exists(plugin_path):
        return True, get_plugin_info(plugin_path)[1]
    else:
        return False, "0.0.0"
