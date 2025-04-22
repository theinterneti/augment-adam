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

from dukat.web import launch_web_interface
from dukat.core.assistant import Assistant
from dukat.memory.working import Message

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
    console.print(f"Using model: [bold]{model}[/bold]")

    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")

    # Create the assistant
    assistant = Assistant(model_name=model)

    # Start the interactive session
    console.print("\nType 'exit' or 'quit' to exit.")

    while True:
        # Get user input
        user_input = console.input("\n[bold green]You:[/bold green] ")

        # Check if the user wants to exit
        if user_input.lower() in ("exit", "quit"):
            console.print("Goodbye!")
            break

        # Generate a response
        console.print("[bold blue]Dukat:[/bold blue] ", end="")

        # Add the user message to the assistant
        assistant.add_message(Message(role="user", content=user_input))

        # Generate the response
        response = assistant.generate_response()

        # Print the response
        console.print(response)


@app.command()
def web(
    port: int = typer.Option(7860, "--port", "-p",
                             help="Port to run the web interface on"),
    host: str = typer.Option("127.0.0.1", "--host",
                             "-h", help="Host to run the web interface on"),
    share: bool = typer.Option(
        False, "--share", "-s", help="Create a public link"),
    model: str = typer.Option("llama3:8b", "--model",
                              "-m", help="Model to use for inference"),
):
    """Start the Dukat web interface."""
    console.print(
        Panel.fit(
            "[bold blue]Dukat Web Interface[/bold blue] [bold]v0.1.0[/bold]",
            title="Welcome",
            subtitle="Open Source AI Assistant",
        )
    )
    console.print(f"Starting web interface at [bold]{host}:{port}[/bold]")

    if share:
        console.print("Creating public link...")

    # Launch the web interface
    launch_web_interface(
        host=host,
        port=port,
        share=share,
        model_name=model,
        title="Dukat Assistant",
        description="An open-source AI assistant focused on personal automation.",
        version="0.1.0",
    )


if __name__ == "__main__":
    app()
