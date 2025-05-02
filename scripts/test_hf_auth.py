#!/usr/bin/env python3
"""
Test Hugging Face Authentication.

This script tests authentication with Hugging Face and access to the Qwen3 model.
"""

import argparse
import os
import sys
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_hf_auth(token):
    """Test Hugging Face authentication and model access.
    
    Args:
        token: Hugging Face token
    """
    print("Logging in to Hugging Face...")
    login(token)
    
    print("Testing access to Qwen3 model...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen3-7B-Instruct", 
            trust_remote_code=True
        )
        print("Successfully loaded tokenizer!")
        
        # Don't actually load the full model as it's very large
        # Just check if we can access the config
        print("Checking model config...")
        config = AutoModelForCausalLM.config_class.from_pretrained(
            "Qwen/Qwen3-7B-Instruct",
            trust_remote_code=True
        )
        print("Successfully accessed model config!")
        print("Authentication and access test successful!")
        return True
    except Exception as e:
        print(f"Error accessing model: {e}")
        return False

def main():
    """Run the Hugging Face authentication test."""
    parser = argparse.ArgumentParser(description="Test Hugging Face authentication")
    parser.add_argument("--token", help="Hugging Face token")
    args = parser.parse_args()
    
    # Get token from args, environment, or prompt
    token = args.token
    if not token:
        token = os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        token = input("Enter your Hugging Face token: ")
    
    success = test_hf_auth(token)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
