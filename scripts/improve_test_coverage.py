#!/usr/bin/env python3
"""
Test Coverage Improvement Script.

This script improves test coverage by generating and running tests for priority areas,
tracking the coverage improvement, and updating the TASKS file.
"""

import argparse
import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("improve_test_coverage")

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

def get_current_coverage() -> float:
    """
    Get the current test coverage percentage.

    Returns:
        The current test coverage percentage
    """
    try:
        # Run pytest with coverage
        result = subprocess.run(
            ["python", "-m", "pytest", "--cov=src/augment_adam", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Extract the coverage percentage from the output
        output = result.stdout
        for line in output.split('\n'):
            if "TOTAL" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        coverage = float(parts[3].rstrip('%'))
                        return coverage
                    except ValueError:
                        pass
        
        logger.warning("Could not extract coverage percentage from pytest output")
        return 0.0
    
    except subprocess.SubprocessError as e:
        logger.error(f"Error running pytest: {e}")
        return 0.0

def generate_tests_for_area(area: str, output_dir: str = "tests/unit") -> List[str]:
    """
    Generate tests for a priority area.

    Args:
        area: The priority area to generate tests for
        output_dir: The directory to save the test files

    Returns:
        A list of generated test file paths
    """
    logger.info(f"Generating tests for priority area: {area}")
    
    try:
        # Run the bulk test generator for the priority area
        result = subprocess.run(
            [
                "python", 
                "scripts/bulk_enhanced_test_generator.py", 
                "--priority-area", area,
                "--output-dir", output_dir,
                "--skip-existing"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract the generated file paths from the output
        output = result.stdout
        generated_files = []
        for line in output.split('\n'):
            if "Generated unit tests saved to:" in line:
                file_path = line.split("Generated unit tests saved to:")[1].strip()
                generated_files.append(file_path)
        
        logger.info(f"Generated {len(generated_files)} test files for {area}")
        return generated_files
    
    except subprocess.SubprocessError as e:
        logger.error(f"Error generating tests for {area}: {e}")
        return []

def run_tests(test_files: List[str]) -> bool:
    """
    Run the specified test files.

    Args:
        test_files: List of test files to run

    Returns:
        True if all tests passed, False otherwise
    """
    if not test_files:
        logger.warning("No test files to run")
        return True
    
    logger.info(f"Running {len(test_files)} test files")
    
    try:
        # Run pytest on the test files
        result = subprocess.run(
            ["python", "-m", "pytest"] + test_files,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if the tests passed
        if result.returncode == 0:
            logger.info("All tests passed")
            return True
        else:
            logger.warning(f"Some tests failed: {result.stderr}")
            return False
    
    except subprocess.SubprocessError as e:
        logger.error(f"Error running tests: {e}")
        return False

def update_tasks_file(area: str, generated_files: List[str], coverage_before: float, coverage_after: float) -> None:
    """
    Update the TASKS file with the test generation results.

    Args:
        area: The priority area
        generated_files: List of generated test files
        coverage_before: Coverage percentage before test generation
        coverage_after: Coverage percentage after test generation
    """
    tasks_file = os.path.join("tests", "TASKS")
    
    if not os.path.exists(tasks_file):
        logger.warning(f"TASKS file not found at {tasks_file}")
        return
    
    with open(tasks_file, "r") as f:
        content = f.read()
    
    # Find the section for the priority area
    area_name = area.replace("/", " ").title()
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
    
    # Add coverage improvement information
    coverage_improvement = coverage_after - coverage_before
    new_lines.append(f"  - [x] Improved coverage from {coverage_before:.2f}% to {coverage_after:.2f}% (+{coverage_improvement:.2f}%)")
    
    # Update the content
    updated_content = []
    in_section = False
    for line in content.split('\n'):
        if section_pattern in line:
            # Mark the section as completed if all tests passed
            updated_line = line.replace("- [ ]", "- [x]")
            updated_content.append(updated_line)
            in_section = True
            
            # Add the new lines
            for new_line in new_lines:
                updated_content.append(new_line)
        else:
            updated_content.append(line)
    
    # Write the updated content
    with open(tasks_file, "w") as f:
        f.write('\n'.join(updated_content))
    
    logger.info(f"Updated TASKS file with {len(new_lines)} new entries for {area_name}")

def main():
    """Run the test coverage improvement script."""
    parser = argparse.ArgumentParser(description="Improve test coverage for priority areas")
    parser.add_argument("--target", type=float, default=80.0, help="Target coverage percentage (default: 80.0)")
    parser.add_argument("--output-dir", default="tests/unit", help="Directory to save the test files (default: tests/unit)")
    parser.add_argument("--area", help="Generate tests for a specific priority area")
    args = parser.parse_args()

    # Get the current coverage
    initial_coverage = get_current_coverage()
    logger.info(f"Initial test coverage: {initial_coverage:.2f}%")
    
    # Check if we've already reached the target
    if initial_coverage >= args.target:
        logger.info(f"Target coverage of {args.target:.2f}% already reached!")
        return
    
    # Generate tests for the specified area or all priority areas
    if args.area:
        areas = [args.area]
    else:
        areas = PRIORITY_AREAS
    
    current_coverage = initial_coverage
    
    for area in areas:
        logger.info(f"Processing priority area: {area}")
        
        # Get coverage before generating tests for this area
        coverage_before = current_coverage
        
        # Generate tests for the area
        generated_files = generate_tests_for_area(area, args.output_dir)
        
        if not generated_files:
            logger.warning(f"No tests generated for {area}")
            continue
        
        # Run the generated tests
        tests_passed = run_tests(generated_files)
        
        # Get the updated coverage
        coverage_after = get_current_coverage()
        logger.info(f"Coverage after generating tests for {area}: {coverage_after:.2f}% (change: {coverage_after - coverage_before:.2f}%)")
        
        # Update the TASKS file
        if tests_passed:
            update_tasks_file(area, generated_files, coverage_before, coverage_after)
        
        # Update the current coverage
        current_coverage = coverage_after
        
        # Check if we've reached the target
        if current_coverage >= args.target:
            logger.info(f"Target coverage of {args.target:.2f}% reached!")
            break
    
    # Final coverage report
    logger.info(f"Final test coverage: {current_coverage:.2f}% (improvement: {current_coverage - initial_coverage:.2f}%)")
    
    if current_coverage >= args.target:
        logger.info(f"Successfully reached target coverage of {args.target:.2f}%!")
    else:
        logger.warning(f"Did not reach target coverage of {args.target:.2f}%. Current coverage: {current_coverage:.2f}%")

if __name__ == "__main__":
    main()
