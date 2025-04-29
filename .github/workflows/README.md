# GitHub Workflows

This directory contains GitHub Actions workflows for the Augment Adam project.

## Current Workflows

### Basic Tests (`test.yml`)

The Basic Tests workflow runs on every push to main, feature/*, and release/* branches, as well as on pull requests to main. It includes:

- **Simple Tests**: Runs basic tests that are known to pass
- **Additional Tests**: Attempts to run any additional tests but doesn't fail if they don't pass

### Basic Code Quality (`pre-commit.yml`)

The Basic Code Quality workflow runs on pull requests to main. It includes:

- **File Formatting**: Checks code formatting with Black
- **Import Sorting**: Checks import sorting with isort
- **Linting**: Runs basic linting with flake8

### Simplified CI (`ci.yml`)

The Simplified CI workflow runs on every push to main, feature/*, and release/* branches, as well as on pull requests to main. It includes:

- **Basic Checks**: Runs code quality checks
- **Simple Tests**: Runs basic tests
- **Build**: Builds the package and uploads it as an artifact (only on push to main or release/* branches)

### Basic Documentation (`docs.yml`)

The Basic Documentation workflow runs on pushes and pull requests that modify documentation files. It includes:

- **Documentation Check**: Checks if documentation can be built
- **Markdown Check**: Counts markdown files in the repository

### Basic Security Checks (`security.yml`)

The Basic Security Checks workflow runs on pushes to main, pull requests to main, and on a monthly schedule. It includes:

- **Basic Security Scan**: Runs a basic security scan with bandit
- **Secret Scanning**: Checks for secrets in the repository

## Future Improvements

As the project matures, these workflows will be expanded to include:

1. More comprehensive testing
2. Stricter code quality checks
3. Automated documentation deployment
4. More thorough security scanning
5. Performance testing
6. Compatibility testing with multiple Python versions
