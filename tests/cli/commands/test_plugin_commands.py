"""Tests for plugin commands."""

import os
import shutil
import unittest
from unittest.mock import patch

from ncatbot.cli.commands import plugin_commands


class TestPluginCommands(unittest.TestCase):
    """Test plugin commands."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary plugins directory for testing
        self.test_plugin_dir = "test_plugins_dir"
        os.makedirs(self.test_plugin_dir, exist_ok=True)

        # Path for plugin templates
        self.orig_template_dir = plugin_commands.TEMPLATE_DIR
        plugin_commands.TEMPLATE_DIR = os.path.join(
            os.path.dirname(__file__), "templates"
        )
        os.makedirs(plugin_commands.TEMPLATE_DIR, exist_ok=True)

        # Create mock template files
        # TEMPLATE_FILES doesn't exist in the source code, use a fixed list instead
        template_files = ["__init__.py", "main.py", "README.md", "requirements.txt"]
        for filename in template_files:
            template_path = os.path.join(plugin_commands.TEMPLATE_DIR, filename)
            with open(template_path, "w") as f:
                if filename in ["__init__.py", "main.py", "README.md"]:
                    f.write("Plugin Name\nYour Name\nPlugin description")
                else:
                    f.write("# Mock template file")

    def tearDown(self):
        """Clean up after tests."""
        # Remove test directories
        if os.path.exists(self.test_plugin_dir):
            shutil.rmtree(self.test_plugin_dir)

        # Restore template directory
        plugin_commands.TEMPLATE_DIR = self.orig_template_dir
        if os.path.exists(os.path.join(os.path.dirname(__file__), "templates")):
            shutil.rmtree(os.path.join(os.path.dirname(__file__), "templates"))

    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_versions")
    def test_install_plugin_not_exists(self, mock_get_versions):
        """Test installing a non-existent plugin."""
        # Setup mock to return that plugin doesn't exist
        mock_get_versions.return_value = (False, {})

        with patch("builtins.print") as mock_print:
            # Call function
            result = plugin_commands.install("nonexistent_plugin")

            # Verify function returns False
            self.assertFalse(result)

            # More flexible approach to find the error message
            call_found = False
            for call in mock_print.call_args_list:
                if (
                    call[0]
                    and "nonexistent_plugin" in str(call[0])
                    and "不存在" in str(call[0])
                ):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "Plugin not found message not found in print calls"
            )

    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_versions")
    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_info_by_name")
    def test_install_plugin_already_latest(self, mock_get_info, mock_get_versions):
        """Test installing a plugin that's already at the latest version."""
        # Setup mocks
        mock_get_versions.return_value = (True, {"versions": ["1.0.0"]})
        mock_get_info.return_value = (True, {"version": "1.0.0"})

        with patch("builtins.print") as mock_print:
            # Call function
            result = plugin_commands.install("existing_plugin")

            # More flexible approach to find the success message
            call_found = False
            for call in mock_print.call_args_list:
                if (
                    call[0]
                    and "existing_plugin" in str(call[0])
                    and "最新版本" in str(call[0])
                ):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "Already latest version message not found in print calls"
            )

    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_versions")
    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_info_by_name")
    @patch("builtins.input")
    def test_install_plugin_update_no(
        self, mock_input, mock_get_info, mock_get_versions
    ):
        """Test declining to update an existing plugin."""
        # Setup mocks
        mock_get_versions.return_value = (True, {"versions": ["1.1.0"]})
        mock_get_info.return_value = (True, {"version": "1.0.0"})
        mock_input.return_value = "n"

        with patch("builtins.print") as mock_print:
            # Call function
            result = plugin_commands.install("existing_plugin")

            # Verify input was called asking for confirmation
            mock_input.assert_called_once()
            self.assertIn("是否更新插件", mock_input.call_args[0][0])

    @patch(
        "ncatbot.cli.commands.plugin_commands.config.plugin.plugins_dir",
        "test_plugins_dir",
    )
    @patch("ncatbot.cli.commands.plugin_commands.re.match")
    def test_create_plugin_invalid_name(self, mock_match):
        """Test creating a plugin with an invalid name."""
        # Setup mock to indicate invalid name
        mock_match.return_value = None

        with patch("builtins.print") as mock_print:
            # Call function
            plugin_commands.create_plugin_template("invalid-name")

            # More flexible approach to find the error message
            call_found = False
            for call in mock_print.call_args_list:
                if (
                    call[0]
                    and "invalid-name" in str(call[0])
                    and "不合法" in str(call[0])
                ):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "Invalid plugin name message not found in print calls"
            )

    @patch(
        "ncatbot.cli.commands.plugin_commands.config.plugin.plugins_dir",
        "test_plugins_dir",
    )
    @patch("ncatbot.cli.commands.plugin_commands.re.match")
    @patch("builtins.input")
    def test_create_plugin_overwrite_no(self, mock_input, mock_match):
        """Test declining to overwrite an existing plugin."""
        # Setup mocks
        mock_match.return_value = True
        mock_input.return_value = "n"

        # Create a directory to simulate existing plugin
        os.makedirs(os.path.join(self.test_plugin_dir, "test_plugin"), exist_ok=True)

        with patch("builtins.print") as mock_print:
            # Call function
            plugin_commands.create_plugin_template("test_plugin")

            # Verify input was called asking for confirmation
            mock_input.assert_called_once()
            self.assertIn("是否覆盖?", mock_input.call_args[0][0])

    @patch(
        "ncatbot.cli.commands.plugin_commands.config.plugin.plugins_dir",
        "test_plugins_dir",
    )
    def test_list_plugins_empty(self):
        """Test listing plugins when none are installed."""
        with patch("builtins.print") as mock_print:
            # Call function
            result = plugin_commands.list_plugins()

            # Verify result is empty dict
            self.assertEqual(result, {})

            # More flexible approach to find the message
            call_found = False
            for call in mock_print.call_args_list:
                if call[0] and "没有安装任何插件" in str(call[0]):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "No installed plugins message not found in print calls"
            )

    @patch("ncatbot.cli.utils.get_plugin_index")
    def test_list_remote_plugins_error(self, mock_get_index):
        """Test listing remote plugins with an error."""
        # Setup mock to raise exception
        mock_get_index.side_effect = Exception("Test error")

        with patch("builtins.print") as mock_print:
            # Call function
            plugin_commands.list_remote_plugins()

            # More flexible approach to find the error message
            call_found = False
            for call in mock_print.call_args_list:
                if call[0] and "获取插件列表时出错" in str(call[0]):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "Plugin list error message not found in print calls"
            )

    @patch("ncatbot.cli.utils.get_plugin_index")
    def test_list_remote_plugins_empty(self, mock_get_index):
        """Test listing remote plugins when none are available."""
        # Setup mock to return empty list
        mock_get_index.return_value = {"plugins": {}}

        with patch("builtins.print") as mock_print:
            # Call function
            plugin_commands.list_remote_plugins()

            # More flexible approach to find the message
            call_found = False
            for call in mock_print.call_args_list:
                if call[0] and "没有找到可用的插件" in str(call[0]):
                    call_found = True
                    break
            self.assertTrue(
                call_found, "No available plugins message not found in print calls"
            )


if __name__ == "__main__":
    unittest.main()
