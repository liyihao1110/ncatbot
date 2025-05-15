"""Tests for info commands."""

import unittest
from unittest.mock import patch

from ncatbot.cli.commands import info_commands
from ncatbot.cli.commands.registry import CommandRegistry


class TestInfoCommands(unittest.TestCase):
    """Test info commands."""

    def setUp(self):
        """Set up test environment."""
        # Create a test registry
        self.test_registry = CommandRegistry()

        # Register some test commands
        @self.test_registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.test_registry.register(
            "test2",
            "Test command 2",
            "test2 usage",
            aliases=["t2"],
            category="Category1",
        )
        def test_func2():
            pass

        @self.test_registry.register(
            "test3", "Test command 3", "test3 usage", category="Category2"
        )
        def test_func3():
            pass

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_command_help_no_args(self):
        """Test show_command_help with no arguments."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        # Patch the show_help function
        with patch("ncatbot.cli.commands.info_commands.show_help") as mock_show_help:
            # Call the function
            info_commands.show_command_help()
            # Verify that show_help was called
            mock_show_help.assert_called_once()

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_command_help_category(self):
        """Test show_command_help with a category argument."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        with patch("builtins.print") as mock_print:
            # Call with valid category
            info_commands.show_command_help("Category1")
            # Verify that print was called with help text
            self.assertTrue(mock_print.called)
            help_text = mock_print.call_args[0][0]
            self.assertIn("Category1", help_text)

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_command_help_command(self):
        """Test show_command_help with a command argument."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        with patch("builtins.print") as mock_print:
            # Call with valid command
            info_commands.show_command_help("test1")
            # Verify that print was called with command details
            self.assertEqual(
                mock_print.call_count, 4
            )  # name, category, usage, description

            # Reset mock
            mock_print.reset_mock()

            # Call with invalid command
            info_commands.show_command_help("nonexistent")
            # Verify that print was called with error message
            mock_print.assert_called_once_with("不支持的命令: nonexistent")

    def test_show_meta(self):
        """Test show_meta command."""
        with patch("builtins.print") as mock_print:
            with patch("pkg_resources.get_distribution") as mock_dist:
                mock_dist.return_value.version = "1.0.0"
                with patch("sys.version", "Python 3.8.0"):
                    with patch("sys.platform", "win32"):
                        with patch("os.getcwd", return_value="/test/path"):
                            with patch(
                                "ncatbot.utils.ncatbot_config.bt_uin", "123456789"
                            ):
                                # Call the function
                                info_commands.show_meta()
                                # Verify that print was called with version info
                                self.assertEqual(mock_print.call_count, 5)
                                # Check that QQ number is printed
                                mock_print.assert_any_call("QQ 号: 123456789")

    def test_show_meta_exception(self):
        """Test show_meta command with exception."""
        with patch("builtins.print") as mock_print:
            with patch("pkg_resources.get_distribution", side_effect=ImportError):
                # Call the function
                info_commands.show_meta()
                # Verify that print was called with error message
                mock_print.assert_called_once_with("无法获取 NcatBot 版本信息")

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_categories(self):
        """Test show_categories command."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        with patch("builtins.print") as mock_print:
            # Call the function
            info_commands.show_categories()
            # Verify that print was called with categories
            self.assertEqual(mock_print.call_count, 3)  # header + 2 categories
            mock_print.assert_any_call("可用的命令分类:")

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_categories_empty(self):
        """Test show_categories command with no categories."""
        # Create empty registry
        empty_registry = CommandRegistry()
        info_commands.registry = empty_registry

        with patch("builtins.print") as mock_print:
            # Call the function
            info_commands.show_categories()
            # Verify that print was called with message
            mock_print.assert_called_once_with("没有可用的命令分类")

    def test_show_help(self):
        """Test show_help function."""
        with patch("builtins.print") as mock_print:
            with patch(
                "ncatbot.cli.commands.info_commands.registry.get_help",
                return_value="Help text",
            ) as mock_get_help:
                # Call the function
                info_commands.show_help("123456789")
                # Verify that print was called with QQ number and help text
                self.assertEqual(mock_print.call_count, 5)
                mock_print.assert_any_call("当前 QQ 号为: 123456789")
                mock_get_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
