#!/usr/bin/env python3
"""
Script to build the Sphinx documentation with locale handling.
"""

import os
import sys
import subprocess
import locale

def run_command(command):
    """Run a command and print the output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    
    if stderr:
        print(stderr)
    
    return process.returncode

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Install required packages
    dependencies = [
        "sphinx",
        "myst-parser",
        "sphinx-rtd-theme",
        "sphinxcontrib-mermaid"
    ]
    
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        run_command(f"pip install {dependency}")

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
    
    # Install dependencies
    install_dependencies()
    
    # Build the documentation
    print("Building documentation...")
    
    # Set the source and build directories
    source_dir = "docs"
    build_dir = "docs/_build/html"
    
    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)
    
    # Build the documentation
    returncode = run_command(f"cd {source_dir} && sphinx-build -b html . _build/html")
    if returncode != 0:
        print("Failed to build documentation")
        sys.exit(1)
    
    print(f"\nDocumentation built successfully in {build_dir}")
    print("To view the documentation, run:")
    print("cd docs/_build/html && python -m http.server 8033")

if __name__ == "__main__":
    main()
