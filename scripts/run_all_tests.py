#!/usr/bin/env python
"""
Run all tests for the Augment Adam project.

This script runs all tests and generates a coverage report.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_tests(test_paths=None, coverage=True, verbose=True, html_report=True, xml_report=False):
    """
    Run tests with proper setup.

    Args:
        test_paths: List of paths to test files or directories (default: all tests)
        coverage: Whether to generate a coverage report
        verbose: Whether to run in verbose mode
        html_report: Whether to generate an HTML coverage report
        xml_report: Whether to generate an XML coverage report for CI

    Returns:
        The exit code from pytest
    """
    # Build the command
    cmd = ["python", "-m", "pytest"]

    # Add options
    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=augment_adam"])

        if html_report:
            cmd.extend(["--cov-report=html"])

        if xml_report:
            cmd.extend(["--cov-report=xml"])

        cmd.extend(["--cov-report=term"])

    # Add the test paths
    if test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append("tests/")

    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Run all tests for Augment Adam")
    parser.add_argument("--test-path", nargs='+', help="The path(s) to the test file(s) or directory")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--no-html", action="store_true", help="Disable HTML coverage report")
    parser.add_argument("--xml", action="store_true", help="Generate XML coverage report for CI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run in verbose mode")
    args = parser.parse_args()

    # Run the tests
    exit_code = run_tests(
        test_paths=args.test_path,
        coverage=not args.no_coverage,
        verbose=args.verbose,
        html_report=not args.no_html,
        xml_report=args.xml
    )

    # Print a message about the coverage report
    if not args.no_coverage and not args.no_html:
        print("\nCoverage report generated in htmlcov/index.html")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
