# Test Generation Framework

This document describes the automated test generation framework for the project. The framework is designed to help developers ensure their code meets our quality standards and has comprehensive test coverage.

## Overview

The test generation framework consists of three main components:

1. **Code Quality Checklist**: A comprehensive list of quality criteria that all code files should meet.
2. **Code Quality Checker**: A tool that analyzes code files against the checklist and generates reports.
3. **Test Generator**: A tool that generates test files based on the code's functionality.

## Workflow

The typical workflow for using this framework is:

1. Write your code following the project's coding standards.
2. Run the code quality checker to identify any issues.
3. Address the issues identified by the checker.
4. Run the checker again to verify that all issues have been resolved.
5. Generate tests for your code using the test generator.
6. Implement the test logic in the generated test files.
7. Run the tests to ensure they pass.

## Code Quality Checklist

The code quality checklist is defined in `docs/development/CODE_QUALITY_CHECKLIST.md`. It covers the following areas:

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

The code quality checker is a tool that analyzes code files against the checklist and generates reports. It can be run on a single file or on multiple files in batch mode.

### Running the Checker on a Single File

```bash
python scripts/code_quality_checker.py --file path/to/your/file.py
```

This will print a report to the console. You can also save the report to a file:

```bash
python scripts/code_quality_checker.py --file path/to/your/file.py --output report.md
```

### Running the Checker in Batch Mode

```bash
python scripts/batch_code_quality_check.py --directory src
```

This will check all Python files in the `src` directory and its subdirectories. You can exclude directories:

```bash
python scripts/batch_code_quality_check.py --directory src --exclude tests venv
```

You can also save reports for all files:

```bash
python scripts/batch_code_quality_check.py --directory src --output-dir reports
```

And run checks in parallel for faster processing:

```bash
python scripts/batch_code_quality_check.py --directory src --parallel
```

## Test Generator

The test generator is a tool that generates test files based on the code's functionality. It can generate unit tests, integration tests, and end-to-end tests.

### Generating Tests for a Single File

```bash
python scripts/generate_tests.py --file path/to/your/file.py
```

This will generate unit, integration, and end-to-end test files in the `tests` directory. You can specify a different output directory:

```bash
python scripts/generate_tests.py --file path/to/your/file.py --output-dir my_tests
```

You can also generate only specific types of tests:

```bash
python scripts/generate_tests.py --file path/to/your/file.py --unit-only
python scripts/generate_tests.py --file path/to/your/file.py --integration-only
python scripts/generate_tests.py --file path/to/your/file.py --e2e-only
```

## Test Structure

The generated tests follow the project's test structure:

```
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
└── e2e/                # End-to-end tests
```

### Unit Tests

Unit tests are designed to test individual functions and methods in isolation. They should be fast, independent, and cover all code paths.

### Integration Tests

Integration tests are designed to test the interaction between different components. They should verify that components work together correctly.

### End-to-End Tests

End-to-end tests are designed to test the entire system from a user's perspective. They should verify that the system works as expected in real-world scenarios.

## Test Markers

The generated tests include pytest markers to categorize them:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests

You can run tests with specific markers:

```bash
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m e2e
```

## Test Coverage

The project aims for at least 80% test coverage. You can generate a coverage report:

```bash
python -m pytest --cov=src/augment_adam --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Pre-Commit Hooks

The project uses pre-commit hooks to run tests on modified files before each commit. You can set up pre-commit hooks:

```bash
python scripts/setup_pre_commit.py
```

You can also run pre-commit tests manually:

```bash
python scripts/run_pre_commit_tests.py
```

## CI/CD Integration

The project's CI/CD pipeline runs tests automatically on pull requests and pushes to the main branch. The pipeline includes:

- Running unit tests
- Running integration tests
- Running end-to-end tests
- Generating a coverage report
- Running code quality checks

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

## Troubleshooting

### Common Issues

- **ImportError**: Make sure the module you're testing is in the Python path.
- **ModuleNotFoundError**: Make sure the module you're testing is installed.
- **AttributeError**: Make sure the class or function you're testing exists.
- **TypeError**: Make sure you're calling functions with the correct arguments.
- **AssertionError**: Make sure your test assertions are correct.

### Getting Help

If you encounter issues with the test generation framework, please:

1. Check the documentation in this file and in `docs/development/CODE_QUALITY_CHECKLIST.md`.
2. Check the code comments in the scripts.
3. Ask for help in the project's communication channels.

## Contributing

If you'd like to contribute to the test generation framework, please:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Run the tests to ensure they pass.
5. Submit a pull request.

## License

The test generation framework is licensed under the same license as the rest of the project.
