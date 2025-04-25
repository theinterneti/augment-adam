"""
End-to-end test runner.

This module provides a runner for end-to-end tests, which test the entire system.
"""

import sys
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, TextIO

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.result import TestResult, VerboseTestResult
from augment_adam.testing.utils.loader import E2ETestLoader
from augment_adam.testing.utils.suite import E2ETestSuite


@tag("testing.runners")
class E2ETestRunner:
    """
    Runner for end-to-end tests.
    
    This class provides a runner for end-to-end tests, which test the entire system.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
        loader: The loader to use for loading tests.
    
    TODO(Issue #13): Add support for end-to-end test runner dependencies
    TODO(Issue #13): Implement end-to-end test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        loader: Optional[E2ETestLoader] = None
    ) -> None:
        """
        Initialize the end-to-end test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
            loader: The loader to use for loading tests.
        """
        self.stream = stream or sys.stderr
        self.verbosity = verbosity
        self.result_class = result_class or (VerboseTestResult if verbosity > 1 else TestResult)
        self.metadata = metadata or {}
        self.loader = loader or E2ETestLoader()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test runner.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test runner.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def run(self, test_or_suite: Any) -> TestResult:
        """
        Run a test or test suite.
        
        Args:
            test_or_suite: The test or test suite to run.
            
        Returns:
            The test result.
        """
        # Create a test result
        result = self.result_class(self.stream, self.metadata) if self.verbosity > 1 else self.result_class(self.metadata)
        
        # Start the test run
        result.startTestRun()
        
        try:
            # Run the test or test suite
            test_or_suite(result)
        finally:
            # Stop the test run
            result.stopTestRun()
        
        # Print errors if verbose
        if self.verbosity > 1 and hasattr(result, "printErrors"):
            result.printErrors()
            
            if hasattr(result, "printSummary"):
                result.printSummary()
        
        return result
    
    def run_tests(self, test_names: List[str]) -> TestResult:
        """
        Run tests by name.
        
        Args:
            test_names: The names of the tests to run.
            
        Returns:
            The test result.
        """
        # Load the tests
        suite = self.loader.loadTestsFromNames(test_names)
        
        # Run the tests
        return self.run(suite)
    
    def run_module(self, module_name: str) -> TestResult:
        """
        Run tests in a module.
        
        Args:
            module_name: The name of the module to run tests from.
            
        Returns:
            The test result.
        """
        # Load the tests
        suite = self.loader.loadTestsFromName(module_name)
        
        # Run the tests
        return self.run(suite)
    
    def run_directory(self, directory: str, pattern: str = "test_*.py") -> TestResult:
        """
        Run tests in a directory.
        
        Args:
            directory: The directory to run tests from.
            pattern: A pattern to match test file names against.
            
        Returns:
            The test result.
        """
        # Load the tests
        suite = self.loader.loadTestsFromDirectory(directory, pattern)
        
        # Run the tests
        return self.run(suite)
    
    def discover_and_run(self, start_dir: str = "tests/e2e", pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestResult:
        """
        Discover and run tests in a directory.
        
        Args:
            start_dir: The directory to start discovering tests from.
            pattern: A pattern to match test file names against.
            top_level_dir: The top-level directory of the project.
            
        Returns:
            The test result.
        """
        # Discover the tests
        suite = self.loader.discover(start_dir, pattern, top_level_dir)
        
        # Run the tests
        return self.run(suite)
