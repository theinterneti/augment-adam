# Testing Guide

This guide explains how to use the Testing Framework in Augment Adam for testing your code. It covers unit testing, integration testing, end-to-end testing, and performance testing.

## Getting Started

The Testing Framework in Augment Adam provides a comprehensive set of tools and utilities for testing your code. It supports unit testing, integration testing, end-to-end testing, and performance testing, with a focus on testing AI components such as the Context Engine, Memory System, and Agent Coordination system.

To get started with testing, you'll need to import the appropriate modules from the `augment_adam.testing` package:

```python
from augment_adam.testing import TestCase, UnitTestRunner
from augment_adam.testing.fixtures import MemoryFixture

# Create a test case
class MyTest(TestCase):
    def setUp(self):
        # Set up test fixtures
        self.memory_fixture = MemoryFixture()
        self.memory = self.memory_fixture.setup()
        
    def test_something(self):
        # Test something
        self.assertEqual(1 + 1, 2)
        
    def tearDown(self):
        # Clean up test fixtures
        self.memory_fixture.teardown()
        
# Run the test
runner = UnitTestRunner()
result = runner.run(MyTest())

# Print the result
print(f"Ran {result.testsRun} tests")
print(f"Success: {result.wasSuccessful()}")
```

## Test Fixtures

Test fixtures are used to set up and tear down test environments. They provide a consistent way to create and manage test dependencies, such as memory components, model components, and agent components.

### Using Fixtures

The Testing Framework provides several fixtures for testing different components:

```python
from augment_adam.testing.fixtures import (
    MemoryFixture,
    ModelFixture,
    AgentFixture,
    ContextFixture,
    PluginFixture,
)

# Create a memory fixture
memory_fixture = MemoryFixture(memory_type="in_memory")

# Use the fixture in a test
with memory_fixture() as memory:
    # Test the memory component
    memory.add("key", "value")
    assert memory.get("key") == "value"

# Create a model fixture
model_fixture = ModelFixture(model_type="mock")

# Use the fixture in a test
with model_fixture() as model:
    # Configure the mock model
    model.generate.return_value = "Hello, world!"
    
    # Test the model component
    result = model.generate("Say hello")
    assert result == "Hello, world!"
```

### Creating Custom Fixtures

You can create custom fixtures by extending the `Fixture` base class:

```python
from typing import Any, Dict, Optional
from augment_adam.testing.fixtures.base import Fixture

class MyFixture(Fixture):
    def __init__(
        self,
        name: str = "my_fixture",
        scope: str = "function",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, scope=scope, metadata=metadata)
        self.config = config or {}
        self._resource = None
    
    def setup(self) -> Any:
        # Set up the resource
        self._resource = MyResource(**self.config)
        return self._resource
    
    def teardown(self) -> None:
        # Clean up the resource
        if self._resource is not None:
            self._resource.cleanup()
            self._resource = None
```

## Unit Testing

Unit testing focuses on testing individual components in isolation. The Testing Framework provides utilities for creating and running unit tests for various components.

### Creating Unit Tests

To create a unit test, extend the `TestCase` class and implement test methods:

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.memory import Memory

class MemoryTest(TestCase):
    def setUp(self):
        # Set up the test
        self.memory = Memory()
        
    def test_add_and_retrieve(self):
        # Add an item to memory
        item_id = self.memory.add("Hello, world!", {"source": "test"})
        
        # Retrieve the item
        item = self.memory.get(item_id)
        
        # Assert that the item was retrieved correctly
        self.assertEqual(item["text"], "Hello, world!")
        self.assertEqual(item["metadata"]["source"], "test")
        
    def tearDown(self):
        # Clean up the test
        self.memory.clear()
```

### Running Unit Tests

To run unit tests, use the `UnitTestRunner` class:

```python
from augment_adam.testing.runners import UnitTestRunner

# Create a unit test runner
runner = UnitTestRunner(verbosity=2)

# Run tests in a directory
result = runner.run_directory("tests/unit")

# Print the results
print(f"Ran {result.testsRun} tests")
print(f"Success: {result.wasSuccessful()}")

# Run tests in a module
result = runner.run_module("tests.unit.test_memory")

# Run specific tests
result = runner.run_tests(["tests.unit.test_memory.MemoryTest.test_add_and_retrieve"])
```

## Integration Testing

Integration testing focuses on testing the interactions between different components. The Testing Framework provides utilities for creating and running integration tests that verify the correct behavior of component interactions.

### Creating Integration Tests

To create an integration test, extend the `TestCase` class and use the `TestEnvironment` class to set up and tear down the test environment:

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.testing.fixtures import MemoryFixture, ContextFixture

class MemoryContextIntegrationTest(TestCase):
    def setUp(self):
        # Set up the test environment
        self.memory_fixture = MemoryFixture(memory_type="in_memory")
        self.memory = self.memory_fixture.setup()
        
        self.context_fixture = ContextFixture(context_type="basic", memory=self.memory)
        self.context = self.context_fixture.setup()
        
    def test_context_retrieval(self):
        # Add items to memory
        self.memory.add("The quick brown fox jumps over the lazy dog.", {"source": "test", "type": "document"})
        self.memory.add("The five boxing wizards jump quickly.", {"source": "test", "type": "document"})
        
        # Retrieve context using the context engine
        context = self.context.retrieve("fox jumps", max_items=1)
        
        # Assert that the context contains the correct item
        self.assertEqual(len(context), 1)
        self.assertIn("quick brown fox", context[0]["text"])
        
    def tearDown(self):
        # Clean up the test environment
        self.context_fixture.teardown()
        self.memory_fixture.teardown()
```

### Running Integration Tests

To run integration tests, use the `IntegrationTestRunner` class:

```python
from augment_adam.testing.runners import IntegrationTestRunner

# Create an integration test runner
runner = IntegrationTestRunner(verbosity=2)

# Run tests in a directory
result = runner.run_directory("tests/integration")

# Print the results
print(f"Ran {result.testsRun} tests")
print(f"Success: {result.wasSuccessful()}")

# Run tests in a module
result = runner.run_module("tests.integration.test_memory_context")

# Run specific tests
result = runner.run_tests(["tests.integration.test_memory_context.MemoryContextIntegrationTest.test_context_retrieval"])
```

## End-to-End Testing

End-to-end testing focuses on testing the entire system from end to end. The Testing Framework provides utilities for creating and running end-to-end tests that verify the correct behavior of the system as a whole.

### Creating End-to-End Tests

To create an end-to-end test, extend the `TestCase` class and use the `SystemTest` class to set up and tear down the system:

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.testing import SystemTest

class AgentSystemTest(TestCase):
    def setUp(self):
        # Create a system test
        self.system_test = SystemTest()
        
        # Configure the system
        self.system_test.configure({
            "memory": {
                "type": "in_memory",
                "max_items": 1000
            },
            "context_engine": {
                "type": "basic",
                "max_context_size": 5
            },
            "agent": {
                "type": "basic",
                "max_steps": 10
            }
        })
        
        # Start the system
        self.system_test.start()
        
    def test_agent_task(self):
        # Create a task for the agent
        task = {
            "type": "search",
            "query": "What is the capital of France?"
        }
        
        # Run the task
        result = self.system_test.run_task(task)
        
        # Assert that the result is correct
        self.assertIn("Paris", result["answer"])
        
    def tearDown(self):
        # Stop the system
        self.system_test.stop()
```

### Running End-to-End Tests

To run end-to-end tests, use the `E2ETestRunner` class:

```python
from augment_adam.testing.runners import E2ETestRunner

# Create an end-to-end test runner
runner = E2ETestRunner(verbosity=2)

# Run tests in a directory
result = runner.run_directory("tests/e2e")

# Print the results
print(f"Ran {result.testsRun} tests")
print(f"Success: {result.wasSuccessful()}")

# Run tests in a module
result = runner.run_module("tests.e2e.test_agent_system")

# Run specific tests
result = runner.run_tests(["tests.e2e.test_agent_system.AgentSystemTest.test_agent_task"])
```

## Performance Testing

Performance testing focuses on measuring and testing the performance of components and the system as a whole. The Testing Framework provides utilities for creating and running performance tests that verify that components and the system meet performance requirements.

### Creating Performance Tests

To create a performance test, extend the `TestCase` class and use the `PerformanceTest` class to set up and run the performance test:

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.testing import PerformanceTest

class MemoryPerformanceTest(TestCase):
    def setUp(self):
        # Create a performance test
        self.perf_test = PerformanceTest()
        
        # Configure the test
        self.perf_test.configure({
            "component": "memory",
            "operations": ["add", "search", "get", "delete"],
            "iterations": 1000,
            "data_size": 1000
        })
        
    def test_memory_performance(self):
        # Run the performance test
        results = self.perf_test.run()
        
        # Assert that the performance meets requirements
        self.assertLess(results["add"]["avg_time"], 0.001)  # Less than 1ms per add
        self.assertLess(results["search"]["avg_time"], 0.01)  # Less than 10ms per search
        self.assertLess(results["get"]["avg_time"], 0.001)  # Less than 1ms per get
        self.assertLess(results["delete"]["avg_time"], 0.001)  # Less than 1ms per delete
```

### Measuring Performance Metrics

To measure performance metrics, use the `PerformanceMetrics` class:

```python
from augment_adam.testing import PerformanceMetrics

# Create a performance metrics collector
metrics = PerformanceMetrics()

# Start collecting metrics
metrics.start()

# Run the code to be measured
for i in range(1000):
    memory.add(f"Item {i}", {"index": i})
    
# Stop collecting metrics
results = metrics.stop()

# Print the results
print(f"Total time: {results['total_time']} seconds")
print(f"Average time per operation: {results['avg_time']} seconds")
print(f"Operations per second: {results['ops_per_second']}")
print(f"Memory usage: {results['memory_usage']} MB")
print(f"CPU usage: {results['cpu_usage']}%")
```

## Test Coverage

Test coverage measures how much of your code is covered by tests. The Testing Framework provides utilities for measuring and reporting test coverage.

### Measuring Test Coverage

To measure test coverage, use the `CoverageReporter` class:

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

### Analyzing Test Coverage

To analyze test coverage, use the methods provided by the `CoverageReporter` class:

```python
from augment_adam.testing.coverage import CoverageReporter

# Get the total coverage percentage
total_coverage = reporter.get_total_coverage()
print(f"Total coverage: {total_coverage:.2f}%")

# Get the coverage percentage for a file
file_coverage = reporter.get_file_coverage("src/augment_adam/memory/memory.py")
print(f"File coverage: {file_coverage:.2f}%")

# Get the missing lines for a file
missing_lines = reporter.get_missing_lines("src/augment_adam/memory/memory.py")
print(f"Missing lines: {missing_lines}")
```

## Testing Asynchronous Code

Augment Adam makes extensive use of asynchronous programming with `asyncio`. Testing asynchronous code requires special consideration.

### Using pytest-asyncio

We use the pytest-asyncio plugin to handle event loops in tests. This plugin provides fixtures for working with event loops and running asynchronous tests.

```python
import pytest
import asyncio

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_async_function():
    # Test an asynchronous function
    result = await async_function()
    assert result == expected_result
```

### Testing Asynchronous Components

To test asynchronous components, use the `async_test` decorator provided by the Testing Framework:

```python
from augment_adam.testing import TestCase, async_test

class AsyncTest(TestCase):
    @async_test
    async def test_async_component(self):
        # Test an asynchronous component
        result = await async_component.process("input")
        self.assertEqual(result, "expected output")
```

## Best Practices

This section outlines best practices for testing in Augment Adam.

### Test Organization

Tests should be organized in a way that makes them easy to find and run. Here are some best practices for organizing tests:

1. **Group tests by component**: Tests for a specific component should be grouped together.
2. **Use descriptive test names**: Test names should describe what the test is testing.
3. **Use test fixtures**: Use test fixtures to set up and tear down test environments.
4. **Use test suites**: Group related tests into test suites.
5. **Use test categories**: Categorize tests by type (unit, integration, end-to-end, performance).

### Test Coverage

Tests should cover all critical components and scenarios. Here are some best practices for ensuring good test coverage:

1. **Use code coverage tools**: Use code coverage tools to measure test coverage.
2. **Focus on critical paths**: Focus on testing critical paths through the system.
3. **Test edge cases**: Test edge cases and error conditions.
4. **Test configuration variations**: Test with different configuration settings.
5. **Test with different data**: Test with different types and sizes of data.

### Test Maintenance

Tests should be easy to maintain and update as the system evolves. Here are some best practices for maintaining tests:

1. **Keep tests simple**: Tests should be simple and focused on a single aspect of behavior.
2. **Avoid test duplication**: Avoid duplicating test code.
3. **Use test utilities**: Use test utilities to simplify common test operations.
4. **Update tests when code changes**: Update tests when the code they test changes.
5. **Remove obsolete tests**: Remove tests that are no longer relevant.

### Testing AI Components

Testing AI components presents unique challenges. Here are some best practices for testing AI components:

1. **Use deterministic test data**: Use deterministic test data to ensure reproducible results.
2. **Test with realistic data**: Test with data that is representative of real-world usage.
3. **Test with adversarial data**: Test with data designed to challenge the AI component.
4. **Test for bias**: Test for bias in AI component outputs.
5. **Test for robustness**: Test for robustness to variations in input data.



## Examples

### Unit Test Example

This example demonstrates how to create and run a unit test for a calculator component.

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.utils.calculator import Calculator

class CalculatorTest(TestCase):
    def setUp(self):
        self.calculator = Calculator()
        
    def test_add(self):
        result = self.calculator.add(2, 3)
        self.assertEqual(result, 5)
        
    def test_subtract(self):
        result = self.calculator.subtract(5, 3)
        self.assertEqual(result, 2)
        
    def test_multiply(self):
        result = self.calculator.multiply(2, 3)
        self.assertEqual(result, 6)
        
    def test_divide(self):
        result = self.calculator.divide(6, 3)
        self.assertEqual(result, 2)
        
        # Test division by zero
        with self.assertRaises(ValueError):
            self.calculator.divide(6, 0)
            
if __name__ == "__main__":
    unittest.main()
```

### Integration Test Example

This example demonstrates how to create and run an integration test for a memory and context engine component.

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.testing.fixtures import MemoryFixture, ContextFixture

class MemoryContextIntegrationTest(TestCase):
    def setUp(self):
        # Set up the test environment
        self.memory_fixture = MemoryFixture(memory_type="in_memory")
        self.memory = self.memory_fixture.setup()
        
        self.context_fixture = ContextFixture(context_type="basic", memory=self.memory)
        self.context = self.context_fixture.setup()
        
    def test_context_retrieval(self):
        # Add items to memory
        self.memory.add("The quick brown fox jumps over the lazy dog.", {"source": "test", "type": "document"})
        self.memory.add("The five boxing wizards jump quickly.", {"source": "test", "type": "document"})
        
        # Retrieve context using the context engine
        context = self.context.retrieve("fox jumps", max_items=1)
        
        # Assert that the context contains the correct item
        self.assertEqual(len(context), 1)
        self.assertIn("quick brown fox", context[0]["text"])
        
    def tearDown(self):
        # Clean up the test environment
        self.context_fixture.teardown()
        self.memory_fixture.teardown()
        
if __name__ == "__main__":
    unittest.main()
```

### End-to-End Test Example

This example demonstrates how to create and run an end-to-end test for an agent system.

```python
import unittest
from augment_adam.testing import TestCase
from augment_adam.testing import SystemTest

class AgentSystemTest(TestCase):
    def setUp(self):
        # Create a system test
        self.system_test = SystemTest()
        
        # Configure the system
        self.system_test.configure({
            "memory": {
                "type": "in_memory",
                "max_items": 1000
            },
            "context_engine": {
                "type": "basic",
                "max_context_size": 5
            },
            "agent": {
                "type": "basic",
                "max_steps": 10
            }
        })
        
        # Start the system
        self.system_test.start()
        
    def test_agent_task(self):
        # Create a task for the agent
        task = {
            "type": "search",
            "query": "What is the capital of France?"
        }
        
        # Run the task
        result = self.system_test.run_task(task)
        
        # Assert that the result is correct
        self.assertIn("Paris", result["answer"])
        
    def tearDown(self):
        # Stop the system
        self.system_test.stop()
        
if __name__ == "__main__":
    unittest.main()
```



## Best Practices

### Write Tests First

Write tests before implementing features to ensure that your code meets the requirements and to guide your implementation.

### Keep Tests Simple

Keep tests simple and focused on a single aspect of behavior. Complex tests are harder to understand and maintain.

### Use Test Fixtures

Use test fixtures to set up and tear down test environments. This makes tests more maintainable and reduces duplication.

### Test Edge Cases

Test edge cases and error conditions to ensure that your code handles them correctly.

### Measure Test Coverage

Measure test coverage to identify areas that need more testing.



## Next Steps

- [Learn More About Testing](docs/architecture/TESTING_FRAMEWORK.md): Learn more about the Testing Framework architecture.
- [Explore Test Examples](src/augment_adam/testing/examples): Explore examples of different types of tests.
- [Contribute to Testing](docs/developer_guides/contributing.md): Learn how to contribute to the Testing Framework.

