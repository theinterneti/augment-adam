#!/usr/bin/env python3
"""
Bulk Test Generator.

This script generates test files for multiple Python modules in bulk.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Set

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

def generate_tests_for_module(file_path: str, output_dir: str, test_type: str = None) -> None:
    """
    Generate tests for a single module.

    Args:
        file_path: Path to the Python file
        output_dir: Directory to save the test files
        test_type: Type of test to generate (unit, integration, e2e, or None for all)
    """
    # Create a subdirectory structure that mirrors the module structure
    rel_path = os.path.relpath(file_path, "src/augment_adam")
    module_dir = os.path.dirname(rel_path)
    module_output_dir = os.path.join(output_dir, module_dir)

    # Create the output directory if it doesn't exist
    os.makedirs(module_output_dir, exist_ok=True)

    cmd = ["python", "scripts/generate_tests.py", "--file", file_path, "--output-dir", module_output_dir]

    if test_type == "unit":
        cmd.append("--unit-only")
    elif test_type == "integration":
        cmd.append("--integration-only")
    elif test_type == "e2e":
        cmd.append("--e2e-only")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating tests for {file_path}: {e}")

def main():
    """Run the bulk test generator."""
    parser = argparse.ArgumentParser(description="Generate tests for multiple Python files")
    parser.add_argument("--directory", required=True, help="Directory containing Python files to generate tests for")
    parser.add_argument("--output-dir", default="tests", help="Directory to save the test files (default: tests)")
    parser.add_argument("--test-type", choices=["unit", "integration", "e2e"], help="Type of test to generate")
    parser.add_argument("--skip-existing", action="store_true", help="Skip modules that already have tests")
    args = parser.parse_args()

    # Find all Python files in the directory
    python_files = find_python_files(args.directory)
    print(f"Found {len(python_files)} Python files in {args.directory}")

    # Get existing tests if needed
    existing_tests = set()
    if args.skip_existing:
        existing_tests = get_existing_tests(args.output_dir)
        print(f"Found {len(existing_tests)} existing test files in {args.output_dir}")

    # Generate tests for each file
    for i, file_path in enumerate(python_files):
        # Skip files that already have tests if requested
        file_name = os.path.basename(file_path)
        if args.skip_existing and file_name in existing_tests:
            print(f"Skipping {file_path} (already has tests)")
            continue

        print(f"Generating tests for {file_path} ({i+1}/{len(python_files)})")
        generate_tests_for_module(file_path, args.output_dir, args.test_type)

    print(f"Test generation complete. Tests saved to {args.output_dir}")

if __name__ == "__main__":
    main()
