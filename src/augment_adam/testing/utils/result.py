"""
Test result utilities.

This module provides utilities for test results, including a base test result class
and specialized test result classes for different types of tests.
"""

import unittest
import time
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, Tuple

from augment_adam.utils.tagging import tag, TagCategory


@tag("testing.utils")
class TestResult(unittest.TestResult):
    """
    Base class for test results.
    
    This class extends unittest.TestResult with additional functionality for
    tracking and reporting test results.
    
    Attributes:
        metadata: Additional metadata for the test result.
        start_time: The time when the test run started.
        end_time: The time when the test run ended.
        timings: Dictionary mapping test IDs to their execution times.
    
    TODO(Issue #13): Add support for test result dependencies
    TODO(Issue #13): Implement test result analytics
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the test result.
        
        Args:
            metadata: Additional metadata for the test result.
        """
        super().__init__()
        self.metadata = metadata or {}
        self.start_time = 0.0
        self.end_time = 0.0
        self.timings: Dict[str, float] = {}
        self._current_test_start_time = 0.0
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test result.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test result.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def startTest(self, test: unittest.TestCase) -> None:
        """
        Called when a test starts.
        
        Args:
            test: The test that is starting.
        """
        super().startTest(test)
        self._current_test_start_time = time.time()
    
    def stopTest(self, test: unittest.TestCase) -> None:
        """
        Called when a test stops.
        
        Args:
            test: The test that is stopping.
        """
        super().stopTest(test)
        self.timings[self.getDescription(test)] = time.time() - self._current_test_start_time
    
    def startTestRun(self) -> None:
        """Called when the test run starts."""
        super().startTestRun()
        self.start_time = time.time()
    
    def stopTestRun(self) -> None:
        """Called when the test run stops."""
        super().stopTestRun()
        self.end_time = time.time()
    
    def getDescription(self, test: unittest.TestCase) -> str:
        """
        Get a description of the test.
        
        Args:
            test: The test to describe.
            
        Returns:
            A description of the test.
        """
        return f"{test.__class__.__name__}.{test._testMethodName}"
    
    def get_total_time(self) -> float:
        """
        Get the total time taken by the test run.
        
        Returns:
            The total time taken by the test run.
        """
        return self.end_time - self.start_time
    
    def get_test_time(self, test: unittest.TestCase) -> float:
        """
        Get the time taken by a test.
        
        Args:
            test: The test to get the time for.
            
        Returns:
            The time taken by the test.
        """
        return self.timings.get(self.getDescription(test), 0.0)
    
    def get_success_count(self) -> int:
        """
        Get the number of successful tests.
        
        Returns:
            The number of successful tests.
        """
        return self.testsRun - len(self.failures) - len(self.errors) - len(self.skipped)
    
    def get_failure_count(self) -> int:
        """
        Get the number of failed tests.
        
        Returns:
            The number of failed tests.
        """
        return len(self.failures)
    
    def get_error_count(self) -> int:
        """
        Get the number of tests with errors.
        
        Returns:
            The number of tests with errors.
        """
        return len(self.errors)
    
    def get_skip_count(self) -> int:
        """
        Get the number of skipped tests.
        
        Returns:
            The number of skipped tests.
        """
        return len(self.skipped)
    
    def get_success_rate(self) -> float:
        """
        Get the success rate of the test run.
        
        Returns:
            The success rate of the test run, as a percentage.
        """
        if self.testsRun == 0:
            return 0.0
        
        return 100.0 * self.get_success_count() / self.testsRun
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the test run.
        
        Returns:
            A dictionary containing a summary of the test run.
        """
        return {
            "total": self.testsRun,
            "success": self.get_success_count(),
            "failure": self.get_failure_count(),
            "error": self.get_error_count(),
            "skip": self.get_skip_count(),
            "success_rate": self.get_success_rate(),
            "total_time": self.get_total_time(),
        }
    
    def get_failures(self) -> List[Tuple[unittest.TestCase, str]]:
        """
        Get the list of failed tests.
        
        Returns:
            A list of tuples containing the failed test and the failure message.
        """
        return self.failures
    
    def get_errors(self) -> List[Tuple[unittest.TestCase, str]]:
        """
        Get the list of tests with errors.
        
        Returns:
            A list of tuples containing the test with an error and the error message.
        """
        return self.errors
    
    def get_skipped(self) -> List[Tuple[unittest.TestCase, str]]:
        """
        Get the list of skipped tests.
        
        Returns:
            A list of tuples containing the skipped test and the skip reason.
        """
        return self.skipped


@tag("testing.utils")
class VerboseTestResult(TestResult):
    """
    Test result with verbose output.
    
    This class extends TestResult with verbose output for each test.
    
    Attributes:
        metadata: Additional metadata for the test result.
        start_time: The time when the test run started.
        end_time: The time when the test run ended.
        timings: Dictionary mapping test IDs to their execution times.
        stream: The stream to write output to.
    
    TODO(Issue #13): Add support for verbose test result dependencies
    TODO(Issue #13): Implement verbose test result analytics
    """
    
    def __init__(self, stream: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the verbose test result.
        
        Args:
            stream: The stream to write output to.
            metadata: Additional metadata for the test result.
        """
        super().__init__(metadata)
        self.stream = stream
    
    def startTest(self, test: unittest.TestCase) -> None:
        """
        Called when a test starts.
        
        Args:
            test: The test that is starting.
        """
        super().startTest(test)
        self.stream.write(f"Running {self.getDescription(test)}... ")
        self.stream.flush()
    
    def addSuccess(self, test: unittest.TestCase) -> None:
        """
        Called when a test succeeds.
        
        Args:
            test: The test that succeeded.
        """
        super().addSuccess(test)
        self.stream.write(f"OK ({self.get_test_time(test):.3f}s)\n")
        self.stream.flush()
    
    def addError(self, test: unittest.TestCase, err: Tuple[Type[Exception], Exception, Any]) -> None:
        """
        Called when a test raises an error.
        
        Args:
            test: The test that raised an error.
            err: The error information.
        """
        super().addError(test, err)
        self.stream.write(f"ERROR ({self.get_test_time(test):.3f}s)\n")
        self.stream.flush()
    
    def addFailure(self, test: unittest.TestCase, err: Tuple[Type[Exception], Exception, Any]) -> None:
        """
        Called when a test fails.
        
        Args:
            test: The test that failed.
            err: The failure information.
        """
        super().addFailure(test, err)
        self.stream.write(f"FAIL ({self.get_test_time(test):.3f}s)\n")
        self.stream.flush()
    
    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        """
        Called when a test is skipped.
        
        Args:
            test: The test that was skipped.
            reason: The reason for skipping the test.
        """
        super().addSkip(test, reason)
        self.stream.write(f"SKIP ({reason})\n")
        self.stream.flush()
    
    def addExpectedFailure(self, test: unittest.TestCase, err: Tuple[Type[Exception], Exception, Any]) -> None:
        """
        Called when a test fails as expected.
        
        Args:
            test: The test that failed as expected.
            err: The failure information.
        """
        super().addExpectedFailure(test, err)
        self.stream.write(f"EXPECTED FAIL ({self.get_test_time(test):.3f}s)\n")
        self.stream.flush()
    
    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        """
        Called when a test succeeds unexpectedly.
        
        Args:
            test: The test that succeeded unexpectedly.
        """
        super().addUnexpectedSuccess(test)
        self.stream.write(f"UNEXPECTED SUCCESS ({self.get_test_time(test):.3f}s)\n")
        self.stream.flush()
    
    def printErrors(self) -> None:
        """Print information about all errors and failures."""
        self.stream.write("\n")
        self.printErrorList("ERROR", self.errors)
        self.printErrorList("FAIL", self.failures)
    
    def printErrorList(self, flavor: str, errors: List[Tuple[unittest.TestCase, str]]) -> None:
        """
        Print information about a list of errors or failures.
        
        Args:
            flavor: The type of error ("ERROR" or "FAIL").
            errors: The list of errors or failures.
        """
        for test, err in errors:
            self.stream.write(f"\n{flavor}: {self.getDescription(test)}\n")
            self.stream.write(f"{err}\n")
    
    def printSummary(self) -> None:
        """Print a summary of the test run."""
        summary = self.get_summary()
        
        self.stream.write("\n")
        self.stream.write(f"Ran {summary['total']} tests in {summary['total_time']:.3f}s\n")
        self.stream.write("\n")
        
        if summary['failure'] > 0 or summary['error'] > 0:
            self.stream.write("FAILED")
        else:
            self.stream.write("OK")
        
        details = []
        
        if summary['failure'] > 0:
            details.append(f"failures={summary['failure']}")
        
        if summary['error'] > 0:
            details.append(f"errors={summary['error']}")
        
        if summary['skip'] > 0:
            details.append(f"skipped={summary['skip']}")
        
        if details:
            self.stream.write(f" ({', '.join(details)})")
        
        self.stream.write("\n")
        self.stream.write(f"Success rate: {summary['success_rate']:.2f}%\n")
        self.stream.flush()
