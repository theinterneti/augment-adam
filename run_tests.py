#!/usr/bin/env python3
"""
Run all tests for the model management system.

This script runs all unit tests and integration tests for the model management system.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent))


def run_tests():
    """Run all tests."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
