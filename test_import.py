#!/usr/bin/env python3
"""
Test script to verify that the augment-adam package is properly installed.
"""

try:
    import augment_adam
    print(f"Successfully imported augment_adam package (version: {augment_adam.__version__})")
except ImportError as e:
    print(f"Failed to import augment_adam package: {e}")
