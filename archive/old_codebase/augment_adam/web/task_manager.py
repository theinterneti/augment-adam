"""Task management for the Augment Adam web interface.

This module provides functionality for managing tasks in the Augment Adam web interface.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

import gradio as gr

from augment_adam.core.task_queue import (
    TaskQueue, Task, TaskStatus,
    get_task_queue
)
from augment_adam.core.progress import (
    ProgressTracker, ProgressState,
    get_progress_tracker, get_all_progress_trackers, get_progress_tracker_stats
)

logger = logging.getLogger(__name__)


class TaskManagerUI:
    """UI component for managing tasks in the web interface."""

    def __init__(self, task_queue: Optional[TaskQueue] = None):
        """Initialize the task manager UI.

        Args:
            task_queue: The task queue to use. If None, the default queue will be used.
        """
        self.task_queue = task_queue or get_task_queue()
        self.refresh_interval = 5  # Refresh interval in seconds
        self.auto_refresh = False  # Auto-refresh disabled by default

    def create_ui(self) -> Tuple[List[gr.Component], List[Callable]]:
        """Create the task manager UI components.

        Returns:
            A tuple of (components, event_handlers).
        """
        # Task list
        task_list = gr.Dataframe(
            label="Active Tasks",
            headers=["Task ID", "Status", "Priority",
                     "Created", "Started", "Completed", "Progress"],
            value=self._get_task_list(),
            interactive=False,
        )

        # Task details
        task_details = gr.JSON(
            label="Task Details",
            value={},
        )

        # Progress trackers
        progress_trackers = gr.Dataframe(
            label="Progress Trackers",
            headers=["Task ID", "State", "Progress",
                     "Description", "Elapsed Time", "ETA"],
            value=self._get_progress_trackers(),
            interactive=False,
        )

        # Progress details
        progress_details = gr.JSON(
            label="Progress Details",
            value={},
        )

        # Controls
        with gr.Row():
            refresh_button = gr.Button("Refresh")
            cancel_button = gr.Button("Cancel Selected Task")

        # Status message
        status_message = gr.Textbox(
            label="Status",
            value="",
        )

        # Set up event handlers
        event_handlers = [
            refresh_button.click(
                fn=self._refresh_data,
                inputs=[],
                outputs=[task_list, progress_trackers, status_message],
            ),

            task_list.select(
                fn=self._get_task_details,
                inputs=[task_list],
                outputs=[task_details],
            ),
            progress_trackers.select(
                fn=self._get_progress_details,
                inputs=[progress_trackers],
                outputs=[progress_details],
            ),
            cancel_button.click(
                fn=self._cancel_task,
                inputs=[task_list],
                outputs=[task_list, status_message],
            ),
        ]

        # Note: Auto-refresh is not implemented in this version
        # Manual refresh is available through the refresh button

        components = [
            task_list,
            task_details,
            progress_trackers,
            progress_details,
            refresh_button,
            cancel_button,
            status_message,
        ]

        return components, event_handlers

    def _get_task_list(self) -> List[List[Any]]:
        """Get a list of active tasks.

        Returns:
            A list of task data for the dataframe.
        """
        try:
            # Get tasks from the queue
            tasks = list(self.task_queue.tasks.values())

            # Sort tasks by priority (higher first) and then by creation time
            tasks.sort(key=lambda t: (-t.priority, t.created_at))

            # Format task data for the dataframe
            task_data = []
            for task in tasks:
                # Get progress information if available
                progress = "N/A"
                if task.progress_tracker:
                    progress = f"{task.progress_tracker.current_percentage:.1f}%"

                # Format timestamps
                created = time.strftime("%H:%M:%S", time.localtime(
                    task.created_at)) if task.created_at else "N/A"
                started = time.strftime("%H:%M:%S", time.localtime(
                    task.started_at)) if task.started_at else "N/A"
                completed = time.strftime("%H:%M:%S", time.localtime(
                    task.completed_at)) if task.completed_at else "N/A"

                task_data.append([
                    task.task_id,
                    task.status.value,
                    task.priority,
                    created,
                    started,
                    completed,
                    progress,
                ])

            return task_data

        except Exception as e:
            logger.exception(f"Error getting task list: {str(e)}")
            return []

    def _get_progress_trackers(self) -> List[List[Any]]:
        """Get a list of progress trackers.

        Returns:
            A list of progress tracker data for the dataframe.
        """
        try:
            # Get all progress trackers
            trackers = get_all_progress_trackers()

            # Format tracker data for the dataframe
            tracker_data = []
            for tracker in trackers:
                # Calculate elapsed time and ETA
                elapsed = tracker.get_elapsed_time()
                elapsed_str = f"{elapsed:.1f}s" if elapsed > 0 else "N/A"

                eta = tracker.get_estimated_time_remaining()
                eta_str = f"{eta:.1f}s" if eta is not None else "N/A"

                tracker_data.append([
                    tracker.task_id,
                    tracker.state.value,
                    f"{tracker.current_percentage:.1f}%",
                    tracker.description,
                    elapsed_str,
                    eta_str,
                ])

            return tracker_data

        except Exception as e:
            logger.exception(f"Error getting progress trackers: {str(e)}")
            return []

    def _get_task_details(self, task_row: List[Any]) -> Dict[str, Any]:
        """Get details for a task.

        Args:
            task_row: The selected task row from the dataframe.

        Returns:
            The task details as a dictionary.
        """
        if not task_row or len(task_row) < 1:
            return {}

        try:
            # Get the task ID from the selected row
            task_id = task_row[0]

            # Get the task from the queue
            task = self.task_queue.tasks.get(task_id)

            if not task:
                return {"error": f"Task {task_id} not found"}

            # Get task details
            task_dict = task.to_dict()

            return task_dict

        except Exception as e:
            logger.exception(f"Error getting task details: {str(e)}")
            return {"error": str(e)}

    def _get_progress_details(self, progress_row: List[Any]) -> Dict[str, Any]:
        """Get details for a progress tracker.

        Args:
            progress_row: The selected progress tracker row from the dataframe.

        Returns:
            The progress tracker details as a dictionary.
        """
        if not progress_row or len(progress_row) < 1:
            return {}

        try:
            # Get the task ID from the selected row
            task_id = progress_row[0]

            # Get the progress tracker
            tracker = get_progress_tracker(task_id)

            if not tracker:
                return {"error": f"Progress tracker {task_id} not found"}

            # Get progress details
            progress_dict = tracker.get_progress()

            return progress_dict

        except Exception as e:
            logger.exception(f"Error getting progress details: {str(e)}")
            return {"error": str(e)}

    async def _cancel_task(self, task_row: List[Any]) -> Tuple[List[List[Any]], str]:
        """Cancel a task.

        Args:
            task_row: The selected task row from the dataframe.

        Returns:
            A tuple of (updated_task_list, status_message).
        """
        if not task_row or len(task_row) < 1:
            return self._get_task_list(), "No task selected"

        try:
            # Get the task ID from the selected row
            task_id = task_row[0]

            # Cancel the task
            cancelled = await self.task_queue.cancel_task(task_id)

            if cancelled:
                return self._get_task_list(), f"Task {task_id} cancelled"
            else:
                return self._get_task_list(), f"Could not cancel task {task_id}"

        except Exception as e:
            logger.exception(f"Error cancelling task: {str(e)}")
            return self._get_task_list(), f"Error cancelling task: {str(e)}"

    def _refresh_data(self) -> Tuple[List[List[Any]], List[List[Any]], str]:
        """Refresh the task and progress data.

        Returns:
            A tuple of (task_list, progress_trackers, status_message).
        """
        try:
            task_list = self._get_task_list()
            progress_trackers = self._get_progress_trackers()

            return task_list, progress_trackers, f"Data refreshed at {time.strftime('%H:%M:%S')}"

        except Exception as e:
            logger.exception(f"Error refreshing data: {str(e)}")
            return [], [], f"Error refreshing data: {str(e)}"

    def _delayed_refresh(self) -> Tuple[List[List[Any]], List[List[Any]]]:
        """Refresh the task and progress data after a delay.

        Returns:
            A tuple of (task_list, progress_trackers).
        """
        try:
            task_list = self._get_task_list()
            progress_trackers = self._get_progress_trackers()

            return task_list, progress_trackers

        except Exception as e:
            logger.exception(f"Error in delayed refresh: {str(e)}")
            return [], []

    def _set_auto_refresh(self, auto_refresh: bool) -> None:
        """Set the auto-refresh flag.

        Args:
            auto_refresh: Whether to auto-refresh the data.
        """
        self.auto_refresh = auto_refresh


def create_task_tab() -> Tuple[gr.Tab, List[Callable]]:
    """Create a task management tab for the web interface.

    Returns:
        A tuple of (tab, event_handlers).
    """
    task_manager = TaskManagerUI()

    with gr.Tab("Tasks") as tab:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Task Management")
                gr.Markdown("Monitor and manage background tasks.")

                components, event_handlers = task_manager.create_ui()

    return tab, event_handlers
