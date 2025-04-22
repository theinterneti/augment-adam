#!/bin/bash
set -e

# Print Docker version information
echo "Docker version information:"
docker version --format '{{.Server.Version}}' 2>/dev/null || echo "Docker not available"

# Start Ollama service if it exists
if command -v ollama &> /dev/null; then
    echo "Starting Ollama service..."
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "Ollama is already running"
    else
        echo "Starting Ollama server..."
        # Start Ollama in the background and redirect output to a log file
        nohup ollama serve > /tmp/ollama.log 2>&1 &

        # Wait for Ollama to start
        echo "Waiting for Ollama to start..."
        for i in {1..15}; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                echo "Ollama started successfully"
                break
            fi
            if [ $i -eq 15 ]; then
                echo "Ollama failed to start in time. Check /tmp/ollama.log for details."
                cat /tmp/ollama.log || echo "Log file not found"
            fi
            echo "Waiting for Ollama to start... ($i/15)"
            sleep 2
        done
    fi

    # List available models
    echo "Available Ollama models:"
    curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' || echo "No models found or Ollama not running"
fi

# Print volume information
echo "\nVolume information:"
docker volume ls | grep -E 'OllamaModels|model-cache|huggingface-cache' || echo "No relevant volumes found"

# Execute the command passed to docker run
exec "$@"
