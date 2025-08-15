"""Global state management for NcatBot."""

from threading import Lock
from typing import Any, Set, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ncatbot.core.api import BotAPI


class Status:
    """Global state management class."""

    def __init__(self):
        self.exit = False # 全局退出标志
        self._lock = Lock()
        self.current_github_proxy = None
        self.global_api: BotAPI = None
        self._registered_loggers: Set[str] = set()

    def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        with self._lock:
            setattr(self, key, value)

    def register_logger(self, logger_name: str) -> None:
        """Register a logger created via get_log.

        Args:
            logger_name: The name of the logger to register
        """
        with self._lock:
            self._registered_loggers.add(logger_name)

    def is_registered_logger(self, logger_name: str) -> bool:
        """Check if a logger was created via get_log.

        Args:
            logger_name: The name of the logger to check

        Returns:
            bool: True if the logger was created via get_log, False otherwise
        """
        with self._lock:
            return logger_name in self._registered_loggers

    def update_logger_level(self) -> None:
        """Update the level of all registered loggers."""
        from ncatbot.utils.config import ncatbot_config
        level = logging.DEBUG if ncatbot_config.debug else logging.INFO
        logging.getLogger().setLevel(level)
        with self._lock:
            for logger_name in self._registered_loggers:
                logger = logging.getLogger(logger_name)
                logger.setLevel(level)

    def get_registered_loggers(self) -> Set[str]:
        """Get all registered logger names.

        Returns:
            Set[str]: A set of all registered logger names
        """
        with self._lock:
            return self._registered_loggers.copy()


# Global status instance
status = Status()
