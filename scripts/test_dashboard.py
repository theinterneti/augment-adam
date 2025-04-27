#!/usr/bin/env python
"""
Test Dashboard for Augment Adam.

This script generates a dashboard of test coverage and test results.
It can be used to track test coverage over time and identify areas
that need more testing.
"""

import os
import sys
import json
import argparse
import subprocess
import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

def run_tests_with_coverage():
    """
    Run tests with coverage and return the coverage data.
    
    Returns:
        The coverage data as a dictionary.
    """
    # Run tests with coverage
    subprocess.run([
        "python", "scripts/run_all_tests.py",
        "--xml",
        "--no-html"
    ])
    
    # Parse the coverage XML file
    if not os.path.exists("coverage.xml"):
        print("Error: coverage.xml not found. Tests may have failed.")
        return None
    
    tree = ET.parse("coverage.xml")
    root = tree.getroot()
    
    # Extract coverage data
    coverage_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall": float(root.attrib.get("line-rate", 0)) * 100,
        "modules": {}
    }
    
    # Extract module-level coverage
    for package in root.findall(".//package"):
        package_name = package.attrib.get("name", "")
        
        for module in package.findall("./classes/class"):
            module_name = module.attrib.get("name", "")
            line_rate = float(module.attrib.get("line-rate", 0)) * 100
            
            # Skip empty modules
            if line_rate == 0:
                continue
            
            full_name = f"{package_name}.{module_name}" if package_name else module_name
            coverage_data["modules"][full_name] = line_rate
    
    return coverage_data

def save_coverage_history(coverage_data):
    """
    Save coverage data to the history file.
    
    Args:
        coverage_data: The coverage data to save.
    """
    history_file = "test_coverage_history.json"
    
    # Load existing history
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []
    
    # Add new data
    history.append(coverage_data)
    
    # Save history
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def generate_coverage_report(history_file="test_coverage_history.json"):
    """
    Generate a coverage report from the history file.
    
    Args:
        history_file: The path to the history file.
    """
    if not os.path.exists(history_file):
        print(f"Error: {history_file} not found. Run tests first.")
        return
    
    # Load history
    with open(history_file, "r") as f:
        history = json.load(f)
    
    if not history:
        print("Error: No coverage data found in history file.")
        return
    
    # Extract data for plotting
    timestamps = [entry["timestamp"] for entry in history]
    overall_coverage = [entry["overall"] for entry in history]
    
    # Convert timestamps to datetime objects
    dates = [datetime.datetime.fromisoformat(ts).strftime("%Y-%m-%d") for ts in timestamps]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(dates, overall_coverage, marker='o', linestyle='-', linewidth=2)
    plt.title("Test Coverage Over Time")
    plt.xlabel("Date")
    plt.ylabel("Coverage (%)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig("coverage_trend.png")
    print("Coverage trend saved to coverage_trend.png")
    
    # Get the latest coverage data
    latest = history[-1]
    
    # Sort modules by coverage
    sorted_modules = sorted(
        latest["modules"].items(),
        key=lambda x: x[1]
    )
    
    # Print the report
    print("\nTest Coverage Report")
    print("===================")
    print(f"Overall Coverage: {latest['overall']:.2f}%")
    print(f"Date: {datetime.datetime.fromisoformat(latest['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nModule Coverage:")
    
    for module, coverage in sorted_modules:
        print(f"  {module}: {coverage:.2f}%")
    
    # Create a bar chart of module coverage
    if sorted_modules:
        modules, coverages = zip(*sorted_modules[-20:])  # Get the top 20 modules
        
        plt.figure(figsize=(12, 8))
        y_pos = np.arange(len(modules))
        
        plt.barh(y_pos, coverages, align='center')
        plt.yticks(y_pos, modules)
        plt.xlabel('Coverage (%)')
        plt.title('Module Coverage')
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot
        plt.savefig("module_coverage.png")
        print("Module coverage saved to module_coverage.png")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Dashboard for Augment Adam")
    parser.add_argument("--run-tests", action="store_true", help="Run tests and update coverage data")
    parser.add_argument("--report", action="store_true", help="Generate a coverage report")
    args = parser.parse_args()
    
    if args.run_tests:
        coverage_data = run_tests_with_coverage()
        if coverage_data:
            save_coverage_history(coverage_data)
            print("Coverage data saved to test_coverage_history.json")
    
    if args.report or not args.run_tests:
        generate_coverage_report()

if __name__ == "__main__":
    main()
