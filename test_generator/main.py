#!/usr/bin/env python3
"""
Main entry point for the test generator.
"""

import os
import sys
import typer
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from test_generator.code_analyzer import CodeAnalyzer
from test_generator.test_generator import TestGenerator
from test_generator.model_manager import ModelManager

app = typer.Typer(help="Automated test generator using local LLMs")
console = Console()

@app.command()
def generate(
    source_file: str = typer.Argument(..., help="Path to the source file to generate tests for"),
    test_file: Optional[str] = typer.Option(None, help="Path to the test file (will be created if it doesn't exist)"),
    model: str = typer.Option("codellama:7b-instruct", help="Model to use for test generation"),
    max_tests: int = typer.Option(10, help="Maximum number of tests to generate"),
    target_coverage: float = typer.Option(80.0, help="Target coverage percentage"),
    include_files: Optional[List[str]] = typer.Option(None, help="Additional files to include for context"),
):
    """Generate tests for a given source file."""
    
    # Display banner
    console.print(Panel.fit(
        "[bold green]Test Generator[/bold green] - Automated test generation using local LLMs",
        border_style="green"
    ))
    
    # Validate source file
    if not os.path.exists(source_file):
        console.print(f"[bold red]Error:[/bold red] Source file '{source_file}' does not exist.")
        sys.exit(1)
    
    # Determine test file path if not provided
    if test_file is None:
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        test_file = f"test_{base_name}.py"
        console.print(f"Test file not specified, using: [bold]{test_file}[/bold]")
    
    # Initialize components
    console.print("Initializing model manager...")
    model_manager = ModelManager(model_name=model)
    
    console.print("Analyzing source code...")
    code_analyzer = CodeAnalyzer(source_file, include_files or [])
    code_info = code_analyzer.analyze()
    
    console.print("Generating tests...")
    test_generator = TestGenerator(model_manager, code_info)
    generated_tests = test_generator.generate_tests(max_tests=max_tests, target_coverage=target_coverage)
    
    # Write tests to file
    with open(test_file, "w") as f:
        f.write(generated_tests)
    
    console.print(f"[bold green]Success![/bold green] Generated tests written to: [bold]{test_file}[/bold]")
    
    # Run tests to check coverage
    console.print("Running tests to check coverage...")
    # TODO: Implement test runner and coverage checker
    
    return 0

if __name__ == "__main__":
    app()
