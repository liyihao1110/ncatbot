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

    def assert_print_contains(self, mock_print, text):
        """Assert that mock_print was called with a string containing text."""
        found = False
        for call_args, _ in mock_print.call_args_list:
            if text in call_args[0]:
                found = True
                break

        if not found:
            raise AssertionError(f"No print call contains '{text}'")

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
            # Find a call with Category1
            self.assert_print_contains(mock_print, "Category1")

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_command_help_command(self):
        """Test show_command_help with a command argument."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        with patch("builtins.print") as mock_print:
            # Call with valid command
            info_commands.show_command_help("test1")
            # Verify that print was called with command details
            self.assertTrue(mock_print.called)
            self.assert_print_contains(mock_print, "命令:")
            self.assert_print_contains(mock_print, "分类:")
            self.assert_print_contains(mock_print, "用法:")
            self.assert_print_contains(mock_print, "描述:")

            # Reset mock
            mock_print.reset_mock()

            # Call with invalid command
            info_commands.show_command_help("nonexistent")
            # Verify that print was called with error message
            self.assert_print_contains(mock_print, "不支持的命令: nonexistent")

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
                                self.assertTrue(mock_print.called)
                                # Check that QQ number is printed
                                self.assert_print_contains(mock_print, "QQ 号:")
                                self.assert_print_contains(mock_print, "123456789")

    def test_show_meta_exception(self):
        """Test show_meta command with exception."""
        with patch("builtins.print") as mock_print:
            with patch("pkg_resources.get_distribution", side_effect=ImportError):
                # Call the function
                info_commands.show_meta()
                # Verify that print was called with error message
                self.assert_print_contains(mock_print, "无法获取 NcatBot 版本信息")

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_categories(self):
        """Test show_categories command."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        with patch("builtins.print") as mock_print:
            # Call the function
            info_commands.show_categories()
            # Verify that print was called with categories
            self.assertTrue(mock_print.called)
            self.assert_print_contains(mock_print, "可用的命令分类:")

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
            self.assert_print_contains(mock_print, "没有可用的命令分类")

    @patch("ncatbot.cli.commands.info_commands.registry", None)
    def test_show_categories_with_filter(self):
        """Test show_categories command with category filter."""
        # Replace registry with our test registry
        info_commands.registry = self.test_registry

        # Add a command to 'info' category for testing filter
        @self.test_registry.register(
            "test_info", "Info command", "test_info usage", category="info"
        )
        def test_info_func():
            pass

        with patch("builtins.print") as mock_print:
            # Call the function with a filter
            info_commands.show_categories("info")
            # Verify that print was called with filtered commands
            self.assert_print_contains(mock_print, "分类")
            self.assert_print_contains(mock_print, "info")
            self.assert_print_contains(mock_print, "命令")

    def test_show_help(self):
        """Test show_help function."""
        with patch("builtins.print") as mock_print:
            with patch(
                "ncatbot.cli.commands.info_commands.registry.get_help",
                return_value="Help text",
            ):
                with patch(
                    "ncatbot.cli.commands.info_commands.registry.get_categories",
                    return_value=["Category1", "Category2"],
                ):
                    # Call the function
                    info_commands.show_help("123456789")
                    # Verify that print was called with QQ number
                    self.assert_print_contains(mock_print, "当前 QQ 号为:")
                    self.assert_print_contains(mock_print, "123456789")
                    # Make sure the cat command explanation is included
                    self.assert_print_contains(mock_print, "cat <分类名>")
                    self.assert_print_contains(mock_print, "cat info")


if __name__ == "__main__":
    unittest.main()
