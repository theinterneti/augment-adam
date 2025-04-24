#!/usr/bin/env python3
"""Example of progress tracking.

This example demonstrates how to use the progress tracking system.

Version: 0.1.0
Created: 2025-04-26
"""

import asyncio
import time
import random
from typing import Optional

from dukat.core.progress import (
    ProgressTracker, create_progress_tracker, get_progress_tracker_stats
)
from dukat.cli.progress_bar import create_progress_bar
from dukat.core.task_queue import add_task


async def task_with_steps(
    steps: int,
    min_delay: float = 0.1,
    max_delay: float = 0.5,
    progress_tracker: Optional[ProgressTracker] = None,
) -> str:
    """A task that reports progress by steps.
    
    Args:
        steps: Number of steps to complete
        min_delay: Minimum delay between steps
        max_delay: Maximum delay between steps
        progress_tracker: Progress tracker to use
        
    Returns:
        A completion message
    """
    # If no progress tracker was provided, create one
    if progress_tracker is None:
        progress_tracker = create_progress_tracker(
            task_id="task_with_steps",
            total_steps=steps,
            description="Task with steps",
        )
        progress_tracker.start()
    
    # Create a progress bar
    progress_bar = create_progress_bar(progress_tracker)
    
    # Perform the steps
    for i in range(steps):
        # Simulate some work
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
        
        # Update progress
        progress_tracker.update_step(
            i + 1,
            message=f"Completed step {i + 1}/{steps}",
            details={"step": i + 1, "delay": delay},
        )
    
    # Complete the task
    progress_tracker.complete(message="Task completed successfully")
    
    return "Task completed successfully"


async def task_with_percentage(
    total_percentage: float = 100.0,
    steps: int = 10,
    min_delay: float = 0.1,
    max_delay: float = 0.5,
    progress_tracker: Optional[ProgressTracker] = None,
) -> str:
    """A task that reports progress by percentage.
    
    Args:
        total_percentage: Total percentage to reach
        steps: Number of steps to complete
        min_delay: Minimum delay between steps
        max_delay: Maximum delay between steps
        progress_tracker: Progress tracker to use
        
    Returns:
        A completion message
    """
    # If no progress tracker was provided, create one
    if progress_tracker is None:
        progress_tracker = create_progress_tracker(
            task_id="task_with_percentage",
            total_percentage=total_percentage,
            description="Task with percentage",
        )
        progress_tracker.start()
    
    # Create a progress bar
    progress_bar = create_progress_bar(progress_tracker)
    
    # Calculate the percentage increment per step
    increment = total_percentage / steps
    
    # Perform the steps
    for i in range(steps):
        # Simulate some work
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
        
        # Update progress
        current_percentage = (i + 1) * increment
        progress_tracker.update_percentage(
            current_percentage,
            message=f"Progress: {current_percentage:.1f}%",
            details={"step": i + 1, "delay": delay},
        )
    
    # Complete the task
    progress_tracker.complete(message="Task completed successfully")
    
    return "Task completed successfully"


async def task_with_children() -> str:
    """A task with child tasks.
    
    Returns:
        A completion message
    """
    # Create a parent progress tracker
    parent = create_progress_tracker(
        task_id="parent_task",
        description="Parent task with children",
    )
    parent.start()
    
    # Create a progress bar for the parent
    parent_bar = create_progress_bar(parent)
    
    # Create child trackers
    child1 = parent.add_child(
        child_id="child1",
        weight=0.6,  # 60% of parent's progress
        total_steps=5,
        description="Child task 1",
    )
    
    child2 = parent.add_child(
        child_id="child2",
        weight=0.4,  # 40% of parent's progress
        total_steps=3,
        description="Child task 2",
    )
    
    # Start the first child
    child1.start()
    child1_bar = create_progress_bar(child1)
    
    # Perform steps for the first child
    for i in range(5):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        child1.update_step(
            i + 1,
            message=f"Child 1: Step {i + 1}/5",
        )
    
    # Complete the first child
    child1.complete()
    
    # Start the second child
    child2.start()
    child2_bar = create_progress_bar(child2)
    
    # Perform steps for the second child
    for i in range(3):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        child2.update_step(
            i + 1,
            message=f"Child 2: Step {i + 1}/3",
        )
    
    # Complete the second child
    child2.complete()
    
    # The parent should now be at 100%
    parent.complete(message="All child tasks completed")
    
    return "Task with children completed successfully"


async def task_queue_example() -> None:
    """Example of using progress tracking with the task queue."""
    print("\nTask Queue Example:")
    print("------------------")
    
    # Add tasks to the queue
    task1 = await add_task(
        task_with_steps,
        args=[5, 0.1, 0.3],
        task_id="queue_task_1",
        description="Queue Task 1",
        total_steps=5,
    )
    
    task2 = await add_task(
        task_with_percentage,
        args=[100.0, 8, 0.1, 0.3],
        task_id="queue_task_2",
        description="Queue Task 2",
        priority=1,  # Higher priority
    )
    
    # Wait for the tasks to complete
    await asyncio.gather(
        task1.future,
        task2.future,
    )
    
    # Print the task statistics
    print("\nTask Statistics:")
    print(f"Task 1: {task1.status.value}, Elapsed: {task1.completed_at - task1.started_at:.2f}s")
    print(f"Task 2: {task2.status.value}, Elapsed: {task2.completed_at - task2.started_at:.2f}s")


async def main() -> None:
    """Run the examples."""
    print("Progress Tracking Examples")
    print("=========================")
    
    print("\nExample 1: Task with Steps")
    print("--------------------------")
    await task_with_steps(5)
    
    print("\nExample 2: Task with Percentage")
    print("------------------------------")
    await task_with_percentage(100.0, 8)
    
    print("\nExample 3: Task with Children")
    print("----------------------------")
    await task_with_children()
    
    # Example with the task queue
    await task_queue_example()
    
    # Print all progress tracker statistics
    print("\nProgress Tracker Statistics:")
    stats = get_progress_tracker_stats()
    for task_id, progress in stats.items():
        print(f"- {task_id}: {progress['state']}, {progress['current_percentage']:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
