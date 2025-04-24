# Development Setup Guide

This guide will help you set up your development environment for working with the Augment Adam project.

## Using VS Code Devcontainer (Recommended)

The Augment Adam project is designed to run in a VS Code devcontainer, which provides a consistent development environment with all necessary dependencies pre-installed.

### Prerequisites for Devcontainer

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

### Setting Up with Devcontainer

1. Clone the repository:

   ```bash
   git clone https://github.com/theinterneti/augment-adam.git
   cd augment-adam
   ```

2. Open the project in VS Code:

   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container".

4. VS Code will build the devcontainer and open the project inside it. This may take a few minutes the first time.

5. Once inside the devcontainer, all dependencies are already installed and the environment is ready to use.

## Manual Setup (Alternative)

If you prefer not to use the devcontainer, you can set up the development environment manually.

### Prerequisites

- Python 3.8 or higher
- Git
- Poetry (for dependency management)

### Setting Up Manually

### 1. Clone the Repository

```bash
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam
```

### 2. Install Poetry

If you don't have Poetry installed, you can install it using:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or on Windows:

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 3. Install Dependencies

```bash
# Install all dependencies including development dependencies
poetry install --with dev
```

### 4. Activate the Virtual Environment

```bash
poetry shell
```

### 5. Set Up Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/unit/test_memory.py

# Run tests with coverage report
pytest --cov=augment_adam
```

## Code Style

We follow the Black code style. You can format your code using:

```bash
black augment_adam tests
```

And check imports with:

```bash
isort augment_adam tests
```

## Building Documentation

```bash
# Install documentation dependencies
poetry install --with docs

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## Common Development Tasks

### Creating a New Feature

1. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run tests to ensure everything works:

   ```bash
   pytest
   ```

4. Format your code:

   ```bash
   black augment_adam tests
   isort augment_adam tests
   ```

5. Commit your changes:

   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

6. Push your changes:

   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a pull request on GitHub

### Updating Dependencies

To update dependencies:

```bash
poetry update
```

## Troubleshooting

### Poetry Installation Issues

If you encounter issues with Poetry, try:

```bash
poetry config virtualenvs.in-project true
poetry env remove --all
poetry install
```

### Import Errors

If you encounter import errors, make sure you're running in the Poetry virtual environment:

```bash
poetry shell
```

Or prefix your commands with `poetry run`:

```bash
poetry run pytest
```

## Getting Help

If you need help with development setup, please:

1. Check the existing documentation in the `docs/` directory
2. Open an issue on GitHub with details about your problem

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [MkDocs Documentation](https://www.mkdocs.org/)
