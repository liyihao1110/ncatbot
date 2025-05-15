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
        self.assertEqual(cmd.show_in_help, True)  # Default should be True

    def test_init_defaults(self):
        """Test initialization with default values."""

        def test_func():
            return None

        cmd = Command("test", test_func, "Test command", "test usage")

        self.assertEqual(cmd.help_text, "Test command")
        self.assertEqual(cmd.aliases, [])
        self.assertEqual(cmd.category, "General")
        self.assertEqual(cmd.show_in_help, True)

    def test_init_show_in_help_false(self):
        """Test initialization with show_in_help=False."""

        def test_func():
            return None

        cmd = Command(
            "test", test_func, "Test command", "test usage", show_in_help=False
        )

        self.assertEqual(cmd.show_in_help, False)


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

    def test_register_with_show_in_help(self):
        """Test command registration with show_in_help parameter."""

        @self.registry.register(
            "test",
            "Test command",
            "test usage",
            show_in_help=False,
        )
        def test_func():
            return "test"

        cmd = self.registry.commands["test"]
        self.assertEqual(cmd.show_in_help, False)

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
            # The actual implementation adds color formatting to the command name
            # but the text itself should be "不支持的命令: nonexistent" or similar
            if mock_print.call_args:
                printed_msg = mock_print.call_args[0][0]
                self.assertTrue(
                    "不支持的命令" in printed_msg and "nonexistent" in printed_msg,
                    f"Expected error message not found in: {printed_msg}",
                )
            else:
                self.fail("No error message was printed")
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
        # Check for specific text fragments, ignoring color codes
        self.assertTrue("Category1" in help_text, "Category1 not found in help text")
        self.assertTrue(
            "test1 usage" in help_text, "test1 usage not found in help text"
        )
        self.assertTrue(
            "test2 usage" in help_text, "test2 usage not found in help text"
        )
        self.assertTrue("t2" in help_text, "Alias t2 not found in help text")
        self.assertTrue(
            "Test command 1" in help_text, "Test command 1 not found in help text"
        )
        self.assertTrue(
            "Test command 2" in help_text, "Test command 2 not found in help text"
        )
        # test3 should not be in Category1 help
        self.assertTrue(
            "test3" not in help_text or "Test command 3" not in help_text,
            "Test command 3 incorrectly found in Category1 help text",
        )

        # Test general help
        help_text = self.registry.get_help()
        self.assertTrue(
            "test1 usage" in help_text, "test1 usage not found in general help text"
        )
        self.assertTrue(
            "test2 usage" in help_text, "test2 usage not found in general help text"
        )
        self.assertTrue(
            "test3 usage" in help_text, "test3 usage not found in general help text"
        )

        # Test invalid category
        help_text = self.registry.get_help("InvalidCategory")
        # The message format includes color codes, so just check for basic text
        self.assertTrue(
            "未知的分类" in help_text and "InvalidCategory" in help_text,
            "Invalid category error not found",
        )

    def test_get_help_only_important(self):
        """Test help text generation with only_important=True."""

        @self.registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.registry.register(
            "test2",
            "Test command 2",
            "test2 usage",
            category="Category1",
            show_in_help=False,
        )
        def test_func2():
            pass

        # Test general help with only_important=True
        help_text = self.registry.get_help(only_important=True)
        self.assertIn("test1 usage", help_text)
        self.assertNotIn("test2 usage", help_text)

        # Test category help with only_important=True
        help_text = self.registry.get_help("Category1", only_important=True)
        self.assertIn("test1 usage", help_text)
        self.assertNotIn("test2 usage", help_text)

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

    def test_get_commands_by_category_only_important(self):
        """Test getting commands by category with only_important=True."""

        @self.registry.register(
            "test1", "Test command 1", "test1 usage", category="Category1"
        )
        def test_func1():
            pass

        @self.registry.register(
            "test2",
            "Test command 2",
            "test2 usage",
            category="Category1",
            show_in_help=False,
        )
        def test_func2():
            pass

        # Get all commands
        commands = self.registry.get_commands_by_category("Category1")
        self.assertEqual(len(commands), 2)

        # Get only important commands
        commands = self.registry.get_commands_by_category(
            "Category1", only_important=True
        )
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][0], "test1")


if __name__ == "__main__":
    unittest.main()
