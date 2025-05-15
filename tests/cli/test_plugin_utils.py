"""Unit tests for plugin utils."""

import unittest
from unittest.mock import MagicMock, mock_open, patch

import requests

from ncatbot.cli.utils.plugin_utils import (
    download_plugin_file,
    gen_plugin_download_url,
    get_plugin_index,
    get_plugin_versions,
)


class TestPluginUtils(unittest.TestCase):
    """Test cases for plugin utils functions."""

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_with_proxy(self, mock_get, mock_get_proxy):
        """Test getting plugin index with proxy."""
        # Setup mocks
        mock_get_proxy.return_value = "https://proxy.example.com/"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plugins": {}}
        mock_get.return_value = mock_response

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertEqual(result, {"plugins": {}})
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_without_proxy(self, mock_get, mock_get_proxy):
        """Test getting plugin index without proxy."""
        # Setup mocks
        mock_get_proxy.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"plugins": {}}
        mock_get.return_value = mock_response

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertEqual(result, {"plugins": {}})
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_error(self, mock_get, mock_get_proxy):
        """Test getting plugin index with error."""
        # Setup mocks
        mock_get_proxy.return_value = None
        mock_get.side_effect = Exception("Connection error")

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_timeout(self, mock_get, mock_get_proxy):
        """Test getting plugin index with timeout."""
        # Setup mocks
        mock_get_proxy.return_value = None
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_invalid_json(self, mock_get, mock_get_proxy):
        """Test getting plugin index with invalid JSON."""
        # Setup mocks
        mock_get_proxy.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    @patch("requests.get")
    def test_get_plugin_index_missing_plugins(self, mock_get, mock_get_proxy):
        """Test getting plugin index without plugins key."""
        # Setup mocks
        mock_get_proxy.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"other_data": "value"}  # No plugins key
        mock_get.return_value = mock_response

        # Call the function
        result = get_plugin_index()

        # Assertions
        self.assertIsNone(result)
        mock_get.assert_called_once()
        mock_get_proxy.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.requests.get")
    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    def test_gen_plugin_download_url_first_url(self, mock_get_proxy, mock_get):
        """Test generating plugin download URL with first URL valid."""
        # Setup mocks
        mock_get_proxy.return_value = "https://proxy.example.com/"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Call the function
        result = gen_plugin_download_url(
            "test_plugin", "1.0.0", "https://github.com/user/repo"
        )

        # Assertions
        expected_url = "https://proxy.example.com/https://github.com/user/repo/raw/refs/heads/v1.0.0/release/test_plugin-1.0.0.zip"
        self.assertEqual(result, expected_url)
        mock_get.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.requests.get")
    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    def test_gen_plugin_download_url_second_url(self, mock_get_proxy, mock_get):
        """Test generating plugin download URL with second URL valid."""
        # Setup mocks
        mock_get_proxy.return_value = None

        # First URL fails, second URL succeeds
        mock_response1 = MagicMock()
        mock_response1.status_code = 404
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_get.side_effect = [mock_response1, mock_response2]

        # Call the function
        result = gen_plugin_download_url(
            "test_plugin", "1.0.0", "https://github.com/user/repo"
        )

        # Assertions
        expected_url = "https://github.com/user/repo/releases/download/v1.0.0/test_plugin-1.0.0.zip"
        self.assertEqual(result, expected_url)
        self.assertEqual(mock_get.call_count, 2)

    @patch("ncatbot.cli.utils.plugin_utils.requests.get")
    @patch("ncatbot.cli.utils.plugin_utils.get_proxy_url")
    def test_gen_plugin_download_url_both_invalid(self, mock_get_proxy, mock_get):
        """Test generating plugin download URL with both URLs invalid."""
        # Setup mocks
        mock_get_proxy.return_value = None

        # Both URLs fail
        mock_response1 = MagicMock()
        mock_response1.status_code = 404
        mock_response2 = MagicMock()
        mock_response2.status_code = 404
        mock_get.side_effect = [mock_response1, mock_response2]

        # Call the function - should raise exception
        with self.assertRaises(Exception):
            gen_plugin_download_url(
                "test_plugin", "1.0.0", "https://github.com/user/repo"
            )

        # Assertions
        self.assertEqual(mock_get.call_count, 2)

    @patch("ncatbot.cli.utils.plugin_utils.gen_plugin_download_url")
    @patch("requests.get")
    def test_download_plugin_file_success(self, mock_get, mock_gen_url):
        """Test downloading plugin file successfully."""
        # Setup mocks
        mock_gen_url.return_value = "https://example.com/plugin.zip"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_get.return_value = mock_response

        # Mock the file open and write operations
        mock_file = mock_open()

        plugin_info = {
            "name": "test_plugin",
            "versions": ["1.0.0"],
            "repository": "https://github.com/user/repo",
        }

        # Call the function with file mock
        with patch("builtins.open", mock_file):
            result = download_plugin_file(plugin_info, "test_plugin.zip")

        # Assertions
        self.assertTrue(result)
        mock_gen_url.assert_called_once_with(
            "test_plugin", "1.0.0", "https://github.com/user/repo"
        )
        mock_get.assert_called_once_with("https://example.com/plugin.zip", timeout=30)
        mock_file.assert_called_once_with("test_plugin.zip", "wb")
        mock_file().write.assert_called_once_with(b"file content")

    @patch("ncatbot.cli.utils.plugin_utils.gen_plugin_download_url")
    @patch("requests.get")
    def test_download_plugin_file_failure(self, mock_get, mock_gen_url):
        """Test downloading plugin file with failure."""
        # Setup mocks
        mock_gen_url.return_value = "https://example.com/plugin.zip"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        plugin_info = {
            "name": "test_plugin",
            "versions": ["1.0.0"],
            "repository": "https://github.com/user/repo",
        }

        # Call the function
        result = download_plugin_file(plugin_info, "test_plugin.zip")

        # Assertions
        self.assertFalse(result)
        mock_gen_url.assert_called_once_with(
            "test_plugin", "1.0.0", "https://github.com/user/repo"
        )
        mock_get.assert_called_once_with("https://example.com/plugin.zip", timeout=30)

    @patch("ncatbot.cli.utils.plugin_utils.get_plugin_index")
    def test_get_plugin_versions_success(self, mock_get_index):
        """Test getting plugin versions successfully."""
        # Setup mocks
        mock_get_index.return_value = {
            "plugins": {
                "test_plugin": {
                    "versions": ["1.0.0", "0.9.0"],
                    "repository": "https://github.com/user/repo",
                    "name": "test_plugin",
                }
            }
        }

        # Call the function
        success, plugin_info = get_plugin_versions("test_plugin")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(
            plugin_info,
            {
                "versions": ["1.0.0", "0.9.0"],
                "repository": "https://github.com/user/repo",
                "name": "test_plugin",
            },
        )
        mock_get_index.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_plugin_index")
    def test_get_plugin_versions_not_found(self, mock_get_index):
        """Test getting plugin versions for nonexistent plugin."""
        # Setup mocks
        mock_get_index.return_value = {"plugins": {}}

        # Call the function
        success, plugin_info = get_plugin_versions("nonexistent_plugin")

        # Assertions
        self.assertFalse(success)
        self.assertEqual(plugin_info, {})
        mock_get_index.assert_called_once()

    @patch("ncatbot.cli.utils.plugin_utils.get_plugin_index")
    def test_get_plugin_versions_no_versions(self, mock_get_index):
        """Test getting plugin versions with no available versions."""
        # Setup mocks
        mock_get_index.return_value = {
            "plugins": {
                "test_plugin": {
                    "versions": [],
                    "repository": "https://github.com/user/repo",
                    "name": "test_plugin",
                }
            }
        }

        # Call the function
        success, plugin_info = get_plugin_versions("test_plugin")

        # Assertions
        self.assertFalse(success)
        self.assertEqual(plugin_info, {})
        mock_get_index.assert_called_once()


if __name__ == "__main__":
    unittest.main()
