#!/usr/bin/env python3
"""
Test Qwen3 Access.

This script tests if we can access the Qwen3 model with the provided token.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import AutoTokenizer, AutoConfig

# Load environment variables from .env file
load_dotenv()

def test_qwen3_access():
    """Test access to the Qwen3 model."""
    # Get the token from environment variables
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN not found in environment variables")
        return False

    print(f"Using token: {token[:5]}...{token[-5:]}")

    # We'll use the token directly instead of logging in
    print("Using token directly without login...")

    # Test access to the Qwen3 model
    print("Testing access to Qwen3 model...")
    try:
        print("Attempting to load tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen3-7B-Instruct",
            trust_remote_code=True,
            token=token
        )
        print("Successfully loaded tokenizer!")

        print("Attempting to load model config...")
        config = AutoConfig.from_pretrained(
            "Qwen/Qwen3-7B-Instruct",
            trust_remote_code=True,
            token=token
        )
        print("Successfully loaded model config!")

        print("Access test successful!")
        return True
    except Exception as e:
        print(f"Error accessing Qwen3 model: {e}")
        return False

if __name__ == "__main__":
    success = test_qwen3_access()
    sys.exit(0 if success else 1)
