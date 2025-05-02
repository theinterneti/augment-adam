"""
Test Helpers for Augment Adam.

This module provides helper functions and utilities for writing tests.
"""

import os
import sys
import time
import inspect
import unittest
import tempfile
import functools
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

import pytest
from unittest.mock import MagicMock, patch


def skip_if_no_module(module_name: str) -> Callable:
    """
    Skip a test if a module is not available.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        Decorator function
    """
    try:
        __import__(module_name)
        skip = False
    except ImportError:
        skip = True
    
    return pytest.mark.skipif(
        skip, reason=f"Module {module_name} not available"
    )


def skip_if_no_env_var(env_var: str) -> Callable:
    """
    Skip a test if an environment variable is not set.
    
    Args:
        env_var: Name of the environment variable to check
        
    Returns:
        Decorator function
    """
    return pytest.mark.skipif(
        env_var not in os.environ,
        reason=f"Environment variable {env_var} not set"
    )


def timed(func: Callable) -> Callable:
    """
    Decorator to time a test function.
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f}s")
        return result
    return wrapper


def create_temp_file(content: str = "", suffix: str = ".txt") -> Path:
    """
    Create a temporary file with the given content.
    
    Args:
        content: Content to write to the file
        suffix: File suffix
        
    Returns:
        Path to the temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    
    with open(path, "w") as f:
        f.write(content)
    
    return Path(path)


def create_temp_dir() -> Path:
    """
    Create a temporary directory.
    
    Returns:
        Path to the temporary directory
    """
    return Path(tempfile.mkdtemp())


def assert_dict_subset(test_case: unittest.TestCase, subset: Dict, superset: Dict) -> None:
    """
    Assert that a dictionary is a subset of another dictionary.
    
    Args:
        test_case: TestCase instance
        subset: Dictionary that should be a subset
        superset: Dictionary that should be a superset
    """
    for key, value in subset.items():
        test_case.assertIn(key, superset)
        test_case.assertEqual(value, superset[key])


def assert_lists_equal_unordered(test_case: unittest.TestCase, 
                                list1: List, list2: List) -> None:
    """
    Assert that two lists contain the same elements, regardless of order.
    
    Args:
        test_case: TestCase instance
        list1: First list
        list2: Second list
    """
    test_case.assertEqual(sorted(list1), sorted(list2))


def assert_approx_equal(test_case: unittest.TestCase, 
                       value1: float, value2: float, 
                       tolerance: float = 1e-6) -> None:
    """
    Assert that two values are approximately equal.
    
    Args:
        test_case: TestCase instance
        value1: First value
        value2: Second value
        tolerance: Tolerance for equality
    """
    test_case.assertTrue(
        abs(value1 - value2) < tolerance,
        f"{value1} and {value2} differ by more than {tolerance}"
    )


def mock_async_return(return_value: Any) -> MagicMock:
    """
    Create a mock for an async function that returns a value.
    
    Args:
        return_value: Value to return
        
    Returns:
        Mock object
    """
    mock = MagicMock()
    
    async def async_magic():
        return return_value
    
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    mock.__await__ = lambda: async_magic().__await__()
    
    return mock


def mock_async_side_effect(side_effect: Callable) -> MagicMock:
    """
    Create a mock for an async function with a side effect.
    
    Args:
        side_effect: Side effect function
        
    Returns:
        Mock object
    """
    mock = MagicMock()
    
    async def async_magic(*args, **kwargs):
        return side_effect(*args, **kwargs)
    
    mock.__aenter__.return_value = mock
    mock.__aexit__.return_value = None
    mock.__await__ = lambda *args, **kwargs: async_magic(*args, **kwargs).__await__()
    
    return mock


class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    
    def run_async(self, coro):
        """
        Run an async coroutine in the test.
        
        Args:
            coro: Coroutine to run
            
        Returns:
            Result of the coroutine
        """
        import asyncio
        
        # Get the current event loop or create a new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the coroutine
        return loop.run_until_complete(coro)


class MemoryLeakTestCase(unittest.TestCase):
    """Base class for memory leak test cases."""
    
    def setUp(self):
        """Set up the test case."""
        import gc
        import psutil
        
        self.process = psutil.Process()
        gc.collect()
        self.memory_before = self.process.memory_info().rss
    
    def tearDown(self):
        """Tear down the test case."""
        import gc
        import psutil
        
        gc.collect()
        memory_after = self.process.memory_info().rss
        memory_diff = memory_after - self.memory_before
        
        print(f"Memory usage: {memory_diff / 1024 / 1024:.2f} MB")
        
        # Assert that memory usage hasn't increased significantly
        # This is a rough check and may need adjustment
        self.assertLess(memory_diff, 10 * 1024 * 1024)  # 10 MB


class PerformanceTestCase(unittest.TestCase):
    """Base class for performance test cases."""
    
    def setUp(self):
        """Set up the test case."""
        self.start_time = time.time()
    
    def tearDown(self):
        """Tear down the test case."""
        end_time = time.time()
        elapsed = end_time - self.start_time
        
        print(f"Test took {elapsed:.2f}s")
        
        # Get the test method name
        test_method = getattr(self, self._testMethodName)
        
        # Check if the test method has a time limit
        time_limit = getattr(test_method, "time_limit", None)
        
        if time_limit is not None:
            self.assertLess(elapsed, time_limit)


def time_limit(seconds: float) -> Callable:
    """
    Decorator to set a time limit for a performance test.
    
    Args:
        seconds: Time limit in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        func.time_limit = seconds
        return func
    return decorator
