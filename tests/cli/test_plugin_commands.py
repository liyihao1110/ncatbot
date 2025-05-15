"""Unit tests for plugin commands."""

import unittest
from unittest.mock import mock_open, patch

# Mock the get_plugin_info_by_name function before importing
with patch("ncatbot.plugin.get_plugin_info_by_name") as mock_get_plugin_info:
    # Set up the mock to return a valid tuple
    mock_get_plugin_info.return_value = (False, None)

    # Patch the registry before importing the module with plugin commands
    with patch("ncatbot.cli.commands.registry.Command") as MockCommand:
        from ncatbot.cli.commands.plugin_commands import (
            create_plugin_template,
            install,
            list_plugins,
            list_remote_plugins,
            remove_plugin,
        )


class TestPluginCommands(unittest.TestCase):
    """Test cases for plugin commands."""

    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_versions")
    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_info_by_name")
    @patch("ncatbot.cli.commands.plugin_commands.download_plugin_file")
    @patch("ncatbot.cli.commands.plugin_commands.os.makedirs")
    @patch("ncatbot.cli.commands.plugin_commands.shutil.unpack_archive")
    @patch("ncatbot.cli.commands.plugin_commands.os.remove")
    @patch("ncatbot.cli.commands.plugin_commands.install_pip_dependencies")
    @patch("ncatbot.cli.commands.plugin_commands.config")
    def test_install_new_plugin(
        self,
        mock_config,
        mock_install_deps,
        mock_remove,
        mock_unpack,
        mock_makedirs,
        mock_download,
        mock_get_info,
        mock_get_versions,
    ):
        """Test installing a new plugin."""
        # Setup mocks
        mock_config.plugin.plugins_dir = "/path/to/plugins"
        mock_get_versions.return_value = (
            True,
            {
                "name": "test_plugin",
                "versions": ["1.0.0"],
                "repository": "https://github.com/test/test_plugin",
            },
        )
        mock_get_info.return_value = (False, None)  # Plugin doesn't exist yet
        mock_download.return_value = True

        # Call the function
        result = install("test_plugin")

        # Assertions
        mock_get_versions.assert_called_once_with("test_plugin")
        mock_download.assert_called_once()
        mock_makedirs.assert_called()
        mock_unpack.assert_called_once()
        mock_remove.assert_called_once()
        mock_install_deps.assert_called_once()

    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_versions")
    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_info_by_name")
    @patch("ncatbot.cli.commands.plugin_commands.shutil.rmtree")
    @patch("ncatbot.cli.commands.plugin_commands.os.path.exists")
    @patch("ncatbot.cli.commands.plugin_commands.config")
    def test_install_force(
        self, mock_config, mock_exists, mock_rmtree, mock_get_info, mock_get_versions
    ):
        """Test force installing a plugin."""
        # Setup mocks
        mock_config.plugin.plugins_dir = "/path/to/plugins"
        mock_exists.return_value = True
        mock_get_versions.return_value = (
            True,
            {
                "name": "test_plugin",
                "versions": ["1.0.0"],
                "repository": "https://github.com/test/test_plugin",
            },
        )
        mock_get_info.return_value = (False, None)  # Return a valid tuple

        # Call the function with force flag
        install("test_plugin", "-f")

        # Assertions
        mock_rmtree.assert_called_once_with("/path/to/plugins/test_plugin")

    @patch("ncatbot.cli.commands.plugin_commands.re.match")
    @patch("ncatbot.cli.commands.plugin_commands.os.path.exists")
    @patch("ncatbot.cli.commands.plugin_commands.os.makedirs")
    @patch("ncatbot.cli.commands.plugin_commands.shutil.copy2")
    @patch("builtins.open", new_callable=mock_open, read_data="Plugin Name\nYour Name")
    @patch("ncatbot.cli.commands.plugin_commands.input")
    @patch("ncatbot.cli.commands.plugin_commands.config")
    @patch("ncatbot.cli.commands.plugin_commands.os.path.join")
    def test_create_plugin_template(
        self,
        mock_join,
        mock_config,
        mock_input,
        mock_file,
        mock_copy,
        mock_makedirs,
        mock_exists,
        mock_match,
    ):
        """Test creating a plugin template."""
        # Setup mocks
        mock_config.plugin.plugins_dir = "/path/to/plugins"
        mock_match.return_value = True  # Valid plugin name
        mock_exists.return_value = False  # Directory doesn't exist
        mock_input.return_value = "Test Author"

        # Mock os.path.join to return expected values
        mock_join.side_effect = lambda *args: "/".join(args)

        # Call the function
        create_plugin_template("test_plugin")

        # Assertions
        mock_match.assert_called_once()
        mock_exists.assert_called_once()
        mock_makedirs.assert_called_once_with(
            "/path/to/plugins/test_plugin", exist_ok=True
        )
        self.assertEqual(mock_copy.call_count, 5)  # 5 template files

    @patch("ncatbot.cli.commands.plugin_commands.list_plugins")
    @patch("ncatbot.cli.commands.plugin_commands.shutil.rmtree")
    @patch("ncatbot.cli.commands.plugin_commands.config")
    def test_remove_plugin(self, mock_config, mock_rmtree, mock_list_plugins):
        """Test removing a plugin."""
        # Setup mocks
        mock_config.plugin.plugins_dir = "/path/to/plugins"
        mock_list_plugins.return_value = {"test_plugin": "1.0.0"}

        # Call the function
        remove_plugin("test_plugin")

        # Assertions
        mock_rmtree.assert_called_once_with("/path/to/plugins/test_plugin")

    @patch("ncatbot.cli.commands.plugin_commands.os.listdir")
    @patch("ncatbot.cli.commands.plugin_commands.get_plugin_info_by_name")
    @patch("ncatbot.cli.commands.plugin_commands.config")
    def test_list_plugins(self, mock_config, mock_get_info, mock_listdir):
        """Test listing installed plugins."""
        # Setup mocks
        mock_config.plugin.plugins_dir = "/path/to/plugins"
        mock_listdir.return_value = ["plugin1", "plugin2"]
        mock_get_info.side_effect = [
            (True, {"version": "1.0.0"}),
            (True, {"version": "2.0.0"}),
        ]

        # Call the function
        result = list_plugins(enable_print=False)

        # Assertions
        self.assertEqual(
            result, {"plugin1": {"version": "1.0.0"}, "plugin2": {"version": "2.0.0"}}
        )
        mock_listdir.assert_called_once()
        self.assertEqual(mock_get_info.call_count, 2)

    @patch("ncatbot.cli.utils.get_plugin_index")
    def test_list_remote_plugins(self, mock_get_index):
        """Test listing remote plugins."""
        # Setup mocks
        mock_get_index.return_value = {
            "plugins": {
                "plugin1": {"author": "Author1", "description": "Description1"},
                "plugin2": {"author": "Author2", "description": "Description2"},
            }
        }

        # Call the function - should just print plugin info, no return value
        list_remote_plugins()

        # Assertions
        mock_get_index.assert_called_once()


if __name__ == "__main__":
    unittest.main()
