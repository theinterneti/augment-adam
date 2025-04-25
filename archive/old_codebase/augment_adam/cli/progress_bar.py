"""CLI progress bar component.

This module provides a progress bar component for the CLI.

Version: 0.1.0
Created: 2025-04-26
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional, Union

from augment_adam.core.progress import ProgressTracker, ProgressState


class ProgressBar:
    """A progress bar for the CLI."""

    def __init__(
        self,
        tracker: ProgressTracker,
        width: int = 40,
        fill_char: str = "█",
        empty_char: str = "░",
        show_percentage: bool = True,
        show_time: bool = True,
        show_description: bool = True,
        show_message: bool = True,
        update_interval: float = 0.1,
    ):
        """Initialize the progress bar.
        
        Args:
            tracker: The progress tracker to display
            width: Width of the progress bar in characters
            fill_char: Character to use for filled portion of the bar
            empty_char: Character to use for empty portion of the bar
            show_percentage: Whether to show the percentage
            show_time: Whether to show elapsed and estimated time
            show_description: Whether to show the task description
            show_message: Whether to show the progress message
            update_interval: Interval in seconds between updates
        """
        self.tracker = tracker
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.show_percentage = show_percentage
        self.show_time = show_time
        self.show_description = show_description
        self.show_message = show_message
        self.update_interval = update_interval
        
        self.last_update = 0.0
        self.last_line_length = 0
        
        # Add a callback to the tracker to update the progress bar
        self.tracker.add_callback(self._update_callback)
    
    def _update_callback(self, tracker: ProgressTracker) -> None:
        """Callback for progress updates.
        
        Args:
            tracker: The progress tracker that was updated
        """
        # Check if it's time to update
        now = time.time()
        if now - self.last_update < self.update_interval:
            return
        
        self.last_update = now
        self.render()
    
    def render(self) -> None:
        """Render the progress bar to the console."""
        # Get terminal width
        try:
            terminal_width = os.get_terminal_size().columns
        except (AttributeError, OSError):
            terminal_width = 80
        
        # Calculate the progress bar
        progress = self.tracker.current_percentage / self.tracker.total_percentage
        filled_width = int(self.width * progress)
        empty_width = self.width - filled_width
        
        bar = self.fill_char * filled_width + self.empty_char * empty_width
        
        # Build the progress line
        line_parts = []
        
        # Add description
        if self.show_description and self.tracker.description:
            line_parts.append(f"{self.tracker.description}")
        
        # Add the progress bar
        line_parts.append(f"[{bar}]")
        
        # Add percentage
        if self.show_percentage:
            line_parts.append(f"{self.tracker.current_percentage:.1f}%")
        
        # Add step information if available
        if self.tracker.total_steps is not None:
            line_parts.append(
                f"{self.tracker.current_step}/{self.tracker.total_steps} steps"
            )
        
        # Add time information
        if self.show_time:
            elapsed = self.tracker.get_elapsed_time()
            elapsed_str = f"{elapsed:.1f}s"
            
            # Add estimated time remaining if available
            remaining = self.tracker.get_estimated_time_remaining()
            if remaining is not None:
                elapsed_str += f" (ETA: {remaining:.1f}s)"
            
            line_parts.append(elapsed_str)
        
        # Join the parts
        line = " | ".join(line_parts)
        
        # Add message on a new line if needed
        if self.show_message and self.tracker.message:
            message = self.tracker.message
            # Truncate message if it's too long
            if len(message) > terminal_width - 4:
                message = message[:terminal_width - 7] + "..."
            line += f"\n  {message}"
        
        # Clear the previous line
        if self.last_line_length > 0:
            sys.stdout.write("\r" + " " * self.last_line_length + "\r")
        
        # Print the new line
        sys.stdout.write(line)
        sys.stdout.flush()
        
        # Remember the line length
        self.last_line_length = len(line.split("\n")[0])
        
        # Add a newline if the task is completed or failed
        if self.tracker.state in (ProgressState.COMPLETED, ProgressState.FAILED, ProgressState.CANCELLED):
            sys.stdout.write("\n")
            sys.stdout.flush()
            
            # Remove the callback
            self.tracker.remove_callback(self._update_callback)


def create_progress_bar(
    tracker: ProgressTracker,
    width: int = 40,
    fill_char: str = "█",
    empty_char: str = "░",
    show_percentage: bool = True,
    show_time: bool = True,
    show_description: bool = True,
    show_message: bool = True,
    update_interval: float = 0.1,
) -> ProgressBar:
    """Create a progress bar for a tracker.
    
    Args:
        tracker: The progress tracker to display
        width: Width of the progress bar in characters
        fill_char: Character to use for filled portion of the bar
        empty_char: Character to use for empty portion of the bar
        show_percentage: Whether to show the percentage
        show_time: Whether to show elapsed and estimated time
        show_description: Whether to show the task description
        show_message: Whether to show the progress message
        update_interval: Interval in seconds between updates
        
    Returns:
        The created progress bar
    """
    return ProgressBar(
        tracker=tracker,
        width=width,
        fill_char=fill_char,
        empty_char=empty_char,
        show_percentage=show_percentage,
        show_time=show_time,
        show_description=show_description,
        show_message=show_message,
        update_interval=update_interval,
    )
