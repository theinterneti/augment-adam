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
        "sphinx-copybutton",
        "sphinx-design",
        "sphinx-togglebutton",
        "sphinx-tabs",
        "furo",
        "sphinx-rtd-theme"
    ]

    # Special handling for sphinx-viewcode
    special_dependencies = {
        "sphinx-viewcode": "sphinx.ext.viewcode"  # This is actually a built-in Sphinx extension
    }

    print("Installing dependencies...")
    for dependency in dependencies:
        returncode = run_command(f"pip install {dependency}")
        if returncode != 0:
            print(f"Failed to install {dependency}")
            return False

    # Check if special dependencies are available
    for package, module in special_dependencies.items():
        try:
            __import__(module)
            print(f"{package} is available (as {module})")
        except ImportError:
            print(f"Warning: {package} ({module}) is not available. Some features may not work.")

    return True

def build_docs():
    """Build the Sphinx documentation."""
    print("Building documentation...")

    # Set the source and build directories
    source_dir = "/workspace/docs"
    build_dir = "/workspace/docs/_build/html"

    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)

    # Build the documentation with verbose output
    returncode = run_command(f"sphinx-build -b html -v {source_dir} {build_dir}")
    if returncode != 0:
        print("Failed to build documentation")

        # Check if conf.py exists
        if not os.path.exists(os.path.join(source_dir, "conf.py")):
            print(f"Error: conf.py not found in {source_dir}")
            print("Copying conf.py from /workspace/dev/sphinx/conf.py")
            run_command(f"cp /workspace/dev/sphinx/conf.py {source_dir}/")

        # Try building again
        print("Trying to build again...")
        returncode = run_command(f"sphinx-build -b html -v {source_dir} {build_dir}")
        if returncode != 0:
            print("Failed to build documentation again")
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
        print("Warning: Some dependencies could not be installed.")
        print("Continuing with documentation build...")

    # Build the documentation
    if not build_docs():
        print("Error: Documentation build failed.")
        sys.exit(1)

    # Print success message
    print("\nDocumentation build completed successfully!")
    print("To view the documentation, run:")
    print("python -m http.server 8033 --directory /workspace/docs/_build/html")

if __name__ == "__main__":
    main()
