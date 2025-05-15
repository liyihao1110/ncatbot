#!/usr/bin/env python
"""
Run all utils tests or specific test classes.
"""
import argparse
import sys
import unittest

from tests.ultils.test_config import (
    TestBaseConfig,
    TestConfig,
    TestNapCatConfig,
    TestPluginConfig,
)
from tests.ultils.test_logger import TestLogger


def run_logger_tests():
    """Run all logger tests."""
    print("Running logger tests...")
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLogger))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite).wasSuccessful()


def run_config_tests():
    """Run all config tests."""
    print("Running config tests...")
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestBaseConfig))
    test_suite.addTest(unittest.makeSuite(TestNapCatConfig))
    test_suite.addTest(unittest.makeSuite(TestPluginConfig))
    test_suite.addTest(unittest.makeSuite(TestConfig))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite).wasSuccessful()


def run_all_tests():
    """Run all tests."""
    logger_success = run_logger_tests()
    config_success = run_config_tests()
    return logger_success and config_success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run utility tests")
    parser.add_argument("--logger", action="store_true", help="Run only logger tests")
    parser.add_argument("--config", action="store_true", help="Run only config tests")

    args = parser.parse_args()

    if args.logger:
        success = run_logger_tests()
    elif args.config:
        success = run_config_tests()
    else:
        success = run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
