#!/usr/bin/env python3
"""
Run Tests in Batches.

This script runs tests in smaller batches to avoid memory issues.
It also aggregates test results and generates a report.

Features:
- Run tests in smaller batches
- Aggregate test results
- Generate a detailed report
- Support for different test types (unit, integration, e2e)
- Support for test filtering
"""

import os
import sys
import argparse
import subprocess
import logging
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_tests_in_batches")

def find_test_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    Find all test files in a directory recursively.

    Args:
        directory: The directory to search
        pattern: Optional pattern to filter test files

    Returns:
        A list of test file paths
    """
    test_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                if pattern is None or pattern in file:
                    test_files.append(os.path.join(root, file))

    return test_files

def run_test_batch(test_files: List[str], verbose: bool = False) -> Tuple[Dict[str, Any], str, str]:
    """
    Run a batch of tests.

    Args:
        test_files: List of test files to run
        verbose: Whether to enable verbose output

    Returns:
        Tuple of (results, stdout, stderr)
    """
    cmd = ["python", "-m", "pytest"]
    
    # Add test files
    cmd.extend(test_files)
    
    # Add options
    cmd.append("--verbose" if verbose else "--quiet")
    cmd.append("--junit-xml=test_results.xml")
    
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        
        # Parse test results
        results = {
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "files": test_files,
        }
        
        return results, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return {"returncode": -1, "success": False, "files": test_files}, "", str(e)

def aggregate_results(batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate results from multiple test batches.

    Args:
        batch_results: List of batch results

    Returns:
        Aggregated results
    """
    total_files = 0
    total_success = 0
    failed_files = []
    
    for batch in batch_results:
        total_files += len(batch["files"])
        if batch["success"]:
            total_success += len(batch["files"])
        else:
            # If the batch failed, we don't know exactly which files failed,
            # so we count all files in the batch as failed
            failed_files.extend(batch["files"])
    
    return {
        "total_files": total_files,
        "total_success": total_success,
        "total_failed": len(failed_files),
        "failed_files": failed_files,
        "success_rate": total_success / total_files if total_files > 0 else 0,
    }

def main():
    """Run tests in batches."""
    parser = argparse.ArgumentParser(description="Run tests in smaller batches")
    parser.add_argument("--directory", default="tests", help="Directory containing test files (default: tests)")
    parser.add_argument("--pattern", help="Pattern to filter test files")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of test files to run in each batch")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--report", action="store_true", help="Generate a detailed report")
    parser.add_argument("--output-dir", default="test_results", help="Directory to save test results (default: test_results)")
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    start_time = time.time()

    # Find all test files
    test_files = find_test_files(args.directory, args.pattern)
    logger.info(f"Found {len(test_files)} test files in {args.directory}")

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Run tests in batches
    batch_results = []
    for i in range(0, len(test_files), args.batch_size):
        batch = test_files[i:i + args.batch_size]
        logger.info(f"Running batch {i // args.batch_size + 1}/{(len(test_files) + args.batch_size - 1) // args.batch_size} ({len(batch)} files)")
        
        batch_result, stdout, stderr = run_test_batch(batch, args.verbose)
        batch_results.append(batch_result)
        
        # Save batch results
        batch_dir = os.path.join(args.output_dir, f"batch_{i // args.batch_size + 1}")
        os.makedirs(batch_dir, exist_ok=True)
        
        with open(os.path.join(batch_dir, "results.json"), "w", encoding="utf-8") as f:
            json.dump(batch_result, f, indent=2)
        
        with open(os.path.join(batch_dir, "stdout.txt"), "w", encoding="utf-8") as f:
            f.write(stdout)
        
        with open(os.path.join(batch_dir, "stderr.txt"), "w", encoding="utf-8") as f:
            f.write(stderr)
        
        logger.info(f"Batch {i // args.batch_size + 1} {'succeeded' if batch_result['success'] else 'failed'}")

    # Aggregate results
    aggregated_results = aggregate_results(batch_results)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Print summary
    logger.info(f"Test run complete. Results saved to {args.output_dir}")
    logger.info(f"Summary: {aggregated_results['total_success']} succeeded, {aggregated_results['total_failed']} failed, {elapsed_time:.2f} seconds elapsed")
    
    # Generate detailed report if requested
    if args.report:
        report_path = os.path.join(args.output_dir, "test_run_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Test Run Report\n")
            f.write(f"==============\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Directory: {args.directory}\n")
            f.write(f"Pattern: {args.pattern or 'None'}\n")
            f.write(f"Batch size: {args.batch_size}\n\n")
            f.write(f"Summary:\n")
            f.write(f"- Total files: {aggregated_results['total_files']}\n")
            f.write(f"- Succeeded: {aggregated_results['total_success']}\n")
            f.write(f"- Failed: {aggregated_results['total_failed']}\n")
            f.write(f"- Success rate: {aggregated_results['success_rate'] * 100:.2f}%\n")
            f.write(f"- Elapsed time: {elapsed_time:.2f} seconds\n\n")
            
            if aggregated_results['total_failed'] > 0:
                f.write(f"Failed files:\n")
                for file_path in aggregated_results['failed_files']:
                    f.write(f"- {file_path}\n")
        
        logger.info(f"Detailed report saved to {report_path}")
    
    # Save aggregated results
    with open(os.path.join(args.output_dir, "aggregated_results.json"), "w", encoding="utf-8") as f:
        json.dump(aggregated_results, f, indent=2)
    
    # Exit with appropriate status code
    sys.exit(0 if aggregated_results['total_failed'] == 0 else 1)

if __name__ == "__main__":
    main()
