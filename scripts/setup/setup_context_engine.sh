#!/bin/bash

# Setup script for the context engine

# Create necessary directories
mkdir -p api
mkdir -p worker
mkdir -p redis-config
mkdir -p neo4j-config

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
docker compose build

# Start the containers
echo "Starting containers..."
docker compose up -d

# Wait for the containers to start
echo "Waiting for containers to start..."
sleep 10

# Check if the containers are running
if docker compose ps | grep -q "Up"; then
  echo "Containers are running."
else
  echo "Containers failed to start. Please check the logs with 'docker compose logs'."
  exit 1
fi

# Create the Redis index
echo "Creating Redis index..."
docker compose exec redis-vector redis-cli -a redispassword <<EOF
FT.CREATE vector_index ON HASH PREFIX 1 vector: SCHEMA vector VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE metadata TEXT
EOF

# Create the Neo4j index
echo "Creating Neo4j index..."
docker compose exec neo4j cypher-shell -u neo4j -p neopassword <<EOF
CREATE VECTOR INDEX vector_index IF NOT EXISTS
FOR (n:Vector) ON (n.embedding)
OPTIONS {
  indexConfig: {
    \`vector.dimensions\`: 384,
    \`vector.similarity_function\`: 'cosine'
  }
}
EOF

echo "Context engine setup complete!"
echo "API is available at http://localhost:8080"
echo "Redis Insight is available at http://localhost:8001"
echo "Neo4j Browser is available at http://localhost:7474"
