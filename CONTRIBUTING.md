# Contributing to Augment Adam

Thank you for your interest in contributing to Augment Adam! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](docs/CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment:
   - **Recommended**: Use the VS Code devcontainer for a consistent environment (see [Devcontainer Documentation](docs/DEVCONTAINER.md))
   - **Alternative**: Follow the manual setup in the [Development Setup Guide](DEVELOPMENT_SETUP.md)
4. Create a new branch for your changes

## Development Workflow

1. Make your changes in a new git branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Follow the code style guidelines (we use Black and isort)
3. Add tests for your changes
4. Run the tests to ensure they pass
5. Update documentation if necessary
6. Commit your changes using a descriptive commit message
7. Push your branch to GitHub
8. Submit a pull request to the main repository

## Pull Request Guidelines

- Fill in the required pull request template
- Include a clear description of the changes
- Link any related issues
- Update documentation for any new features
- Add tests for new features or bug fixes
- Ensure all tests pass
- Follow the code style guidelines

## Commit Message Guidelines

We follow conventional commits for our commit messages:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:

```
feat(memory): add new FAISS memory implementation
```

## Testing Guidelines

- Write tests for all new features and bug fixes
- Maintain or improve test coverage
- Run the full test suite before submitting a pull request

## Documentation Guidelines

- Update documentation for any new features or changes to existing features
- Use clear, concise language
- Include examples where appropriate
- Follow the existing documentation style

## Code Style Guidelines

We use the following tools to maintain code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For type checking

Run these tools before submitting a pull request:

```bash
black augment_adam tests
isort augment_adam tests
flake8 augment_adam tests
mypy augment_adam
```

> **Note**: If you're using the VS Code devcontainer, these tools are pre-installed and configured. VS Code will also automatically format your code on save.

## Creating a New Release

Only project maintainers can create new releases. The process is:

1. Update the version in `pyproject.toml`
2. Update the changelog
3. Create a new tag with the version number
4. Push the tag to GitHub
5. GitHub Actions will automatically build and publish the package to PyPI

## Getting Help

If you need help with contributing, please:

1. Check the existing documentation
2. Open an issue on GitHub with details about your problem

## Thank You!

Your contributions to Augment Adam are greatly appreciated. Thank you for helping make this project better!
