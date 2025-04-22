#!/bin/bash
set -e

echo "Running post-start setup..."

# Make sure scripts are executable
chmod +x /workspace/scripts/*.py 2>/dev/null || echo "Warning: Could not make scripts executable"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing now..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama installed. Starting service..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
fi

# Wait for Ollama to be fully started
echo "Waiting for Ollama to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "Ollama failed to start in time. Check /tmp/ollama.log for details."
        cat /tmp/ollama.log 2>/dev/null || echo "Log file not found"
        echo "Continuing anyway..."
    fi
    echo "Waiting for Ollama... ($i/20)"
    sleep 3
done

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected, configuring Ollama for GPU usage..."
    # Set Ollama to use GPU
    export OLLAMA_HOST=0.0.0.0
    export OLLAMA_KEEP_ALIVE=1h
    # Restart Ollama to apply settings
    pkill ollama || echo "No Ollama process to kill"
    sleep 2
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    echo "Waiting for Ollama to restart..."
    sleep 5

    # Verify Ollama is using GPU
    echo "Verifying Ollama GPU configuration..."
    curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && echo "Ollama restarted successfully" || echo "Warning: Ollama may not have restarted properly"
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
