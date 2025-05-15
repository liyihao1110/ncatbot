"""Unit tests for the PipTool module."""

import json
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

from ncatbot.cli.utils.pip_tool import PipManagerException, PipTool


class TestPipTool(unittest.TestCase):
    """Test cases for the PipTool class."""

    def setUp(self):
        """Set up test environment."""
        self.pip_tool = PipTool(python_path=sys.executable)

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test the _run_command method for a successful command."""
        mock_process = MagicMock()
        mock_process.stdout = "Success"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = self.pip_tool._run_command(["test_arg"])

        mock_run.assert_called_once()
        self.assertEqual(result.stdout, "Success")

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test the _run_command method for a failing command."""
        error = subprocess.CalledProcessError(1, ["pip", "test_arg"])
        error.stdout = ""
        error.stderr = "Error"
        mock_run.side_effect = error

        with self.assertRaises(PipManagerException):
            self.pip_tool._run_command(["test_arg"])

    @patch.object(PipTool, "_run_command")
    def test_install_success(self, mock_run_command):
        """Test the install method for a successful installation."""
        mock_run_command.return_value = MagicMock()

        result = self.pip_tool.install("test_package", version="1.0.0")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["package"], "test_package==1.0.0")

    @patch.object(PipTool, "_run_command")
    def test_install_failure(self, mock_run_command):
        """Test the install method for a failed installation."""
        mock_run_command.side_effect = PipManagerException("Installation failed")

        result = self.pip_tool.install("test_package")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["package"], "test_package")
        self.assertIn("error", result)

    @patch.object(PipTool, "_run_command")
    def test_uninstall_success(self, mock_run_command):
        """Test the uninstall method for a successful uninstallation."""
        mock_run_command.return_value = MagicMock()

        result = self.pip_tool.uninstall("test_package")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["package"], "test_package")

    @patch.object(PipTool, "_run_command")
    def test_uninstall_failure(self, mock_run_command):
        """Test the uninstall method for a failed uninstallation."""
        mock_run_command.side_effect = PipManagerException("Uninstallation failed")

        result = self.pip_tool.uninstall("test_package")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["package"], "test_package")
        self.assertIn("error", result)

    @patch.object(PipTool, "_run_command")
    def test_list_installed(self, mock_run_command):
        """Test the list_installed method."""
        mock_process = MagicMock()
        mock_process.stdout = """Package    Version  Location
---------  -------  ---------
package1   1.0.0    /path/to/package1
package2   2.0.0    /path/to/package2
"""
        mock_run_command.return_value = mock_process

        result = self.pip_tool.list_installed()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "package1")
        self.assertEqual(result[0]["version"], "1.0.0")
        self.assertEqual(result[1]["name"], "package2")
        self.assertEqual(result[1]["version"], "2.0.0")

    @patch.object(PipTool, "_run_command")
    def test_show_info(self, mock_run_command):
        """Test the show_info method."""
        mock_process = MagicMock()
        mock_process.stdout = """Name: test_package
Version: 1.0.0
Summary: Test package
Home-page: https://example.com
Author: Test Author
License: MIT
"""
        mock_run_command.return_value = mock_process

        result = self.pip_tool.show_info("test_package")

        self.assertEqual(result["name"], "test_package")
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(result["summary"], "Test package")

    def test_format_output_dict(self):
        """Test the _format_output method with dict format."""
        data = {"key": "value"}
        result = self.pip_tool._format_output(data, "dict")
        self.assertEqual(result, data)

    def test_format_output_json(self):
        """Test the _format_output method with JSON format."""
        data = {"key": "value"}
        result = self.pip_tool._format_output(data, "json")
        self.assertEqual(result, json.dumps(data, indent=2, ensure_ascii=False))

    def test_compare_versions(self):
        """Test the compare_versions method."""
        # Test exact version match
        self.assertTrue(self.pip_tool.compare_versions("1.0.0", "1.0.0"))

        # Test version with operators
        self.assertTrue(self.pip_tool.compare_versions("1.0.0", ">=0.9.0"))
        self.assertFalse(self.pip_tool.compare_versions("0.9.0", ">=1.0.0"))


if __name__ == "__main__":
    unittest.main()
