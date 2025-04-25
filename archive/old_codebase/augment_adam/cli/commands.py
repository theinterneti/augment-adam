"""Commands for the Augment Adam CLI.

This module contains the commands for the Augment Adam CLI.
"""

import typer
from rich.console import Console

from augment_adam.cli import app
from augment_adam.core import Agent

console = Console()


@app.command()
def chat(
    model: str = typer.Option("default", help="The model to use."),
    memory_type: str = typer.Option("faiss", help="The memory system to use."),
):
    """Start an interactive chat session with Augment Adam."""
    console.print("[bold green]Starting chat with Augment Adam...[/bold green]")
    console.print("Type 'exit' to end the session.")
    
    agent = Agent(model_name=model)
    
    while True:
        user_input = typer.prompt("You")
        if user_input.lower() in ("exit", "quit"):
            break
        
        response = agent.run(user_input)
        console.print(f"[bold blue]Augment Adam:[/bold blue] {response}")


@app.command()
def version():
    """Show the version of Augment Adam."""
    from augment_adam import __version__
    console.print(f"Augment Adam version: [bold]{__version__}[/bold]")


if __name__ == "__main__":
    app()
