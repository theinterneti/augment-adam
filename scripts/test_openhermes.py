#!/usr/bin/env python3
"""
Test OpenHermes Model Access.

This script tests if we can access the OpenHermes model.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig

# Load environment variables from .env file
load_dotenv()

def test_model_access():
    """Test access to the OpenHermes model."""
    # Test access to the OpenHermes model
    model_name = "teknium/OpenHermes-2.5-Mistral-7B"
    print(f"Testing access to {model_name}...")
    try:
        print("Attempting to load tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("Successfully loaded tokenizer!")
        
        print("Attempting to load model config...")
        config = AutoConfig.from_pretrained(model_name)
        print("Successfully loaded model config!")
        
        # Try a simple tokenization
        print("Testing tokenization...")
        tokens = tokenizer.encode("Hello, world!")
        print(f"Tokenized 'Hello, world!' to {len(tokens)} tokens")
        
        print("Access test successful!")
        return True
    except Exception as e:
        print(f"Error accessing model: {e}")
        return False

if __name__ == "__main__":
    success = test_model_access()
    sys.exit(0 if success else 1)
