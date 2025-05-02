#!/usr/bin/env python3
"""
Background Test Service.

This script provides a background service that monitors code changes,
generates tests, runs tests, and reports results in real-time.

Features:
- File watching to detect code changes
- Automatic test generation using Hugging Face models
- Background test execution
- Real-time test result reporting
- Resource monitoring to avoid overloading the system
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.test_watcher import TestWatcher
from scripts.test_generator import TestGenerator
from scripts.test_executor import TestExecutor
from scripts.test_reporter import TestReporter
from scripts.resource_monitor import ResourceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/background_test_service.log"),
    ],
)
logger = logging.getLogger("background_test_service")


class BackgroundTestService:
    """Background test service that monitors code changes and runs tests."""

    def __init__(
        self,
        source_dir: str = "src/augment_adam",
        test_dir: str = "tests",
        model_name: str = "Qwen/Qwen2-7B-Instruct",
        watch_interval: float = 2.0,
        max_concurrent_tests: int = 2,
        resource_threshold: float = 0.8,
        verbose: bool = False,
    ):
        """Initialize the background test service.

        Args:
            source_dir: Directory containing source code to monitor
            test_dir: Directory containing tests
            model_name: Name of the Hugging Face model to use
            watch_interval: Interval in seconds to check for file changes
            max_concurrent_tests: Maximum number of concurrent test runs
            resource_threshold: Resource threshold (0.0-1.0) to throttle testing
            verbose: Whether to enable verbose output
        """
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.model_name = model_name
        self.watch_interval = watch_interval
        self.max_concurrent_tests = max_concurrent_tests
        self.resource_threshold = resource_threshold
        self.verbose = verbose

        # Create components
        self.watcher = TestWatcher(source_dir, watch_interval)
        self.generator = TestGenerator(model_name)
        self.executor = TestExecutor(max_concurrent_tests)
        self.reporter = TestReporter()
        self.resource_monitor = ResourceMonitor(resource_threshold)

        # State
        self.running = False
        self.tasks = set()

    async def start(self):
        """Start the background test service."""
        logger.info("Starting background test service")
        self.running = True

        # Register signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda: asyncio.create_task(self.stop())
            )

        # Start the watcher
        self.watcher.start()

        # Main service loop
        try:
            while self.running:
                # Check for changes
                changed_files = self.watcher.get_changed_files()
                if changed_files:
                    logger.info(f"Detected changes in {len(changed_files)} files")
                    await self.process_changed_files(changed_files)

                # Check resource usage
                if self.resource_monitor.should_throttle():
                    logger.warning("Resource usage high, throttling test execution")
                    await asyncio.sleep(5)  # Wait longer when resources are constrained
                else:
                    await asyncio.sleep(1)

                # Clean up completed tasks
                self.tasks = {task for task in self.tasks if not task.done()}

        except Exception as e:
            logger.error(f"Error in background test service: {e}", exc_info=True)
        finally:
            await self.stop()

    async def process_changed_files(self, changed_files: List[str]):
        """Process changed files by generating and running tests.

        Args:
            changed_files: List of changed file paths
        """
        # Generate tests for changed files
        for file_path in changed_files:
            if self.should_generate_tests(file_path):
                task = asyncio.create_task(self.generate_and_run_tests(file_path))
                self.tasks.add(task)

    async def generate_and_run_tests(self, file_path: str):
        """Generate and run tests for a file.

        Args:
            file_path: Path to the file to generate tests for
        """
        try:
            # Check resource usage
            if self.resource_monitor.should_throttle():
                logger.warning(f"Resource usage high, skipping test generation for {file_path}")
                return

            # Generate tests
            logger.info(f"Generating tests for {file_path}")
            test_file = await self.generator.generate_tests(file_path, self.test_dir)

            if not test_file:
                logger.warning(f"Failed to generate tests for {file_path}")
                return

            # Run tests
            logger.info(f"Running tests for {file_path}")
            result = await self.executor.run_tests(test_file)

            # Report results
            self.reporter.report_result(file_path, result)

            # Update TASKS.md
            await self.update_tasks_file(file_path, result)

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)

    def should_generate_tests(self, file_path: str) -> bool:
        """Check if tests should be generated for a file.

        Args:
            file_path: Path to the file

        Returns:
            Whether tests should be generated
        """
        # Skip non-Python files
        if not file_path.endswith(".py"):
            return False

        # Skip test files
        if "/tests/" in file_path or file_path.startswith("tests/"):
            return False

        # Skip certain directories
        skip_dirs = ["__pycache__", ".git", ".venv", "venv", "build", "dist"]
        if any(skip_dir in file_path for skip_dir in skip_dirs):
            return False

        return True

    async def update_tasks_file(self, file_path: str, result: Dict[str, Any]):
        """Update the TASKS.md file with test results.

        Args:
            file_path: Path to the file
            result: Test result dictionary
        """
        try:
            # Get the module name from the file path
            module_path = file_path.replace("/", ".").replace(".py", "")
            if module_path.startswith("src."):
                module_path = module_path[4:]

            # Read the TASKS.md file
            tasks_file = os.path.join(self.test_dir, "TASKS.md")
            if not os.path.exists(tasks_file):
                logger.warning(f"TASKS.md file not found at {tasks_file}")
                return

            with open(tasks_file, "r") as f:
                content = f.read()

            # Find the appropriate section
            sections = {
                "memory": "## Memory System Tests",
                "context": "## Context Engine Tests",
                "monte_carlo": "## Monte Carlo Methods Tests",
                "parallel": "## Parallel Processing Tests",
            }

            section = None
            for key, section_header in sections.items():
                if key in module_path:
                    section = section_header
                    break

            if not section:
                logger.warning(f"Could not determine section for {module_path}")
                return

            # Update the content
            lines = content.split("\n")
            section_index = -1
            for i, line in enumerate(lines):
                if line == section:
                    section_index = i
                    break

            if section_index == -1:
                logger.warning(f"Section {section} not found in TASKS.md")
                return

            # Add the test result
            module_name = os.path.basename(file_path).replace(".py", "")
            test_status = "x" if result.get("success", False) else " "
            new_line = f"  - [{test_status}] Generated tests for {module_name}"

            # Check if the line already exists
            for i in range(section_index + 1, len(lines)):
                if lines[i].startswith("##"):
                    # We've reached the next section
                    lines.insert(i, new_line)
                    break
                if module_name in lines[i]:
                    # Update the existing line
                    lines[i] = new_line
                    break
            else:
                # Add to the end of the section
                lines.append(new_line)

            # Write the updated content
            with open(tasks_file, "w") as f:
                f.write("\n".join(lines))

            logger.info(f"Updated TASKS.md for {module_name}")

        except Exception as e:
            logger.error(f"Error updating TASKS.md: {e}", exc_info=True)

    async def stop(self):
        """Stop the background test service."""
        if not self.running:
            return

        logger.info("Stopping background test service")
        self.running = False

        # Stop the watcher
        self.watcher.stop()

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()

        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        logger.info("Background test service stopped")


async def main():
    """Run the background test service."""
    parser = argparse.ArgumentParser(description="Background test service")
    parser.add_argument("--source-dir", default="src/augment_adam", help="Directory containing source code to monitor")
    parser.add_argument("--test-dir", default="tests", help="Directory containing tests")
    parser.add_argument("--model-name", default="Qwen/Qwen2-7B-Instruct", help="Name of the Hugging Face model to use")
    parser.add_argument("--watch-interval", type=float, default=2.0, help="Interval in seconds to check for file changes")
    parser.add_argument("--max-concurrent-tests", type=int, default=2, help="Maximum number of concurrent test runs")
    parser.add_argument("--resource-threshold", type=float, default=0.8, help="Resource threshold (0.0-1.0) to throttle testing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create and start the service
    service = BackgroundTestService(
        source_dir=args.source_dir,
        test_dir=args.test_dir,
        model_name=args.model_name,
        watch_interval=args.watch_interval,
        max_concurrent_tests=args.max_concurrent_tests,
        resource_threshold=args.resource_threshold,
        verbose=args.verbose,
    )
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
