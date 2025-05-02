#!/usr/bin/env python3
"""
Test Mistral Model Access.

This script tests if we can access the Mistral model.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig

# Load environment variables from .env file
load_dotenv()

def test_mistral_access():
    """Test access to the Mistral model."""
    # Get the token from environment variables
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN not found in environment variables")
        return False
    
    print(f"Using token: {token[:5]}...{token[-5:]}")
    
    # Test access to the Mistral model
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
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
        print(f"Error accessing Mistral model: {e}")
        return False

if __name__ == "__main__":
    success = test_mistral_access()
    sys.exit(0 if success else 1)
