#!/bin/bash
# Script to start the devcontainer with BuildKit and verify volumes

set -e

echo "Starting devcontainer with BuildKit..."

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)
cd "${REPO_ROOT}/.devcontainer"

# Start the container
echo "Starting container..."
docker-compose up -d

# Verify that the volumes were created
echo "Verifying volumes..."
docker volume ls | grep -E 'dukat-(pip|apt|torch)-cache'

echo "Container started successfully!"
echo "To connect to the container, run 'Dev Containers: Reopen in Container' in VS Code"
