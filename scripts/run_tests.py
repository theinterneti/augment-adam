#!/usr/bin/env python
"""
Test runner script.

This script runs tests with proper setup to avoid import issues.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_tests(test_path: str, coverage: bool = False, verbose: bool = False) -> int:
    """
    Run tests with proper setup.
    
    Args:
        test_path: The path to the test file or directory
        coverage: Whether to generate a coverage report
        verbose: Whether to run in verbose mode
        
    Returns:
        The exit code from pytest
    """
    # Build the command
    cmd = ["python", "-m", "pytest"]
    
    # Add options
    if verbose:
        cmd.append("-v")
        
    if coverage:
        cmd.extend(["--cov=src/augment_adam", "--cov-report=html", "--cov-report=term"])
    
    # Add the test path
    cmd.append(test_path)
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Run tests with proper setup")
    parser.add_argument("test_path", nargs="?", default="temp_tests", help="The path to the test file or directory")
    parser.add_argument("--coverage", action="store_true", help="Generate a coverage report")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run in verbose mode")
    args = parser.parse_args()
    
    # Run the tests
    exit_code = run_tests(args.test_path, args.coverage, args.verbose)
    
    # Print a message about the coverage report
    if args.coverage:
        print("\nCoverage report generated in htmlcov/index.html")
    
    sys.exit(exit_code)
    
if __name__ == "__main__":
    main()
