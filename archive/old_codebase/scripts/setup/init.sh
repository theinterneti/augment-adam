#!/bin/bash
# Initialize the Dukat project

set -e

echo "Initializing Dukat: Augment Linux Assistant..."

# Create directories if they don't exist
mkdir -p src/{commands,models,views,utils} tests frameworks models

# Make Python scripts executable
chmod +x src/models/*.py
chmod +x scripts/*.py
chmod +x tests/*.py

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "Docker is installed."
else
    echo "Docker is not installed. Please install Docker to use the devcontainer."
    exit 1
fi

# Check if VS Code is installed
if command -v code &> /dev/null; then
    echo "VS Code is installed."
else
    echo "VS Code is not installed. Please install VS Code to use the devcontainer."
    exit 1
fi

echo "Initialization complete!"
echo "To start development:"
echo "1. Open this folder in VS Code"
echo "2. When prompted, click 'Reopen in Container'"
echo "3. Wait for the devcontainer to build and start"
echo ""
echo "Or run: code ."
