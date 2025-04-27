#!/usr/bin/env python
"""
Test Generator Service.

This script runs the test generator as a service, automatically generating tests
for untested functions and classes on a schedule.
"""

import os
import sys
import argparse
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'test_generator_service.log')
    ]
)
logger = logging.getLogger('test_generator_service')

def run_test_generator(package: str, output_dir: str, interval_hours: float, report: bool = True) -> None:
    """
    Run the test generator as a service.

    Args:
        package: The package to scan for untested functions
        output_dir: The directory to write test files to
        interval_hours: How often to run the test generation (in hours)
        report: Whether to generate a report of test coverage
    """
    # Build the command
    cmd = [
        sys.executable,
        str(Path(__file__).parent / 'generate_tests_no_tags.py'),
        '--package', package,
        '--output-dir', output_dir,
        '--schedule', str(interval_hours)
    ]

    if report:
        cmd.append('--report')

    logger.info(f"Starting test generator service with command: {' '.join(cmd)}")

    # Run the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Test generator service failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test generator service stopped by user")
        sys.exit(0)

def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the test generator as a service")
    parser.add_argument("--package", default="augment_adam", help="The package to scan for untested functions")
    parser.add_argument("--output-dir", default="tests/unit", help="The directory to write test files to")
    parser.add_argument("--interval", type=float, default=24.0, help="How often to run the test generation (in hours)")
    parser.add_argument("--no-report", action="store_true", help="Don't generate a report of test coverage")
    args = parser.parse_args()

    # Run the test generator
    run_test_generator(args.package, args.output_dir, args.interval, not args.no_report)

if __name__ == "__main__":
    main()
