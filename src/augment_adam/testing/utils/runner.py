"""
Test runner utilities.

This module provides utilities for test runners, including a base test runner class
and specialized test runner classes for different types of tests.
"""

import unittest
import sys
import time
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, TextIO

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.result import TestResult, VerboseTestResult


@tag("testing.utils")
class TestRunner:
    """
    Base class for test runners.
    
    This class provides functionality for running tests and reporting results.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
    
    TODO(Issue #13): Add support for test runner dependencies
    TODO(Issue #13): Implement test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
        """
        self.stream = stream or sys.stderr
        self.verbosity = verbosity
        self.result_class = result_class or (VerboseTestResult if verbosity > 1 else TestResult)
        self.metadata = metadata or {}
    
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
    
    def run(self, test: unittest.TestCase) -> TestResult:
        """
        Run a test.
        
        Args:
            test: The test to run.
            
        Returns:
            The test result.
        """
        # Create a test result
        result = self.result_class(self.stream, self.metadata) if self.verbosity > 1 else self.result_class(self.metadata)
        
        # Start the test run
        result.startTestRun()
        
        try:
            # Run the test
            test(result)
        finally:
            # Stop the test run
            result.stopTestRun()
        
        # Print errors if verbose
        if self.verbosity > 1:
            result.printErrors()
            result.printSummary()
        
        return result


@tag("testing.utils")
class UnitTestRunner(TestRunner):
    """
    Runner for unit tests.
    
    This class provides a runner for unit tests, which test individual
    components in isolation.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
    
    TODO(Issue #13): Add support for unit test runner dependencies
    TODO(Issue #13): Implement unit test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the unit test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
        """
        super().__init__(stream, verbosity, result_class, metadata)
        self.set_metadata("test_type", "unit")


@tag("testing.utils")
class IntegrationTestRunner(TestRunner):
    """
    Runner for integration tests.
    
    This class provides a runner for integration tests, which test
    interactions between components.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
    
    TODO(Issue #13): Add support for integration test runner dependencies
    TODO(Issue #13): Implement integration test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the integration test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
        """
        super().__init__(stream, verbosity, result_class, metadata)
        self.set_metadata("test_type", "integration")


@tag("testing.utils")
class E2ETestRunner(TestRunner):
    """
    Runner for end-to-end tests.
    
    This class provides a runner for end-to-end tests, which test
    the entire system.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
    
    TODO(Issue #13): Add support for end-to-end test runner dependencies
    TODO(Issue #13): Implement end-to-end test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the end-to-end test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
        """
        super().__init__(stream, verbosity, result_class, metadata)
        self.set_metadata("test_type", "e2e")


@tag("testing.utils")
class ParallelTestRunner(TestRunner):
    """
    Runner for parallel tests.
    
    This class provides a runner for running tests in parallel.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
        num_processes: The number of processes to use.
    
    TODO(Issue #13): Add support for parallel test runner dependencies
    TODO(Issue #13): Implement parallel test runner analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        verbosity: int = 1,
        result_class: Optional[Type[TestResult]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        num_processes: int = 0
    ) -> None:
        """
        Initialize the parallel test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
            num_processes: The number of processes to use. If 0, use the number of CPU cores.
        """
        super().__init__(stream, verbosity, result_class, metadata)
        self.num_processes = num_processes
    
    def run(self, test: unittest.TestCase) -> TestResult:
        """
        Run a test in parallel.
        
        Args:
            test: The test to run.
            
        Returns:
            The test result.
        """
        import multiprocessing
        
        # Determine the number of processes to use
        if self.num_processes <= 0:
            self.num_processes = multiprocessing.cpu_count()
        
        # Create a test result
        result = self.result_class(self.stream, self.metadata) if self.verbosity > 1 else self.result_class(self.metadata)
        
        # Start the test run
        result.startTestRun()
        
        try:
            # Get the tests to run
            tests = list(self._get_tests(test))
            
            # Create a pool of processes
            with multiprocessing.Pool(processes=self.num_processes) as pool:
                # Run the tests in parallel
                for test_result in pool.map(self._run_test, tests):
                    # Update the result
                    self._update_result(result, test_result)
        finally:
            # Stop the test run
            result.stopTestRun()
        
        # Print errors if verbose
        if self.verbosity > 1:
            result.printErrors()
            result.printSummary()
        
        return result
    
    def _get_tests(self, test: unittest.TestCase) -> List[unittest.TestCase]:
        """
        Get the individual tests from a test case or test suite.
        
        Args:
            test: The test case or test suite.
            
        Returns:
            A list of individual test cases.
        """
        tests = []
        
        # If the test is a test suite, get the individual tests
        if isinstance(test, unittest.TestSuite):
            for t in test:
                tests.extend(self._get_tests(t))
        else:
            # Otherwise, add the test
            tests.append(test)
        
        return tests
    
    def _run_test(self, test: unittest.TestCase) -> Dict[str, Any]:
        """
        Run a test and return the result.
        
        Args:
            test: The test to run.
            
        Returns:
            A dictionary containing the test result.
        """
        # Create a test result
        result = TestResult()
        
        # Run the test
        test(result)
        
        # Return the result
        return {
            "test": test,
            "success": result.wasSuccessful(),
            "failures": result.failures,
            "errors": result.errors,
            "skipped": result.skipped,
            "time": result.get_test_time(test),
        }
    
    def _update_result(self, result: TestResult, test_result: Dict[str, Any]) -> None:
        """
        Update a test result with the results of a test.
        
        Args:
            result: The test result to update.
            test_result: The results of a test.
        """
        # Get the test
        test = test_result["test"]
        
        # Update the test count
        result.testsRun += 1
        
        # Update the timings
        result.timings[result.getDescription(test)] = test_result["time"]
        
        # Update the failures, errors, and skipped tests
        result.failures.extend(test_result["failures"])
        result.errors.extend(test_result["errors"])
        result.skipped.extend(test_result["skipped"])
