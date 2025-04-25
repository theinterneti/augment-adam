#!/bin/bash
# Pull required models for Ollama

echo "Pulling models for Ollama..."
docker exec -it dukat-ollama ollama pull codellama:7b
docker exec -it ai-test-ollama ollama pull codellama:7b

echo "Verifying models..."
docker exec -it dukat-ollama ollama list
