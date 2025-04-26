#!/usr/bin/env python3
"""
Script to build the Sphinx documentation without Docker.

This script installs the necessary dependencies and builds the documentation.
"""

import os
import sys
import subprocess
from pathlib import Path

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
    """Install the necessary dependencies."""
    dependencies = [
        "sphinx",
        "myst-parser",
        "sphinx-autodoc-typehints",
        "sphinxcontrib-mermaid",
        "sphinx-viewcode",
        "sphinx-copybutton",
        "sphinx-design",
        "sphinx-togglebutton",
        "sphinx-tabs",
        "furo",
        "sphinx-rtd-theme"
    ]
    
    print("Installing dependencies...")
    for dependency in dependencies:
        returncode = run_command(f"pip install {dependency}")
        if returncode != 0:
            print(f"Failed to install {dependency}")
            return False
    
    return True

def build_docs():
    """Build the Sphinx documentation."""
    print("Building documentation...")
    
    # Set the source and build directories
    source_dir = "/workspace/docs"
    build_dir = "/workspace/docs/_build/html"
    
    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)
    
    # Build the documentation
    returncode = run_command(f"sphinx-build -b html {source_dir} {build_dir}")
    if returncode != 0:
        print("Failed to build documentation")
        return False
    
    print(f"\nDocumentation built successfully in {build_dir}")
    return True

def serve_docs():
    """Serve the documentation using Python's built-in HTTP server."""
    print("Serving documentation...")
    
    # Set the build directory
    build_dir = "/workspace/docs/_build/html"
    
    # Serve the documentation
    print(f"Serving documentation at http://localhost:8033")
    print("Press Ctrl+C to stop the server")
    
    # Change to the build directory
    os.chdir(build_dir)
    
    # Start the server
    returncode = run_command("python -m http.server 8033")
    if returncode != 0:
        print("Failed to serve documentation")
        return False
    
    return True

def main():
    """Main function."""
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Build the documentation
    if not build_docs():
        sys.exit(1)
    
    # Serve the documentation
    if not serve_docs():
        sys.exit(1)

if __name__ == "__main__":
    main()
