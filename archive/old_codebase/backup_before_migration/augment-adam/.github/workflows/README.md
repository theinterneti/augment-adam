# Augment Adam CI/CD Workflows

This directory contains GitHub Actions workflows for the Augment Adam project.

## Workflows

### CI Workflow (`ci.yml`)

The CI workflow runs on every push to main, feature/_, and release/_ branches, as well as on pull requests to main. It includes:

- **Code Quality Checks**: Runs Black, isort, flake8, and mypy to ensure code quality.
- **Unit Tests**: Runs unit tests and uploads coverage reports.
- **Integration Tests**: Runs integration tests.
- **Performance Tests**: Runs performance tests on pull requests.
- **Compatibility Tests**: Runs compatibility tests on pull requests with multiple Python versions.
- **Build**: Builds the package and uploads it as an artifact.

### CD Workflow (`cd.yml`)

The CD workflow runs when a new release is created. It includes:

- **Deploy to PyPI**: Builds and publishes the package to PyPI.
- **Docker**: Builds and pushes the Docker image to DockerHub.

### Scheduled Tests Workflow (`scheduled-tests.yml`)

The scheduled tests workflow runs every day at 2 AM UTC. It includes:

- **Full Test Suite**: Runs all tests and uploads coverage reports.
- **Notification**: Sends a Slack notification if tests fail.

### Security Checks Workflow (`security.yml`)

The security checks workflow runs on pushes to main, pull requests to main, and every Monday at 1 AM UTC. It includes:

- **Dependency Scanning**: Checks dependencies for vulnerabilities.
- **Code Scanning**: Scans code for security issues.
- **Secret Scanning**: Checks for secrets in the codebase.

### Documentation Workflow (`docs.yml`)

The documentation workflow runs on pushes to main and pull requests to main that affect documentation. It includes:

- **Build Documentation**: Builds the documentation.
- **Deploy Documentation**: Deploys the documentation to GitHub Pages.

### Dependencies Workflow (`dependencies.yml`)

The dependencies workflow runs every Monday at 3 AM UTC. It includes:

- **Update Dependencies**: Updates dependencies and creates a pull request.

## Required Secrets

The following secrets need to be set in the repository settings:

- `PYPI_TOKEN`: API token for PyPI publishing.
- `DOCKER_USERNAME`: Docker Hub username.
- `DOCKER_PASSWORD`: Docker Hub password or access token.
- `SLACK_WEBHOOK_URL`: Webhook URL for Slack notifications.

## Local Development

For local development, you can use Docker Compose:

```bash
docker-compose up
```

This will start the application and run the tests.
