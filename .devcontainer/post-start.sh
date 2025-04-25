#!/bin/bash
set -e

echo "Running post-start setup..."

# Make sure scripts are executable
chmod +x /workspace/scripts/*.py 2>/dev/null || echo "Warning: Could not make scripts executable"

# Wait for Ollama service to be fully started
echo "Waiting for Ollama service to be ready..."
for i in {1..20}; do
    if curl -s http://ollama:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama service is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "Ollama service failed to start in time."
        echo "Continuing anyway..."
    fi
    echo "Waiting for Ollama service... ($i/20)"
    sleep 3
done

# Check for other services
echo "Checking for ChromaDB service..."
for i in {1..10}; do
    if curl -s http://chroma:8000/api/v1/heartbeat >/dev/null 2>&1; then
        echo "ChromaDB service is ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "ChromaDB service failed to start in time."
        echo "Continuing anyway..."
    fi
    echo "Waiting for ChromaDB service... ($i/10)"
    sleep 3
done

# Check for Neo4j
echo "Checking for Neo4j service..."
for i in {1..15}; do
    if curl -s http://neo4j:7474 >/dev/null 2>&1; then
        echo "Neo4j service is ready"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "Neo4j service failed to start in time."
        echo "Continuing anyway..."
    fi
    echo "Waiting for Neo4j service... ($i/15)"
    sleep 3
done

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected, verifying configuration..."
    nvidia-smi || echo "Failed to run nvidia-smi"
fi

# Pull required models
echo "Setting up models..."
python /workspace/scripts/setup_models.py --domains docker wsl devcontainer || echo "Warning: Failed to set up models"

# Run a simple test to verify GPU is working
if command -v nvidia-smi &> /dev/null; then
    echo "Running a simple PyTorch GPU test..."
    python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA device count:', torch.cuda.device_count()); print('CUDA device name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" || echo "Failed to run PyTorch GPU test"
fi

echo "Post-start setup completed"
