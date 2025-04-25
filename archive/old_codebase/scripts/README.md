# Augment Adam Scripts

This directory contains utility scripts for development, testing, and deployment of Augment Adam.

## Directory Structure

- **setup/**: Scripts for setting up the development environment
  - `setup_environment.sh`: Sets up the basic development environment
  - `setup_context_engine.sh`: Sets up the context engine
  - `setup_mcp_context_engine.sh`: Sets up the MCP context engine
  - `configure_services.sh`: Configures services like Neo4j and Redis
  - `init.sh`: Initializes the project
  - `pull_models.sh`: Downloads required models
  - `setup_models.py`: Sets up models for use with Augment Adam

- **test_utils/**: Scripts for testing
  - `test_cuda.py`: Tests CUDA availability
  - `test_context_engine.py`: Tests the context engine
  - `verify_gpu.py`: Verifies GPU availability
  - `verify_pytorch_gpu.py`: Verifies PyTorch GPU support
  - `test_devcontainer_gpu.py`: Tests GPU support in the devcontainer
  - `run_tests.sh`: Runs the test suite

- **deployment/**: Scripts for deployment
  - `bake_all.sh`: Bakes all Docker images
  - `bake_devcontainer.sh`: Bakes the devcontainer image
  - `bake_test_gen.sh`: Bakes the test generator image
  - `build_devcontainer.sh`: Builds the devcontainer
  - `docker-compose.yml`: Docker Compose configuration
  - `docker-compose.test-gen.yml`: Docker Compose configuration for test generation
  - `start_devcontainer.sh`: Starts the devcontainer

- **migration/**: Scripts for migration
  - `migrate.py`: Migrates code from dukat to augment_adam
  - `migrate_structure.sh`: Migrates the directory structure
  - `update_docs.py`: Updates documentation references
  - `update_imports.py`: Updates import statements
  - `update_test_imports.py`: Updates import statements in tests

- **monitoring/**: Scripts for monitoring (to be implemented)

## Usage

Most scripts can be run directly from the command line. For example:

```bash
# Set up the development environment
./scripts/setup/setup_environment.sh

# Run tests
./scripts/test_utils/run_tests.sh

# Deploy with Docker
./scripts/deployment/bake_all.sh
```

## Contributing

If you create a new script, please add it to the appropriate directory and update this README.md file.
