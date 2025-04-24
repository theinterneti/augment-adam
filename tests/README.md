# Augment Adam Tests

This directory contains tests for the Augment Adam project.

## Test Structure

The tests are organized into the following directories:

- `unit/`: Unit tests for individual components
  - `ai_agent/`: Tests for the AI Agent module
    - `smc/`: Tests for the Sequential Monte Carlo components
    - `types/`: Tests for the agent types
    - `reasoning/`: Tests for the reasoning components
    - `memory_integration/`: Tests for the memory integration components
  - `context_engine/`: Tests for the Context Engine module
  - `memory/`: Tests for the Memory module
- `integration/`: Integration tests for multiple components
  - `ai_agent/`: Tests for the AI Agent module
  - `context_engine/`: Tests for the Context Engine module
  - `memory/`: Tests for the Memory module

## Running Tests

To run all tests:

```bash
python -m unittest discover
```

To run a specific test file:

```bash
python -m unittest tests/unit/ai_agent/test_base_agent.py
```

To run a specific test case:

```bash
python -m unittest tests.unit.ai_agent.test_base_agent.TestBaseAgent
```

To run a specific test method:

```bash
python -m unittest tests.unit.ai_agent.test_base_agent.TestBaseAgent.test_initialization
```

## Test Coverage

To generate a test coverage report:

```bash
coverage run -m unittest discover
coverage report
coverage html  # Generates an HTML report
```

## Writing Tests

When writing tests, follow these guidelines:

1. **Test Structure**: Use the `unittest` framework and organize tests into classes.
2. **Test Naming**: Name test methods with a `test_` prefix followed by a descriptive name.
3. **Test Setup**: Use the `setUp` method to set up test fixtures.
4. **Test Teardown**: Use the `tearDown` method to clean up after tests.
5. **Mocking**: Use the `unittest.mock` module to mock dependencies.
6. **Assertions**: Use the appropriate assertion methods for different types of checks.
7. **Documentation**: Document test classes and methods with docstrings.

Example:

```python
import unittest
from unittest.mock import MagicMock, patch

from augment_adam.ai_agent.base_agent import BaseAgent


class TestBaseAgent(unittest.TestCase):
    """Tests for the BaseAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = BaseAgent(name="Test Agent")
    
    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "Test Agent")
    
    @patch('augment_adam.context_engine.context_manager.ContextManager.retrieve')
    def test_process(self, mock_retrieve):
        """Test the process method."""
        mock_retrieve.return_value = []
        result = self.agent.process("Test input")
        self.assertIn("response", result)


if __name__ == '__main__':
    unittest.main()
```
