"""Tests for command registry."""

import unittest
from unittest.mock import MagicMock, patch

from ncatbot.cli.commands.registry import Command, CommandRegistry


class TestCommand(unittest.TestCase):
    """Test Command class."""

    def test_init(self):
        """Test initialization of Command."""

        def test_func():
            return None

        cmd = Command(
            "test", test_func, "Test command", "test usage", "help text", ["t"], "Test"
        )

        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.func, test_func)
        self.assertEqual(cmd.description, "Test command")
        self.assertEqual(cmd.usage, "test usage")
        self.assertEqual(cmd.help_text, "help text")
        self.assertEqual(cmd.aliases, ["t"])
        self.assertEqual(cmd.category, "Test")

    def test_init_defaults(self):
        """Test initialization with default values."""

        def test_func():
            return None

        cmd = Command("test", test_func, "Test command", "test usage")

        self.assertEqual(cmd.help_text, "Test command")
        self.assertEqual(cmd.aliases, [])
        self.assertEqual(cmd.category, "General")


class TestCommandRegistry(unittest.TestCase):
    """Test CommandRegistry class."""

    def setUp(self):
        """Set up test environment."""
        self.registry = CommandRegistry()

    def test_register(self):
        """Test command registration."""

        @self.registry.register(
            "test",
            "Test command",
            "test usage",
            help_text="help text",
            aliases=["t"],
            category="Test",
        )
        def test_func():
            return "test"

        # Verify command registration
        self.assertIn("test", self.registry.commands)
        cmd = self.registry.commands["test"]
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.description, "Test command")

        # Verify alias registration
        self.assertIn("t", self.registry.aliases)
        self.assertEqual(self.registry.aliases["t"], "test")

        # Verify category registration
        self.assertIn("Test", self.registry.categories)
        self.assertIn("test", self.registry.categories["Test"])

    def test_execute(self):
        """Test command execution."""
        test_func = MagicMock(return_value="test result")

        @self.registry.register("test", "Test command", "test usage")
        def registered_func(*args, **kwargs):
            return test_func(*args, **kwargs)

        # Execute with direct command name
        result = self.registry.execute("test", "arg1", kwarg1="value")
        test_func.assert_called_once_with("arg1", kwarg1="value")
        self.assertEqual(result, "test result")

        # Reset mock
        test_func.reset_mock()

        # Add alias and test execution via alias
        self.registry.aliases["t"] = "test"
        result = self.registry.execute("t", "arg2", kwarg2="value2")
        test_func.assert_called_once_with("arg2", kwarg2="value2")
        self.assertEqual(result, "test result")

    def test_execute_not_found(self):
        """Test execution of non-existent command."""
        with patch("builtins.print") as mock_print:
            result = self.registry.execute("nonexistent")
            mock_print.assert_called_once_with("不支持的命令: nonexistent")
            self.assertIsNone(result)

    def test_get_help(self):
        """Test help text generation."""

        @self.registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.registry.register(
            "test2",
            "Test command 2",
            "test2 usage",
            aliases=["t2"],
            category="Category1",
        )
        def test_func2():
            pass

        @self.registry.register(
            "test3", "Test command 3", "test3 usage", category="Category2"
        )
        def test_func3():
            pass

        # Test category help
        help_text = self.registry.get_help("Category1")
        self.assertIn("Category1 分类的命令:", help_text)
        self.assertIn("test1 usage", help_text)
        self.assertIn("test2 usage", help_text)
        self.assertIn("别名: t2", help_text)
        self.assertNotIn("test3", help_text)

        # Test general help
        help_text = self.registry.get_help()
        self.assertIn("支持的命令:", help_text)
        self.assertIn("test1 usage", help_text)
        self.assertIn("test2 usage", help_text)
        self.assertIn("test3 usage", help_text)

        # Test invalid category
        help_text = self.registry.get_help("InvalidCategory")
        self.assertEqual(help_text, "未知的分类: InvalidCategory")

    def test_get_categories(self):
        """Test getting command categories."""

        @self.registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.registry.register(
            "test2", "Test command 2", "test2 usage", category="Category2"
        )
        def test_func2():
            pass

        categories = self.registry.get_categories()
        self.assertEqual(categories, ["Category1", "Category2"])

    def test_get_commands_by_category(self):
        """Test getting commands by category."""

        @self.registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.registry.register(
            "test2", "Test command 2", "test2 usage", category="Category1"
        )
        def test_func2():
            pass

        commands = self.registry.get_commands_by_category("Category1")
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0][0], "test1")
        self.assertEqual(commands[1][0], "test2")

        # Test invalid category
        commands = self.registry.get_commands_by_category("InvalidCategory")
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
