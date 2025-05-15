#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Integration test script that discovers and runs all tests in the project.
"""

import argparse
import os
import sys
import unittest
from pathlib import Path

from tests.cli.commands.test_config_commands import TestConfigCommands
from tests.cli.commands.test_info_commands import TestInfoCommands

# CLI tests from the original src/ncatbot/tests
from tests.cli.commands.test_registry import TestCommand, TestCommandRegistry
from tests.cli.commands.test_system_commands import TestSystemCommands


def discover_and_run_tests(
    verbose=1, pattern="test*.py", start_dir=None, run_specific=False
):
    """
    Discover and run all tests in the project.

    Args:
        verbose (int): Verbosity level (0-3)
        pattern (str): Pattern to match test files
        start_dir (str): Directory to start discovery
        run_specific (bool): Whether to run only specific tests

    Returns:
        bool: True if all tests pass, False otherwise
    """
    # Add project root to sys.path to ensure imports work correctly
    project_root = str(Path(__file__).parent.parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if start_dir is None:
        # Default to tests directory (parent of this file)
        start_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Discovering tests in {start_dir} with pattern '{pattern}'")

    # Create test suite
    test_suite = unittest.TestSuite()

    if run_specific:
        # Add specific tests that were previously in src/ncatbot/tests
        loader = unittest.TestLoader()
        test_suite.addTest(loader.loadTestsFromTestCase(TestCommand))
        test_suite.addTest(loader.loadTestsFromTestCase(TestCommandRegistry))
        test_suite.addTest(loader.loadTestsFromTestCase(TestInfoCommands))
        test_suite.addTest(loader.loadTestsFromTestCase(TestConfigCommands))
        test_suite.addTest(loader.loadTestsFromTestCase(TestSystemCommands))
    else:
        # Discover and add all tests
        loader = unittest.TestLoader()
        discovered_tests = loader.discover(start_dir=start_dir, pattern=pattern)
        test_suite.addTest(discovered_tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbose)
    result = runner.run(test_suite)

    # Return True if successful, False otherwise
    return result.wasSuccessful()


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run all tests in the project.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="Increase verbosity (can be used multiple times)",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default="test*.py",
        help="Pattern to match test files (default: test*.py)",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=None,
        help="Directory to start discovery (default: tests)",
    )
    parser.add_argument(
        "--specific", action="store_true", help="Run only specific CLI command tests"
    )

    args = parser.parse_args()

    # Run tests and exit with appropriate status code
    success = discover_and_run_tests(
        verbose=args.verbose,
        pattern=args.pattern,
        start_dir=args.directory,
        run_specific=args.specific,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
