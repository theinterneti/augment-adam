#!/usr/bin/env python3
"""
Batch Code Quality Checker.

This script runs the code quality checker on multiple Python files and generates
a summary report.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import concurrent.futures

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the code quality checker
from code_quality_checker import CodeQualityChecker


def find_python_files(directory: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
    """
    Find all Python files in a directory and its subdirectories.
    
    Args:
        directory: Directory to search
        exclude_dirs: List of directories to exclude
        
    Returns:
        List of paths to Python files
    """
    if exclude_dirs is None:
        exclude_dirs = []
        
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
                
    return python_files


def check_file(file_path: str, output_dir: Optional[str] = None) -> Tuple[str, int, int]:
    """
    Check a single file and optionally save the report.
    
    Args:
        file_path: Path to the Python file to check
        output_dir: Directory to save the report (optional)
        
    Returns:
        Tuple of (file_path, num_passes, num_issues)
    """
    checker = CodeQualityChecker(file_path)
    passes, issues = checker.check_all()
    
    if output_dir:
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a report file name based on the input file path
        relative_path = os.path.relpath(file_path, Path(__file__).parent.parent)
        report_file = os.path.join(output_dir, f"{relative_path.replace('/', '_').replace('.py', '_report.md')}")
        
        # Save the report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(checker.generate_report())
    
    return file_path, len(passes), len(issues)


def main():
    """Run the batch code quality checker."""
    parser = argparse.ArgumentParser(description="Run code quality checks on multiple files")
    parser.add_argument("--directory", default="src", help="Directory to search for Python files (default: src)")
    parser.add_argument("--exclude", nargs="+", default=["tests", "venv", "env", ".venv", ".env", "build", "dist"], 
                        help="Directories to exclude (default: tests venv env .venv .env build dist)")
    parser.add_argument("--output-dir", help="Directory to save reports (default: don't save)")
    parser.add_argument("--parallel", action="store_true", help="Run checks in parallel")
    parser.add_argument("--summary-only", action="store_true", help="Print only the summary")
    args = parser.parse_args()
    
    # Find all Python files
    python_files = find_python_files(args.directory, args.exclude)
    
    if not python_files:
        print(f"No Python files found in {args.directory}")
        return
        
    print(f"Found {len(python_files)} Python files to check")
    
    # Check all files
    results = []
    
    if args.parallel:
        # Run checks in parallel
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(check_file, file, args.output_dir) for file in python_files]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    else:
        # Run checks sequentially
        for file in python_files:
            results.append(check_file(file, args.output_dir))
    
    # Sort results by number of issues (descending)
    results.sort(key=lambda x: x[2], reverse=True)
    
    # Print results
    if not args.summary_only:
        print("\nResults:")
        print(f"{'File':<60} {'Passes':<10} {'Issues':<10}")
        print("-" * 80)
        
        for file_path, num_passes, num_issues in results:
            relative_path = os.path.relpath(file_path, Path(__file__).parent.parent)
            print(f"{relative_path:<60} {num_passes:<10} {num_issues:<10}")
    
    # Print summary
    total_passes = sum(result[1] for result in results)
    total_issues = sum(result[2] for result in results)
    
    print("\nSummary:")
    print(f"Total files checked: {len(results)}")
    print(f"Total passes: {total_passes}")
    print(f"Total issues: {total_issues}")
    print(f"Average passes per file: {total_passes / len(results):.2f}")
    print(f"Average issues per file: {total_issues / len(results):.2f}")
    
    # Print files with the most issues
    if results:
        print("\nFiles with the most issues:")
        for file_path, num_passes, num_issues in results[:5]:
            relative_path = os.path.relpath(file_path, Path(__file__).parent.parent)
            print(f"{relative_path}: {num_issues} issues")
    
    if args.output_dir:
        print(f"\nReports saved to {args.output_dir}")


if __name__ == "__main__":
    main()
