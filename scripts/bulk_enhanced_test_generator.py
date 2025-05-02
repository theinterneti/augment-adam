#!/usr/bin/env python3
"""
Bulk Enhanced Test Generator.

This script generates functional tests for multiple Python modules in bulk,
focusing on priority areas for test coverage improvement.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Set, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bulk_enhanced_test_generator")

# Priority areas for testing
PRIORITY_AREAS = [
    "memory/core",
    "memory/vector",
    "memory/graph",
    "memory/episodic",
    "memory/semantic",
    "memory/working",
    "context/core",
    "context/chunking",
    "context/composition",
    "context/retrieval",
    "context/prompt",
    "context/storage",
    "monte_carlo/mcmc",
    "monte_carlo/mcts",
    "monte_carlo/particle_filter",
    "monte_carlo/sequential_mc",
    "monte_carlo/importance_sampling",
    "monte_carlo/utils",
    "parallel/base",
    "parallel/thread",
    "parallel/process",
    "parallel/async_module",
    "parallel/workflow",
    "parallel/utils",
]

def find_python_files(directory: str, priority_only: bool = False) -> List[str]:
    """
    Find all Python files in a directory recursively.

    Args:
        directory: The directory to search
        priority_only: Whether to only include files in priority areas

    Returns:
        A list of Python file paths
    """
    python_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                # Check if the file is in a priority area
                if priority_only:
                    rel_path = os.path.relpath(file_path, directory)
                    if not any(area in rel_path for area in PRIORITY_AREAS):
                        continue
                
                python_files.append(file_path)

    return python_files

def get_existing_tests(test_dir: str) -> Set[str]:
    """
    Get a set of existing test files.

    Args:
        test_dir: The directory containing test files

    Returns:
        A set of test file names
    """
    existing_tests = set()

    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                existing_tests.add(file)

    return existing_tests

def generate_tests_for_module(file_path: str, output_dir: str) -> Optional[str]:
    """
    Generate tests for a single module using the enhanced test generator.

    Args:
        file_path: Path to the Python file
        output_dir: Directory to save the test files

    Returns:
        The path to the generated test file, or None if generation failed
    """
    # Create a subdirectory structure that mirrors the module structure
    rel_path = os.path.relpath(file_path, "src/augment_adam")
    module_dir = os.path.dirname(rel_path)
    module_output_dir = os.path.join(output_dir, module_dir)

    # Create the output directory if it doesn't exist
    os.makedirs(module_output_dir, exist_ok=True)

    cmd = ["python", "scripts/enhanced_test_generator.py", "--file", file_path, "--output-dir", module_output_dir]

    try:
        subprocess.run(cmd, check=True)
        module_name = os.path.basename(file_path).replace('.py', '')
        test_file_path = os.path.join(module_output_dir, f"test_{module_name}.py")
        return test_file_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating tests for {file_path}: {e}")
        return None

def update_tasks_file(generated_files: List[str], priority_area: str) -> None:
    """
    Update the TASKS file for a priority area.

    Args:
        generated_files: List of generated test files
        priority_area: The priority area being tested
    """
    tasks_file = os.path.join("tests", "TASKS")
    
    if not os.path.exists(tasks_file):
        logger.warning(f"TASKS file not found at {tasks_file}")
        return
    
    with open(tasks_file, "r") as f:
        content = f.read()
    
    # Find the section for the priority area
    area_name = priority_area.replace("/", " ").title()
    section_pattern = f"- [ ] {area_name}"
    
    if section_pattern not in content:
        logger.warning(f"Section for {area_name} not found in TASKS file")
        return
    
    # Add the generated files to the section
    new_lines = []
    for file_path in generated_files:
        file_name = os.path.basename(file_path)
        module_name = file_name.replace('test_', '').replace('.py', '')
        new_lines.append(f"  - [x] Generated tests for {module_name}")
    
    # Update the content
    updated_content = []
    in_section = False
    for line in content.split('\n'):
        updated_content.append(line)
        
        if section_pattern in line:
            in_section = True
            for new_line in new_lines:
                updated_content.append(new_line)
    
    # Write the updated content
    with open(tasks_file, "w") as f:
        f.write('\n'.join(updated_content))
    
    logger.info(f"Updated TASKS file with {len(new_lines)} new entries for {area_name}")

def main():
    """Run the bulk test generator."""
    parser = argparse.ArgumentParser(description="Generate tests for multiple Python files")
    parser.add_argument("--directory", default="src/augment_adam", help="Directory containing Python files to generate tests for")
    parser.add_argument("--output-dir", default="tests/unit", help="Directory to save the test files (default: tests/unit)")
    parser.add_argument("--priority-only", action="store_true", help="Only generate tests for priority areas")
    parser.add_argument("--skip-existing", action="store_true", help="Skip modules that already have tests")
    parser.add_argument("--priority-area", help="Generate tests for a specific priority area")
    args = parser.parse_args()

    # Find all Python files in the directory
    if args.priority_area:
        # Generate tests for a specific priority area
        priority_path = os.path.join(args.directory, args.priority_area.replace("/", os.path.sep))
        if not os.path.exists(priority_path):
            logger.error(f"Priority area path not found: {priority_path}")
            return
        
        python_files = find_python_files(priority_path)
        logger.info(f"Found {len(python_files)} Python files in priority area {args.priority_area}")
    else:
        # Generate tests for all files or all priority areas
        python_files = find_python_files(args.directory, args.priority_only)
        logger.info(f"Found {len(python_files)} Python files in {args.directory}")

    # Get existing tests if needed
    existing_tests = set()
    if args.skip_existing:
        existing_tests = get_existing_tests(args.output_dir)
        logger.info(f"Found {len(existing_tests)} existing test files in {args.output_dir}")

    # Generate tests for each file
    generated_files = []
    for i, file_path in enumerate(python_files):
        # Skip files that already have tests if requested
        file_name = os.path.basename(file_path)
        test_file_name = f"test_{file_name}"
        if args.skip_existing and test_file_name in existing_tests:
            logger.info(f"Skipping {file_path} (already has tests)")
            continue

        logger.info(f"Generating tests for {file_path} ({i+1}/{len(python_files)})")
        test_file_path = generate_tests_for_module(file_path, args.output_dir)
        
        if test_file_path:
            generated_files.append(test_file_path)

    logger.info(f"Test generation complete. Generated {len(generated_files)} test files.")
    
    # Update the TASKS file if a specific priority area was specified
    if args.priority_area and generated_files:
        update_tasks_file(generated_files, args.priority_area)

if __name__ == "__main__":
    main()
