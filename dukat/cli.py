"""Command-line interface for the Dukat assistant.

This module provides the command-line interface for interacting with
the Dukat assistant.

Version: 0.1.0
Created: 2025-04-22
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

app = typer.Typer(
    name="dukat",
    help="An open-source AI assistant focused on personal automation.",
    add_completion=False,
)

console = Console()


@app.command()
def main(
    model: str = typer.Option(
        "llama3:8b", "--model", "-m", help="Model to use for inference"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Start the Dukat assistant CLI."""
    console.print(
        Panel.fit(
            "[bold blue]Dukat[/bold blue] [bold]v0.1.0[/bold]",
            title="Welcome",
            subtitle="Open Source AI Assistant",
        )
    )
    console.print(
        "This is a placeholder for the Dukat CLI. Implementation coming soon."
    )
    console.print(f"Using model: [bold]{model}[/bold]")
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@app.command()
def web(
    port: int = typer.Option(7860, "--port", "-p", help="Port to run the web interface on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to run the web interface on"),
):
    """Start the Dukat web interface."""
    console.print(
        Panel.fit(
            "[bold blue]Dukat Web Interface[/bold blue] [bold]v0.1.0[/bold]",
            title="Welcome",
            subtitle="Open Source AI Assistant",
        )
    )
    console.print(
        "This is a placeholder for the Dukat web interface. Implementation coming soon."
    )
    console.print(f"Web interface would start on [bold]{host}:{port}[/bold]")


if __name__ == "__main__":
    app()
