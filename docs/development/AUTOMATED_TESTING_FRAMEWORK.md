# Automated Testing Framework

This document provides an overview of our automated testing framework, which is designed to ensure code quality and comprehensive test coverage across the project.

## Framework Components

Our automated testing framework consists of the following components:

1. **Code Quality Checklist**: A comprehensive list of quality criteria that all code files should meet.
2. **Code Quality Checker**: A tool that analyzes code files against the checklist and generates reports.
3. **Test Generator**: A tool that generates test files based on the code's functionality.
4. **Test Runner**: A tool that runs tests and generates coverage reports.
5. **Pre-Commit Hooks**: Hooks that run tests and quality checks before each commit.
6. **CI/CD Integration**: Automated testing in the CI/CD pipeline.

## Quick Start

To quickly check a file and generate tests:

```bash
./scripts/run_test_framework.sh --file path/to/your/file.py --generate-tests
```

To check all files in a directory:

```bash
./scripts/run_test_framework.sh --directory src/augment_adam/core --parallel
```

## Code Quality Checklist

The code quality checklist is defined in `docs/development/CODE_QUALITY_CHECKLIST.md`. It covers:

- Documentation Standards
- Type Hints
- Testing
- Code Style
- Error Handling
- Performance
- Security
- Tagging
- GitHub Integration

Each item in the checklist is marked as either "Required" or "Recommended" and indicates whether it can be automatically checked.

## Code Quality Checker

The code quality checker analyzes code files against the checklist and generates reports. It can be run on a single file or on multiple files in batch mode.

### Single File Check

```bash
python scripts/code_quality_checker.py --file path/to/your/file.py
```

### Batch Mode Check

```bash
python scripts/batch_code_quality_check.py --directory src --parallel
```

## Test Generator

The test generator creates test files based on the code's functionality. It can generate unit tests, integration tests, and end-to-end tests.

```bash
python scripts/generate_tests.py --file path/to/your/file.py
```

## Test Types

Our framework supports three types of tests:

### Unit Tests

Unit tests verify that individual functions and methods work correctly in isolation. They should be:

- Fast
- Independent
- Comprehensive (covering all code paths)
- Easy to maintain

Example unit test:

```python
def test_add_numbers():
    """Test the add_numbers function."""
    result = add_numbers(2, 3)
    assert result == 5
```

### Integration Tests

Integration tests verify that different components work together correctly. They should:

- Test component interactions
- Verify data flow between components
- Test error handling between components
- Use realistic test data

Example integration test:

```python
@pytest.mark.integration
def test_database_service_integration():
    """Test the integration between the database and service layers."""
    # Create a test record in the database
    record_id = db.create_record({"name": "Test"})
    
    # Retrieve the record using the service layer
    service = RecordService()
    record = service.get_record(record_id)
    
    # Verify the record was retrieved correctly
    assert record["name"] == "Test"
```

### End-to-End Tests

End-to-end tests verify that the entire system works correctly from a user's perspective. They should:

- Test complete user workflows
- Verify system behavior in realistic scenarios
- Test performance and reliability
- Use realistic test data

Example end-to-end test:

```python
@pytest.mark.e2e
def test_user_registration_workflow():
    """Test the complete user registration workflow."""
    # Create a test user
    user = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    
    # Register the user
    response = client.post("/api/register", json=user)
    assert response.status_code == 200
    
    # Verify the user can log in
    login_response = client.post("/api/login", json={"username": user["username"], "password": user["password"]})
    assert login_response.status_code == 200
    assert "token" in login_response.json()
```

## Test Coverage

The project aims for at least 80% test coverage. You can generate a coverage report:

```bash
python -m pytest --cov=src/augment_adam --cov-report=html
```

## Pre-Commit Hooks

The project uses pre-commit hooks to run tests on modified files before each commit:

```bash
python scripts/setup_pre_commit.py
```

## CI/CD Integration

The project's CI/CD pipeline runs tests automatically on pull requests and pushes to the main branch.

## Best Practices

When writing tests, follow these best practices:

1. **Test Isolation**: Tests should not depend on each other or on external state.
2. **Test Coverage**: Aim for at least 80% test coverage.
3. **Test Naming**: Use descriptive names for test functions.
4. **Test Documentation**: Document what each test is testing.
5. **Test Fixtures**: Use fixtures for common setup and teardown.
6. **Test Parameterization**: Use parameterized tests for testing multiple inputs.
7. **Test Mocking**: Use mocking for external dependencies.
8. **Test Performance**: Tests should be fast.
9. **Test Maintainability**: Tests should be easy to maintain.
10. **Test Readability**: Tests should be easy to read and understand.

## Checklist for Code Files

Before submitting code for review, ensure it meets the following criteria:

- [ ] Code follows the project's coding standards
- [ ] Code has comprehensive docstrings
- [ ] Code has appropriate type hints
- [ ] Code has unit tests with at least 80% coverage
- [ ] Code has integration tests for complex components
- [ ] Code has end-to-end tests for user-facing features
- [ ] All tests pass
- [ ] Code passes all quality checks
- [ ] Code is properly tagged
- [ ] Code references GitHub issues where appropriate

## Detailed Documentation

For more detailed information, see:

- [Code Quality Checklist](CODE_QUALITY_CHECKLIST.md)
- [Test Generation Framework](TEST_GENERATION_FRAMEWORK.md)
- [Testing Guidelines](../TESTING_GUIDELINES.md)

## Troubleshooting

If you encounter issues with the testing framework, please:

1. Check the documentation in this file and in the related files.
2. Check the code comments in the scripts.
3. Ask for help in the project's communication channels.

## Contributing

If you'd like to contribute to the testing framework, please:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Run the tests to ensure they pass.
5. Submit a pull request.
