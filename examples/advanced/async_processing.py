#!/usr/bin/env python3
"""Example demonstrating async processing capabilities in Dukat.

This example shows how to use the AsyncAssistant class to perform
parallel task execution and scheduled tasks.

Usage:
    python examples/async_processing.py
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from dukat.core.async_assistant import get_async_assistant
from dukat.core.parallel_executor import ResourceRequirement, ResourceType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Example tasks
async def task_1(progress_tracker=None):
    """A simple task that sleeps for 2 seconds."""
    logger.info("Task 1 started")
    
    if progress_tracker:
        progress_tracker.start()
    
    # Simulate work with progress updates
    for i in range(10):
        await asyncio.sleep(0.2)
        if progress_tracker:
            progress_tracker.update_percentage((i + 1) * 10)
    
    if progress_tracker:
        progress_tracker.complete()
    
    logger.info("Task 1 completed")
    return "Task 1 result"


async def task_2(progress_tracker=None):
    """A task that depends on external resources."""
    logger.info("Task 2 started")
    
    if progress_tracker:
        progress_tracker.start()
    
    # Simulate work with progress updates
    for i in range(5):
        await asyncio.sleep(0.5)
        if progress_tracker:
            progress_tracker.update_percentage((i + 1) * 20)
    
    if progress_tracker:
        progress_tracker.complete()
    
    logger.info("Task 2 completed")
    return "Task 2 result"


async def task_3(arg1, arg2, progress_tracker=None):
    """A task that takes arguments."""
    logger.info(f"Task 3 started with args: {arg1}, {arg2}")
    
    if progress_tracker:
        progress_tracker.start()
    
    # Simulate work with progress updates
    for i in range(8):
        await asyncio.sleep(0.3)
        if progress_tracker:
            progress_tracker.update_percentage((i + 1) * 12.5)
    
    if progress_tracker:
        progress_tracker.complete()
    
    logger.info("Task 3 completed")
    return f"Task 3 result: {arg1} + {arg2} = {arg1 + arg2}"


async def scheduled_task(name="Scheduled Task"):
    """A task that runs on a schedule."""
    logger.info(f"{name} executed at {datetime.now()}")
    return f"{name} executed successfully"


async def main():
    """Main function demonstrating async processing capabilities."""
    # Create an async assistant
    assistant = await get_async_assistant(
        model_name="llama3:8b",
        max_parallel_tasks=3,
    )
    
    # 1. Execute tasks in parallel
    logger.info("Executing tasks in parallel...")
    
    tasks = [
        {
            "func": task_1,
            "task_id": "task_1",
            "description": "Simple sleep task",
            "total_steps": 10,
            "type": "example_task",
        },
        {
            "func": task_2,
            "task_id": "task_2",
            "description": "External resource task",
            "total_steps": 5,
            "type": "example_task",
            "resource_requirements": [
                ResourceRequirement(ResourceType.NETWORK, amount=0.5),
            ],
        },
        {
            "func": task_3,
            "args": [10, 20],
            "task_id": "task_3",
            "description": "Task with arguments",
            "total_steps": 8,
            "type": "example_task",
            "dependencies": ["task_1"],  # This task depends on task_1
        },
    ]
    
    results = await assistant.execute_tasks_in_parallel(tasks)
    
    logger.info("Parallel execution results:")
    for task_id, result in results.items():
        logger.info(f"  {task_id}: {result}")
    
    # 2. Schedule periodic tasks
    logger.info("Scheduling periodic tasks...")
    
    # Schedule a task to run every 2 seconds
    periodic_task_id = await assistant.schedule_periodic_task(
        func=scheduled_task,
        interval=2.0,
        kwargs={"name": "Periodic Task"},
        max_runs=3,
        description="A task that runs every 2 seconds",
    )
    
    # Schedule a task to run at a specific time
    future_time = datetime.now() + timedelta(seconds=5)
    scheduled_task_id = await assistant.schedule_task_at_time(
        func=scheduled_task,
        schedule_time=future_time,
        kwargs={"name": "One-time Task"},
        description=f"A task scheduled for {future_time}",
    )
    
    # Wait for scheduled tasks to complete
    logger.info("Waiting for scheduled tasks to complete...")
    await asyncio.sleep(10)
    
    # 3. Get task statistics
    logger.info("Getting task statistics...")
    stats = await assistant.get_queue_stats()
    
    logger.info("Task queue statistics:")
    logger.info(f"  Active tasks: {stats.get('active_tasks', 0)}")
    logger.info(f"  Completed tasks: {stats.get('completed_tasks', 0)}")
    logger.info(f"  Failed tasks: {stats.get('failed_tasks', 0)}")
    
    if "circuit_breakers" in stats:
        logger.info("Circuit breakers:")
        for name, breaker in stats["circuit_breakers"].items():
            logger.info(f"  {name}: {breaker['state']}")
    
    if "parallel_executor" in stats:
        logger.info("Parallel executor metrics:")
        metrics = stats["parallel_executor"]
        logger.info(f"  Total tasks: {metrics.get('total_tasks', 0)}")
        logger.info(f"  Completed tasks: {metrics.get('completed_tasks', 0)}")
        logger.info(f"  Resource usage: {metrics.get('resource_usage', {})}")
    
    logger.info("Example completed")


if __name__ == "__main__":
    asyncio.run(main())
