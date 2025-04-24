#!/usr/bin/env python3
"""
Setup Models Script for Dukat

This script pulls the required models for the Dukat assistant.
It's designed to be run after the container starts to ensure all models are available.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the models we want to use
REQUIRED_MODELS = {
    "docker": ["codellama:7b-instruct", "llama3:8b"],
    "wsl": ["llama3:8b", "mistral:7b-instruct-v0.2"],
    "devcontainer": ["codellama:7b-instruct", "llama3:8b"],
    "general": ["llama3:8b"]
}

def run_command(cmd: List[str]) -> tuple:
    """Run a shell command and return stdout, stderr, and return code."""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def get_available_models() -> List[str]:
    """Get a list of available Ollama models."""
    try:
        # Check if Ollama is running
        _, _, rc = run_command(["curl", "-s", "http://localhost:11434/api/tags"])
        if rc != 0:
            logger.error("Ollama is not running. Please start Ollama first.")
            return []
        
        # Get the list of models
        stdout, _, rc = run_command(["curl", "-s", "http://localhost:11434/api/tags"])
        if rc != 0 or not stdout:
            return []
        
        # Parse the JSON response
        try:
            data = json.loads(stdout)
            return [model["name"] for model in data.get("models", [])]
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Ollama response: {stdout}")
            return []
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []

def pull_model(model_name: str) -> bool:
    """Pull a model using Ollama."""
    logger.info(f"Pulling model: {model_name}")
    stdout, stderr, rc = run_command(["ollama", "pull", model_name])
    
    if rc != 0:
        logger.error(f"Failed to pull model {model_name}: {stderr}")
        return False
    
    logger.info(f"Successfully pulled model: {model_name}")
    return True

def setup_models(domains: List[str] = None, force: bool = False) -> None:
    """Set up the required models for the specified domains."""
    if domains is None:
        domains = ["general"]
    
    # Get the list of available models
    available_models = get_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Determine which models to pull
    models_to_pull = set()
    for domain in domains:
        if domain in REQUIRED_MODELS:
            models_to_pull.update(REQUIRED_MODELS[domain])
    
    # Pull the required models
    for model in models_to_pull:
        if model not in available_models or force:
            pull_model(model)
        else:
            logger.info(f"Model {model} is already available")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Set up models for Dukat")
    parser.add_argument("--domains", nargs="+", choices=["docker", "wsl", "devcontainer", "general"],
                        default=["general"], help="Domains to set up models for")
    parser.add_argument("--force", action="store_true", help="Force pull models even if they are already available")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Wait for Ollama to start
    for i in range(5):
        stdout, _, rc = run_command(["curl", "-s", "http://localhost:11434/api/tags"])
        if rc == 0:
            break
        logger.info(f"Waiting for Ollama to start... ({i+1}/5)")
        time.sleep(2)
    
    # Set up the models
    setup_models(args.domains, args.force)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
