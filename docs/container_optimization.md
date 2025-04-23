# Container Optimization Guide

This document explains the optimization techniques used for Docker containers in this project.

## Caching Strategies

We use several caching strategies to speed up container builds:

### 1. Volume Caching

Named volumes are used to persist cache data between builds:

- **dukat-pip-cache**: Caches Python packages downloaded by pip
- **dukat-apt-cache**: Caches Debian packages downloaded by apt
- **dukat-torch-cache**: Caches PyTorch models and weights
- **model-cache**: Caches ML models
- **huggingface-cache**: Caches Hugging Face models and datasets
- **OllamaModels**: Caches Ollama models

These named volumes are shared between the devcontainer and test-gen container, ensuring that cached packages and models are reused across different containers.

These volumes are defined in the docker-compose.yml files and mounted into the containers.

### 2. BuildKit Cache Mounts

We use BuildKit's cache mounts in the Dockerfiles to cache package installations:

```dockerfile
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y ...
```

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install ...
```

### 3. Layer Optimization

The Dockerfiles are structured to optimize layer caching:

- Frequently changing files are added later in the Dockerfile
- Dependencies are installed before application code
- Multi-stage builds are used where appropriate

## Docker Compose Baking

"Baking" refers to pre-building container images and storing them locally. This significantly speeds up container startup times because the images don't need to be rebuilt each time.

### Build and Baking Scripts

We provide several scripts for building and baking container images:

#### Simple Build Scripts (Recommended)

- **build_devcontainer_simple.sh**: Builds the development container with BuildKit optimizations
- **bake_test_gen_simple.sh**: Builds the test generation container with BuildKit optimizations

#### Advanced Baking Scripts

- **bake_devcontainer.sh**: Bakes the development container
- **bake_test_gen.sh**: Bakes the test generation container
- **bake_all.sh**: Bakes all containers

### How Baking Works

1. The script creates a temporary docker-compose file for building the image
2. It builds the image with BuildKit optimizations
3. It updates the main docker-compose.yml to use the pre-built image
4. A backup of the original docker-compose.yml is created

### Using Baked Images

After baking, you can use the containers as usual:

- For the devcontainer: Use "Dev Containers: Reopen in Container" in VS Code
- For the test-gen container: Run the setup script: `./scripts/setup_test_gen.sh`

### Rebuilding from Scratch

If you need to rebuild the containers from scratch:

1. Restore the original docker-compose.yml from the backup
2. Rebuild the container

## Best Practices

- Run the baking scripts when you make significant changes to the Dockerfiles
- Keep the cache volumes to speed up subsequent builds
- Use the `--no-cache` flag only when you need to force a complete rebuild

## Troubleshooting

If you encounter issues with the baked images:

1. Check if the image exists: `docker images | grep dukat`
2. Restore the original docker-compose.yml from the backup
3. Try rebuilding with: `DOCKER_BUILDKIT=1 docker-compose build --no-cache`
