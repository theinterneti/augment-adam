#!/bin/bash
# Setup script for Hugging Face models
# This script downloads and sets up Hugging Face models for test generation

set -e  # Exit on error

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== HUGGING FACE MODEL SETUP ==========${NC}"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version | cut -d' ' -f2)
echo -e "${GREEN}Python version: ${PYTHON_VERSION}${NC}"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip is not installed${NC}"
    exit 1
fi

# Create directories
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p .cache/huggingface
mkdir -p .cache/models
mkdir -p logs

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install torch transformers accelerate bitsandbytes optimum

# Check if CUDA is available
echo -e "${GREEN}Checking for CUDA...${NC}"
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    echo -e "${GREEN}CUDA is available${NC}"
    CUDA_AVAILABLE=true
else
    echo -e "${YELLOW}CUDA is not available, using CPU${NC}"
    CUDA_AVAILABLE=false
fi

# Download models
echo -e "${GREEN}Downloading models...${NC}"

# Function to download a model
download_model() {
    MODEL_NAME=$1
    TRUST_REMOTE_CODE=$2

    echo -e "${GREEN}Downloading ${MODEL_NAME}...${NC}"

    if [ "$TRUST_REMOTE_CODE" = "true" ]; then
        echo -e "${YELLOW}Using trust_remote_code=True for ${MODEL_NAME}${NC}"
        python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; tokenizer = AutoTokenizer.from_pretrained('${MODEL_NAME}', cache_dir='.cache/huggingface', trust_remote_code=True); model = AutoModelForCausalLM.from_pretrained('${MODEL_NAME}', cache_dir='.cache/huggingface', trust_remote_code=True)"
    else
        python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; tokenizer = AutoTokenizer.from_pretrained('${MODEL_NAME}', cache_dir='.cache/huggingface'); model = AutoModelForCausalLM.from_pretrained('${MODEL_NAME}', cache_dir='.cache/huggingface')"
    fi

    echo -e "${GREEN}Downloaded ${MODEL_NAME}${NC}"
}

# Download models based on available resources
if [ "$CUDA_AVAILABLE" = true ]; then
    # Download Qwen models if CUDA is available
    echo -e "${GREEN}Downloading Qwen 2 models for code generation...${NC}"
    download_model "Qwen/Qwen2-7B-Instruct"

    # Check if we have enough VRAM for larger models
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | awk '{s+=$1} END {print s}')
    if [ $VRAM -gt 24000 ]; then
        echo -e "${GREEN}Sufficient VRAM available, downloading larger Qwen model...${NC}"
        download_model "Qwen/Qwen2.5-14B-Instruct"
    else
        echo -e "${YELLOW}Limited VRAM available, using smaller Qwen model${NC}"
    fi
else
    # Download smaller models for CPU
    echo -e "${GREEN}Downloading smaller Qwen model for CPU...${NC}"
    download_model "Qwen/Qwen2-1.5B-Instruct"
fi

# Create a model config file
echo -e "${GREEN}Creating model config file...${NC}"
cat > config/model_config.json << EOL
{
    "models": {
        "small": {
            "name": "Qwen/Qwen2-1.5B-Instruct",
            "requires_gpu": false,
            "min_vram_mb": 2000,
            "description": "Small Qwen model for basic test generation"
        },
        "medium": {
            "name": "Qwen/Qwen2-7B-Instruct",
            "requires_gpu": true,
            "min_vram_mb": 8000,
            "description": "Medium-sized Qwen model for comprehensive test generation"
        },
        "large": {
            "name": "Qwen/Qwen2.5-14B-Instruct",
            "requires_gpu": true,
            "min_vram_mb": 16000,
            "description": "Large Qwen model for advanced test generation"
        }
    },
    "default_model": "medium",
    "cache_dir": ".cache/huggingface",
    "use_gpu": $CUDA_AVAILABLE
}
EOL

echo -e "${GREEN}Model config file created at config/model_config.json${NC}"

# Create a test script
echo -e "${GREEN}Creating test script...${NC}"
cat > scripts/test_huggingface_models.py << EOL
#!/usr/bin/env python3
"""
Test Hugging Face models.

This script tests the Hugging Face models to ensure they are working correctly.
"""

import json
import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model(model_name):
    """Test a Hugging Face model."""
    print(f"Testing model: {model_name}")

    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=".cache/huggingface")
    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=".cache/huggingface")

    # Test the model
    prompt = "def add(a, b):\\n    return a + b\\n\\n# Write a test for this function"
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate text
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode the generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"Generated text:\\n{generated_text}")
    print("Model test successful")

def main():
    """Run the model tests."""
    # Load the model config
    with open("config/model_config.json", "r") as f:
        config = json.load(f)

    # Test the default model
    default_model = config["models"][config["default_model"]]["name"]
    test_model(default_model)

if __name__ == "__main__":
    main()
EOL

chmod +x scripts/test_huggingface_models.py
echo -e "${GREEN}Test script created at scripts/test_huggingface_models.py${NC}"

# Create the config directory if it doesn't exist
mkdir -p config

# Create a test generation config file
echo -e "${GREEN}Creating test generation config file...${NC}"
cat > config/test_generator_config.json << EOL
{
    "models": {
        "small": {
            "name": "Qwen/Qwen2-1.5B-Instruct",
            "requires_gpu": false,
            "min_vram_mb": 2000,
            "description": "Small Qwen model for basic test generation",
            "temperature": 0.7,
            "max_length": 1024
        },
        "medium": {
            "name": "Qwen/Qwen2-7B-Instruct",
            "requires_gpu": true,
            "min_vram_mb": 8000,
            "description": "Medium-sized Qwen model for comprehensive test generation",
            "temperature": 0.2,
            "max_length": 2048
        },
        "large": {
            "name": "Qwen/Qwen2.5-14B-Instruct",
            "requires_gpu": true,
            "min_vram_mb": 16000,
            "description": "Large Qwen model for advanced test generation",
            "temperature": 0.1,
            "max_length": 4096
        }
    },
    "default_model": "medium",
    "cache_dir": ".cache/huggingface",
    "use_gpu": $CUDA_AVAILABLE,
    "test_types": ["unit", "integration", "property"],
    "test_frameworks": ["pytest", "hypothesis"],
    "merge_existing_tests": true,
    "update_tasks_file": true,
    "resource_monitoring": {
        "enabled": true,
        "threshold": 0.8,
        "check_interval": 5.0
    },
    "background_service": {
        "enabled": true,
        "watch_interval": 2.0,
        "max_concurrent_tests": 2
    }
}
EOL

echo -e "${GREEN}Test generation config file created at config/test_generator_config.json${NC}"

# Test the setup
echo -e "${GREEN}Testing the setup...${NC}"
if [ -f "scripts/test_huggingface_models.py" ]; then
    python scripts/test_huggingface_models.py
else
    echo -e "${RED}Error: Test script not found${NC}"
    exit 1
fi

echo -e "${BLUE}========== HUGGING FACE MODEL SETUP COMPLETE ==========${NC}"
echo ""
echo -e "${GREEN}You can now use the Hugging Face models for test generation.${NC}"
echo -e "${GREEN}To start the background test service, run:${NC}"
echo -e "${YELLOW}python scripts/background_test_service.py${NC}"
echo ""
