# GitHub Workflow Guide

This document outlines the GitHub workflow for the Augment Adam project. Following these guidelines will help maintain a clean, organized, and efficient development process.

## Branch Strategy

### Main Branches

- **`main`**: The production-ready branch. This branch should always be stable and deployable.
- **`develop`**: The integration branch for features. This is where features are combined and tested before being merged to `main`.

### Supporting Branches

- **`feature/*`**: For developing new features. Branch off from `develop` and merge back into `develop`.
  - Example: `feature/add-neo4j-integration`
- **`bugfix/*`**: For fixing bugs in the development process. Branch off from `develop` and merge back into `develop`.
  - Example: `bugfix/fix-memory-leak`
- **`hotfix/*`**: For urgent fixes to production. Branch off from `main` and merge back into both `main` and `develop`.
  - Example: `hotfix/critical-security-fix`
- **`release/*`**: For preparing releases. Branch off from `develop` and merge back into both `main` and `develop`.
  - Example: `release/v1.0.0`

## Commit Guidelines

### Commit Message Format

We follow a structured commit message format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **Type**: Describes the kind of change:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, missing semicolons, etc.)
  - `refactor`: Code refactoring
  - `test`: Adding or modifying tests
  - `chore`: Maintenance tasks

- **Scope**: The part of the codebase affected (optional)
  - Examples: `tagging`, `memory`, `agent`, `context`

- **Subject**: A short description of the change
  - Use imperative mood ("Add" not "Added")
  - Don't capitalize the first letter
  - No period at the end

- **Body**: Detailed explanation of the change (optional)
  - Explain the motivation for the change
  - Contrast with previous behavior

- **Footer**: References to issues, breaking changes, etc. (optional)
  - Reference issues: `Fixes #123`
  - Breaking changes: `BREAKING CHANGE: <description>`

### Examples

```
feat(memory): add support for Redis-based vector storage

Implement Redis as an alternative backend for vector storage to improve scalability.
The implementation uses Redis' vector search capabilities for efficient similarity search.

Fixes #456
```

```
fix(tagging): resolve issue with tag hashability

Tags were not properly hashable, causing errors when used as dictionary keys.
This fix implements proper __hash__ and __eq__ methods.

Fixes #789
```

## Pull Request Process

1. **Create a Pull Request (PR)** from your feature/bugfix branch to the appropriate target branch.
2. **Fill out the PR template** with all relevant information.
3. **Request reviews** from appropriate team members.
4. **Address review comments** and make necessary changes.
5. **Ensure all CI checks pass** before merging.
6. **Merge the PR** once approved.
7. **Delete the branch** after merging.

## Release Process

1. **Create a release branch** from `develop` named `release/vX.Y.Z`.
2. **Update version numbers** in all relevant files.
3. **Update CHANGELOG.md** with all changes since the last release.
4. **Create a PR** from the release branch to `main`.
5. **After merging to main**, tag the release with `vX.Y.Z`.
6. **Merge the release branch back to develop** to incorporate any release-specific changes.

## CI/CD Pipeline

Our CI/CD pipeline includes:

1. **Linting and Code Style Checks**: Ensures code follows our style guidelines.
2. **Unit Tests**: Verifies individual components work as expected.
3. **Integration Tests**: Ensures components work together correctly.
4. **Build Checks**: Verifies the package builds correctly.
5. **Documentation Generation**: Automatically generates and publishes documentation.

## Best Practices

- **Keep branches short-lived**: Merge or delete branches promptly.
- **Rebase frequently**: Keep your branch up-to-date with the target branch.
- **Write meaningful commit messages**: Help others understand your changes.
- **Include tests**: Add tests for new features and bug fixes.
- **Update documentation**: Keep documentation in sync with code changes.
- **Review your own code**: Self-review before requesting reviews from others.
- **Keep PRs focused**: Each PR should address a single concern.

## Tools and Setup

### Git Configuration

Set up the commit message template:

```bash
git config --global commit.template .gitmessage
```

### Pre-commit Hooks

Install and set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

### GitHub CLI

Install GitHub CLI for easier PR management:

```bash
# For macOS
brew install gh

# For Linux
sudo apt install gh

# For Windows
winget install GitHub.cli
```

## Additional Resources

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
