# Testing Framework

## Overview

The Testing Framework provides a comprehensive solution for testing the project, including unit tests, integration tests, end-to-end tests, and CI/CD setup. It includes features for test fixtures, test utilities, test runners, test coverage, and test examples.

## Components

### Test Fixtures

The Test Fixtures module provides fixtures for testing, including:

- **MemoryFixture**: Fixture for memory components
- **ModelFixture**: Fixture for model components
- **AgentFixture**: Fixture for agent components
- **ContextFixture**: Fixture for context components
- **PluginFixture**: Fixture for plugin components

### Test Utilities

The Test Utilities module provides utilities for testing, including:

- **TestCase**: Base class for test cases
- **TestSuite**: Base class for test suites
- **TestResult**: Base class for test results
- **TestRunner**: Base class for test runners
- **TestLoader**: Base class for test loaders
- **TestReporter**: Base class for test reporters

### Test Runners

The Test Runners module provides runners for different types of tests:

- **UnitTestRunner**: Runner for unit tests
- **IntegrationTestRunner**: Runner for integration tests
- **E2ETestRunner**: Runner for end-to-end tests
- **ParallelTestRunner**: Runner for running tests in parallel

### Test Coverage

The Test Coverage module provides utilities for measuring and reporting test coverage:

- **CoverageReporter**: Reporter for test coverage
- **CoverageConfig**: Configuration for test coverage

### Test Examples

The Test Examples module provides examples for testing:

- **Unit Test Example**: Example of a unit test
- **Integration Test Example**: Example of an integration test
- **End-to-End Test Example**: Example of an end-to-end test

## Usage

### Using Test Fixtures

```python
from augment_adam.testing.fixtures import MemoryFixture

# Create a memory fixture
memory_fixture = MemoryFixture(memory_type="faiss")

# Use the fixture in a test
with memory_fixture() as memory:
    # Test the memory component
    memory.add("key", "value")
    assert memory.get("key") == "value"
```

### Using Test Utilities

```python
from augment_adam.testing.utils import TestCase

# Create a test case
class MyTest(TestCase):
    def test_something(self):
        # Test something
        self.assertEqual(1 + 1, 2)
```

### Using Test Runners

```python
from augment_adam.testing.runners import UnitTestRunner

# Create a unit test runner
runner = UnitTestRunner(verbosity=2)

# Run tests in a directory
result = runner.run_directory("tests/unit")

# Print the results
print(f"Ran {result.testsRun} tests")
print(f"Success: {result.wasSuccessful()}")
```

### Using Test Coverage

```python
from augment_adam.testing.coverage import CoverageReporter, CoverageConfig

# Create a coverage configuration
config = CoverageConfig(
    source=["src"],
    include=["src/**/*.py"],
    omit=["**/test_*.py"],
    branch=True,
)

# Create a coverage reporter
reporter = CoverageReporter(config)

# Start measuring coverage
reporter.start()

# Run tests
# ...

# Stop measuring coverage
reporter.stop()

# Save coverage data
reporter.save()

# Generate a coverage report
reporter.report()

# Generate an HTML coverage report
reporter.html_report("coverage_html")
```

### Using Test Examples

```python
from augment_adam.testing.examples.unit_test_example import CalculatorTest

# Run the calculator test
unittest.main(defaultTest="CalculatorTest")
```

## CI/CD Setup

The Testing Framework includes support for CI/CD setup, including:

- **GitHub Actions**: Workflow for running tests on GitHub
- **Travis CI**: Configuration for running tests on Travis CI
- **CircleCI**: Configuration for running tests on CircleCI

## Future Enhancements

- Add property-based testing
- Implement mutation testing
- Add performance testing
- Implement security testing
- Add load testing
