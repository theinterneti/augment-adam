#!/usr/bin/env python
"""
Generate Tests for All Modules.

This script generates tests for all modules in the codebase.
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'generate_all_tests.log')
    ]
)
logger = logging.getLogger('generate_all_tests')

def generate_all_tests(package: str, output_dir: str, report: bool = True) -> None:
    """
    Generate tests for all modules in the package.

    Args:
        package: The package to scan for untested functions
        output_dir: The directory to write test files to
        report: Whether to generate a report of test coverage
    """
    # Build the command
    cmd = [
        sys.executable,
        str(Path(__file__).parent / 'generate_tests_no_tags.py'),
        '--package', package,
        '--output-dir', output_dir
    ]

    if report:
        cmd.append('--report')

    logger.info(f"Generating tests for all modules with command: {' '.join(cmd)}")

    # Run the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Test generation failed: {e}")
        sys.exit(1)

def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate tests for all modules in the codebase")
    parser.add_argument("--package", default="augment_adam", help="The package to scan for untested functions")
    parser.add_argument("--output-dir", default="tests/unit", help="The directory to write test files to")
    parser.add_argument("--no-report", action="store_true", help="Don't generate a report of test coverage")
    args = parser.parse_args()

    # Generate tests
    generate_all_tests(args.package, args.output_dir, not args.no_report)

if __name__ == "__main__":
    main()
