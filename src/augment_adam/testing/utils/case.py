"""
Test case utilities.

This module provides utilities for test cases, including a base test case class
and specialized test case classes for different types of tests.
"""

import unittest
import pytest
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("testing.utils")
class TestCase(unittest.TestCase):
    """
    Base class for test cases.
    
    This class extends unittest.TestCase with additional functionality for
    testing Augment Adam components.
    
    Attributes:
        metadata: Additional metadata for the test case.
    
    TODO(Issue #13): Add support for test case dependencies
    TODO(Issue #13): Implement test case analytics
    """
    
    def __init__(self, methodName: str = "runTest", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the test case.
        
        Args:
            methodName: The name of the test method to run.
            metadata: Additional metadata for the test case.
        """
        super().__init__(methodName)
        self.metadata = metadata or {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test case.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test case.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def assertDictContains(self, expected: Dict[str, Any], actual: Dict[str, Any], msg: Optional[str] = None) -> None:
        """
        Assert that a dictionary contains all the key-value pairs in another dictionary.
        
        Args:
            expected: The expected dictionary.
            actual: The actual dictionary.
            msg: Optional message to use on failure.
        """
        for key, value in expected.items():
            self.assertIn(key, actual, msg=msg)
            self.assertEqual(value, actual[key], msg=msg)
    
    def assertListContains(self, expected: List[Any], actual: List[Any], msg: Optional[str] = None) -> None:
        """
        Assert that a list contains all the elements in another list.
        
        Args:
            expected: The expected list.
            actual: The actual list.
            msg: Optional message to use on failure.
        """
        for item in expected:
            self.assertIn(item, actual, msg=msg)
    
    def assertAlmostEqualDict(self, expected: Dict[str, Any], actual: Dict[str, Any], places: int = 7, msg: Optional[str] = None) -> None:
        """
        Assert that two dictionaries are almost equal.
        
        Args:
            expected: The expected dictionary.
            actual: The actual dictionary.
            places: The number of decimal places to compare.
            msg: Optional message to use on failure.
        """
        self.assertEqual(set(expected.keys()), set(actual.keys()), msg=msg)
        
        for key in expected:
            if isinstance(expected[key], (int, float)) and isinstance(actual[key], (int, float)):
                self.assertAlmostEqual(expected[key], actual[key], places=places, msg=msg)
            else:
                self.assertEqual(expected[key], actual[key], msg=msg)
    
    def assertAlmostEqualList(self, expected: List[Any], actual: List[Any], places: int = 7, msg: Optional[str] = None) -> None:
        """
        Assert that two lists are almost equal.
        
        Args:
            expected: The expected list.
            actual: The actual list.
            places: The number of decimal places to compare.
            msg: Optional message to use on failure.
        """
        self.assertEqual(len(expected), len(actual), msg=msg)
        
        for i in range(len(expected)):
            if isinstance(expected[i], (int, float)) and isinstance(actual[i], (int, float)):
                self.assertAlmostEqual(expected[i], actual[i], places=places, msg=msg)
            else:
                self.assertEqual(expected[i], actual[i], msg=msg)
    
    def assertRaises(self, expected_exception: Type[Exception], *args: Any, **kwargs: Any) -> Any:
        """
        Assert that a function call raises an exception.
        
        Args:
            expected_exception: The expected exception.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            A context manager for the assertion.
        """
        return super().assertRaises(expected_exception, *args, **kwargs)
    
    def assertRaisesRegex(self, expected_exception: Type[Exception], expected_regex: str, *args: Any, **kwargs: Any) -> Any:
        """
        Assert that a function call raises an exception with a message matching a regular expression.
        
        Args:
            expected_exception: The expected exception.
            expected_regex: The regular expression to match against the exception message.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            A context manager for the assertion.
        """
        return super().assertRaisesRegex(expected_exception, expected_regex, *args, **kwargs)
    
    def assertLogs(self, logger: Optional[str] = None, level: Optional[str] = None) -> Any:
        """
        Assert that logs are emitted.
        
        Args:
            logger: The logger to check.
            level: The minimum level to check.
            
        Returns:
            A context manager for the assertion.
        """
        return super().assertLogs(logger, level)
    
    def assertWarns(self, expected_warning: Type[Warning], *args: Any, **kwargs: Any) -> Any:
        """
        Assert that a function call emits a warning.
        
        Args:
            expected_warning: The expected warning.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            A context manager for the assertion.
        """
        return super().assertWarns(expected_warning, *args, **kwargs)
    
    def assertWarnsRegex(self, expected_warning: Type[Warning], expected_regex: str, *args: Any, **kwargs: Any) -> Any:
        """
        Assert that a function call emits a warning with a message matching a regular expression.
        
        Args:
            expected_warning: The expected warning.
            expected_regex: The regular expression to match against the warning message.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            A context manager for the assertion.
        """
        return super().assertWarnsRegex(expected_warning, expected_regex, *args, **kwargs)


@tag("testing.utils")
class AsyncTestCase(TestCase):
    """
    Base class for asynchronous test cases.
    
    This class extends TestCase with additional functionality for
    testing asynchronous code.
    
    Attributes:
        metadata: Additional metadata for the test case.
    
    TODO(Issue #13): Add support for async test case dependencies
    TODO(Issue #13): Implement async test case analytics
    """
    
    async def asyncSetUp(self) -> None:
        """Set up the test case asynchronously."""
        pass
    
    async def asyncTearDown(self) -> None:
        """Tear down the test case asynchronously."""
        pass
    
    def setUp(self) -> None:
        """Set up the test case."""
        import asyncio
        
        # Run asyncSetUp
        asyncio.run(self.asyncSetUp())
    
    def tearDown(self) -> None:
        """Tear down the test case."""
        import asyncio
        
        # Run asyncTearDown
        asyncio.run(self.asyncTearDown())
    
    async def assertAsyncRaises(self, expected_exception: Type[Exception], coro: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Assert that an asynchronous function call raises an exception.
        
        Args:
            expected_exception: The expected exception.
            coro: The coroutine function to call.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        with self.assertRaises(expected_exception):
            await coro(*args, **kwargs)
    
    async def assertAsyncRaisesRegex(self, expected_exception: Type[Exception], expected_regex: str, coro: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """
        Assert that an asynchronous function call raises an exception with a message matching a regular expression.
        
        Args:
            expected_exception: The expected exception.
            expected_regex: The regular expression to match against the exception message.
            coro: The coroutine function to call.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        with self.assertRaisesRegex(expected_exception, expected_regex):
            await coro(*args, **kwargs)


@tag("testing.utils")
class PytestCase:
    """
    Base class for pytest test cases.
    
    This class provides a base for pytest test cases with additional functionality
    for testing Augment Adam components.
    
    Attributes:
        metadata: Additional metadata for the test case.
    
    TODO(Issue #13): Add support for pytest test case dependencies
    TODO(Issue #13): Implement pytest test case analytics
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the pytest test case.
        
        Args:
            metadata: Additional metadata for the test case.
        """
        self.metadata = metadata or {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test case.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test case.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def setup_method(self, method: Callable) -> None:
        """
        Set up the test method.
        
        Args:
            method: The test method to set up.
        """
        pass
    
    def teardown_method(self, method: Callable) -> None:
        """
        Tear down the test method.
        
        Args:
            method: The test method to tear down.
        """
        pass
    
    @classmethod
    def setup_class(cls) -> None:
        """Set up the test class."""
        pass
    
    @classmethod
    def teardown_class(cls) -> None:
        """Tear down the test class."""
        pass
