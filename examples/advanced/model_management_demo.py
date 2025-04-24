#!/usr/bin/env python
"""
Demo script for the AI agent model management.

This script demonstrates how to use the ModelManager class to
download, load, and use models for code generation.
"""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dukat.ai_agent.models import ModelManager, CodePromptTemplates

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("dukat.ai_agent")
console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Model management demo")
    parser.add_argument(
        "--model", 
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        help="Model to use"
    )
    parser.add_argument(
        "--task",
        choices=["docstring", "test", "explain", "review", "complete", "refactor"],
        default="docstring",
        help="Task to perform"
    )
    parser.add_argument(
        "--file",
        help="Python file to process"
    )
    parser.add_argument(
        "--quantization",
        choices=["4bit", "8bit", "none"],
        default="4bit",
        help="Quantization method"
    )
    return parser.parse_args()

def main():
    """Run the demo."""
    args = parse_args()
    
    # Create model manager
    manager = ModelManager()
    
    # Download and load the model
    with console.status(f"Downloading model {args.model}..."):
        manager.download_model(args.model)
    
    with console.status(f"Loading model {args.model}..."):
        manager.load_model(args.model, quantization=args.quantization)
    
    # Read the input file
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    else:
        # Use a sample code snippet
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    # Generate prompt based on the task
    if args.task == "docstring":
        prompt = CodePromptTemplates.docstring_generation(code)
        system_prompt = "You are an expert Python developer. Generate comprehensive, accurate docstrings for the given code."
    elif args.task == "test":
        prompt = CodePromptTemplates.test_generation(code)
        system_prompt = "You are an expert Python developer. Generate comprehensive, effective tests for the given code."
    elif args.task == "explain":
        prompt = CodePromptTemplates.code_explanation(code)
        system_prompt = "You are an expert Python developer. Explain the given code clearly and accurately."
    elif args.task == "review":
        prompt = CodePromptTemplates.code_review(code)
        system_prompt = "You are an expert Python developer. Review the given code and provide constructive feedback."
    elif args.task == "complete":
        prompt = CodePromptTemplates.code_completion(code, "Complete the function implementation.")
        system_prompt = "You are an expert Python developer. Complete the given code according to the requirements."
    elif args.task == "refactor":
        prompt = CodePromptTemplates.refactoring(code)
        system_prompt = "You are an expert Python developer. Refactor the given code to improve its quality."
    
    # Generate text
    with console.status(f"Generating {args.task} with model {args.model}..."):
        response, metadata = manager.generate(
            prompt=prompt,
            model_id=args.model,
            system_prompt=system_prompt,
            temperature=0.2
        )
    
    # Print the response
    console.print(f"\n[bold green]Generated {args.task}:[/bold green]")
    console.print(response)
    
    # Print metadata
    console.print("\n[dim]Metadata:[/dim]")
    console.print(f"[dim]Model: {metadata['model']}[/dim]")
    console.print(f"[dim]Prompt tokens: {metadata['prompt_tokens']}[/dim]")
    console.print(f"[dim]Completion tokens: {metadata['completion_tokens']}[/dim]")
    
    # Unload the model
    with console.status(f"Unloading model {args.model}..."):
        manager.unload_model(args.model)

if __name__ == "__main__":
    main()
