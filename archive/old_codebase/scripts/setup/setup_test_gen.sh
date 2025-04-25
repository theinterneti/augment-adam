#!/bin/bash
# Setup script for the test generation environment

set -e

# Create necessary directories
mkdir -p models templates config

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check for GPU support
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Enabling GPU support in Docker Compose."
    # Uncomment GPU support in docker-compose.test-gen.yml
    sed -i 's/# Uncomment the following section if you have a GPU/# GPU support enabled/g' docker-compose.test-gen.yml
    sed -i 's/# resources:/resources:/g' docker-compose.test-gen.yml
    sed -i 's/#   reservations:/  reservations:/g' docker-compose.test-gen.yml
    sed -i 's/#     devices:/    devices:/g' docker-compose.test-gen.yml
    sed -i 's/#       - driver: nvidia/      - driver: nvidia/g' docker-compose.test-gen.yml
    sed -i 's/#         count: 1/        count: 1/g' docker-compose.test-gen.yml
    sed -i 's/#         capabilities: \[gpu\]/        capabilities: [gpu]/g' docker-compose.test-gen.yml
else
    echo "No NVIDIA GPU detected. Using CPU only."
fi

# Build the Docker images
echo "Building Docker images..."
docker-compose -f docker-compose.test-gen.yml build

# Pull Ollama models
echo "Pulling Ollama models..."
docker-compose -f docker-compose.test-gen.yml up -d ollama
sleep 5  # Wait for Ollama to start

# Pull the models
echo "Pulling small model (TinyLlama)..."
docker-compose -f docker-compose.test-gen.yml exec -T ollama ollama pull tinyllama:1.1b

echo "Pulling medium model (CodeLlama)..."
docker-compose -f docker-compose.test-gen.yml exec -T ollama ollama pull codellama:7b

# Ask if the user wants to pull the large model
read -p "Do you want to pull the large model (WizardCoder, 15GB)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pulling large model (WizardCoder)..."
    docker-compose -f docker-compose.test-gen.yml exec -T ollama ollama pull wizardcoder:15b
fi

# Verify GPU support
echo "Verifying GPU support..."
docker-compose -f docker-compose.test-gen.yml run --rm test-generator python /app/scripts/verify_gpu.py

# Stop the containers
docker-compose -f docker-compose.test-gen.yml down

echo "Setup complete! You can now run the test generation environment with:"
echo "docker-compose -f docker-compose.test-gen.yml up"
echo
echo "To generate tests for a module, run:"
echo "docker-compose -f docker-compose.test-gen.yml run test-generator --source-file path/to/file.py --output-dir tests/"
echo
echo "To verify GPU support again, run:"
echo "docker-compose -f docker-compose.test-gen.yml run --rm test-generator python /app/scripts/verify_gpu.py"
