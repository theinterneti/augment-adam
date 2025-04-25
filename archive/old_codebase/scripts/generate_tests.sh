#!/bin/bash
# Wrapper script for the test generator

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please run scripts/setup_local_test_gen.sh first."
    exit 1
fi

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Check if the model is available
MODEL=${MODEL:-codellama:7b}
if ! ollama list | grep -q "$MODEL"; then
    echo "Model $MODEL is not available. Pulling it now..."
    ollama pull $MODEL
fi

# Run the test generator
python -m scripts.auto_test_generator "$@"
