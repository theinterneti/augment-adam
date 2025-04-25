"""
Parallel test runner.

This module provides a runner for running tests in parallel.
"""

import sys
import multiprocessing
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, TextIO

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.result import TestResult, VerboseTestResult
from augment_adam.testing.utils.loader import TestLoader
from augment_adam.testing.utils.suite import TestSuite


@tag("testing.runners")
class ParallelTestRunner:
    """
    Runner for parallel tests.
    
    This class provides a runner for running tests in parallel.
    
    Attributes:
        metadata: Additional metadata for the test runner.
        stream: The stream to write output to.
        verbosity: The verbosity level.
        result_class: The class to use for test results.
        loader: The loader to use for loading tests.
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
        loader: Optional[TestLoader] = None,
        num_processes: int = 0
    ) -> None:
        """
        Initialize the parallel test runner.
        
        Args:
            stream: The stream to write output to.
            verbosity: The verbosity level.
            result_class: The class to use for test results.
            metadata: Additional metadata for the test runner.
            loader: The loader to use for loading tests.
            num_processes: The number of processes to use. If 0, use the number of CPU cores.
        """
        self.stream = stream or sys.stderr
        self.verbosity = verbosity
        self.result_class = result_class or (VerboseTestResult if verbosity > 1 else TestResult)
        self.metadata = metadata or {}
        self.loader = loader or TestLoader()
        self.num_processes = num_processes if num_processes > 0 else multiprocessing.cpu_count()
    
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
        Run a test or test suite in parallel.
        
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
            # Get the tests to run
            tests = list(self._get_tests(test_or_suite))
            
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
        if self.verbosity > 1 and hasattr(result, "printErrors"):
            result.printErrors()
            
            if hasattr(result, "printSummary"):
                result.printSummary()
        
        return result
    
    def run_tests(self, test_names: List[str]) -> TestResult:
        """
        Run tests by name in parallel.
        
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
        Run tests in a module in parallel.
        
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
        Run tests in a directory in parallel.
        
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
    
    def discover_and_run(self, start_dir: str = "tests", pattern: str = "test_*.py", top_level_dir: Optional[str] = None) -> TestResult:
        """
        Discover and run tests in a directory in parallel.
        
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
    
    def _get_tests(self, test_or_suite: Any) -> List[Any]:
        """
        Get the individual tests from a test case or test suite.
        
        Args:
            test_or_suite: The test case or test suite.
            
        Returns:
            A list of individual test cases.
        """
        tests = []
        
        # If the test is a test suite, get the individual tests
        if isinstance(test_or_suite, TestSuite) or hasattr(test_or_suite, "_tests"):
            for test in test_or_suite:
                tests.extend(self._get_tests(test))
        else:
            # Otherwise, add the test
            tests.append(test_or_suite)
        
        return tests
    
    def _run_test(self, test: Any) -> Dict[str, Any]:
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
            "time": result.timings.get(result.getDescription(test), 0.0),
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
