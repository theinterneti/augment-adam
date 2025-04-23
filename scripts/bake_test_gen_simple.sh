#!/bin/bash
# Simple script to build the test-gen container with BuildKit

set -e

echo "Building test-gen container with BuildKit..."

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)

# Build the image
echo "Building image..."
docker-compose -f docker-compose.test-gen.yml build --progress=plain

echo "Build completed successfully!"
echo "To use the container, run the setup script: ./scripts/setup_test_gen.sh"
