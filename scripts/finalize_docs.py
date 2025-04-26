#!/usr/bin/env python3
"""
Master script to finalize the Sphinx documentation.

This script runs all the enhancement scripts in sequence.
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
    
    print("=== Finalizing Sphinx Documentation ===")
    
    # Run the enhancement scripts
    scripts = [
        "scripts/fix_title_underlines.py",
        "scripts/add_detailed_api_docs.py",
        "scripts/customize_theme.py"
    ]
    
    for script in scripts:
        returncode = run_script(script)
        if returncode != 0:
            print(f"Error running {script}")
            sys.exit(1)
    
    # Build the documentation
    print("\n=== Building Documentation ===\n")
    
    # Set the source and build directories
    source_dir = "docs"
    build_dir = "docs/_build/html"
    
    # Create the build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)
    
    # Build the documentation
    returncode = subprocess.run(
        ["sphinx-build", "-b", "html", source_dir, build_dir],
        check=False,
        env=dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
    ).returncode
    
    if returncode != 0:
        print("Failed to build documentation")
        sys.exit(1)
    
    print(f"\nDocumentation built successfully in {build_dir}")
    print("\n=== Documentation Finalization Complete ===")
    print("To view the documentation, run:")
    print("cd docs/_build/html && python -m http.server 8033")
    print("Then open a browser and navigate to http://localhost:8033")

if __name__ == "__main__":
    main()
