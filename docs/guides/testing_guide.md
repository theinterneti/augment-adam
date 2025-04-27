# Testing Guide

This guide provides information on how to write, run, and maintain tests for the Augment Adam project.

## Table of Contents

- [Introduction](#introduction)
- [Testing Philosophy](#testing-philosophy)
- [Types of Tests](#types-of-tests)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Introduction

Testing is a critical part of the Augment Adam development process. It helps ensure that the code works as expected, prevents regressions, and provides documentation for how the code should be used.

## Testing Philosophy

Our testing philosophy is based on the following principles:

1. **Test-Driven Development**: Write tests before implementing features when possible.
2. **Comprehensive Coverage**: Aim for high test coverage, especially for core components.
3. **Isolation**: Tests should be isolated from each other and from external dependencies.
4. **Readability**: Tests should be easy to read and understand.
5. **Maintainability**: Tests should be easy to maintain and update.

## Types of Tests

Augment Adam uses several types of tests:

### Unit Tests

Unit tests focus on testing individual components in isolation. They should be fast, reliable, and not depend on external services.

Location: `tests/unit/`

Example:
```python
def test_add():
    """Test the add function."""
    assert add(1, 2) == 3
```

### Integration Tests

Integration tests verify that different components work together correctly.

Location: `tests/integration/`

Example:
```python
def test_memory_and_context():
    """Test that memory and context components work together."""
    memory = FAISSMemory()
    context = ContextManager(memory=memory)
    # Test their interaction
```

### Performance Tests

Performance tests ensure that the code meets performance requirements.

Location: `tests/performance/`

Example:
```python
def test_search_performance():
    """Test that search is fast enough."""
    memory = FAISSMemory()
    # Add many items
    start_time = time.time()
    results = memory.search("query", limit=10)
    end_time = time.time()
    assert end_time - start_time < 0.1  # Should be fast
```

### Compatibility Tests

Compatibility tests verify that the code works with different versions of dependencies.

Location: `tests/compatibility/`

### Stress Tests

Stress tests check how the system behaves under heavy load.

Location: `tests/stress/`

## Writing Tests

### Test Structure

Tests should follow the Arrange-Act-Assert pattern:

1. **Arrange**: Set up the test data and environment.
2. **Act**: Perform the action being tested.
3. **Assert**: Verify the results.

Example:
```python
def test_add_item_to_memory():
    """Test adding an item to memory."""
    # Arrange
    memory = FAISSMemory()
    item = {"id": "1", "content": "test", "embedding": [0.1, 0.2, 0.3]}
    
    # Act
    memory.add(item)
    
    # Assert
    results = memory.search("test", limit=1)
    assert len(results) == 1
    assert results[0]["id"] == "1"
```

### Test Naming

Test names should clearly describe what they're testing:

- Use the prefix `test_` for test functions.
- Include the name of the function being tested.
- Describe the scenario and expected outcome.

Example: `test_add_item_to_memory_returns_success`

### Using Fixtures

Fixtures are a way to set up test data or environments that can be reused across tests.

Example:
```python
@pytest.fixture
def memory():
    """Create a memory instance for tests."""
    return FAISSMemory()

def test_add(memory):
    """Test adding an item to memory."""
    memory.add({"id": "1", "content": "test"})
    # ...
```

### Mocking

Use mocks to isolate the code being tested from external dependencies:

```python
@patch('augment_adam.memory.neo4j_memory.Neo4jClient')
def test_neo4j_memory(mock_client):
    """Test Neo4j memory with a mock client."""
    mock_client.return_value.query.return_value = [{"id": "1"}]
    memory = Neo4jMemory()
    # Test with the mock
```

## Running Tests

### Running All Tests

To run all tests:

```bash
python -m scripts.run_tests
```

### Running Specific Tests

To run a specific test file:

```bash
python -m scripts.run_tests tests/unit/test_file.py
```

To run tests with a specific marker:

```bash
python -m pytest -m "unit"
```

### Running with Coverage

To run tests with coverage:

```bash
python -m scripts.run_tests --coverage
```

## Test Coverage

We use the `pytest-cov` plugin to measure test coverage. The goal is to maintain high coverage, especially for core components.

To view the coverage report:

1. Run tests with coverage: `python -m scripts.run_tests --coverage`
2. Open `htmlcov/index.html` in a web browser

## Continuous Integration

Tests are automatically run in GitHub Actions when you push code or create a pull request. The workflow is defined in `.github/workflows/ci.yml`.

The CI pipeline runs:
1. Linting checks
2. Unit tests
3. Integration tests
4. Performance tests (on pull requests)
5. Compatibility tests (on pull requests)

## Troubleshooting

### Common Issues

#### Import Errors

If you encounter import errors when running tests, make sure:
- The package is installed in development mode: `pip install -e .`
- The imports use the correct package structure

#### Tag Registry Errors

If you see errors related to the tag registry, try:
- Using `safe_tag` instead of `tag` in tests
- Resetting the tag registry before tests: `reset_tag_registry()`

#### Slow Tests

If tests are running slowly:
- Use mocks for external dependencies
- Mark slow tests with `@pytest.mark.slow`
- Run only fast tests during development: `pytest -m "not slow"`

### Getting Help

If you need help with testing, you can:
- Check the existing tests for examples
- Read the pytest documentation: https://docs.pytest.org/
- Ask for help in the project's communication channels
