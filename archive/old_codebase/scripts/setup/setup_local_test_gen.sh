#!/bin/bash
# Setup script for local test generation environment (without docker-compose)

set -e

echo "Setting up local test generation environment..."

# Create necessary directories
mkdir -p models templates config

# Check if GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. GPU acceleration will be used."
    nvidia-smi
else
    echo "No NVIDIA GPU detected or nvidia-smi not in path. Using CPU only."
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements-test-gen.txt
pip install pynguin hypothesis pytest pytest-cov

# Install Ollama directly in the container
echo "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    # Wait for Ollama service to start
    echo "Waiting for Ollama service to start..."
    sleep 5
else
    echo "Ollama is already installed."
fi

# Start Ollama service
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
echo "Ollama started with PID: $OLLAMA_PID"

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 5

# Pull models
echo "Pulling models..."
echo "Pulling small model (TinyLlama)..."
ollama pull tinyllama:1.1b

echo "Pulling medium model (CodeLlama)..."
ollama pull codellama:7b

# Ask if the user wants to pull the large model
read -p "Do you want to pull the large model (WizardCoder, 15GB)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pulling large model (WizardCoder)..."
    ollama pull wizardcoder:15b
fi

# Create a simple script to run the test generator
cat > run_test_gen.sh << 'EOF'
#!/bin/bash
# Run the test generator

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Run the test generator
python -m scripts.auto_test_generator "$@"
EOF

chmod +x run_test_gen.sh

echo "Setup complete!"
echo "You can now generate tests using:"
echo "./run_test_gen.sh --source-file path/to/file.py --output-dir tests/ --model codellama:7b"
echo
echo "Available models:"
ollama list

# Keep Ollama running in the background
echo "Ollama is running in the background. To stop it, run: pkill ollama"
