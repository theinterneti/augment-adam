#!/usr/bin/env python3
"""
Repository Selector for Augment Linux Assistant

This script automatically selects and clones appropriate repositories based on
project requirements and framework preferences.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

# Define framework options with their repositories
FRAMEWORKS = {
    "vscode-extension": {
        "base": "https://github.com/microsoft/vscode-extension-samples.git",
        "examples": [
            "https://github.com/microsoft/vscode-extension-samples.git",
            "https://github.com/microsoft/vscode-extension-templates.git"
        ],
        "description": "VS Code Extension development framework"
    },
    "langchain": {
        "base": "https://github.com/langchain-ai/langchain.git",
        "examples": [
            "https://github.com/langchain-ai/langchainjs.git",
            "https://github.com/langchain-ai/langchain-examples.git"
        ],
        "description": "Framework for building applications with LLMs"
    },
    "llama-index": {
        "base": "https://github.com/run-llama/llama_index.git",
        "examples": [
            "https://github.com/run-llama/llama_index.git",
            "https://github.com/run-llama/llama-hub.git"
        ],
        "description": "Data framework for LLM applications"
    },
    "ollama": {
        "base": "https://github.com/ollama/ollama.git",
        "examples": [
            "https://github.com/ollama/ollama-js.git",
            "https://github.com/ollama/ollama-python.git"
        ],
        "description": "Run open-source large language models locally"
    }
}

# Define model options
MODELS = {
    "llama3": {
        "repo": "https://huggingface.co/meta-llama/Meta-Llama-3-8B",
        "ollama": "llama3",
        "description": "Meta's Llama 3 model (8B parameters)"
    },
    "mistral": {
        "repo": "https://huggingface.co/mistralai/Mistral-7B-v0.1",
        "ollama": "mistral",
        "description": "Mistral 7B model"
    },
    "gemma": {
        "repo": "https://huggingface.co/google/gemma-7b",
        "ollama": "gemma",
        "description": "Google's Gemma model (7B parameters)"
    }
}

def run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, and stderr."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def clone_repository(repo_url: str, target_dir: str) -> bool:
    """Clone a git repository to the target directory."""
    print(f"Cloning {repo_url} to {target_dir}...")
    
    if os.path.exists(target_dir):
        print(f"Directory {target_dir} already exists. Skipping clone.")
        return True
    
    exit_code, stdout, stderr = run_command(["git", "clone", repo_url, target_dir])
    
    if exit_code != 0:
        print(f"Error cloning repository: {stderr}")
        return False
    
    print(f"Successfully cloned {repo_url}")
    return True

def setup_framework(framework_name: str, target_dir: str = "frameworks") -> bool:
    """Set up the selected framework."""
    if framework_name not in FRAMEWORKS:
        print(f"Error: Framework '{framework_name}' not found.")
        return False
    
    framework = FRAMEWORKS[framework_name]
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Clone the base repository
    framework_dir = os.path.join(target_dir, framework_name)
    if not clone_repository(framework["base"], framework_dir):
        return False
    
    # Clone example repositories
    examples_dir = os.path.join(framework_dir, "examples")
    os.makedirs(examples_dir, exist_ok=True)
    
    for i, example_repo in enumerate(framework["examples"]):
        example_name = os.path.basename(example_repo).replace(".git", "")
        example_dir = os.path.join(examples_dir, example_name)
        clone_repository(example_repo, example_dir)
    
    print(f"Framework {framework_name} set up successfully in {framework_dir}")
    return True

def setup_model(model_name: str) -> bool:
    """Set up the selected model."""
    if model_name not in MODELS:
        print(f"Error: Model '{model_name}' not found.")
        return False
    
    model = MODELS[model_name]
    
    # Pull the model using Ollama
    print(f"Pulling {model_name} model using Ollama...")
    exit_code, stdout, stderr = run_command(["ollama", "pull", model["ollama"]])
    
    if exit_code != 0:
        print(f"Error pulling model: {stderr}")
        return False
    
    print(f"Successfully pulled {model_name} model")
    return True

def main():
    parser = argparse.ArgumentParser(description="Repository and Model Selector for Augment Linux Assistant")
    parser.add_argument("--framework", type=str, choices=FRAMEWORKS.keys(), help="Framework to set up")
    parser.add_argument("--model", type=str, choices=MODELS.keys(), help="Model to set up")
    parser.add_argument("--list", action="store_true", help="List available frameworks and models")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available Frameworks:")
        for name, info in FRAMEWORKS.items():
            print(f"  - {name}: {info['description']}")
        
        print("\nAvailable Models:")
        for name, info in MODELS.items():
            print(f"  - {name}: {info['description']}")
        return 0
    
    if args.framework:
        if not setup_framework(args.framework):
            return 1
    
    if args.model:
        if not setup_model(args.model):
            return 1
    
    if not args.framework and not args.model and not args.list:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
