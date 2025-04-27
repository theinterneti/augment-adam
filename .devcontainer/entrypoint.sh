#!/bin/bash
set -e

# Print Docker version information
echo "Docker version information:"
docker version --format '{{.Server.Version}}' 2>/dev/null || echo "Docker not available"

# Install dependencies using Poetry if pyproject.toml exists
if [ -f /workspace/pyproject.toml ]; then
    echo "Found pyproject.toml, installing dependencies with Poetry..."
    cd /workspace
    poetry install --no-interaction --no-ansi || echo "Poetry install completed with warnings/errors"
    echo "Poetry dependencies installed successfully"
else
    echo "No pyproject.toml found, skipping Poetry install"
fi

# Check for Ollama service
echo "Checking for Ollama service..."
# We'll check the Ollama service in the docker-compose network
if curl -s http://ollama:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama service is available"

    # List available models
    echo "Available Ollama models:"
    curl -s http://ollama:11434/api/tags | grep -o '"name":"[^"]*"' || echo "No models found"
else
    echo "Ollama service is not yet available. It will be checked again during post-start."
fi

# Check for NVIDIA GPU availability
echo -e "\nChecking for NVIDIA GPU:"
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected:"
    nvidia-smi

    # Check PyTorch CUDA availability
    echo -e "\nChecking PyTorch CUDA availability:"
    if [ -f /workspace/scripts/verify_pytorch_gpu.py ]; then
        python /workspace/scripts/verify_pytorch_gpu.py || echo "GPU verification script completed with errors"
    else
        python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA device count:', torch.cuda.device_count()); print('CUDA device name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" || echo "Failed to check PyTorch CUDA availability"
    fi
else
    echo "NVIDIA GPU not detected or nvidia-smi not available"
fi

# Print volume information
echo -e "\nVolume information:"
docker volume ls | grep -E 'ollama-models|model-cache|huggingface-cache|augment-adam' || echo "No relevant volumes found"

# Execute the command passed to docker run
exec "$@"
