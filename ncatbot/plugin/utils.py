"""Plugin utility functions."""

import os
import sys

from ncatbot.utils.logger import get_log

LOG = get_log("Plugin")


def install_plugin_dependencies(plugin_name: str) -> None:
    """Install dependencies for a plugin.

    Args:
        plugin_name: Name of the plugin
    """
    try:
        requirements_path = os.path.join("plugins", plugin_name, "requirements.txt")
        if os.path.exists(requirements_path):
            import subprocess

            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    requirements_path,
                    "-i",
                    "https://mirrors.aliyun.com/pypi/simple/",
                ]
            )
            LOG.info(f"Installed dependencies for plugin {plugin_name}")
    except Exception as e:
        LOG.error(f"Failed to install dependencies for plugin {plugin_name}: {e}")
        raise
