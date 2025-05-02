#!/usr/bin/env python3
"""
Bulk Test Generator.

This script generates test files for multiple Python modules in bulk.
It supports generating unit tests, integration tests, or both, and can
run in batches to avoid memory issues.

Features:
- Batch processing to avoid memory issues
- Support for different test types
- Skip modules that already have tests
- Parallel test generation
- Detailed reporting
"""

import os
import sys
import argparse
import subprocess
import logging
import time
import multiprocessing
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bulk_test_generator")

def find_python_files(directory: str) -> List[str]:
    """
    Find all Python files in a directory recursively.

    Args:
        directory: The directory to search

    Returns:
        A list of Python file paths
    """
    python_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))

    return python_files

def get_existing_tests(test_dir: str) -> Set[str]:
    """
    Get the names of modules that already have tests.

    Args:
        test_dir: The directory containing test files

    Returns:
        A set of module names that have tests
    """
    tested_modules = set()

    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                # Extract the module name from the test file name
                module_name = file[5:].replace("_integration.py", ".py").replace("_e2e.py", ".py")
                tested_modules.add(module_name)

    return tested_modules

def generate_tests_for_module(file_path: str, output_dir: str, test_type: str = "unit",
                        verbose: bool = False, merge: bool = True) -> Tuple[str, bool, Optional[str]]:
    """
    Generate tests for a single module.

    Args:
        file_path: Path to the Python file
        output_dir: Directory to save the test files
        test_type: Type of test to generate (unit, integration, both)
        verbose: Whether to enable verbose output
        merge: Whether to merge with existing tests

    Returns:
        Tuple of (file_path, success, error_message)
    """
    # Create a subdirectory structure that mirrors the module structure
    try:
        if "src/augment_adam" in file_path:
            rel_path = os.path.relpath(file_path, "src/augment_adam")
        elif "augment_adam" in file_path:
            parts = file_path.split("augment_adam")
            if len(parts) > 1:
                rel_path = parts[1].lstrip("/\\")
            else:
                rel_path = os.path.basename(file_path)
        else:
            rel_path = os.path.basename(file_path)

        module_dir = os.path.dirname(rel_path)
        module_output_dir = os.path.join(output_dir, module_dir)

        # Create the output directory if it doesn't exist
        os.makedirs(module_output_dir, exist_ok=True)

        # Use the enhanced test generator
        cmd = ["python", "scripts/enhanced_test_generator.py", "--file", file_path, "--output-dir", module_output_dir, "--test-type", test_type]

        # Add merge option
        if merge:
            cmd.append("--merge")
        else:
            cmd.append("--overwrite")

        if verbose:
            cmd.append("--verbose")

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return file_path, True, None
    except subprocess.CalledProcessError as e:
        error_message = f"Error generating tests: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
        logger.error(f"Error generating tests for {file_path}: {error_message}")
        return file_path, False, error_message
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error generating tests for {file_path}: {error_message}")
        return file_path, False, error_message

def generate_tests_in_batch(files: List[str], output_dir: str, test_type: str, verbose: bool,
                       max_workers: int, merge: bool = True) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    Generate tests for a batch of files in parallel.

    Args:
        files: List of file paths
        output_dir: Directory to save the test files
        test_type: Type of test to generate
        verbose: Whether to enable verbose output
        max_workers: Maximum number of parallel workers
        merge: Whether to merge with existing tests

    Returns:
        Dictionary mapping file paths to (success, error_message) tuples
    """
    results = {}

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(generate_tests_for_module, file_path, output_dir, test_type, verbose, merge): file_path
            for file_path in files
        }

        for future in as_completed(future_to_file):
            file_path, success, error_message = future.result()
            results[file_path] = (success, error_message)

            if success:
                logger.info(f"Successfully generated tests for {file_path}")
            else:
                logger.error(f"Failed to generate tests for {file_path}: {error_message}")

    return results

def main():
    """Run the bulk test generator."""
    parser = argparse.ArgumentParser(description="Generate tests for multiple Python files")
    parser.add_argument("--directory", required=True, help="Directory containing Python files to generate tests for")
    parser.add_argument("--output-dir", default="tests", help="Directory to save the test files (default: tests)")
    parser.add_argument("--test-type", choices=["unit", "integration", "both"], default="unit", help="Type of test to generate")
    parser.add_argument("--skip-existing", action="store_true", help="Skip modules that already have tests")
    parser.add_argument("--merge", action="store_true", default=True, help="Merge with existing tests (default: True)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing tests instead of merging")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of files to process in each batch")
    parser.add_argument("--max-workers", type=int, default=multiprocessing.cpu_count(), help="Maximum number of parallel workers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--report", action="store_true", help="Generate a detailed report")
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine whether to merge or overwrite
    merge = args.merge and not args.overwrite
    if args.overwrite:
        logger.info("Overwriting existing tests")
    elif merge:
        logger.info("Merging with existing tests")

    start_time = time.time()

    # Find all Python files in the directory
    python_files = find_python_files(args.directory)
    logger.info(f"Found {len(python_files)} Python files in {args.directory}")

    # Get existing tests if needed
    existing_tests = set()
    if args.skip_existing:
        existing_tests = get_existing_tests(args.output_dir)
        logger.info(f"Found {len(existing_tests)} existing test files in {args.output_dir}")

    # Filter out files that already have tests if skip_existing is True
    if args.skip_existing:
        filtered_files = []
        for file_path in python_files:
            file_name = os.path.basename(file_path)
            if file_name in existing_tests:
                logger.info(f"Skipping {file_path} (already has tests)")
            else:
                filtered_files.append(file_path)

        logger.info(f"Filtered down to {len(filtered_files)} files that need tests")
        python_files = filtered_files

    # Process files in batches
    results = {}
    for i in range(0, len(python_files), args.batch_size):
        batch = python_files[i:i + args.batch_size]
        logger.info(f"Processing batch {i // args.batch_size + 1}/{(len(python_files) + args.batch_size - 1) // args.batch_size} ({len(batch)} files)")

        batch_results = generate_tests_in_batch(batch, args.output_dir, args.test_type, args.verbose, args.max_workers, merge=merge)
        results.update(batch_results)

    # Calculate statistics
    success_count = sum(1 for success, _ in results.values() if success)
    failure_count = len(results) - success_count

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print summary
    logger.info(f"Test generation complete. Tests saved to {args.output_dir}")
    logger.info(f"Summary: {success_count} succeeded, {failure_count} failed, {elapsed_time:.2f} seconds elapsed")

    # Generate detailed report if requested
    if args.report:
        report_path = os.path.join(args.output_dir, "test_generation_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Test Generation Report\n")
            f.write(f"=====================\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Directory: {args.directory}\n")
            f.write(f"Output directory: {args.output_dir}\n")
            f.write(f"Test type: {args.test_type}\n")
            f.write(f"Batch size: {args.batch_size}\n")
            f.write(f"Max workers: {args.max_workers}\n\n")
            f.write(f"Summary:\n")
            f.write(f"- Total files: {len(results)}\n")
            f.write(f"- Succeeded: {success_count}\n")
            f.write(f"- Failed: {failure_count}\n")
            f.write(f"- Elapsed time: {elapsed_time:.2f} seconds\n\n")

            if failure_count > 0:
                f.write(f"Failed files:\n")
                for file_path, (success, error_message) in results.items():
                    if not success:
                        f.write(f"- {file_path}: {error_message}\n")

        logger.info(f"Detailed report saved to {report_path}")

if __name__ == "__main__":
    main()
