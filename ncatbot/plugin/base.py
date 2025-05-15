"""Base plugin implementation."""

from typing import Any, Dict


class BasePlugin:
    """Base class for all plugins."""

    def __init__(self, name: str, version: str = "0.0.0"):
        self.name = name
        self.version = version
        self.config: Dict[str, Any] = {}

    async def on_load(self) -> None:
        """Called when the plugin is loaded."""
        pass

    async def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        pass
