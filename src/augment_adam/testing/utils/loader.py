"""
Test loader utilities.

This module provides utilities for test loaders, including a base test loader class
and specialized test loader classes for different types of tests.
"""

import os
import unittest
import importlib
import inspect
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.case import TestCase
from augment_adam.testing.utils.suite import TestSuite, UnitTestSuite, IntegrationTestSuite, E2ETestSuite


@tag("testing.utils")
class TestLoader(unittest.TestLoader):
    """
    Base class for test loaders.
    
    This class extends unittest.TestLoader with additional functionality for
    loading tests.
    
    Attributes:
        metadata: Additional metadata for the test loader.
        suite_class: The class to use for test suites.
    
    TODO(Issue #13): Add support for test loader dependencies
    TODO(Issue #13): Implement test loader analytics
    """
    
    def __init__(
        self,
        suite_class: Optional[Type[TestSuite]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the test loader.
        
        Args:
            suite_class: The class to use for test suites.
            metadata: Additional metadata for the test loader.
        """
        super().__init__()
        self.suite_class = suite_class or TestSuite
        self.metadata = metadata or {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test loader.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test loader.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def loadTestsFromTestCase(self, testCaseClass: Type[unittest.TestCase]) -> TestSuite:
        """
        Load tests from a test case class.
        
        Args:
            testCaseClass: The test case class to load tests from.
            
        Returns:
            A test suite containing the tests.
        """
        # Get the test method names
        test_method_names = self.getTestCaseNames(testCaseClass)
        
        # Create a test suite
        suite = self.suite_class()
        
        # Add the tests to the suite
        for test_method_name in test_method_names:
            suite.addTest(testCaseClass(test_method_name))
        
        return suite
    
    def loadTestsFromModule(self, module: Any, pattern: Optional[str] = None) -> TestSuite:
        """
        Load tests from a module.
        
        Args:
            module: The module to load tests from.
            pattern: A pattern to match test names against.
            
        Returns:
            A test suite containing the tests.
        """
        # Create a test suite
        suite = self.suite_class()
        
        # Get the test case classes
        for name in dir(module):
            obj = getattr(module, name)
            
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj.__module__ == module.__name__:
                # Load tests from the test case class
                tests = self.loadTestsFromTestCase(obj)
                
                # Add the tests to the suite
                suite.addTest(tests)
        
        return suite
    
    def loadTestsFromName(self, name: str, module: Optional[Any] = None) -> TestSuite:
        """
        Load tests from a name.
        
        Args:
            name: The name to load tests from.
            module: The module to load tests from.
            
        Returns:
            A test suite containing the tests.
        """
        # Create a test suite
        suite = self.suite_class()
        
        # Split the name into parts
        parts = name.split(".")
        
        # Get the module
        if module is None:
            # Import the module
            module_name = parts[0]
            module = importlib.import_module(module_name)
            parts = parts[1:]
        
        # Get the object
        obj = module
        
        for part in parts:
            obj = getattr(obj, part)
        
        # Load tests from the object
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            # Load tests from the test case class
            tests = self.loadTestsFromTestCase(obj)
            
            # Add the tests to the suite
            suite.addTest(tests)
        elif isinstance(obj, unittest.TestCase):
            # Add the test to the suite
            suite.addTest(obj)
        elif inspect.isfunction(obj) and obj.__name__.startswith("test"):
            # Create a test case class
            class TestClass(unittest.TestCase):
                pass
            
            # Add the test method to the test case class
            setattr(TestClass, obj.__name__, obj)
            
            # Load tests from the test case class
            tests = self.loadTestsFromTestCase(TestClass)
            
            # Add the tests to the suite
            suite.addTest(tests)
        elif inspect.ismodule(obj):
            # Load tests from the module
            tests = self.loadTestsFromModule(obj)
            
            # Add the tests to the suite
            suite.addTest(tests)
        
        return suite
    
    def loadTestsFromNames(self, names: List[str], module: Optional[Any] = None) -> TestSuite:
        """
        Load tests from names.
        
        Args:
            names: The names to load tests from.
            module: The module to load tests from.
            
        Returns:
            A test suite containing the tests.
        """
        # Create a test suite
        suite = self.suite_class()
        
        # Load tests from each name
        for name in names:
            # Load tests from the name
            tests = self.loadTestsFromName(name, module)
            
            # Add the tests to the suite
            suite.addTest(tests)
        
        return suite
    
    def loadTestsFromDirectory(self, directory: str, pattern: str = "test_*.py") -> TestSuite:
        """
        Load tests from a directory.
        
        Args:
            directory: The directory to load tests from.
            pattern: A pattern to match test file names against.
            
        Returns:
            A test suite containing the tests.
        """
        # Create a test suite
        suite = self.suite_class()
        
        # Get the test files
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if the file matches the pattern
                if not file.endswith(".py") or not file.startswith("test_"):
                    continue
                
                # Get the module name
                module_name = os.path.splitext(file)[0]
                
                # Get the module path
                module_path = os.path.join(root, file)
                
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Load tests from the module
                tests = self.loadTestsFromModule(module)
                
                # Add the tests to the suite
                suite.addTest(tests)
        
        return suite
    
    def discover(self, start_dir: str, pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestSuite:
        """
        Discover tests in a directory.
        
        Args:
            start_dir: The directory to start discovering tests from.
            pattern: A pattern to match test file names against.
            top_level_dir: The top-level directory of the project.
            
        Returns:
            A test suite containing the tests.
        """
        # Create a test suite
        suite = self.suite_class()
        
        # Discover tests
        tests = super().discover(start_dir, pattern, top_level_dir)
        
        # Add the tests to the suite
        suite.addTest(tests)
        
        return suite


@tag("testing.utils")
class UnitTestLoader(TestLoader):
    """
    Loader for unit tests.
    
    This class provides a loader for unit tests, which test individual
    components in isolation.
    
    Attributes:
        metadata: Additional metadata for the test loader.
        suite_class: The class to use for test suites.
    
    TODO(Issue #13): Add support for unit test loader dependencies
    TODO(Issue #13): Implement unit test loader analytics
    """
    
    def __init__(
        self,
        suite_class: Optional[Type[TestSuite]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the unit test loader.
        
        Args:
            suite_class: The class to use for test suites.
            metadata: Additional metadata for the test loader.
        """
        super().__init__(suite_class or UnitTestSuite, metadata)
        self.set_metadata("test_type", "unit")
    
    def discover(self, start_dir: str = "tests/unit", pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestSuite:
        """
        Discover unit tests in a directory.
        
        Args:
            start_dir: The directory to start discovering tests from.
            pattern: A pattern to match test file names against.
            top_level_dir: The top-level directory of the project.
            
        Returns:
            A test suite containing the tests.
        """
        return super().discover(start_dir, pattern, top_level_dir)


@tag("testing.utils")
class IntegrationTestLoader(TestLoader):
    """
    Loader for integration tests.
    
    This class provides a loader for integration tests, which test
    interactions between components.
    
    Attributes:
        metadata: Additional metadata for the test loader.
        suite_class: The class to use for test suites.
    
    TODO(Issue #13): Add support for integration test loader dependencies
    TODO(Issue #13): Implement integration test loader analytics
    """
    
    def __init__(
        self,
        suite_class: Optional[Type[TestSuite]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the integration test loader.
        
        Args:
            suite_class: The class to use for test suites.
            metadata: Additional metadata for the test loader.
        """
        super().__init__(suite_class or IntegrationTestSuite, metadata)
        self.set_metadata("test_type", "integration")
    
    def discover(self, start_dir: str = "tests/integration", pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestSuite:
        """
        Discover integration tests in a directory.
        
        Args:
            start_dir: The directory to start discovering tests from.
            pattern: A pattern to match test file names against.
            top_level_dir: The top-level directory of the project.
            
        Returns:
            A test suite containing the tests.
        """
        return super().discover(start_dir, pattern, top_level_dir)


@tag("testing.utils")
class E2ETestLoader(TestLoader):
    """
    Loader for end-to-end tests.
    
    This class provides a loader for end-to-end tests, which test
    the entire system.
    
    Attributes:
        metadata: Additional metadata for the test loader.
        suite_class: The class to use for test suites.
    
    TODO(Issue #13): Add support for end-to-end test loader dependencies
    TODO(Issue #13): Implement end-to-end test loader analytics
    """
    
    def __init__(
        self,
        suite_class: Optional[Type[TestSuite]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the end-to-end test loader.
        
        Args:
            suite_class: The class to use for test suites.
            metadata: Additional metadata for the test loader.
        """
        super().__init__(suite_class or E2ETestSuite, metadata)
        self.set_metadata("test_type", "e2e")
    
    def discover(self, start_dir: str = "tests/e2e", pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestSuite:
        """
        Discover end-to-end tests in a directory.
        
        Args:
            start_dir: The directory to start discovering tests from.
            pattern: A pattern to match test file names against.
            top_level_dir: The top-level directory of the project.
            
        Returns:
            A test suite containing the tests.
        """
        return super().discover(start_dir, pattern, top_level_dir)
