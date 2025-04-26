# Testing Guidelines

This document provides detailed guidelines for testing in the Augment Adam project. Testing is a critical aspect of the project, and these guidelines help ensure that our code is reliable, maintainable, and of high quality.

## Testing Requirements

### Unit Tests

Unit tests are required for all code in the Augment Adam project. These tests should verify that individual units of code (functions, methods, classes) work as expected in isolation.

### Integration Tests

Integration tests are required for all components that interact with other components. These tests should verify that components work together as expected.

### End-to-End Tests

End-to-end tests are recommended but not required. These tests should verify that the entire system works as expected from a user's perspective.

### Coverage Target

The target code coverage for the Augment Adam project is 80%. This means that at least 80% of the code should be executed by the tests.

## Pre-Commit Testing

Pre-commit testing is required for the Augment Adam project. This means that tests should be run before each commit to ensure that the code is in a good state.

### Setting Up Pre-Commit Hooks

To set up pre-commit hooks, run the following command:

```bash
python scripts/setup_pre_commit.py
```

This will install the pre-commit hooks defined in `.pre-commit-config.yaml`, which include running tests on modified files.

### Running Pre-Commit Tests Manually

To run pre-commit tests manually, use the following command:

```bash
python scripts/run_pre_commit_tests.py
```

This will run tests on files that have been modified in the current commit.

## CI Integration

CI integration is required for the Augment Adam project. This means that tests should be run automatically on pull requests and pushes to the main branch.

### GitHub Actions Workflows

The following GitHub Actions workflows are set up for the Augment Adam project:

- `test.yml`: Runs tests on multiple Python versions
- `pre-commit.yml`: Runs pre-commit checks
- `coverage.yml`: Generates and uploads test coverage reports

### Branch Protection Rules

Branch protection rules are set up to require that tests pass before code can be merged into the main branch. This helps ensure that only high-quality code is merged.

## Test Isolation

Test isolation is required for the Augment Adam project. This means that tests should not interfere with each other or with the system under test.

### Using TestCase

Tests should use the `TestCase` class from `augment_adam.testing.utils.case`, which provides utilities for test isolation.

```python
from augment_adam.testing.utils.case import TestCase

class MyTest(TestCase):
    def setUp(self):
        # Set up test environment
        pass
        
    def tearDown(self):
        # Clean up test environment
        pass
        
    def test_something(self):
        # Test something
        pass
```

### Using Mocks

Tests should use mocks to isolate the code under test from its dependencies.

```python
from unittest.mock import patch, MagicMock

class MyTest(TestCase):
    @patch('module.dependency')
    def test_something(self, mock_dependency):
        # Configure the mock
        mock_dependency.return_value = 'mocked value'
        
        # Test something that uses the dependency
        result = function_under_test()
        
        # Assert that the result is as expected
        self.assertEqual(result, 'expected value')
        
        # Assert that the dependency was called as expected
        mock_dependency.assert_called_once_with('expected arg')
```

## Tag Registry Isolation

Tag registry isolation is required for the Augment Adam project. This means that tests should use an isolated tag registry to avoid interfering with other tests.

### Using reset_tag_registry

Tests should use the `reset_tag_registry` function to reset the tag registry before each test.

```python
from augment_adam.testing.utils.tag_utils import reset_tag_registry

class MyTest(TestCase):
    def setUp(self):
        # Reset the tag registry
        reset_tag_registry()
        
        # Set up test environment
        pass
```

### Using isolated_tag_registry

Tests should use the `isolated_tag_registry` context manager to create an isolated tag registry for the duration of the test.

```python
from augment_adam.testing.utils.tag_utils import isolated_tag_registry

class MyTest(TestCase):
    def test_something(self):
        with isolated_tag_registry():
            # Test something that uses tags
            pass
```

## Test Generation

The Augment Adam project includes a test generator that can automatically generate test stubs for untested code.

### Running the Test Generator

To run the test generator, use the following command:

```bash
python scripts/generate_tests_no_tags.py --module augment_adam.module.to.test --output-dir tests/unit
```

This will generate test stubs for untested functions and classes in the specified module.

### Customizing Generated Tests

Generated tests are just stubs and should be customized to properly test the code. This includes adding assertions, setting up test data, and configuring mocks.

## Best Practices

### Write Tests First

When possible, write tests before implementing the code. This helps ensure that the code is testable and meets the requirements.

### Keep Tests Simple

Tests should be simple and focused on a single aspect of the code. This makes them easier to understand and maintain.

### Use Descriptive Test Names

Test names should describe what the test is checking. This makes it easier to understand what a test is doing and why it's failing.

```python
def test_memory_add_stores_item_with_correct_id(self):
    # Test that adding an item to memory stores it with the correct ID
    pass
```

### Use Assertions Effectively

Tests should use assertions to verify that the code behaves as expected. Use the most specific assertion available for the situation.

```python
# Good
self.assertEqual(result, expected_value)
self.assertTrue(condition)
self.assertIn(item, collection)

# Less good
self.assertTrue(result == expected_value)
self.assertEqual(condition, True)
self.assertTrue(item in collection)
```

### Test Edge Cases

Tests should cover edge cases and error conditions, not just the happy path.

```python
def test_memory_add_handles_empty_content(self):
    # Test that adding an item with empty content works correctly
    pass
    
def test_memory_add_raises_error_for_invalid_id(self):
    # Test that adding an item with an invalid ID raises an error
    pass
```

### Use Fixtures

Use fixtures to set up common test data and environments.

```python
@pytest.fixture
def memory():
    # Set up a memory instance for testing
    return FAISSMemory()
    
def test_memory_add(memory):
    # Test adding an item to memory
    pass
    
def test_memory_search(memory):
    # Test searching memory
    pass
```

## Conclusion

Testing is a critical aspect of the Augment Adam project. By following these guidelines, we can ensure that our code is reliable, maintainable, and of high quality.
