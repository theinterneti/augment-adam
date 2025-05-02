#!/usr/bin/env python3
"""
Coverage Report Generator for Augment Adam.

This script generates a coverage report for the Augment Adam project.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional, Set, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


def generate_coverage_report(test_paths: List[str], 
                            output_dir: str = "coverage_html",
                            source_dirs: List[str] = None,
                            omit_patterns: List[str] = None,
                            verbose: bool = False) -> bool:
    """
    Generate a coverage report for the specified test paths.
    
    Args:
        test_paths: Paths to test files or directories
        output_dir: Directory to save the HTML report
        source_dirs: Directories to measure coverage for
        omit_patterns: Patterns of files to omit from coverage
        verbose: Whether to use verbose output
        
    Returns:
        True if the coverage report was generated successfully, False otherwise
    """
    if not COVERAGE_AVAILABLE:
        print("Error: coverage is not installed. Please install it with 'pip install coverage'.")
        return False
    
    if not PYTEST_AVAILABLE:
        print("Error: pytest is not installed. Please install it with 'pip install pytest'.")
        return False
    
    # Set default source directories if not provided
    if source_dirs is None:
        source_dirs = ["src/augment_adam", "augment_adam"]
    
    # Set default omit patterns if not provided
    if omit_patterns is None:
        omit_patterns = [
            "*/test_*.py",
            "*/tests/*",
            "*/conftest.py",
            "*/__pycache__/*",
            "*/setup.py",
        ]
    
    # Create a coverage configuration
    cov = coverage.Coverage(
        source=source_dirs,
        omit=omit_patterns,
        branch=True,
    )
    
    # Start measuring coverage
    cov.start()
    
    # Build the pytest command
    args = []
    
    # Add verbosity
    if verbose:
        args.append("-v")
    
    # Add test paths
    args.extend(test_paths)
    
    # Run pytest
    result = pytest.main(args)
    
    # Stop measuring coverage
    cov.stop()
    
    # Save coverage data
    cov.save()
    
    # Generate a text report
    print("\nCoverage Report:")
    cov.report()
    
    # Generate an HTML report
    print(f"\nGenerating HTML report in {output_dir}...")
    cov.html_report(directory=output_dir)
    
    # Generate an XML report for CI/CD integration
    xml_output = os.path.join(os.path.dirname(output_dir), "coverage.xml")
    print(f"Generating XML report in {xml_output}...")
    cov.xml_report(outfile=xml_output)
    
    print(f"\nCoverage reports generated successfully.")
    print(f"HTML report: {os.path.abspath(output_dir)}/index.html")
    print(f"XML report: {os.path.abspath(xml_output)}")
    
    return result == 0


def generate_badge(coverage_percentage: float, output_file: str = "coverage-badge.svg") -> bool:
    """
    Generate a coverage badge.
    
    Args:
        coverage_percentage: Coverage percentage
        output_file: Output file path
        
    Returns:
        True if the badge was generated successfully, False otherwise
    """
    try:
        import anybadge
    except ImportError:
        print("Error: anybadge is not installed. Please install it with 'pip install anybadge'.")
        return False
    
    # Define thresholds for badge colors
    thresholds = {
        50: 'red',
        60: 'orange',
        70: 'yellow',
        80: 'yellowgreen',
        90: 'green',
        100: 'brightgreen',
    }
    
    # Create the badge
    badge = anybadge.Badge(
        label='coverage',
        value=f"{coverage_percentage:.1f}%",
        thresholds=thresholds,
    )
    
    # Save the badge
    badge.write_badge(output_file)
    
    print(f"Coverage badge generated: {os.path.abspath(output_file)}")
    
    return True


def extract_coverage_percentage(coverage_file: str = ".coverage") -> Optional[float]:
    """
    Extract the coverage percentage from a coverage file.
    
    Args:
        coverage_file: Path to the coverage file
        
    Returns:
        Coverage percentage or None if it couldn't be extracted
    """
    if not COVERAGE_AVAILABLE:
        print("Error: coverage is not installed. Please install it with 'pip install coverage'.")
        return None
    
    if not os.path.exists(coverage_file):
        print(f"Error: Coverage file {coverage_file} not found.")
        return None
    
    try:
        # Load the coverage data
        cov = coverage.Coverage()
        cov.load()
        
        # Get the coverage percentage
        total_statements = 0
        covered_statements = 0
        
        for filename in cov.get_data().measured_files():
            # Skip files that are not in the source directories
            if not any(filename.startswith(src) for src in ["src/augment_adam", "augment_adam"]):
                continue
            
            # Get the coverage data for the file
            file_data = cov.get_data().lines(filename)
            
            if file_data is None:
                continue
            
            # Count the total and covered statements
            analysis = cov._analyze(filename)
            total_statements += len(analysis.statements)
            covered_statements += len(analysis.statements) - len(analysis.missing)
        
        # Calculate the coverage percentage
        if total_statements == 0:
            return 0.0
        
        return (covered_statements / total_statements) * 100
    
    except Exception as e:
        print(f"Error extracting coverage percentage: {e}")
        return None


def main():
    """Parse arguments and generate coverage report."""
    parser = argparse.ArgumentParser(description="Generate a coverage report for Augment Adam")
    
    # Test selection options
    test_selection = parser.add_argument_group("Test Selection")
    test_selection.add_argument("--unit", action="store_true", help="Run unit tests")
    test_selection.add_argument("--integration", action="store_true", help="Run integration tests")
    test_selection.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    test_selection.add_argument("--all", action="store_true", help="Run all tests")
    test_selection.add_argument("--path", nargs="+", help="Run tests at specific path(s)")
    
    # Coverage options
    coverage_options = parser.add_argument_group("Coverage Options")
    coverage_options.add_argument("--source", nargs="+", default=None,
                                help="Source directories to measure coverage for")
    coverage_options.add_argument("--omit", nargs="+", default=None,
                                help="Patterns of files to omit from coverage")
    coverage_options.add_argument("--output-dir", default="coverage_html",
                                help="Directory to save the HTML report")
    
    # Output options
    output_options = parser.add_argument_group("Output Options")
    output_options.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    output_options.add_argument("--badge", action="store_true", help="Generate a coverage badge")
    output_options.add_argument("--badge-file", default="coverage-badge.svg",
                              help="Output file for the coverage badge")
    
    args = parser.parse_args()
    
    # Check if coverage is available
    if not COVERAGE_AVAILABLE:
        print("Error: coverage is not installed. Please install it with 'pip install coverage'.")
        return 1
    
    # Determine which tests to run
    test_paths = []
    
    if args.unit or args.all:
        test_paths.append("tests/unit")
    
    if args.integration or args.all:
        test_paths.append("tests/integration")
    
    if args.e2e or args.all:
        test_paths.append("tests/e2e")
    
    # If specific paths are provided, use those instead
    if args.path:
        test_paths = args.path
    
    # If no test paths are specified, run all tests
    if not test_paths:
        test_paths = ["tests"]
    
    # Generate the coverage report
    success = generate_coverage_report(
        test_paths=test_paths,
        output_dir=args.output_dir,
        source_dirs=args.source,
        omit_patterns=args.omit,
        verbose=args.verbose,
    )
    
    # Generate a coverage badge if requested
    if args.badge:
        coverage_percentage = extract_coverage_percentage()
        
        if coverage_percentage is not None:
            generate_badge(coverage_percentage, args.badge_file)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
