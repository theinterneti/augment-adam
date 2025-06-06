"""Command-line interface for Augment Adam.

This module contains the command-line interface for Augment Adam,
allowing users to interact with the system from the terminal.

Version: 0.1.0
Created: 2025-04-25
Updated: 2025-04-24
"""

import typer

app = typer.Typer(help="Augment Adam: An intelligent assistant with advanced memory capabilities.")

from augment_adam.cli.commands import *  # noqa
from augment_adam.cli.progress_bar import ProgressBar  # noqa

__all__ = ["app", "ProgressBar"]