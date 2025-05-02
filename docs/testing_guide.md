# Testing Guide for Augment Adam

This guide explains how to write and run tests for the Augment Adam project.

## Table of Contents

- [Introduction](#introduction)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [End-to-End Tests](#end-to-end-tests)
  - [Performance Tests](#performance-tests)
  - [Stress Tests](#stress-tests)
  - [Compatibility Tests](#compatibility-tests)
- [Test Utilities](#test-utilities)
- [Test Fixtures](#test-fixtures)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Best Practices](#best-practices)

## Introduction

The Augment Adam project uses a comprehensive testing framework to ensure code quality and reliability. The testing framework includes:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test the entire system from end to end
- **Performance Tests**: Test the performance of critical components
- **Stress Tests**: Test the system under heavy load
- **Compatibility Tests**: Test compatibility with different environments

## Test Structure

The test directory structure is organized as follows:

```
tests/
├── __init__.py
├── conftest.py
├── templates/
│   ├── __init__.py
│   ├── unit_test_template.py
│   ├── integration_test_template.py
│   └── e2e_test_template.py
├── utils/
│   ├── __init__.py
│   └── test_helpers.py
├── unit/
│   └── ...
├── integration/
│   └── ...
├── e2e/
│   └── ...
├── performance/
│   └── ...
├── stress/
│   └── ...
└── compatibility/
    └── ...
```

- `conftest.py`: Contains pytest fixtures and configuration
- `templates/`: Contains templates for different types of tests
- `utils/`: Contains utility functions for testing
- `unit/`: Contains unit tests
- `integration/`: Contains integration tests
- `e2e/`: Contains end-to-end tests
- `performance/`: Contains performance tests
- `stress/`: Contains stress tests
- `compatibility/`: Contains compatibility tests

## Running Tests

The project includes a comprehensive test runner that can run different types of tests:

```bash
# Run all tests
python run_tests.py --all

# Run unit tests
python run_tests.py --unit

# Run integration tests
python run_tests.py --integration

# Run end-to-end tests
python run_tests.py --e2e

# Run tests in parallel
python run_tests.py --all --parallel

# Run tests with coverage
python run_tests.py --all --use-pytest --coverage

# Run specific tests
python run_tests.py --path tests/unit/test_specific.py
```

You can also generate a coverage report:

```bash
python scripts/generate_coverage_report.py --all --badge
```

## Writing Tests

### Unit Tests

Unit tests test individual components in isolation. They should be fast, focused, and independent.

To write a unit test, use the unit test template:

```python
import unittest
import pytest
from unittest.mock import MagicMock, patch

# Import the module to test
from augment_adam.module import Class, function

# Import test utilities
from tests.utils import skip_if_no_module, timed

@pytest.mark.unit
class TestClass(unittest.TestCase):
    """Test cases for the Class class."""
    
    def setUp(self):
        """Set up the test case."""
        self.obj = Class()
    
    def test_method(self):
        """Test the method method."""
        expected = "expected result"
        result = self.obj.method()
        self.assertEqual(expected, result)
```

### Integration Tests

Integration tests test interactions between components. They ensure that components work together correctly.

To write an integration test, use the integration test template:

```python
import unittest
import pytest
from unittest.mock import MagicMock, patch

# Import the modules to test
from augment_adam.module1 import Class1
from augment_adam.module2 import Class2

# Import test utilities
from tests.utils import skip_if_no_env_var, timed

@pytest.mark.integration
class TestIntegration(unittest.TestCase):
    """Integration tests for the module."""
    
    def setUp(self):
        """Set up the test case."""
        self.obj1 = Class1()
        self.obj2 = Class2()
    
    def test_integration_scenario(self):
        """Test an integration scenario."""
        input_value = "input"
        expected = "expected result"
        
        result = self.obj1.method(input_value)
        final_result = self.obj2.process(result)
        
        self.assertEqual(expected, final_result)
```

### End-to-End Tests

End-to-end tests test the entire system from end to end. They ensure that the system works correctly as a whole.

To write an end-to-end test, use the end-to-end test template:

```python
import unittest
import pytest
import os
import time
from unittest.mock import MagicMock, patch

# Import the modules to test
from augment_adam.module1 import Class1
from augment_adam.module2 import Class2
from augment_adam.server import Server

# Import test utilities
from tests.utils import skip_if_no_env_var, timed

@pytest.mark.e2e
class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        cls.server = Server()
        cls.server.start()
    
    @classmethod
    def tearDownClass(cls):
        """Tear down the test class."""
        cls.server.stop()
    
    def setUp(self):
        """Set up the test case."""
        self.client = Client(self.server.url)
    
    def test_end_to_end_scenario(self):
        """Test an end-to-end scenario."""
        input_data = {"key": "value"}
        expected = {"result": "success"}
        
        response = self.client.send_request(input_data)
        
        self.assertEqual(expected, response)
```

### Performance Tests

Performance tests test the performance of critical components. They ensure that the system meets performance requirements.

To write a performance test, use the `PerformanceTestCase` class and the `time_limit` decorator:

```python
import unittest
import pytest
from tests.utils import PerformanceTestCase, time_limit

@pytest.mark.performance
class TestPerformance(PerformanceTestCase):
    """Performance tests for the module."""
    
    @time_limit(1.0)  # 1 second time limit
    def test_performance_critical_method(self):
        """Test a performance-critical method."""
        result = self.obj.performance_critical_method()
        self.assertEqual(expected, result)
```

### Stress Tests

Stress tests test the system under heavy load. They ensure that the system can handle high loads without failing.

To write a stress test, use the stress test template:

```python
import unittest
import pytest
import threading
import time
from tests.utils import timed

@pytest.mark.stress
class TestStress(unittest.TestCase):
    """Stress tests for the module."""
    
    def setUp(self):
        """Set up the test case."""
        self.obj = Class()
    
    @timed
    def test_stress_scenario(self):
        """Test a stress scenario."""
        # Create multiple threads to stress the system
        threads = []
        for i in range(100):
            thread = threading.Thread(target=self.obj.method, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert that the system is still in a valid state
        self.assertTrue(self.obj.is_valid())
```

### Compatibility Tests

Compatibility tests test compatibility with different environments. They ensure that the system works correctly in different environments.

To write a compatibility test, use the compatibility test template:

```python
import unittest
import pytest
import platform
import sys
from tests.utils import skip_if_no_module

@pytest.mark.compatibility
class TestCompatibility(unittest.TestCase):
    """Compatibility tests for the module."""
    
    def test_python_version_compatibility(self):
        """Test compatibility with different Python versions."""
        # Skip if not running on Python 3.9+
        if sys.version_info < (3, 9):
            self.skipTest("Requires Python 3.9+")
        
        # Test the module
        self.assertTrue(self.obj.is_compatible())
    
    @skip_if_no_module("optional_module")
    def test_optional_module_compatibility(self):
        """Test compatibility with an optional module."""
        # This test will be skipped if the optional_module is not available
        self.assertTrue(self.obj.is_compatible_with_optional_module())
```

## Test Utilities

The project includes a variety of test utilities to make writing tests easier:

- `skip_if_no_module(module_name)`: Skip a test if a module is not available
- `skip_if_no_env_var(env_var)`: Skip a test if an environment variable is not set
- `timed`: Decorator to time a test function
- `create_temp_file(content, suffix)`: Create a temporary file with the given content
- `create_temp_dir()`: Create a temporary directory
- `assert_dict_subset(test_case, subset, superset)`: Assert that a dictionary is a subset of another dictionary
- `assert_lists_equal_unordered(test_case, list1, list2)`: Assert that two lists contain the same elements, regardless of order
- `assert_approx_equal(test_case, value1, value2, tolerance)`: Assert that two values are approximately equal
- `mock_async_return(return_value)`: Create a mock for an async function that returns a value
- `mock_async_side_effect(side_effect)`: Create a mock for an async function with a side effect
- `AsyncTestCase`: Base class for async test cases
- `MemoryLeakTestCase`: Base class for memory leak test cases
- `PerformanceTestCase`: Base class for performance test cases
- `time_limit(seconds)`: Decorator to set a time limit for a performance test

## Test Fixtures

The project includes a variety of test fixtures to make writing tests easier:

- `temp_dir`: Create a temporary directory for tests
- `mock_faiss_memory`: Create a mocked FAISS memory instance for tests
- `mock_neo4j_memory`: Create a mocked Neo4j memory instance for tests
- `mcp_api_key`: Get the MCP API key for tests

You can add your own fixtures in `tests/conftest.py`.

## Test Coverage

The project includes a coverage report generator that can generate coverage reports in HTML and XML formats:

```bash
python scripts/generate_coverage_report.py --all --badge
```

The coverage report will be generated in the `coverage_html` directory.

## Continuous Integration

The project includes a GitHub Actions workflow that runs tests on every push and pull request:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        python run_tests.py --all --use-pytest --coverage
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## Best Practices

Here are some best practices for writing tests:

1. **Write tests first**: Write tests before implementing features to ensure that the implementation meets the requirements.
2. **Keep tests simple**: Tests should be simple, focused, and easy to understand.
3. **Use descriptive names**: Use descriptive names for test classes and methods to make it clear what they're testing.
4. **Test edge cases**: Test edge cases and error conditions to ensure that the code handles them correctly.
5. **Use mocks and stubs**: Use mocks and stubs to isolate the code being tested from its dependencies.
6. **Keep tests independent**: Tests should be independent of each other and should not rely on the state of other tests.
7. **Clean up after tests**: Clean up any resources created during tests to avoid affecting other tests.
8. **Run tests regularly**: Run tests regularly to catch regressions early.
9. **Measure coverage**: Measure test coverage to identify untested code.
10. **Refactor tests**: Refactor tests to keep them clean, maintainable, and efficient.
