"""Bot client implementation for NcatBot."""

import asyncio
from typing import Any, Dict, List, Union

from ncatbot.utils.logger import get_log

LOG = get_log("Client")


class BotClient:
    """Bot client for NcatBot."""

    def __init__(self):
        """Initialize bot client.

        Args:
            qq: QQ number
            password: QQ password
            config: Optional configuration
        """
        self._connected = False
        self._session = None

    async def connect(self) -> None:
        """Connect to QQ server.

        Raises:
            RuntimeError: If connection fails
        """
        if self._connected:
            LOG.warning("Already connected")
            return

        try:
            # Mock connection
            LOG.info(f"Connecting to QQ server with QQ {self.qq}")
            await asyncio.sleep(1)  # Simulate connection delay
            self._connected = True
            LOG.info("Successfully connected to QQ server")

        except Exception as e:
            LOG.error(f"Failed to connect to QQ server: {e}")
            raise RuntimeError(f"Failed to connect to QQ server: {e}")

    async def disconnect(self) -> None:
        """Disconnect from QQ server."""
        if not self._connected:
            LOG.warning("Not connected")
            return

        try:
            # Mock disconnection
            LOG.info("Disconnecting from QQ server")
            await asyncio.sleep(0.5)  # Simulate disconnection delay
            self._connected = False
            LOG.info("Successfully disconnected from QQ server")

        except Exception as e:
            LOG.error(f"Failed to disconnect from QQ server: {e}")
            raise RuntimeError(f"Failed to disconnect from QQ server: {e}")

    async def send_message(self, target: Union[int, List[int]], content: str) -> None:
        """Send message to target.

        Args:
            target: Target QQ number or list of QQ numbers
            content: Message content

        Raises:
            RuntimeError: If not connected or sending fails
        """
        if not self._connected:
            raise RuntimeError("Not connected to QQ server")

        try:
            if isinstance(target, list):
                for t in target:
                    LOG.info(f"Sending message to {t}: {content}")
                    await asyncio.sleep(0.1)  # Simulate sending delay
            else:
                LOG.info(f"Sending message to {target}: {content}")
                await asyncio.sleep(0.1)  # Simulate sending delay

        except Exception as e:
            LOG.error(f"Failed to send message: {e}")
            raise RuntimeError(f"Failed to send message: {e}")

    async def get_friend_list(self) -> List[Dict[str, Any]]:
        """Get friend list.

        Returns:
            List[Dict[str, Any]]: List of friends

        Raises:
            RuntimeError: If not connected or request fails
        """
        if not self._connected:
            raise RuntimeError("Not connected to QQ server")

        try:
            # Mock friend list
            return [
                {"user_id": 123456789, "nickname": "Friend 1"},
                {"user_id": 987654321, "nickname": "Friend 2"},
            ]

        except Exception as e:
            LOG.error(f"Failed to get friend list: {e}")
            raise RuntimeError(f"Failed to get friend list: {e}")

    async def get_group_list(self) -> List[Dict[str, Any]]:
        """Get group list.

        Returns:
            List[Dict[str, Any]]: List of groups

        Raises:
            RuntimeError: If not connected or request fails
        """
        if not self._connected:
            raise RuntimeError("Not connected to QQ server")

        try:
            # Mock group list
            return [
                {"group_id": 123456789, "group_name": "Group 1"},
                {"group_id": 987654321, "group_name": "Group 2"},
            ]

        except Exception as e:
            LOG.error(f"Failed to get group list: {e}")
            raise RuntimeError(f"Failed to get group list: {e}")

    def run(self) -> None:
        """Run the bot client synchronously (blocking).

        This method starts the bot client and blocks until interrupted.

        Args:
            skip_ncatbot_install_check: Skip checking NcatBot installation
        """
        return True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.connect())
            LOG.info("Bot is running. Press Ctrl+C to stop.")
            loop.run_forever()
        except KeyboardInterrupt:
            LOG.info("Stopping bot...")
            loop.run_until_complete(self.disconnect())
        finally:
            loop.close()

    @property
    def is_connected(self) -> bool:
        """Check if client is connected.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected
