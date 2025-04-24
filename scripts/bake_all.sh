#!/bin/bash
# Script to bake all container images for faster builds

set -e

echo "Baking all container images..."

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)

# Bake the devcontainer
echo "Baking devcontainer..."
"${REPO_ROOT}/scripts/bake_devcontainer.sh"

# Bake the test-gen container
echo "Baking test-gen container..."
"${REPO_ROOT}/scripts/bake_test_gen.sh"

echo "All containers baked successfully!"
echo ""
echo "To use the baked images:"
echo "1. For devcontainer: Run 'Dev Containers: Reopen in Container' in VS Code"
echo "2. For test-gen: Run the setup script: ./scripts/setup_test_gen.sh"
