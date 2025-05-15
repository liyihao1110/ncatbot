"""Tests for config commands."""

import unittest
from unittest.mock import patch

from ncatbot.cli.commands import config_commands


class TestConfigCommands(unittest.TestCase):
    """Test config commands."""

    def test_set_qq_valid(self):
        """Test set_qq command with valid input."""
        with patch("builtins.input") as mock_input:
            with patch("builtins.print") as mock_print:
                with patch(
                    "ncatbot.utils.ncatbot_config.save_permanent_config"
                ) as mock_save:
                    # Setup inputs for valid QQ number
                    mock_input.side_effect = ["123456789", "123456789"]

                    # Call the function
                    result = config_commands.set_qq()

                    # Verify that the function asked for input twice
                    self.assertEqual(mock_input.call_count, 2)
                    # Verify that save_permanent_config was called with correct args
                    mock_save.assert_called_once_with("bt_uin", "123456789")
                    # Verify that print was called at least once
                    self.assertTrue(mock_print.called)
                    # Verify that the function returned the QQ number
                    self.assertEqual(result, "123456789")

    def test_set_qq_non_numeric(self):
        """Test set_qq command with non-numeric input."""
        with patch("builtins.input") as mock_input:
            with patch("builtins.print") as mock_print:
                # We don't mock set_qq recursively here since we want to test the actual function flow

                # First test with invalid input, then valid on second try
                mock_input.side_effect = ["invalid", "123456789", "123456789"]

                # Call the function
                with patch(
                    "ncatbot.utils.ncatbot_config.save_permanent_config"
                ) as mock_save:
                    result = config_commands.set_qq()
                    # Verify that save_permanent_config was called
                    self.assertTrue(mock_save.called)

                # Verify that print was called with error message
                mock_print.assert_any_call("QQ 号必须为数字!")
                # Verify that the function returned the QQ number
                self.assertEqual(result, "123456789")

    def test_set_qq_mismatch(self):
        """Test set_qq command with mismatched inputs."""
        with patch("builtins.input") as mock_input:
            with patch("builtins.print") as mock_print:
                # We don't mock set_qq recursively here since we want to test the actual function flow

                # First test with mismatched inputs, then valid on second try
                mock_input.side_effect = [
                    "123456789",
                    "987654321",
                    "123456789",
                    "123456789",
                ]

                # Call the function
                with patch(
                    "ncatbot.utils.ncatbot_config.save_permanent_config"
                ) as mock_save:
                    result = config_commands.set_qq()
                    # Verify that save_permanent_config was called
                    self.assertTrue(mock_save.called)

                # Verify that print was called with error message
                mock_print.assert_any_call("两次输入的 QQ 号不一致!")
                # Verify that the function returned the QQ number
                self.assertEqual(result, "123456789")


if __name__ == "__main__":
    unittest.main()
