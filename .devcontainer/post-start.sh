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

# Pull required models
echo "Setting up models..."
python /workspace/scripts/setup_models.py --domains docker wsl devcontainer || echo "Warning: Failed to set up models"

echo "Post-start setup completed"
