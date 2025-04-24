#!/bin/bash
# Set up the Dukat environment

set -e  # Exit on error

echo "Setting up Dukat environment..."

# Pull required Docker images
echo "Pulling Docker images..."
docker pull nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
docker pull ollama/ollama:latest
docker pull chromadb/chroma:latest
docker pull neo4j:5.13.0
docker pull redis:latest

# Build and start the main development environment
echo "Building and starting development environment..."
DOCKER_BUILDKIT=1 docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
docker-compose up -d dukat-ollama dukat-chroma dukat-neo4j dukat-redis
docker-compose up -d dukat-dev

# Build and start the test environment
echo "Building and starting test environment..."
DOCKER_BUILDKIT=1 docker-compose -f docker-compose.test-gen.yml build --build-arg BUILDKIT_INLINE_CACHE=1
docker-compose -f docker-compose.test-gen.yml up -d ai-test-ollama
docker-compose -f docker-compose.test-gen.yml up -d dukat-test-generator

# Verify the containers are running
echo "Verifying containers..."
docker-compose ps
docker-compose -f docker-compose.test-gen.yml ps

echo "Environment setup complete!"
echo "Run ./pull_models.sh to pull required models for Ollama."
