"""Progress tracking for long-running tasks.

This module provides a progress tracking system for long-running tasks,
allowing tasks to report their progress and clients to monitor it.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import enum
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union, cast

from dukat.core.errors import ValidationError, wrap_error, log_error

logger = logging.getLogger(__name__)


class ProgressState(enum.Enum):
    """States for progress tracking."""

    NOT_STARTED = "not_started"  # Task has not started yet
    IN_PROGRESS = "in_progress"  # Task is in progress
    COMPLETED = "completed"      # Task has completed successfully
    FAILED = "failed"            # Task has failed
    CANCELLED = "cancelled"      # Task was cancelled


class ProgressTracker:
    """Progress tracker for long-running tasks.

    The progress tracker allows tasks to report their progress and clients
    to monitor it. It supports both percentage-based and step-based progress
    tracking.
    """

    def __init__(
        self,
        task_id: str,
        total_steps: Optional[int] = None,
        total_percentage: float = 100.0,
        description: str = "",
        parent: Optional["ProgressTracker"] = None,
    ):
        """Initialize the progress tracker.

        Args:
            task_id: Unique identifier for the task
            total_steps: Total number of steps for step-based tracking
            total_percentage: Total percentage for percentage-based tracking
            description: Description of the task
            parent: Parent progress tracker for nested tasks
        """
        self.task_id = task_id
        self.total_steps = total_steps
        self.total_percentage = total_percentage
        self.description = description
        self.parent = parent

        self.state = ProgressState.NOT_STARTED
        self.current_step = 0
        self.current_percentage = 0.0
        self.start_time = 0.0
        self.end_time = 0.0
        self.message = ""
        self.details: Dict[str, Any] = {}
        self.children: Dict[str, "ProgressTracker"] = {}
        self.callbacks: List[Callable[["ProgressTracker"], None]] = []
        self.weight = 1.0  # Default weight for use in parent's progress calculation

        logger.debug(f"Created progress tracker for task {task_id}")

    def __str__(self) -> str:
        """Return a string representation of the progress tracker."""
        if self.total_steps is not None:
            return (
                f"ProgressTracker(task_id='{self.task_id}', "
                f"state={self.state.value}, "
                f"progress={self.current_step}/{self.total_steps} steps, "
                f"{self.current_percentage:.1f}%)"
            )
        else:
            return (
                f"ProgressTracker(task_id='{self.task_id}', "
                f"state={self.state.value}, "
                f"progress={self.current_percentage:.1f}%)"
            )

    def add_callback(self, callback: Callable[["ProgressTracker"], None]) -> None:
        """Add a callback to be called when progress is updated.

        Args:
            callback: The callback function to add
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[["ProgressTracker"], None]) -> None:
        """Remove a callback.

        Args:
            callback: The callback function to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def start(self, message: str = "") -> None:
        """Start the progress tracking.

        Args:
            message: Optional message to set
        """
        if self.state != ProgressState.NOT_STARTED:
            logger.warning(
                f"Cannot start progress tracking for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        self.state = ProgressState.IN_PROGRESS
        self.start_time = time.time()
        if message:
            self.message = message

        logger.debug(f"Started progress tracking for task {self.task_id}")
        self._notify_callbacks()

    def complete(self, message: str = "") -> None:
        """Complete the progress tracking.

        Args:
            message: Optional message to set
        """
        if self.state != ProgressState.IN_PROGRESS:
            logger.warning(
                f"Cannot complete progress tracking for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        # Set progress to 100%
        if self.total_steps is not None:
            self.current_step = self.total_steps
        self.current_percentage = self.total_percentage

        self.state = ProgressState.COMPLETED
        self.end_time = time.time()
        if message:
            self.message = message

        logger.debug(f"Completed progress tracking for task {self.task_id}")
        self._notify_callbacks()

    def fail(self, message: str = "") -> None:
        """Mark the progress tracking as failed.

        Args:
            message: Optional error message to set
        """
        if self.state not in (ProgressState.NOT_STARTED, ProgressState.IN_PROGRESS):
            logger.warning(
                f"Cannot fail progress tracking for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        self.state = ProgressState.FAILED
        self.end_time = time.time()
        if message:
            self.message = message

        logger.debug(
            f"Failed progress tracking for task {self.task_id}: {message}")
        self._notify_callbacks()

    def cancel(self, message: str = "") -> None:
        """Cancel the progress tracking.

        Args:
            message: Optional message to set
        """
        if self.state not in (ProgressState.NOT_STARTED, ProgressState.IN_PROGRESS):
            logger.warning(
                f"Cannot cancel progress tracking for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        self.state = ProgressState.CANCELLED
        self.end_time = time.time()
        if message:
            self.message = message

        logger.debug(f"Cancelled progress tracking for task {self.task_id}")
        self._notify_callbacks()

    def update_step(
        self,
        step: int,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the progress by step.

        Args:
            step: The current step
            message: Optional message to set
            details: Optional details to update
        """
        if self.state != ProgressState.IN_PROGRESS:
            logger.warning(
                f"Cannot update progress for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        if self.total_steps is None:
            raise ValidationError(
                "Cannot update step for percentage-based progress tracker",
                details={
                    "task_id": self.task_id,
                    "step": step,
                },
            )

        if step < 0 or step > self.total_steps:
            raise ValidationError(
                f"Step {step} out of range [0, {self.total_steps}]",
                details={
                    "task_id": self.task_id,
                    "step": step,
                    "total_steps": self.total_steps,
                },
            )

        self.current_step = step
        self.current_percentage = (
            step / self.total_steps) * self.total_percentage

        if message:
            self.message = message

        if details:
            self.details.update(details)

        logger.debug(
            f"Updated progress for task {self.task_id}: "
            f"{self.current_step}/{self.total_steps} steps, "
            f"{self.current_percentage:.1f}%"
        )
        self._notify_callbacks()

    def update_percentage(
        self,
        percentage: float,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the progress by percentage.

        Args:
            percentage: The current percentage
            message: Optional message to set
            details: Optional details to update
        """
        if self.state != ProgressState.IN_PROGRESS:
            logger.warning(
                f"Cannot update progress for task {self.task_id} "
                f"in state {self.state.value}"
            )
            return

        if percentage < 0 or percentage > self.total_percentage:
            raise ValidationError(
                f"Percentage {percentage} out of range [0, {self.total_percentage}]",
                details={
                    "task_id": self.task_id,
                    "percentage": percentage,
                    "total_percentage": self.total_percentage,
                },
            )

        self.current_percentage = percentage

        if self.total_steps is not None:
            self.current_step = int(
                (percentage / self.total_percentage) * self.total_steps
            )

        if message:
            self.message = message

        if details:
            self.details.update(details)

        logger.debug(
            f"Updated progress for task {self.task_id}: {self.current_percentage:.1f}%"
        )
        self._notify_callbacks()

    def increment_step(
        self,
        steps: int = 1,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Increment the progress by a number of steps.

        Args:
            steps: The number of steps to increment by
            message: Optional message to set
            details: Optional details to update
        """
        if self.total_steps is None:
            raise ValidationError(
                "Cannot increment step for percentage-based progress tracker",
                details={
                    "task_id": self.task_id,
                    "steps": steps,
                },
            )

        new_step = min(self.current_step + steps, self.total_steps)
        self.update_step(new_step, message, details)

    def increment_percentage(
        self,
        percentage: float,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Increment the progress by a percentage.

        Args:
            percentage: The percentage to increment by
            message: Optional message to set
            details: Optional details to update
        """
        new_percentage = min(
            self.current_percentage + percentage, self.total_percentage
        )
        self.update_percentage(new_percentage, message, details)

    def add_child(
        self,
        child_id: str,
        weight: float = 1.0,
        total_steps: Optional[int] = None,
        description: str = "",
    ) -> "ProgressTracker":
        """Add a child progress tracker.

        Args:
            child_id: Unique identifier for the child task
            weight: Weight of the child task in the parent's progress (0.0 to 1.0)
            total_steps: Total number of steps for step-based tracking
            description: Description of the child task

        Returns:
            The child progress tracker
        """
        if child_id in self.children:
            logger.warning(
                f"Child progress tracker {child_id} already exists for task {self.task_id}"
            )
            return self.children[child_id]

        # Validate weight
        if weight <= 0.0 or weight > 1.0:
            logger.warning(
                f"Invalid weight {weight} for child {child_id}. Using 1.0 instead."
            )
            weight = 1.0

        # Create a child progress tracker
        child = ProgressTracker(
            task_id=f"{self.task_id}.{child_id}",
            total_steps=total_steps,
            total_percentage=100.0,  # Always use 100% for children
            description=description,
            parent=self,
        )

        # Store the weight as a property of the child
        child.weight = weight

        # Add a callback to update the parent's progress
        child.add_callback(self._update_from_children)

        # Add the child to the children dictionary
        self.children[child_id] = child

        logger.debug(
            f"Added child progress tracker {child_id} to task {self.task_id}"
        )
        return child

    def get_child(self, child_id: str) -> Optional["ProgressTracker"]:
        """Get a child progress tracker.

        Args:
            child_id: Unique identifier for the child task

        Returns:
            The child progress tracker, or None if not found
        """
        return self.children.get(child_id)

    def remove_child(self, child_id: str) -> None:
        """Remove a child progress tracker.

        Args:
            child_id: Unique identifier for the child task
        """
        if child_id in self.children:
            child = self.children[child_id]
            child.remove_callback(self._update_from_children)
            del self.children[child_id]
            logger.debug(
                f"Removed child progress tracker {child_id} from task {self.task_id}"
            )

    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress information.

        Returns:
            A dictionary with the current progress information
        """
        progress = {
            "task_id": self.task_id,
            "state": self.state.value,
            "description": self.description,
            "current_percentage": self.current_percentage,
            "total_percentage": self.total_percentage,
            "message": self.message,
            "details": self.details,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_time": self.get_elapsed_time(),
        }

        if self.total_steps is not None:
            progress.update({
                "current_step": self.current_step,
                "total_steps": self.total_steps,
            })

        if self.children:
            progress["children"] = {
                child_id: child.get_progress()
                for child_id, child in self.children.items()
            }

        return progress

    def get_elapsed_time(self) -> float:
        """Get the elapsed time in seconds.

        Returns:
            The elapsed time in seconds
        """
        if self.start_time == 0:
            return 0.0

        if self.end_time > 0:
            return self.end_time - self.start_time

        return time.time() - self.start_time

    def get_estimated_time_remaining(self) -> Optional[float]:
        """Get the estimated time remaining in seconds.

        Returns:
            The estimated time remaining in seconds, or None if not available
        """
        if self.state != ProgressState.IN_PROGRESS or self.current_percentage == 0:
            return None

        elapsed_time = self.get_elapsed_time()
        if elapsed_time == 0:
            return None

        # Calculate the estimated time remaining
        progress_ratio = self.current_percentage / self.total_percentage
        if progress_ratio == 0:
            return None

        total_time = elapsed_time / progress_ratio
        remaining_time = total_time - elapsed_time

        return max(0.0, remaining_time)

    def _notify_callbacks(self) -> None:
        """Notify all callbacks of a progress update."""
        for callback in self.callbacks:
            try:
                callback(self)
            except Exception as e:
                error = wrap_error(
                    e,
                    message=f"Error in progress callback for task {self.task_id}",
                    details={
                        "task_id": self.task_id,
                        "callback": str(callback),
                    },
                )
                log_error(error, logger=logger)

    def _update_from_children(self, child: "ProgressTracker") -> None:
        """Update progress based on children's progress.

        Args:
            child: The child progress tracker that was updated
        """
        if not self.children:
            return

        # Calculate the weighted progress based on each child's weight
        weighted_progress = 0.0
        total_weight = sum(child.weight for child in self.children.values())

        # Normalize weights if their sum is not 1.0
        if total_weight != 1.0 and total_weight > 0.0:
            weight_factor = 1.0 / total_weight
        else:
            weight_factor = 1.0

        for child_tracker in self.children.values():
            # Calculate the child's contribution to the parent's progress
            normalized_weight = child_tracker.weight * weight_factor
            child_progress = (child_tracker.current_percentage /
                              100.0) * normalized_weight * 100.0
            weighted_progress += child_progress

        # Update the parent's progress
        self.update_percentage(weighted_progress)


# Global registry of progress trackers
_progress_trackers: Dict[str, ProgressTracker] = {}


def register_progress_tracker(tracker: ProgressTracker) -> None:
    """Register a progress tracker in the global registry.

    Args:
        tracker: The progress tracker to register
    """
    _progress_trackers[tracker.task_id] = tracker
    logger.debug(f"Registered progress tracker {tracker.task_id}")


def get_progress_tracker(task_id: str) -> Optional[ProgressTracker]:
    """Get a progress tracker from the global registry.

    Args:
        task_id: The task ID of the progress tracker

    Returns:
        The progress tracker, or None if not found
    """
    return _progress_trackers.get(task_id)


def remove_progress_tracker(task_id: str) -> None:
    """Remove a progress tracker from the global registry.

    Args:
        task_id: The task ID of the progress tracker
    """
    if task_id in _progress_trackers:
        del _progress_trackers[task_id]
        logger.debug(f"Removed progress tracker {task_id}")


def get_all_progress_trackers() -> List[ProgressTracker]:
    """Get all progress trackers from the global registry.

    Returns:
        A list of all progress trackers
    """
    return list(_progress_trackers.values())


def get_progress_tracker_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all progress trackers.

    Returns:
        A dictionary mapping task IDs to progress information
    """
    return {
        task_id: tracker.get_progress()
        for task_id, tracker in _progress_trackers.items()
    }


def create_progress_tracker(
    task_id: str,
    total_steps: Optional[int] = None,
    total_percentage: float = 100.0,
    description: str = "",
    parent_id: Optional[str] = None,
) -> ProgressTracker:
    """Create and register a progress tracker.

    Args:
        task_id: Unique identifier for the task
        total_steps: Total number of steps for step-based tracking
        total_percentage: Total percentage for percentage-based tracking
        description: Description of the task
        parent_id: Parent task ID for nested tasks

    Returns:
        The created progress tracker
    """
    # Check if a parent tracker was specified
    parent = None
    if parent_id:
        parent = get_progress_tracker(parent_id)
        if not parent:
            logger.warning(f"Parent progress tracker {parent_id} not found")

    # Create the progress tracker
    tracker = ProgressTracker(
        task_id=task_id,
        total_steps=total_steps,
        total_percentage=total_percentage,
        description=description,
        parent=parent,
    )

    # Register the tracker
    register_progress_tracker(tracker)

    return tracker
