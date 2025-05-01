#!/bin/bash
set -e

echo "Cleaning up Docker containers and volumes..."

# Stop and remove all containers related to the project
echo "Stopping and removing containers..."
docker compose -f .devcontainer/docker-compose.yml down || true

# Remove any existing devcontainer for this project
echo "Removing existing devcontainers..."
docker ps -a | grep augment-adam_devcontainer | awk '{print $1}' | xargs -r docker rm -f || true

# Clean up any dangling volumes
echo "Cleaning up dangling volumes..."
docker volume ls -qf dangling=true | xargs -r docker volume rm || true

# Clean up any dangling images
echo "Cleaning up dangling images..."
docker image prune -f || true

echo "Cleanup complete!"
echo "You can now try rebuilding the devcontainer."
