#!/bin/bash
# Script to bake the devcontainer image for faster builds

set -e

echo "Baking devcontainer image..."

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)

# Define image name and tag
IMAGE_NAME="dukat-devcontainer"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Create a temporary docker-compose file for baking
BAKE_COMPOSE_FILE="${REPO_ROOT}/.devcontainer/docker-compose.bake.yml"

cat > "${BAKE_COMPOSE_FILE}" << EOL
version: '3.8'

services:
  dev:
    image: ${FULL_IMAGE_NAME}
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILDKIT_INLINE_CACHE: 1
    volumes:
      - pip-cache:/root/.cache/pip:cached
      - apt-cache:/var/cache/apt:cached
      - torch-cache:/root/.cache/torch:cached

volumes:
  pip-cache:
  apt-cache:
  torch-cache:
EOL

echo "Created temporary docker-compose file for baking"
echo "Building image ${FULL_IMAGE_NAME}..."

# Build the image
cd "${REPO_ROOT}/.devcontainer"

# Enable BuildKit
echo "Building with BuildKit..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build the image
docker-compose -f docker-compose.bake.yml build --progress=plain

echo "Image built successfully!"

# Update the main docker-compose.yml to use the baked image
MAIN_COMPOSE_FILE="${REPO_ROOT}/.devcontainer/docker-compose.yml"
TEMP_COMPOSE_FILE="${REPO_ROOT}/.devcontainer/docker-compose.yml.tmp"

# Create a backup of the original file
cp "${MAIN_COMPOSE_FILE}" "${MAIN_COMPOSE_FILE}.backup"

# Update the docker-compose.yml to use the baked image
sed "/build:/,/dockerfile: Dockerfile/c\    image: ${FULL_IMAGE_NAME}" "${MAIN_COMPOSE_FILE}" > "${TEMP_COMPOSE_FILE}"
mv "${TEMP_COMPOSE_FILE}" "${MAIN_COMPOSE_FILE}"

echo "Updated docker-compose.yml to use the baked image"
echo "Baking completed successfully!"
echo ""
echo "To use the baked image, run 'Dev Containers: Reopen in Container' in VS Code"
echo "To rebuild from scratch, restore the original docker-compose.yml from .devcontainer/docker-compose.yml.backup"
