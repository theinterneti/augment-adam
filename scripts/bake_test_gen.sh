#!/bin/bash
# Script to bake the test-gen container image for faster builds

set -e

echo "Baking test-gen container image..."

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Set the build context
cd "$(dirname "$0")/.."
REPO_ROOT=$(pwd)

# Define image name and tag
IMAGE_NAME="dukat-test-gen"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Create a temporary docker-compose file for baking
BAKE_COMPOSE_FILE="${REPO_ROOT}/docker-compose.test-gen.bake.yml"

cat > "${BAKE_COMPOSE_FILE}" << EOL
version: '3'

services:
  test-generator:
    image: ${FULL_IMAGE_NAME}
    build:
      context: .
      dockerfile: Dockerfile.test-gen
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
docker-compose -f docker-compose.test-gen.bake.yml build --progress=plain

echo "Image built successfully!"

# Update the main docker-compose.yml to use the baked image
MAIN_COMPOSE_FILE="${REPO_ROOT}/docker-compose.test-gen.yml"
TEMP_COMPOSE_FILE="${REPO_ROOT}/docker-compose.test-gen.yml.tmp"

# Create a backup of the original file
cp "${MAIN_COMPOSE_FILE}" "${MAIN_COMPOSE_FILE}.backup"

# Update the docker-compose.yml to use the baked image
sed "/build:/,/dockerfile: Dockerfile.test-gen/c\    image: ${FULL_IMAGE_NAME}" "${MAIN_COMPOSE_FILE}" > "${TEMP_COMPOSE_FILE}"
mv "${TEMP_COMPOSE_FILE}" "${MAIN_COMPOSE_FILE}"

echo "Updated docker-compose.test-gen.yml to use the baked image"
echo "Baking completed successfully!"
echo ""
echo "To use the baked image, run the setup script: ./scripts/setup_test_gen.sh"
echo "To rebuild from scratch, restore the original docker-compose.yml from docker-compose.test-gen.yml.backup"
