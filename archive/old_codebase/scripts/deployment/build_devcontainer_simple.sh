#!/bin/bash
# Simple script to build the devcontainer with BuildKit

set -e

echo "Building devcontainer with BuildKit..."

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)
cd "${REPO_ROOT}/.devcontainer"

# Build the image
echo "Building image..."
docker-compose build --progress=plain

echo "Build completed successfully!"
echo "To use the container, run 'Dev Containers: Reopen in Container' in VS Code"
