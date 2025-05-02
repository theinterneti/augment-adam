#!/usr/bin/env python3
"""
Test Executor.

This module provides a test executor that runs tests in the background
and reports results.
"""

import asyncio
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

logger = logging.getLogger("test_executor")


class TestExecutor:
    """Test executor that runs tests in the background."""

    def __init__(self, max_concurrent_tests: int = 2):
        """Initialize the test executor.

        Args:
            max_concurrent_tests: Maximum number of concurrent test runs
        """
        self.max_concurrent_tests = max_concurrent_tests
        self.running_tests: Set[str] = set()
        self.semaphore = asyncio.Semaphore(max_concurrent_tests)

    async def run_tests(self, test_file: str) -> Dict[str, Any]:
        """Run tests for a file.

        Args:
            test_file: Path to the test file

        Returns:
            Test result dictionary
        """
        # Check if the test is already running
        if test_file in self.running_tests:
            logger.info(f"Test {test_file} is already running, skipping")
            return {"success": False, "message": "Test is already running"}

        # Acquire the semaphore to limit concurrent tests
        async with self.semaphore:
            try:
                self.running_tests.add(test_file)
                logger.info(f"Running test {test_file}")

                # Create a temporary file for the test output
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                    output_file = tmp.name

                # Run the test
                start_time = time.time()
                process = await asyncio.create_subprocess_exec(
                    "python", "-m", "pytest", test_file, "-v",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                end_time = time.time()

                # Parse the test output
                stdout_str = stdout.decode("utf-8")
                stderr_str = stderr.decode("utf-8")
                output = stdout_str + "\n" + stderr_str

                # Write the output to the temporary file
                with open(output_file, "w") as f:
                    f.write(output)

                # Parse the test result
                success = process.returncode == 0
                result = {
                    "success": success,
                    "returncode": process.returncode,
                    "output": output,
                    "output_file": output_file,
                    "duration": end_time - start_time,
                    "test_file": test_file,
                    "timestamp": time.time(),
                }

                # Log the result
                if success:
                    logger.info(f"Test {test_file} passed in {result['duration']:.2f}s")
                else:
                    logger.warning(f"Test {test_file} failed in {result['duration']:.2f}s")

                return result

            except Exception as e:
                logger.error(f"Error running test {test_file}: {e}", exc_info=True)
                return {
                    "success": False,
                    "message": str(e),
                    "test_file": test_file,
                    "timestamp": time.time(),
                }
            finally:
                self.running_tests.remove(test_file)

    async def run_tests_in_directory(self, test_dir: str) -> Dict[str, Dict[str, Any]]:
        """Run all tests in a directory.

        Args:
            test_dir: Path to the test directory

        Returns:
            Dictionary mapping test files to test results
        """
        # Find all test files
        test_files = []
        for root, _, files in os.walk(test_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))

        # Run tests in parallel
        tasks = []
        for test_file in test_files:
            tasks.append(self.run_tests(test_file))

        # Wait for all tests to complete
        results = await asyncio.gather(*tasks)

        # Create a dictionary mapping test files to results
        return {test_files[i]: results[i] for i in range(len(test_files))}


if __name__ == "__main__":
    # Simple test
    import argparse

    parser = argparse.ArgumentParser(description="Run tests for a Python file")
    parser.add_argument("--file", help="Path to the test file")
    parser.add_argument("--dir", help="Path to the test directory")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async def main():
        executor = TestExecutor()
        if args.file:
            result = await executor.run_tests(args.file)
            print(f"Test result: {result['success']}")
            print(f"Output: {result['output']}")
        elif args.dir:
            results = await executor.run_tests_in_directory(args.dir)
            for test_file, result in results.items():
                print(f"Test {test_file}: {result['success']}")
        else:
            print("Please specify --file or --dir")

    asyncio.run(main())
