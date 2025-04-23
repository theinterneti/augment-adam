#!/bin/bash

# Setup script for the MCP-enabled context engine

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version > /dev/null 2>&1; then
  echo "Docker Compose is not installed. Please install Docker Compose and try again."
  exit 1
fi

# Pull the necessary Docker images
echo "Pulling Docker images..."
docker pull redis/redis-stack:latest
docker pull neo4j:5.13.0

# Build the Docker images
echo "Building Docker images..."
docker compose -f mcp-context-engine-docker-compose.yml build

# Start the containers
echo "Starting containers..."
docker compose -f mcp-context-engine-docker-compose.yml up -d

# Wait for the containers to start
echo "Waiting for containers to start..."
sleep 10

# Check if the containers are running
if docker compose -f mcp-context-engine-docker-compose.yml ps | grep -q "Up"; then
  echo "Containers are running."
else
  echo "Containers failed to start. Please check the logs with 'docker compose -f mcp-context-engine-docker-compose.yml logs'."
  exit 1
fi

echo "MCP-enabled context engine setup complete!"
echo "API is available at http://localhost:8080"
echo "MCP server is available at http://localhost:8080/mcp"
echo "API documentation is available at http://localhost:8080/docs"
echo "Redis Insight is available at http://localhost:8001"
echo "Neo4j Browser is available at http://localhost:7474"
