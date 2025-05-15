"""Tests for system commands."""

import sys
import unittest
from unittest.mock import MagicMock, call, patch

from ncatbot.cli.commands import system_commands


class TestSystemCommands(unittest.TestCase):
    """Test system commands."""

    @patch("ncatbot.cli.commands.system_commands.BotClient")
    def test_start_normal(self, mock_client_class):
        """Test start command without debug option."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Call the function
        system_commands.start()

        # Verify client was created and run
        mock_client_class.assert_called_once()
        mock_client.run.assert_called_once_with(skip_ncatbot_install_check=False)

    @patch("ncatbot.cli.commands.system_commands.BotClient")
    def test_start_debug(self, mock_client_class):
        """Test start command with debug option."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Call the function with debug flag
        system_commands.start("-d")

        # Verify client was created and run with debug flag
        mock_client_class.assert_called_once()
        mock_client.run.assert_called_once_with(skip_ncatbot_install_check=True)

    @patch("ncatbot.cli.commands.system_commands.BotClient")
    def test_start_exception(self, mock_client_class):
        """Test start command with exception."""
        # Setup mock to raise exception
        mock_client_class.side_effect = Exception("Test error")

        # Patch logger
        with patch("ncatbot.cli.commands.system_commands.LOG") as mock_log:
            # Call the function
            system_commands.start()

            # Verify that exception was logged
            mock_log.error.assert_called_once_with("启动失败: Test error")

    @patch("ncatbot.cli.commands.system_commands.install_napcat")
    @patch("ncatbot.cli.commands.system_commands.subprocess.Popen")
    @patch("ncatbot.cli.commands.system_commands.time.sleep")
    @patch("ncatbot.cli.commands.system_commands.exit")
    def test_update(self, mock_exit, mock_sleep, mock_popen, mock_install_napcat):
        """Test update command."""
        # Call the function
        system_commands.update()

        # Verify that install_napcat was called
        mock_install_napcat.assert_called_once()

        # Verify that Popen was called with correct args
        expected_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "ncatbot",
            "-i",
            system_commands.PYPI_SOURCE,
        ]
        mock_popen.assert_called_once()
        popen_args = mock_popen.call_args[0][0]
        self.assertEqual(popen_args, expected_cmd)

        # Verify that sleep was called twice
        mock_sleep.assert_has_calls([call(1), call(10)])

        # Verify that exit was called
        mock_exit.assert_called_once_with(0)

    def test_exit_cli(self):
        """Test exit_cli command."""
        with patch("builtins.print") as mock_print:
            # Call the function and expect CLIExit exception
            from ncatbot.cli.utils import CLIExit

            with self.assertRaises(CLIExit):
                system_commands.exit_cli()

            # Verify that print was called with exit message
            mock_print.assert_called_once_with("\n 正在退出 Ncatbot CLI. 再见!")


if __name__ == "__main__":
    unittest.main()
