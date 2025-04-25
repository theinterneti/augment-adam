# Installation Guide

This guide explains how to install and set up Augment Adam.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- Docker and Docker Compose (optional, for containerized deployment)

## Installation Methods

### Method 1: Install from PyPI

```bash
# Install the base package
pip install augment-adam

# Install with Neo4j support
pip install augment-adam[neo4j]

# Install development dependencies
pip install augment-adam[dev]
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam

# Install the package in development mode
pip install -e ".[dev]"
```

### Method 3: Using Docker

```bash
# Clone the repository
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam

# Build and run with Docker Compose
docker compose up --build
```

## Verifying Installation

To verify that Augment Adam is installed correctly, run:

```bash
python -c "import augment_adam; print(augment_adam.__version__)"
```

You should see the version number of Augment Adam printed to the console.

## Setting Up Development Environment

If you're planning to contribute to Augment Adam, follow these steps to set up your development environment:

```bash
# Clone the repository
git clone https://github.com/theinterneti/augment-adam.git
cd augment-adam

# Install development dependencies
pip install -e ".[dev]"

# Run tests to ensure everything is working
pytest
```

## Troubleshooting

### Common Issues

#### Package Not Found

If you encounter a "Package not found" error, make sure you have the latest version of pip:

```bash
pip install --upgrade pip
```

#### Dependency Conflicts

If you encounter dependency conflicts, try using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install augment-adam
```

#### Docker Issues

If you encounter issues with Docker, make sure Docker and Docker Compose are installed and running:

```bash
docker --version
docker compose --version
```

## Next Steps

After installation, check out the [Getting Started Guide](getting_started.md) to learn how to use Augment Adam.
