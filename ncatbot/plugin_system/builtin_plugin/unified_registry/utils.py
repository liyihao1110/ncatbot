import inspect
from pathlib import Path
from typing import Callable
from ncatbot.utils import ncatbot_config


def get_func_plugin_name(func: Callable) -> str:
    plugin_dir = Path(ncatbot_config.plugin.plugins_dir).resolve()
    file = inspect.getsourcefile(func)
    plugin_name = "ncatbot"
    if file:
        file_path = Path(file).resolve()
        try:
            relative_path = file_path.relative_to(plugin_dir)
            if relative_path.parts:
                plugin_name = relative_path.parts[0]
        except ValueError:
            pass
    return plugin_name
