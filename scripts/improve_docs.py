#!/usr/bin/env python3
"""
Master script to improve the Sphinx documentation.

This script runs all the improvement scripts in sequence.
"""

import os
import sys
import subprocess
import locale

def run_script(script_path):
    """Run a script and print the output."""
    print(f"\n=== Running {script_path} ===\n")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    # Run the script
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    
    if stderr:
        print(stderr)
    
    return process.returncode

def main():
    """Main function."""
    # Set locale to C (minimal locale)
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C')
        except locale.Error:
            print("Warning: Could not set locale. Some features may not work correctly.")
    
    # Set environment variables for locale
    os.environ['LC_ALL'] = 'C.UTF-8'
    os.environ['LANG'] = 'C.UTF-8'
    
    print("=== Improving Sphinx Documentation ===")
    
    # Run the improvement scripts
    scripts = [
        "scripts/improve_sphinx_structure.py",
        "scripts/fix_sphinx_warnings.py",
        "scripts/add_sphinx_diagrams.py",
        "scripts/build_sphinx_docs.py"
    ]
    
    for script in scripts:
        returncode = run_script(script)
        if returncode != 0:
            print(f"Error running {script}")
            sys.exit(1)
    
    print("\n=== Documentation Improvement Complete ===")
    print("To view the documentation, run:")
    print("python -m http.server 8033 --directory docs/_build/html")

if __name__ == "__main__":
    main()
