#!/bin/bash
# Script to build the devcontainer with optimizations

set -e

echo "Building devcontainer with optimizations..."

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)

# Check if local registry is running, start if not
if ! docker ps | grep -q registry; then
  echo "Starting local Docker registry..."
  docker run -d -p 5000:5000 --restart=always --name registry registry:2
fi

# Build the devcontainer
echo "Building devcontainer..."
cd .devcontainer
docker-compose -f docker-compose.yml.buildkit build --progress=plain

echo "Build completed successfully!"
echo "To use the container, run 'Dev Containers: Reopen in Container' in VS Code"
