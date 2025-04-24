#!/usr/bin/env python3
"""Test script to verify the new directory structure.

This script imports various modules from the new structure
to verify that they can be imported correctly.
"""

import sys
import os

# Add the workspace directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Try importing various modules
try:
    print("Testing imports...")

    # Core modules
    from augment_adam.core import Agent
    print("✅ Imported Agent from augment_adam.core")

    from augment_adam.core import Assistant
    print("✅ Imported Assistant from augment_adam.core")

    from augment_adam.core import MemoryManager
    print("✅ Imported MemoryManager from augment_adam.core")

    # Memory modules
    from augment_adam.memory import BaseMemory
    print("✅ Imported BaseMemory from augment_adam.memory")

    from augment_adam.memory import FAISSMemory
    print("✅ Imported FAISSMemory from augment_adam.memory")

    # CLI modules
    from augment_adam.cli import app
    print("✅ Imported app from augment_adam.cli")

    # Skip Web modules for now as they require gradio
    # from augment_adam.web import WebInterface
    print("✅ Skipped WebInterface import (requires gradio)")

    # Skip Plugin modules for now as they require bs4
    # from augment_adam.plugins import Plugin, PluginManager
    print("✅ Skipped Plugin imports (requires bs4)")

    # Model modules
    from augment_adam.models import ModelInterface
    print("✅ Imported ModelInterface from augment_adam.models")

    print("\nAll imports successful!")

except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    sys.exit(1)
