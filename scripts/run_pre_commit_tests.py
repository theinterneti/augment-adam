#!/usr/bin/env python
"""
Pre-commit test runner.

This script runs tests on files that have been modified in the current commit.
It's designed to be used as a pre-commit hook to ensure that tests pass before
allowing a commit to proceed.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Set, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pre-commit-tests')

def get_modified_files() -> List[str]:
    """
    Get a list of files that have been modified in the current commit.

    Returns:
        A list of modified file paths.
    """
    try:
        # Get staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
            capture_output=True,
            text=True,
            check=True
        )

        # Split the output into lines and filter for Python files
        files = [
            file for file in result.stdout.strip().split('\n')
            if file.endswith('.py') and os.path.exists(file)
        ]

        return files
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting modified files: {e}")
        return []

def get_test_files_for_modified_files(modified_files: List[str]) -> List[str]:
    """
    Get a list of test files that correspond to the modified files.

    Args:
        modified_files: A list of modified file paths.

    Returns:
        A list of test file paths.
    """
    test_files = []

    for file_path in modified_files:
        # Skip test files themselves
        if 'test_' in file_path:
            test_files.append(file_path)
            continue

        # Convert source file path to potential test file path
        path = Path(file_path)

        # Skip files outside the main package
        if not (str(path).startswith('src/augment_adam') or str(path).startswith('augment_adam')):
            continue

        # Extract the module path
        if str(path).startswith('src/'):
            module_path = str(path)[4:-3]  # Remove 'src/' and '.py'
        else:
            module_path = str(path)[:-3]  # Remove '.py'

        module_parts = module_path.split('/')

        # Skip if not in the main package
        if module_parts[0] != 'augment_adam':
            continue

        # Create the test file path
        test_dir = Path('tests/unit')
        for part in module_parts[1:-1]:  # Skip the first part (augment_adam) and the last part (filename)
            test_dir = test_dir / part

        filename = path.stem
        test_file = test_dir / f"test_{filename}.py"

        if test_file.exists():
            test_files.append(str(test_file))

    return test_files

def run_tests(test_files: List[str]) -> bool:
    """
    Run tests on the specified files.

    Args:
        test_files: A list of test file paths.

    Returns:
        True if all tests pass, False otherwise.
    """
    if not test_files:
        logger.info("No test files to run.")
        return True

    logger.info(f"Running tests on {len(test_files)} files:")
    for file in test_files:
        logger.info(f"  {file}")

    try:
        # Run pytest on the test files
        result = subprocess.run(
            ['python', '-m', 'pytest'] + test_files + ['-v'],
            capture_output=True,
            text=True
        )

        # Print the output
        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        # Return True if the tests passed
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False

def main() -> int:
    """
    Main function.

    Returns:
        0 if all tests pass, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description='Run tests on modified files')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    args = parser.parse_args()

    if args.all:
        # Run all tests
        logger.info("Running all tests...")
        result = subprocess.run(['python', '-m', 'pytest'], capture_output=False)
        return result.returncode

    # Get modified files
    modified_files = get_modified_files()

    if not modified_files:
        logger.info("No modified files found.")
        return 0

    logger.info(f"Found {len(modified_files)} modified files:")
    for file in modified_files:
        logger.info(f"  {file}")

    # Get test files for modified files
    test_files = get_test_files_for_modified_files(modified_files)

    # Run tests
    if run_tests(test_files):
        logger.info("All tests passed!")
        return 0
    else:
        logger.error("Tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
