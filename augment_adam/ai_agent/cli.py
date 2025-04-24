"""
Command-line interface for the AI coding agent.

This module provides a CLI for interacting with the AI coding agent,
including model management and code generation tasks.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from dukat.ai_agent.models import ModelManager, CodePromptTemplates

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("dukat.ai_agent")

# Create Typer app
app = typer.Typer(help="AI coding agent for development automation")
model_app = typer.Typer(help="Model management commands")
app.add_typer(model_app, name="model")

# Create console for rich output
console = Console()

# Initialize model manager
model_manager = ModelManager()

@model_app.command("list")
def list_models():
    """List all available models."""
    models = model_manager.list_available_models()
    
    if not models:
        console.print("[yellow]No models found. Use 'model download' to download models.[/yellow]")
        return
    
    table = Table(title="Available Models")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Quantization", style="magenta")
    table.add_column("Status", style="yellow")
    
    for model in models:
        status = []
        if model["is_loaded"]:
            status.append("Loaded")
        if model["is_default"]:
            status.append("Default")
        
        table.add_row(
            model["id"],
            model["name"],
            model["description"],
            model["quantization"],
            ", ".join(status) if status else ""
        )
    
    console.print(table)

@model_app.command("download")
def download_model(
    model_id: str = typer.Argument(..., help="Model ID to download"),
    revision: Optional[str] = typer.Option(None, "--revision", "-r", help="Model revision"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download if model exists")
):
    """Download a model from Hugging Face Hub."""
    with console.status(f"Downloading model {model_id}..."):
        success = model_manager.download_model(model_id, revision, force)
    
    if success:
        console.print(f"[green]Model {model_id} downloaded successfully.[/green]")
    else:
        console.print(f"[red]Failed to download model {model_id}.[/red]")
        raise typer.Exit(code=1)

@model_app.command("load")
def load_model(
    model_id: str = typer.Argument(..., help="Model ID to load"),
    quantization: Optional[str] = typer.Option(None, "--quantization", "-q", help="Quantization method (4bit, 8bit, none)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force reload if already loaded")
):
    """Load a model into memory."""
    with console.status(f"Loading model {model_id}..."):
        success = model_manager.load_model(model_id, quantization, force)
    
    if success:
        console.print(f"[green]Model {model_id} loaded successfully.[/green]")
    else:
        console.print(f"[red]Failed to load model {model_id}.[/red]")
        raise typer.Exit(code=1)

@model_app.command("unload")
def unload_model(
    model_id: str = typer.Argument(..., help="Model ID to unload")
):
    """Unload a model from memory."""
    with console.status(f"Unloading model {model_id}..."):
        success = model_manager.unload_model(model_id)
    
    if success:
        console.print(f"[green]Model {model_id} unloaded successfully.[/green]")
    else:
        console.print(f"[red]Failed to unload model {model_id}.[/red]")
        raise typer.Exit(code=1)

@model_app.command("set-default")
def set_default_model(
    model_id: str = typer.Argument(..., help="Model ID to set as default")
):
    """Set the default model."""
    success = model_manager.set_default_model(model_id)
    
    if success:
        console.print(f"[green]Default model set to {model_id}.[/green]")
    else:
        console.print(f"[red]Failed to set default model to {model_id}.[/red]")
        raise typer.Exit(code=1)

@app.command("generate")
def generate_text(
    prompt: str = typer.Argument(..., help="Prompt for text generation"),
    model_id: Optional[str] = typer.Option(None, "--model", "-m", help="Model ID to use"),
    system_prompt: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt"),
    temperature: Optional[float] = typer.Option(None, "--temperature", "-t", help="Sampling temperature"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Maximum tokens to generate")
):
    """Generate text using the specified model."""
    with console.status("Generating..."):
        response, metadata = model_manager.generate(
            prompt=prompt,
            model_id=model_id,
            system_prompt=system_prompt,
            temperature=temperature,
            max_new_tokens=max_tokens
        )
    
    if "error" in metadata:
        console.print(f"[red]Error: {metadata['error']}[/red]")
        raise typer.Exit(code=1)
    
    console.print("\n[bold green]Generated Text:[/bold green]")
    console.print(response)
    
    console.print("\n[dim]Metadata:[/dim]")
    console.print(f"[dim]Model: {metadata['model']}[/dim]")
    console.print(f"[dim]Prompt tokens: {metadata['prompt_tokens']}[/dim]")
    console.print(f"[dim]Completion tokens: {metadata['completion_tokens']}[/dim]")

@app.command("docstring")
def generate_docstring(
    file_path: Path = typer.Argument(..., help="Python file to document"),
    style: str = typer.Option("google", "--style", "-s", help="Docstring style (google, numpy, sphinx)"),
    model_id: Optional[str] = typer.Option(None, "--model", "-m", help="Model ID to use")
):
    """Generate docstrings for Python code."""
    if not file_path.exists():
        console.print(f"[red]File {file_path} does not exist.[/red]")
        raise typer.Exit(code=1)
    
    if file_path.suffix != ".py":
        console.print(f"[red]File {file_path} is not a Python file.[/red]")
        raise typer.Exit(code=1)
    
    with open(file_path, "r") as f:
        code = f.read()
    
    prompt = CodePromptTemplates.docstring_generation(code, style)
    
    with console.status(f"Generating {style} docstrings..."):
        response, metadata = model_manager.generate(
            prompt=prompt,
            model_id=model_id,
            system_prompt="You are an expert Python developer. Generate comprehensive, accurate docstrings for the given code.",
            temperature=0.1  # Low temperature for more deterministic output
        )
    
    if "error" in metadata:
        console.print(f"[red]Error: {metadata['error']}[/red]")
        raise typer.Exit(code=1)
    
    console.print("\n[bold green]Generated Docstring:[/bold green]")
    console.print(response)

@app.command("test")
def generate_test(
    file_path: Path = typer.Argument(..., help="Python file to test"),
    framework: str = typer.Option("pytest", "--framework", "-f", help="Testing framework (pytest, unittest)"),
    coverage_level: str = typer.Option("high", "--coverage", "-c", help="Coverage level (basic, high, comprehensive)"),
    model_id: Optional[str] = typer.Option(None, "--model", "-m", help="Model ID to use"),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Generate tests for Python code."""
    if not file_path.exists():
        console.print(f"[red]File {file_path} does not exist.[/red]")
        raise typer.Exit(code=1)
    
    if file_path.suffix != ".py":
        console.print(f"[red]File {file_path} is not a Python file.[/red]")
        raise typer.Exit(code=1)
    
    with open(file_path, "r") as f:
        code = f.read()
    
    prompt = CodePromptTemplates.test_generation(code, framework, coverage_level)
    
    with console.status(f"Generating {coverage_level} {framework} tests..."):
        response, metadata = model_manager.generate(
            prompt=prompt,
            model_id=model_id,
            system_prompt="You are an expert Python developer. Generate comprehensive, effective tests for the given code.",
            temperature=0.2  # Slightly higher temperature for more creative tests
        )
    
    if "error" in metadata:
        console.print(f"[red]Error: {metadata['error']}[/red]")
        raise typer.Exit(code=1)
    
    if output_path:
        # Create test file
        with open(output_path, "w") as f:
            f.write(response)
        console.print(f"[green]Tests written to {output_path}[/green]")
    else:
        console.print("\n[bold green]Generated Tests:[/bold green]")
        console.print(response)

if __name__ == "__main__":
    app()
