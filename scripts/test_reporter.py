#!/usr/bin/env python3
"""
Test Reporter.

This module provides a test reporter that reports test results in real-time.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger("test_reporter")


class TestReporter:
    """Test reporter that reports test results in real-time."""

    def __init__(self, report_dir: str = "reports/tests"):
        """Initialize the test reporter.

        Args:
            report_dir: Directory to save test reports
        """
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        self.results: Dict[str, Dict[str, Any]] = {}
        self.summary: Dict[str, Any] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "last_updated": time.time(),
        }

    def report_result(self, file_path: str, result: Dict[str, Any]):
        """Report a test result.

        Args:
            file_path: Path to the file that was tested
            result: Test result dictionary
        """
        # Update the results
        self.results[file_path] = result
        self.summary["total"] += 1
        if result.get("success", False):
            self.summary["passed"] += 1
        else:
            self.summary["failed"] += 1
        self.summary["last_updated"] = time.time()

        # Log the result
        if result.get("success", False):
            logger.info(f"Test passed: {file_path}")
        else:
            logger.warning(f"Test failed: {file_path}")

        # Save the result to a file
        self._save_result(file_path, result)
        self._save_summary()

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all test results.

        Returns:
            Dictionary mapping file paths to test results
        """
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of test results.

        Returns:
            Summary dictionary
        """
        return self.summary

    def _save_result(self, file_path: str, result: Dict[str, Any]):
        """Save a test result to a file.

        Args:
            file_path: Path to the file that was tested
            result: Test result dictionary
        """
        try:
            # Create a filename based on the file path
            filename = os.path.basename(file_path).replace(".py", "")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = os.path.join(self.report_dir, f"{filename}_{timestamp}.json")

            # Create a copy of the result without the output
            result_copy = result.copy()
            if "output" in result_copy:
                result_copy["output"] = result_copy["output"][:1000] + "..." if len(result_copy["output"]) > 1000 else result_copy["output"]

            # Save the result
            with open(result_file, "w") as f:
                json.dump(result_copy, f, indent=2)

            logger.debug(f"Saved test result to {result_file}")

        except Exception as e:
            logger.error(f"Error saving test result: {e}", exc_info=True)

    def _save_summary(self):
        """Save a summary of test results."""
        try:
            # Save the summary
            summary_file = os.path.join(self.report_dir, "summary.json")
            with open(summary_file, "w") as f:
                json.dump(self.summary, f, indent=2)

            logger.debug(f"Saved test summary to {summary_file}")

        except Exception as e:
            logger.error(f"Error saving test summary: {e}", exc_info=True)


if __name__ == "__main__":
    # Simple test
    import argparse

    parser = argparse.ArgumentParser(description="Report test results")
    parser.add_argument("--file", required=True, help="Path to the file that was tested")
    parser.add_argument("--success", action="store_true", help="Whether the test passed")
    parser.add_argument("--output", help="Test output")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    reporter = TestReporter()
    reporter.report_result(
        args.file,
        {
            "success": args.success,
            "output": args.output or "No output",
            "timestamp": time.time(),
        },
    )

    print(f"Summary: {reporter.get_summary()}")
