#!/usr/bin/env python3
"""
Enhanced Test Runner for Augment Adam.

This script provides a comprehensive test runner for the Augment Adam project,
supporting various test types (unit, integration, e2e, etc.), parallel execution,
and coverage reporting.
"""

import os
import sys
import argparse
import unittest
import time
import concurrent.futures
from pathlib import Path
from typing import List, Optional, Set, Tuple, Dict, Any

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False


def discover_tests(test_dir: str, pattern: str = "test_*.py") -> unittest.TestSuite:
    """
    Discover tests in the specified directory.

    Args:
        test_dir: Directory to discover tests in
        pattern: Pattern to match test files

    Returns:
        TestSuite containing the discovered tests
    """
    test_loader = unittest.TestLoader()
    return test_loader.discover(test_dir, pattern=pattern)


def run_test_suite(test_suite: unittest.TestSuite, verbosity: int = 2) -> unittest.TestResult:
    """
    Run a test suite.

    Args:
        test_suite: TestSuite to run
        verbosity: Verbosity level (0-3)

    Returns:
        TestResult containing the test results
    """
    test_runner = unittest.TextTestRunner(verbosity=verbosity)
    return test_runner.run(test_suite)


def run_tests_in_directory(directory: str, pattern: str = "test_*.py",
                          verbosity: int = 2) -> unittest.TestResult:
    """
    Run all tests in a directory.

    Args:
        directory: Directory containing tests
        pattern: Pattern to match test files
        verbosity: Verbosity level (0-3)

    Returns:
        TestResult containing the test results
    """
    test_suite = discover_tests(directory, pattern)
    return run_test_suite(test_suite, verbosity)


def run_tests_in_parallel(directories: List[str], pattern: str = "test_*.py",
                         max_workers: int = None) -> Dict[str, unittest.TestResult]:
    """
    Run tests from multiple directories in parallel.

    Args:
        directories: List of directories containing tests
        pattern: Pattern to match test files
        max_workers: Maximum number of worker threads

    Returns:
        Dictionary mapping directory names to TestResults
    """
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_dir = {
            executor.submit(run_tests_in_directory, directory, pattern, 1): directory
            for directory in directories
        }

        for future in concurrent.futures.as_completed(future_to_dir):
            directory = future_to_dir[future]
            try:
                results[directory] = future.result()
            except Exception as exc:
                print(f"Error running tests in {directory}: {exc}")
                results[directory] = None

    return results


def run_pytest(test_paths: List[str], coverage: bool = False,
              markers: Optional[List[str]] = None, verbose: bool = False) -> int:
    """
    Run tests using pytest.

    Args:
        test_paths: Paths to test files or directories
        coverage: Whether to generate coverage report
        markers: List of pytest markers to select
        verbose: Whether to use verbose output

    Returns:
        Exit code from pytest
    """
    if not PYTEST_AVAILABLE:
        print("Error: pytest is not installed. Please install it with 'pip install pytest'.")
        return 1

    import pytest

    args = []

    # Add verbosity
    if verbose:
        args.append("-v")

    # Add coverage
    if coverage and COVERAGE_AVAILABLE:
        args.extend(["--cov=augment_adam", "--cov-report=term-missing", "--cov-report=html"])

    # Add markers
    if markers:
        for marker in markers:
            args.append(f"-m {marker}")

    # Add test paths
    args.extend(test_paths)

    # Run pytest
    return pytest.main(args)


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for Augment Adam")

    # Test selection options
    test_selection = parser.add_argument_group("Test Selection")
    test_selection.add_argument("--unit", action="store_true", help="Run unit tests")
    test_selection.add_argument("--integration", action="store_true", help="Run integration tests")
    test_selection.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    test_selection.add_argument("--performance", action="store_true", help="Run performance tests")
    test_selection.add_argument("--stress", action="store_true", help="Run stress tests")
    test_selection.add_argument("--compatibility", action="store_true", help="Run compatibility tests")
    test_selection.add_argument("--all", action="store_true", help="Run all tests")
    test_selection.add_argument("--path", nargs="+", help="Run tests at specific path(s)")

    # Test execution options
    execution = parser.add_argument_group("Test Execution")
    execution.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    execution.add_argument("--workers", type=int, default=None,
                          help="Number of worker threads for parallel execution")
    execution.add_argument("--use-pytest", action="store_true",
                          help="Use pytest instead of unittest")

    # Output options
    output = parser.add_argument_group("Output")
    output.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    output.add_argument("-q", "--quiet", action="store_true", help="Quiet output")
    output.add_argument("--coverage", action="store_true", help="Generate coverage report")

    args = parser.parse_args()

    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 3
    else:
        verbosity = 2

    # Determine which tests to run
    test_dirs = []

    if args.unit or args.all:
        test_dirs.append("tests/unit")

    if args.integration or args.all:
        test_dirs.append("tests/integration")

    if args.e2e or args.all:
        test_dirs.append("tests/e2e")

    if args.performance or args.all:
        test_dirs.append("tests/performance")

    if args.stress or args.all:
        test_dirs.append("tests/stress")

    if args.compatibility or args.all:
        test_dirs.append("tests/compatibility")

    # If specific paths are provided, use those instead
    if args.path:
        test_dirs = args.path

    # If no test directories are specified, run all tests
    if not test_dirs:
        test_dirs = ["tests"]

    # Run the tests
    start_time = time.time()

    if args.use_pytest and PYTEST_AVAILABLE:
        # Determine markers based on test types
        markers = []
        if args.unit:
            markers.append("unit")
        if args.integration:
            markers.append("integration")
        if args.e2e:
            markers.append("e2e")
        if args.performance:
            markers.append("performance")
        if args.stress:
            markers.append("stress")
        if args.compatibility:
            markers.append("compatibility")

        # Run tests with pytest
        exit_code = run_pytest(test_dirs, args.coverage, markers, args.verbose)
        success = exit_code == 0
    elif args.parallel:
        # Run tests in parallel
        results = run_tests_in_parallel(test_dirs, max_workers=args.workers)

        # Print results
        all_success = True
        total_tests = 0
        total_errors = 0
        total_failures = 0

        for directory, result in results.items():
            if result is None:
                print(f"Error running tests in {directory}")
                all_success = False
                continue

            total_tests += result.testsRun
            total_errors += len(result.errors)
            total_failures += len(result.failures)

            if not result.wasSuccessful():
                all_success = False

        print(f"\nRan {total_tests} tests in {time.time() - start_time:.2f}s")
        print(f"Errors: {total_errors}, Failures: {total_failures}")

        success = all_success
    else:
        # Run tests sequentially
        all_success = True
        total_tests = 0

        for directory in test_dirs:
            print(f"\nRunning tests in {directory}:")
            result = run_tests_in_directory(directory, verbosity=verbosity)

            total_tests += result.testsRun

            if not result.wasSuccessful():
                all_success = False

        print(f"\nRan {total_tests} tests in {time.time() - start_time:.2f}s")

        success = all_success

    # Print coverage information if requested
    if args.coverage and COVERAGE_AVAILABLE and not args.use_pytest:
        print("\nCoverage report is only available when using pytest.")
        print("Please use --use-pytest --coverage to generate a coverage report.")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
