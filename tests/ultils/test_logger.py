import io
import logging
import sys
import unittest
from unittest.mock import MagicMock, patch

from ncatbot.utils.logger import LoggerOriginFilter, get_log, setup_logging, tqdm
from ncatbot.utils.status import status


class TestLogger(unittest.TestCase):
    """Test the logger utility."""

    def setUp(self):
        """Set up test environment."""
        # Save the original stderr/stdout for restoration later
        self.original_stderr = sys.stderr
        self.original_stdout = sys.stdout
        # Create string IO objects to capture output
        self.stderr_capturer = io.StringIO()
        self.stdout_capturer = io.StringIO()
        # Redirect stderr and stdout
        sys.stderr = self.stderr_capturer
        sys.stdout = self.stdout_capturer

        # Clear registered loggers before each test
        status._registered_loggers.clear()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original stderr/stdout
        sys.stderr = self.original_stderr
        sys.stdout = self.original_stdout

    def test_get_log(self):
        """Test that get_log returns a logger instance and registers it."""
        logger = get_log("test_logger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")

        # Verify the logger was registered in status
        self.assertTrue(status.is_registered_logger("test_logger"))
        self.assertIn("test_logger", status.get_registered_loggers())

    def test_log_levels(self):
        """Test that log messages appear at different levels."""
        # Use a StringIO to capture log output directly
        log_output = io.StringIO()

        # Create a handler that writes to our StringIO
        test_handler = logging.StreamHandler(log_output)
        test_handler.setLevel(logging.DEBUG)  # Capture all levels

        # Create a simple formatter without colors for easier testing
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        test_handler.setFormatter(formatter)

        # Get a logger and add our test handler
        logger = get_log("test_log_levels")
        logger.addHandler(test_handler)

        # Ensure the logger level is low enough
        logger.setLevel(logging.DEBUG)

        # Log messages at different levels
        test_message = "This is a test message"

        # Test debug message
        logger.debug(f"DEBUG: {test_message}")

        # Test info message
        logger.info(f"INFO: {test_message}")

        # Test warning message
        logger.warning(f"WARNING: {test_message}")

        # Test error message
        logger.error(f"ERROR: {test_message}")

        # Get the captured output
        captured_logs = log_output.getvalue()

        # Different log levels should be present
        self.assertIn("INFO: INFO: This is a test message", captured_logs)
        self.assertIn("WARNING: WARNING: This is a test message", captured_logs)
        self.assertIn("ERROR: ERROR: This is a test message", captured_logs)

        # Also check stderr for console output (may be empty depending on config)
        console_output = self.stderr_capturer.getvalue()
        if console_output:
            # If there's console output, it should contain our messages
            self.assertIn("This is a test message", console_output)

    def test_tqdm_progress_bar(self):
        """Test the custom tqdm class."""
        # Ensure stderr is reset before capturing tqdm output
        sys.stderr = io.StringIO()

        # Create a small iterable
        items = range(5)

        # Use tqdm to iterate with a progress bar
        for _ in tqdm(items, desc="Testing tqdm"):
            pass

        # Check if tqdm output contains our description and other expected elements
        tqdm_output = sys.stderr.getvalue()

        # Reset stderr to our capturer for other tests
        sys.stderr = self.stderr_capturer

        # Basic content checks - these should be true regardless of styling
        self.assertIn("Testing tqdm", tqdm_output)

        # These might depend on the styling, but at least one should be true
        has_percentage = "%" in tqdm_output
        has_bar = "|" in tqdm_output
        has_progress = "[" in tqdm_output and "]" in tqdm_output

        self.assertTrue(
            has_percentage or has_bar or has_progress,
            "Tqdm output doesn't contain any expected progress indicators",
        )

    @patch("os.getenv")
    def test_setup_logging_custom_level(self, mock_getenv):
        """Test that setup_logging respects custom log levels."""
        # Mock environment variables for logging
        mock_getenv.side_effect = lambda key, default=None: {
            "LOG_LEVEL": "DEBUG",
            "FILE_LOG_LEVEL": "INFO",
            "LOG_FILE_PATH": "./test_logs",
            "LOG_FILE_NAME": "test_%Y_%m_%d.log",
            "FULL_LOG_FILE_NAME": "full_test_%Y_%m_%d.log",
            "BACKUP_COUNT": "3",
        }.get(key, default)

        # Re-setup logging with mocked environment
        setup_logging()

        # Get the root logger and check handlers
        root_logger = logging.getLogger()

        # Should have exactly 3 handlers (console, core log file, full log file)
        self.assertEqual(len(root_logger.handlers), 3)

        # First handler should be console handler with DEBUG level
        self.assertEqual(root_logger.handlers[0].level, logging.DEBUG)

        # Second handler should be core log file handler with INFO level
        self.assertEqual(root_logger.handlers[1].level, logging.INFO)
        # Check that the core log file handler has our filter
        self.assertEqual(len(root_logger.handlers[1].filters), 1)
        self.assertIsInstance(root_logger.handlers[1].filters[0], LoggerOriginFilter)
        self.assertTrue(root_logger.handlers[1].filters[0].from_get_log)

        # Third handler should be full log file handler with INFO level
        self.assertEqual(root_logger.handlers[2].level, logging.INFO)
        # Full log file handler should not have any filters
        self.assertEqual(len(root_logger.handlers[2].filters), 0)

    def test_logger_origin_filter(self):
        """Test the LoggerOriginFilter class."""
        # Create test logger instances
        get_log_logger = get_log("test_get_log_logger")
        direct_logger = logging.getLogger("test_direct_logger")

        # Create filter instances
        get_log_filter = LoggerOriginFilter(from_get_log=True)
        other_filter = LoggerOriginFilter(from_get_log=False)

        # Create mock log records
        get_log_record = MagicMock()
        get_log_record.name = "test_get_log_logger"

        direct_record = MagicMock()
        direct_record.name = "test_direct_logger"

        # Test filtering
        self.assertTrue(get_log_filter.filter(get_log_record))
        self.assertFalse(get_log_filter.filter(direct_record))

        self.assertFalse(other_filter.filter(get_log_record))
        self.assertTrue(other_filter.filter(direct_record))


if __name__ == "__main__":
    unittest.main()
