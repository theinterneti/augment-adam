#!/usr/bin/env python
"""
Test script to verify that augment-adam can be installed and imported correctly.
"""

import sys
import importlib.util
from importlib.metadata import version, PackageNotFoundError

def check_package_installed(package_name):
    """Check if a package is installed."""
    try:
        version_str = version(package_name)
        print(f"✅ {package_name} is installed (version: {version_str})")
        return True
    except PackageNotFoundError:
        print(f"❌ {package_name} is not installed")
        return False

def check_module_imports(module_paths):
    """Check if modules can be imported."""
    success = True
    for module_path in module_paths:
        try:
            importlib.import_module(module_path)
            print(f"✅ Successfully imported {module_path}")
        except ImportError as e:
            print(f"❌ Failed to import {module_path}: {e}")
            success = False
    return success

def main():
    """Main function to test installation and imports."""
    print("Testing augment-adam installation and imports...")
    print("-" * 50)
    
    # Check if the package is installed
    package_installed = check_package_installed("augment-adam")
    
    # List of core modules to test importing
    core_modules = [
        "augment_adam",
        "augment_adam.core",
        "augment_adam.memory",
        "augment_adam.models",
        "augment_adam.plugins",
        "augment_adam.cli",
        "augment_adam.web",
        "augment_adam.context_engine",
        "augment_adam.ai_agent",
        "augment_adam.utils"
    ]
    
    # Check imports only if the package is installed
    if package_installed:
        print("\nTesting core module imports:")
        print("-" * 50)
        imports_success = check_module_imports(core_modules)
        
        # Try to create some basic objects
        print("\nTesting object creation:")
        print("-" * 50)
        try:
            from augment_adam.memory import FAISSMemory
            memory = FAISSMemory()
            print("✅ Successfully created FAISSMemory instance")
            
            from augment_adam.core import Assistant
            assistant = Assistant(memory=memory)
            print("✅ Successfully created Assistant instance")
        except Exception as e:
            print(f"❌ Failed to create objects: {e}")
            imports_success = False
        
        if imports_success:
            print("\n✅ All tests passed! augment-adam is correctly installed and working.")
            return 0
    
    print("\n❌ Some tests failed. Please check the output above for details.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
