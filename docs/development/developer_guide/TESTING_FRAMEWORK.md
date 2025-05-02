# Testing Framework

This document describes the Testing Framework in Augment Adam. The Testing Framework provides tools and utilities for testing the various components of the system, ensuring reliability and correctness.

## Overview

The Testing Framework in Augment Adam provides a comprehensive set of tools and utilities for testing the various components of the system. It supports unit testing, integration testing, and end-to-end testing, with a focus on testing AI components such as the Context Engine, Memory System, and Agent Coordination system.

### Key Features

- **AI Component Testing**: Specialized tools for testing AI components such as language models, embeddings, and retrieval systems.
- **Mock Components**: Mock implementations of external services and components for isolated testing.
- **Test Data Generation**: Utilities for generating test data for various components.
- **Assertion Utilities**: Custom assertion utilities for AI-specific testing scenarios.
- **Performance Testing**: Tools for measuring and testing the performance of components.
- **Integration Testing**: Utilities for testing the integration between components.
- **End-to-End Testing**: Framework for testing the entire system from end to end.

### Design Principles

The Testing Framework is designed with the following principles in mind:

1. **Isolation**: Tests should be isolated from each other and from external dependencies.
2. **Reproducibility**: Tests should be reproducible, with deterministic results.
3. **Clarity**: Test code should be clear and easy to understand.
4. **Efficiency**: Tests should run quickly and efficiently.
5. **Coverage**: Tests should cover all critical components and scenarios.
6. **Maintainability**: Tests should be easy to maintain and update as the system evolves.

## Unit Testing

Unit testing in Augment Adam focuses on testing individual components in isolation. The Testing Framework provides utilities for creating and running unit tests for various components.

```python
import unittest
from augment_adam.testing import MockMemory, MockContextEngine, MockAgent

class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = MockMemory()
        
    def test_add_and_retrieve(self):
        # Add an item to memory
        item_id = self.memory.add("Hello, world!", {"source": "test"})
        
        # Retrieve the item
        item = self.memory.get(item_id)
        
        # Assert that the item was retrieved correctly
        self.assertEqual(item["text"], "Hello, world!")
        self.assertEqual(item["metadata"]["source"], "test")
        
    def test_search(self):
        # Add items to memory
        self.memory.add("Hello, world!", {"source": "test"})
        self.memory.add("Goodbye, world!", {"source": "test"})
        
        # Search for items
        results = self.memory.search("Hello", k=1)
        
        # Assert that the search returned the correct item
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Hello, world!")
        
    def test_delete(self):
        # Add an item to memory
        item_id = self.memory.add("Hello, world!", {"source": "test"})
        
        # Delete the item
        self.memory.delete(item_id)
        
        # Assert that the item was deleted
        self.assertIsNone(self.memory.get(item_id))
        
if __name__ == "__main__":
    unittest.main()
```

### Mock Components

The Testing Framework provides mock implementations of various components for use in unit tests. These mock components implement the same interfaces as the real components, but with simplified behavior that is suitable for testing.

### Test Data Generation

The Testing Framework provides utilities for generating test data for various components. These utilities make it easy to create realistic test data for testing different scenarios.

## Integration Testing

Integration testing in Augment Adam focuses on testing the interaction between components. The Testing Framework provides utilities for creating and running integration tests for various component combinations.

```python
import unittest
from augment_adam.testing import IntegrationTestCase
from augment_adam.memory import FAISSMemory
from augment_adam.context_engine import ContextEngine

class MemoryContextIntegrationTest(IntegrationTestCase):
    def setUp(self):
        # Create real components for integration testing
        self.memory = FAISSMemory(path="./test_data/memory")
        self.context_engine = ContextEngine(memory=self.memory)
        
        # Add test data
        self.memory.add("The capital of France is Paris.", {"source": "test"})
        self.memory.add("The capital of Germany is Berlin.", {"source": "test"})
        self.memory.add("The capital of Italy is Rome.", {"source": "test"})
        
    def tearDown(self):
        # Clean up test data
        self.memory.clear()
        
    def test_context_retrieval(self):
        # Get context for a query
        context = self.context_engine.get_context("What is the capital of France?")
        
        # Assert that the context contains the relevant information
        self.assertIn("France", context)
        self.assertIn("Paris", context)
        
    def test_context_composition(self):
        # Add a document to the context engine
        self.context_engine.add_document("The capital of Spain is Madrid.")
        
        # Get context for a query
        context = self.context_engine.get_context("What are the capitals of European countries?")
        
        # Assert that the context contains information from multiple documents
        self.assertIn("France", context)
        self.assertIn("Paris", context)
        self.assertIn("Germany", context)
        self.assertIn("Berlin", context)
        self.assertIn("Italy", context)
        self.assertIn("Rome", context)
        self.assertIn("Spain", context)
        self.assertIn("Madrid", context)
        
if __name__ == "__main__":
    unittest.main()
```

### Integration Test Case

The Testing Framework provides an `IntegrationTestCase` class that extends the standard `unittest.TestCase` class with additional utilities for integration testing.

```python
import unittest
from typing import Any, Dict, List, Optional

class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""
    
    def assertContextContains(self, context: str, expected_content: str, msg: Optional[str] = None):
        """Assert that a context contains the expected content.
        
        Args:
            context: The context to check.
            expected_content: The content that should be in the context.
            msg: Optional message to display on failure.
        """
        self.assertIn(expected_content, context, msg=msg)
    
    def assertContextDoesNotContain(self, context: str, unexpected_content: str, msg: Optional[str] = None):
        """Assert that a context does not contain the unexpected content.
        
        Args:
            context: The context to check.
            unexpected_content: The content that should not be in the context.
            msg: Optional message to display on failure.
        """
        self.assertNotIn(unexpected_content, context, msg=msg)
    
    def assertMemoryContains(self, memory: Any, expected_text: str, msg: Optional[str] = None):
        """Assert that a memory contains the expected text.
        
        Args:
            memory: The memory to check.
            expected_text: The text that should be in the memory.
            msg: Optional message to display on failure.
        """
        results = memory.search(expected_text, k=10)
        found = any(expected_text in result["text"] for result in results)
        if not found:
            self.fail(msg or f"Memory does not contain '{expected_text}'")
    
    def assertMemoryDoesNotContain(self, memory: Any, unexpected_text: str, msg: Optional[str] = None):
        """Assert that a memory does not contain the unexpected text.
        
        Args:
            memory: The memory to check.
            unexpected_text: The text that should not be in the memory.
            msg: Optional message to display on failure.
        """
        results = memory.search(unexpected_text, k=10)
        found = any(unexpected_text in result["text"] for result in results)
        if found:
            self.fail(msg or f"Memory contains '{unexpected_text}'")
```

### Test Fixtures

The Testing Framework provides test fixtures for integration testing. These fixtures set up the necessary components and test data for integration tests.

```python
from augment_adam.testing import MemoryFixture, ContextEngineFixture, AssistantFixture

# Use fixtures in tests
class MemoryContextIntegrationTest(IntegrationTestCase):
    def setUp(self):
        # Create fixtures
        self.memory_fixture = MemoryFixture()
        self.context_engine_fixture = ContextEngineFixture(memory=self.memory_fixture.memory)
        
        # Set up test data
        self.memory_fixture.add_test_data()
        
    def tearDown(self):
        # Clean up fixtures
        self.memory_fixture.cleanup()
        self.context_engine_fixture.cleanup()
        
    def test_context_retrieval(self):
        # Get context for a query
        context = self.context_engine_fixture.context_engine.get_context("What is the capital of France?")
        
        # Assert that the context contains the relevant information
        self.assertContextContains(context, "France")
        self.assertContextContains(context, "Paris")
```

## End-to-End Testing

End-to-end testing in Augment Adam focuses on testing the entire system from end to end. The Testing Framework provides utilities for creating and running end-to-end tests that simulate real user interactions.

```python
import unittest
from augment_adam.testing import EndToEndTestCase
from augment_adam.core import Assistant

class AssistantEndToEndTest(EndToEndTestCase):
    def setUp(self):
        # Create an assistant for end-to-end testing
        self.assistant = Assistant()
        
        # Set up test data
        self.assistant.memory.add("The capital of France is Paris.", {"source": "test"})
        self.assistant.memory.add("The capital of Germany is Berlin.", {"source": "test"})
        self.assistant.memory.add("The capital of Italy is Rome.", {"source": "test"})
        
    def tearDown(self):
        # Clean up test data
        self.assistant.memory.clear()
        
    def test_assistant_response(self):
        # Chat with the assistant
        response = self.assistant.chat("What is the capital of France?")
        
        # Assert that the response contains the relevant information
        self.assertResponseContains(response, "Paris")
        
    def test_assistant_conversation(self):
        # Have a conversation with the assistant
        responses = self.conversation_with_assistant([
            "What is the capital of France?",
            "And what about Germany?",
            "Can you tell me about Italy?"
        ])
        
        # Assert that the responses contain the relevant information
        self.assertResponseContains(responses[0], "Paris")
        self.assertResponseContains(responses[1], "Berlin")
        self.assertResponseContains(responses[2], "Rome")
        
if __name__ == "__main__":
    unittest.main()
```

### End-to-End Test Case

The Testing Framework provides an `EndToEndTestCase` class that extends the standard `unittest.TestCase` class with additional utilities for end-to-end testing.

```python
import unittest
from typing import Any, Dict, List, Optional

class EndToEndTestCase(unittest.TestCase):
    """Base class for end-to-end tests."""
    
    def assertResponseContains(self, response: str, expected_content: str, msg: Optional[str] = None):
        """Assert that a response contains the expected content.
        
        Args:
            response: The response to check.
            expected_content: The content that should be in the response.
            msg: Optional message to display on failure.
        """
        self.assertIn(expected_content, response, msg=msg)
    
    def assertResponseDoesNotContain(self, response: str, unexpected_content: str, msg: Optional[str] = None):
        """Assert that a response does not contain the unexpected content.
        
        Args:
            response: The response to check.
            unexpected_content: The content that should not be in the response.
            msg: Optional message to display on failure.
        """
        self.assertNotIn(unexpected_content, response, msg=msg)
    
    def conversation_with_assistant(self, messages: List[str]) -> List[str]:
        """Have a conversation with the assistant.
        
        Args:
            messages: List of messages to send to the assistant.
            
        Returns:
            List of responses from the assistant.
        """
        responses = []
        for message in messages:
            response = self.assistant.chat(message)
            responses.append(response)
        return responses
```

### Test Scenarios

The Testing Framework provides test scenarios for end-to-end testing. These scenarios simulate real user interactions with the system.

```python
from augment_adam.testing import TestScenario, TestStep

# Define a test scenario
scenario = TestScenario(
    name="Capital Cities",
    description="Test the assistant's knowledge of capital cities.",
    steps=[
        TestStep(
            name="Ask about France",
            input="What is the capital of France?",
            expected_output="Paris"
        ),
        TestStep(
            name="Ask about Germany",
            input="And what about Germany?",
            expected_output="Berlin"
        ),
        TestStep(
            name="Ask about Italy",
            input="Can you tell me about Italy?",
            expected_output="Rome"
        )
    ]
)

# Run the scenario
results = scenario.run(assistant)

# Check the results
for step, result in zip(scenario.steps, results):
    print(f"Step: {step.name}")
    print(f"Input: {step.input}")
    print(f"Expected Output: {step.expected_output}")
    print(f"Actual Output: {result}")
    print(f"Success: {step.expected_output in result}")
    print()
```

## Performance Testing

Performance testing in Augment Adam focuses on measuring and testing the performance of components. The Testing Framework provides utilities for creating and running performance tests.

```python
import unittest
import time
from augment_adam.testing import PerformanceTestCase
from augment_adam.memory import FAISSMemory

class MemoryPerformanceTest(PerformanceTestCase):
    def setUp(self):
        # Create a memory for performance testing
        self.memory = FAISSMemory(path="./test_data/memory")
        
        # Add test data
        for i in range(1000):
            self.memory.add(f"Test item {i}", {"index": i})
        
    def tearDown(self):
        # Clean up test data
        self.memory.clear()
        
    def test_memory_search_performance(self):
        # Measure the performance of memory search
        with self.measure_time() as timer:
            for i in range(100):
                self.memory.search(f"Test item {i}", k=5)
        
        # Assert that the search is fast enough
        self.assertTimeLessThan(timer.elapsed, 1.0, "Memory search is too slow")
        
    def test_memory_add_performance(self):
        # Measure the performance of memory add
        with self.measure_time() as timer:
            for i in range(100):
                self.memory.add(f"New test item {i}", {"index": i + 1000})
        
        # Assert that the add is fast enough
        self.assertTimeLessThan(timer.elapsed, 1.0, "Memory add is too slow")
        
    def test_memory_get_performance(self):
        # Add items to memory and get their IDs
        ids = []
        for i in range(100):
            id = self.memory.add(f"Get test item {i}", {"index": i + 2000})
            ids.append(id)
        
        # Measure the performance of memory get
        with self.measure_time() as timer:
            for id in ids:
                self.memory.get(id)
        
        # Assert that the get is fast enough
        self.assertTimeLessThan(timer.elapsed, 0.1, "Memory get is too slow")
        
if __name__ == "__main__":
    unittest.main()
```

### Performance Test Case

The Testing Framework provides a `PerformanceTestCase` class that extends the standard `unittest.TestCase` class with additional utilities for performance testing.

```python
import unittest
import time
from typing import Any, Dict, List, Optional, ContextManager
from contextlib import contextmanager

class Timer:
    """Timer for measuring elapsed time."""
    
    def __init__(self):
        """Initialize the timer."""
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        return self.elapsed

class PerformanceTestCase(unittest.TestCase):
    """Base class for performance tests."""
    
    @contextmanager
    def measure_time(self) -> ContextManager[Timer]:
        """Measure the time taken to execute a block of code.
        
        Returns:
            A context manager that yields a Timer object.
        """
        timer = Timer()
        timer.start()
        try:
            yield timer
        finally:
            timer.stop()
    
    def assertTimeLessThan(self, elapsed: float, threshold: float, msg: Optional[str] = None):
        """Assert that the elapsed time is less than the threshold.
        
        Args:
            elapsed: The elapsed time in seconds.
            threshold: The threshold in seconds.
            msg: Optional message to display on failure.
        """
        self.assertLess(elapsed, threshold, msg=msg or f"Elapsed time {elapsed:.2f}s is not less than threshold {threshold:.2f}s")
    
    def assertTimeGreaterThan(self, elapsed: float, threshold: float, msg: Optional[str] = None):
        """Assert that the elapsed time is greater than the threshold.
        
        Args:
            elapsed: The elapsed time in seconds.
            threshold: The threshold in seconds.
            msg: Optional message to display on failure.
        """
        self.assertGreater(elapsed, threshold, msg=msg or f"Elapsed time {elapsed:.2f}s is not greater than threshold {threshold:.2f}s")
```

### Performance Benchmarks

The Testing Framework provides performance benchmarks for various components. These benchmarks measure the performance of components under different conditions and workloads.

```python
from augment_adam.testing import PerformanceBenchmark, BenchmarkResult

# Define a performance benchmark
benchmark = PerformanceBenchmark(
    name="Memory Search Benchmark",
    description="Benchmark for memory search performance.",
    setup=lambda: FAISSMemory(path="./test_data/memory"),
    cleanup=lambda memory: memory.clear(),
    run=lambda memory: [memory.search(f"Test item {i}", k=5) for i in range(100)],
    iterations=10
)

# Run the benchmark
result = benchmark.run()

# Print the results
print(f"Benchmark: {benchmark.name}")
print(f"Description: {benchmark.description}")
print(f"Average Time: {result.average_time:.2f}s")
print(f"Minimum Time: {result.min_time:.2f}s")
print(f"Maximum Time: {result.max_time:.2f}s")
print(f"Standard Deviation: {result.std_dev:.2f}s")
```

## Best Practices

Here are some best practices for testing in Augment Adam:

### Test Organization

- **Test Directory Structure**: Organize tests in a directory structure that mirrors the source code.
- **Test Naming**: Use descriptive names for test files and test methods.
- **Test Grouping**: Group related tests together in test classes.
- **Test Independence**: Ensure that tests are independent of each other and can be run in any order.

### Test Coverage

- **Unit Tests**: Write unit tests for all components and functions.
- **Integration Tests**: Write integration tests for component interactions.
- **End-to-End Tests**: Write end-to-end tests for critical user flows.
- **Edge Cases**: Test edge cases and error conditions.
- **Performance Tests**: Test performance under various conditions and workloads.

### Test Data

- **Test Data Generation**: Use the test data generation utilities to create realistic test data.
- **Test Data Isolation**: Ensure that test data is isolated from production data.
- **Test Data Cleanup**: Clean up test data after tests are complete.
- **Test Data Versioning**: Version test data to ensure reproducibility.

### Test Execution

- **Continuous Integration**: Run tests automatically in a continuous integration environment.
- **Test Parallelization**: Run tests in parallel to reduce execution time.
- **Test Reporting**: Generate test reports to track test results over time.
- **Test Debugging**: Use the test debugging utilities to diagnose test failures.

## Examples

Here are some examples of using the Testing Framework in Augment Adam:

### Testing the Memory System

Example of testing the Memory System.

```python
import unittest
from augment_adam.testing import MockMemory, MemoryTestCase

class FAISSMemoryTest(MemoryTestCase):
    def setUp(self):
        # Create a memory for testing
        from augment_adam.memory import FAISSMemory
        self.memory = FAISSMemory(path="./test_data/memory")
        
    def tearDown(self):
        # Clean up test data
        self.memory.clear()
        
    def test_add_and_retrieve(self):
        # Add an item to memory
        item_id = self.memory.add("Hello, world!", {"source": "test"})
        
        # Retrieve the item
        item = self.memory.get(item_id)
        
        # Assert that the item was retrieved correctly
        self.assertEqual(item["text"], "Hello, world!")
        self.assertEqual(item["metadata"]["source"], "test")
        
    def test_search(self):
        # Add items to memory
        self.memory.add("Hello, world!", {"source": "test"})
        self.memory.add("Goodbye, world!", {"source": "test"})
        
        # Search for items
        results = self.memory.search("Hello", k=1)
        
        # Assert that the search returned the correct item
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "Hello, world!")
        
    def test_delete(self):
        # Add an item to memory
        item_id = self.memory.add("Hello, world!", {"source": "test"})
        
        # Delete the item
        self.memory.delete(item_id)
        
        # Assert that the item was deleted
        self.assertIsNone(self.memory.get(item_id))
        
if __name__ == "__main__":
    unittest.main()
```

### Testing the Context Engine

Example of testing the Context Engine.

```python
import unittest
from augment_adam.testing import MockContextEngine, ContextEngineTestCase

class ContextEngineTest(ContextEngineTestCase):
    def setUp(self):
        # Create a context engine for testing
        from augment_adam.context_engine import ContextEngine
        from augment_adam.memory import FAISSMemory
        self.memory = FAISSMemory(path="./test_data/memory")
        self.context_engine = ContextEngine(memory=self.memory)
        
        # Add test data
        self.memory.add("The capital of France is Paris.", {"source": "test"})
        self.memory.add("The capital of Germany is Berlin.", {"source": "test"})
        self.memory.add("The capital of Italy is Rome.", {"source": "test"})
        
    def tearDown(self):
        # Clean up test data
        self.memory.clear()
        
    def test_add_document(self):
        # Add a document to the context engine
        document_id = self.context_engine.add_document("The capital of Spain is Madrid.")
        
        # Assert that the document was added correctly
        self.assertIsNotNone(document_id)
        self.assertMemoryContains(self.memory, "Spain")
        self.assertMemoryContains(self.memory, "Madrid")
        
    def test_get_context(self):
        # Get context for a query
        context = self.context_engine.get_context("What is the capital of France?")
        
        # Assert that the context contains the relevant information
        self.assertContextContains(context, "France")
        self.assertContextContains(context, "Paris")
        
if __name__ == "__main__":
    unittest.main()
```


