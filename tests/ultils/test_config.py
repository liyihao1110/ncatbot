import os
import tempfile
import unittest
from dataclasses import KW_ONLY, dataclass
from unittest.mock import patch

import yaml

from ncatbot.utils.config import BaseConfig, Config, NapCatConfig, PluginConfig


class TestBaseConfig(unittest.TestCase):
    """Test the BaseConfig class functionality."""

    def test_from_dict(self):
        """Test creating BaseConfig from dictionary."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str
            value: int
            _: KW_ONLY = None

        # Test basic dict conversion
        data = {"name": "test", "value": 42}
        config = TestConfig.from_dict(data)
        self.assertEqual(config.name, "test")
        self.assertEqual(config.value, 42)

        # Test asdict conversion
        result_dict = config.asdict()
        self.assertEqual(result_dict["name"], "test")
        self.assertEqual(result_dict["value"], 42)

    def test_replace(self):
        """Test the __replace__ method."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str
            value: int
            _: KW_ONLY = None

        config = TestConfig.from_dict({"name": "test", "value": 42})
        new_config = config.__replace__(name="new_name")
        self.assertEqual(new_config.name, "new_name")
        self.assertEqual(new_config.value, 42)
        # Original should be unchanged
        self.assertEqual(config.name, "test")


class TestNapCatConfig(unittest.TestCase):
    """Test the NapCatConfig class functionality."""

    def test_default_values(self):
        """Test default configuration values."""
        config = NapCatConfig()
        self.assertEqual(config.ws_uri, "ws://localhost:3001")
        self.assertEqual(config.ws_token, "")
        self.assertEqual(config.ws_listen_ip, "localhost")

    def test_uri_standardization(self):
        """Test URI standardization methods."""
        # Test WebSocket URI standardization
        config = NapCatConfig(ws_uri="localhost:3001")
        config._standardize_ws_uri()
        self.assertEqual(config.ws_uri, "ws://localhost:3001")
        self.assertEqual(config.ws_host, "localhost")
        self.assertEqual(config.ws_port, 3001)

        # Test WebUI URI standardization
        config = NapCatConfig(webui_uri="localhost:6099")
        config._standardize_webui_uri()
        self.assertEqual(config.webui_uri, "http://localhost:6099")
        self.assertEqual(config.webui_host, "localhost")
        self.assertEqual(config.webui_port, 6099)

    def test_validation(self):
        """Test the validate method."""
        config = NapCatConfig(ws_uri="ws://example.com:3001", ws_listen_ip="0.0.0.0")
        with patch("ncatbot.utils.config.logger") as mock_logger:
            config.validate()
            # Should log a warning about remote service
            mock_logger.info.assert_called_with(
                "NapCat 服务不是本地的，请确保远程服务配置正确"
            )


class TestPluginConfig(unittest.TestCase):
    """Test the PluginConfig class functionality."""

    def test_is_plugin_enabled(self):
        """Test plugin enablement logic."""
        # No restrictions
        config = PluginConfig()
        self.assertTrue(config.is_plugin_enabled("test_plugin"))

        # Whitelist only
        config = PluginConfig(plugin_whitelist=["test_plugin", "another_plugin"])
        self.assertTrue(config.is_plugin_enabled("test_plugin"))
        self.assertFalse(config.is_plugin_enabled("unknown_plugin"))

        # Blacklist only
        config = PluginConfig(plugin_blacklist=["bad_plugin"])
        self.assertTrue(config.is_plugin_enabled("test_plugin"))
        self.assertFalse(config.is_plugin_enabled("bad_plugin"))

    def test_validation(self):
        """Test plugin config validation."""
        # Valid config
        config = PluginConfig(plugin_whitelist=["test_plugin"])
        config.validate()  # Should not raise any exceptions

        # Invalid config (both whitelist and blacklist)
        config = PluginConfig(
            plugin_whitelist=["good_plugin"], plugin_blacklist=["bad_plugin"]
        )
        with self.assertRaises(ValueError):
            config.validate()


class TestConfig(unittest.TestCase):
    """Test the main Config class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file path for tests
        self.test_config_path = os.path.join(tempfile.gettempdir(), "test_config.yaml")
        self.config_path_patcher = patch(
            "ncatbot.utils.config.CONFIG_PATH", self.test_config_path
        )
        self.config_path_patcher.start()

        # Mock logger to avoid console output during tests
        self.logger_patcher = patch("ncatbot.utils.config.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        # Stop patchers
        self.config_path_patcher.stop()
        self.logger_patcher.stop()

        # Remove test config file if it exists
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_defaults(self):
        """Test default configuration values."""
        config = Config()
        self.assertEqual(config.bt_uin, "123456")
        self.assertEqual(config.root, "123456")
        self.assertTrue(isinstance(config.napcat, NapCatConfig))
        self.assertTrue(isinstance(config.plugin, PluginConfig))

    def test_load_from_file(self):
        """Test loading configuration from file."""
        # Create test config file
        config_data = {
            "napcat": {"ws_uri": "ws://example.com:3001", "ws_token": "test_token"},
            "plugin": {
                "plugins_dir": "custom_plugins",
                "plugin_whitelist": ["plugin1", "plugin2"],
            },
            "bt_uin": "987654321",
            "root": "123456789",
        }
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Load the config
        config = Config.load_from_file(self.test_config_path)

        # Check main config values
        self.assertEqual(config.bt_uin, "987654321")
        self.assertEqual(config.root, "123456789")

        # Check napcat config values
        self.assertEqual(config.napcat.ws_uri, "ws://example.com:3001")
        self.assertEqual(config.napcat.ws_token, "test_token")

        # Check plugin config values
        self.assertEqual(config.plugin.plugins_dir, "custom_plugins")
        self.assertEqual(config.plugin.plugin_whitelist, ["plugin1", "plugin2"])

    def test_load_file_not_found(self):
        """Test error handling when file is not found."""
        # Ensure the file doesn't exist
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

        with self.assertRaises(ValueError) as context:
            Config.load_from_file(self.test_config_path)
        self.assertIn("配置文件不存在", str(context.exception))

    def test_load_invalid_yaml(self):
        """Test error handling with invalid YAML."""
        # Create invalid YAML file
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: :")

        with patch("yaml.safe_load", side_effect=yaml.YAMLError):
            with self.assertRaises(ValueError) as context:
                Config.load_from_file(self.test_config_path)
            self.assertIn("配置文件格式无效", str(context.exception))

    def test_validate_config(self):
        """Test config validation."""
        # Test with custom values
        config = Config(bt_uin="123123123", root="987987987")
        config.validate_config()
        # Should not prompt for input
        self.assertEqual(config.bt_uin, "123123123")

    @patch("builtins.input", return_value="555555555")
    def test_validate_default_bt_uin(self, mock_input):
        """Test validation with default bt_uin (should prompt)."""
        config = Config()  # Uses default bt_uin
        config.validate_config()
        # Should have prompted and updated the value
        self.assertEqual(config.bt_uin, "555555555")

    @patch("ncatbot.utils.config.Config.load_from_file")
    def test_load(self, mock_load):
        """Test the static load method."""
        mock_load.return_value = Config(bt_uin="test123")
        config = Config.load()
        self.assertEqual(config.bt_uin, "test123")
        mock_load.assert_called_once()

    def test_str_representation(self):
        """Test the string representation of Config."""
        config = Config(
            bt_uin="123456789",
            root="987654321",
            napcat=NapCatConfig(
                ws_uri="ws://test:1234",
                ws_token="testtoken",
                webui_uri="http://webui:5678",
            ),
        )
        str_rep = str(config)
        self.assertIn("123456789", str_rep)  # bt_uin
        self.assertIn("987654321", str_rep)  # root
        self.assertIn("ws://test:1234", str_rep)  # ws_uri
        self.assertIn("testtoken", str_rep)  # ws_token
        self.assertIn("http://webui:5678", str_rep)  # webui_uri

    def test_save_permanent_config_top_level(self):
        """Test saving a top-level config value."""
        # Create an initial config file
        config_data = {"bt_uin": "987654321", "root": "123456789"}
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Create config and save a value
        config = Config.load_from_file(self.test_config_path)
        config.save_permanent_config("bt_uin", "111222333")

        # Read back the file and verify
        with open(self.test_config_path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        # Check if the value was updated
        self.assertEqual(saved_config["bt_uin"], "111222333")
        self.assertEqual(saved_config["root"], "123456789")

        # Check if the value was updated in the object
        self.assertEqual(config.bt_uin, "111222333")

    def test_save_permanent_config_nested(self):
        """Test saving a nested config value."""
        # Create an initial config file
        config_data = {
            "napcat": {"ws_uri": "ws://localhost:3001", "ws_token": "old_token"}
        }
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Create config and save a nested value
        config = Config.load_from_file(self.test_config_path)
        config.save_permanent_config("napcat.ws_token", "new_token")

        # Read back the file and verify
        with open(self.test_config_path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        # Check if the value was updated
        self.assertEqual(saved_config["napcat"]["ws_token"], "new_token")
        self.assertEqual(saved_config["napcat"]["ws_uri"], "ws://localhost:3001")

        # Check if the value was updated in the object
        self.assertEqual(config.napcat.ws_token, "new_token")

    def test_save_permanent_config_new_section(self):
        """Test saving a value in a new section."""
        # Create an initial config file
        config_data = {"bt_uin": "987654321"}
        with open(self.test_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Create config and save a value in a new section
        config = Config.load_from_file(self.test_config_path)
        config.save_permanent_config("plugin.plugins_dir", "new_plugins")

        # Read back the file and verify
        with open(self.test_config_path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        # Check if the values were updated
        self.assertEqual(saved_config["bt_uin"], "987654321")
        self.assertEqual(saved_config["plugin"]["plugins_dir"], "new_plugins")

    def test_save_permanent_config_new_file(self):
        """Test saving a config value when the file doesn't exist."""
        # Ensure the file doesn't exist
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

        # Create config and save a value
        config = Config()
        config.save_permanent_config("bt_uin", "111222333")

        # Read back the file and verify
        with open(self.test_config_path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        # Check if the value was saved
        self.assertEqual(saved_config["bt_uin"], "111222333")

        # Check if the value was updated in the object
        self.assertEqual(config.bt_uin, "111222333")


if __name__ == "__main__":
    unittest.main()
