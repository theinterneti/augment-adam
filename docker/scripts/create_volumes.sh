#!/bin/bash
# Script to create required Docker volumes for Augment Adam

set -e

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating required Docker volumes for Augment Adam...${NC}"

# Create volumes with specific names
docker volume create augment-adam-ollama-models || echo "Volume already exists"
docker volume create augment-adam-model-cache || echo "Volume already exists"
docker volume create augment-adam-huggingface-cache || echo "Volume already exists"
docker volume create augment-adam-pip-cache || echo "Volume already exists"
docker volume create augment-adam-apt-cache || echo "Volume already exists"
docker volume create augment-adam-torch-cache || echo "Volume already exists"
docker volume create augment-adam-chroma-data || echo "Volume already exists"
docker volume create augment-adam-neo4j-data || echo "Volume already exists"
docker volume create augment-adam-redis-data || echo "Volume already exists"
docker volume create augment-adam-redis-vector-data || echo "Volume already exists"

echo -e "${GREEN}Docker volumes created successfully.${NC}"
docker volume ls | grep augment-adam
