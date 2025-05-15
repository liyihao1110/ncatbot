"""Plugin loader implementation."""

import importlib.util
import os
from typing import Any, Dict, Optional, Tuple

from ncatbot.plugin.base import BasePlugin
from ncatbot.utils import ncatbot_config as config
from ncatbot.utils.logger import get_log

LOG = get_log("Plugin")


def get_plugin_info_by_name(name: str) -> Tuple[bool, str]:
    if not os.path.exists(os.path.join(config.plugin.plugins_dir, name)):
        return False, None
    return True, {"name": name, "version": "1.0.0"}


class PluginLoader:
    """Plugin loader and manager."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}

    def get_plugin_info(self, path: str) -> Tuple[str, str]:
        """Get plugin information from a directory.

        Args:
            path: Path to the plugin directory

        Returns:
            Tuple[str, str]: (plugin_name, version)

        Raises:
            ValueError: If plugin info cannot be loaded
        """
        try:
            # Try to load plugin info from __init__.py
            init_path = os.path.join(path, "__init__.py")
            if not os.path.exists(init_path):
                raise ValueError(
                    f"Plugin directory {path} does not contain __init__.py"
                )

            spec = importlib.util.spec_from_file_location("plugin", init_path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Cannot load plugin from {path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "Plugin"):
                raise ValueError(f"Plugin class not found in {path}")

            plugin_class = getattr(module, "Plugin")
            if not issubclass(plugin_class, BasePlugin):
                raise ValueError(
                    f"Plugin class in {path} does not inherit from BasePlugin"
                )

            # Create a temporary instance to get info
            plugin = plugin_class()
            return plugin.name, plugin.version

        except Exception as e:
            LOG.error(f"Failed to load plugin info from {path}: {e}")
            raise ValueError(f"Failed to load plugin info: {e}")

    def load_plugin(self, path: str) -> Optional[BasePlugin]:
        """Load a plugin from a directory.

        Args:
            path: Path to the plugin directory

        Returns:
            Optional[BasePlugin]: Loaded plugin instance or None if loading failed
        """
        try:
            name, version = self.get_plugin_info(path)
            if name in self.loaded_plugins:
                LOG.warning(f"Plugin {name} is already loaded")
                return self.loaded_plugins[name]

            # Load the plugin module
            init_path = os.path.join(path, "__init__.py")
            spec = importlib.util.spec_from_file_location("plugin", init_path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Cannot load plugin from {path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Create plugin instance
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class()
            plugin.config = self.config.get(name, {})

            # Store loaded plugin
            self.loaded_plugins[name] = plugin
            LOG.info(f"Loaded plugin {name} v{version}")
            return plugin

        except Exception as e:
            LOG.error(f"Failed to load plugin from {path}: {e}")
            return None

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin by name.

        Args:
            name: Name of the plugin to unload

        Returns:
            bool: True if plugin was unloaded, False otherwise
        """
        if name not in self.loaded_plugins:
            LOG.warning(f"Plugin {name} is not loaded")
            return False

        try:
            plugin = self.loaded_plugins[name]
            del self.loaded_plugins[name]
            LOG.info(f"Unloaded plugin {name}")
            return True
        except Exception as e:
            LOG.error(f"Failed to unload plugin {name}: {e}")
            return False

    def get_loaded_plugins(self) -> Dict[str, BasePlugin]:
        """Get all loaded plugins.

        Returns:
            Dict[str, BasePlugin]: Dictionary of loaded plugins
        """
        return self.loaded_plugins.copy()
