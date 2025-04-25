"""
Test suite utilities.

This module provides utilities for test suites, including a base test suite class
and specialized test suite classes for different types of tests.
"""

import unittest
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, Iterable

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.case import TestCase


@tag("testing.utils")
class TestSuite(unittest.TestSuite):
    """
    Base class for test suites.
    
    This class extends unittest.TestSuite with additional functionality for
    organizing and running tests.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for test suite dependencies
    TODO(Issue #13): Implement test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests)
        self.metadata = metadata or {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test suite.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test suite.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def add_test(self, test: unittest.TestCase) -> None:
        """
        Add a test to the suite.
        
        Args:
            test: The test to add.
        """
        self.addTest(test)
    
    def add_tests(self, tests: Iterable[unittest.TestCase]) -> None:
        """
        Add multiple tests to the suite.
        
        Args:
            tests: The tests to add.
        """
        for test in tests:
            self.addTest(test)
    
    def run(self, result: Optional[unittest.TestResult] = None, debug: bool = False) -> unittest.TestResult:
        """
        Run the tests in the suite.
        
        Args:
            result: The test result to use.
            debug: Whether to run in debug mode.
            
        Returns:
            The test result.
        """
        return super().run(result, debug)


@tag("testing.utils")
class UnitTestSuite(TestSuite):
    """
    Test suite for unit tests.
    
    This class provides a test suite for unit tests, which test individual
    components in isolation.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for unit test suite dependencies
    TODO(Issue #13): Implement unit test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the unit test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests, metadata)
        self.set_metadata("test_type", "unit")


@tag("testing.utils")
class IntegrationTestSuite(TestSuite):
    """
    Test suite for integration tests.
    
    This class provides a test suite for integration tests, which test
    interactions between components.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for integration test suite dependencies
    TODO(Issue #13): Implement integration test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the integration test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests, metadata)
        self.set_metadata("test_type", "integration")


@tag("testing.utils")
class E2ETestSuite(TestSuite):
    """
    Test suite for end-to-end tests.
    
    This class provides a test suite for end-to-end tests, which test
    the entire system.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for end-to-end test suite dependencies
    TODO(Issue #13): Implement end-to-end test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the end-to-end test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests, metadata)
        self.set_metadata("test_type", "e2e")


@tag("testing.utils")
class PerformanceTestSuite(TestSuite):
    """
    Test suite for performance tests.
    
    This class provides a test suite for performance tests, which test
    the performance of the system.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for performance test suite dependencies
    TODO(Issue #13): Implement performance test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the performance test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests, metadata)
        self.set_metadata("test_type", "performance")


@tag("testing.utils")
class StressTestSuite(TestSuite):
    """
    Test suite for stress tests.
    
    This class provides a test suite for stress tests, which test
    the system under heavy load.
    
    Attributes:
        metadata: Additional metadata for the test suite.
    
    TODO(Issue #13): Add support for stress test suite dependencies
    TODO(Issue #13): Implement stress test suite analytics
    """
    
    def __init__(self, tests: Optional[Iterable] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the stress test suite.
        
        Args:
            tests: The tests to add to the suite.
            metadata: Additional metadata for the test suite.
        """
        super().__init__(tests, metadata)
        self.set_metadata("test_type", "stress")
