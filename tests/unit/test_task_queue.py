"""Unit tests for the task queue system.

This module contains tests for the task queue system for async processing.

Version: 0.1.0
Created: 2025-04-23
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from dukat.core.task_queue import (
    Task,
    TaskQueue,
    TaskStatus,
    add_task,
    get_task,
    cancel_task,
    wait_for_task,
    get_queue_stats,
    get_task_queue,
)


@pytest.fixture
def task_queue():
    """Create a task queue for testing."""
    queue = TaskQueue(max_workers=2, max_queue_size=10)
    return queue


@pytest.mark.asyncio
async def test_task_creation():
    """Test creating a task."""
    # Create a mock function
    mock_func = MagicMock()
    
    # Create a task
    task = Task(
        func=mock_func,
        args=[1, 2, 3],
        kwargs={"a": 1, "b": 2},
        task_id="test-task",
        priority=5,
        timeout=10.0,
        retry_count=3,
        retry_delay=0.5,
        dependencies=["dep1", "dep2"],
    )
    
    # Check that the task was created correctly
    assert task.func is mock_func
    assert task.args == [1, 2, 3]
    assert task.kwargs == {"a": 1, "b": 2}
    assert task.task_id == "test-task"
    assert task.priority == 5
    assert task.timeout == 10.0
    assert task.retry_count == 3
    assert task.retry_delay == 0.5
    assert task.dependencies == ["dep1", "dep2"]
    assert task.status == TaskStatus.PENDING
    assert task.result is None
    assert task.error is None
    assert task.created_at is not None
    assert task.started_at is None
    assert task.completed_at is None
    assert task.retries_left == 3
    assert task.future is None


@pytest.mark.asyncio
async def test_task_execution_sync():
    """Test executing a synchronous task."""
    # Create a mock function
    mock_func = MagicMock(return_value="result")
    
    # Create a task
    task = Task(
        func=mock_func,
        args=[1, 2, 3],
        kwargs={"a": 1, "b": 2},
    )
    
    # Execute the task
    result = await task.execute()
    
    # Check that the task was executed correctly
    assert result == "result"
    assert task.result == "result"
    assert task.status == TaskStatus.COMPLETED
    assert task.started_at is not None
    assert task.completed_at is not None
    assert task.error is None
    
    # Check that the function was called with the correct arguments
    mock_func.assert_called_once_with(1, 2, 3, a=1, b=2)


@pytest.mark.asyncio
async def test_task_execution_async():
    """Test executing an asynchronous task."""
    # Create a mock async function
    mock_func = AsyncMock(return_value="result")
    
    # Create a task
    task = Task(
        func=mock_func,
        args=[1, 2, 3],
        kwargs={"a": 1, "b": 2},
    )
    
    # Execute the task
    result = await task.execute()
    
    # Check that the task was executed correctly
    assert result == "result"
    assert task.result == "result"
    assert task.status == TaskStatus.COMPLETED
    assert task.started_at is not None
    assert task.completed_at is not None
    assert task.error is None
    
    # Check that the function was called with the correct arguments
    mock_func.assert_called_once_with(1, 2, 3, a=1, b=2)


@pytest.mark.asyncio
async def test_task_execution_error():
    """Test executing a task that raises an error."""
    # Create a mock function that raises an error
    mock_func = MagicMock(side_effect=ValueError("test error"))
    
    # Create a task
    task = Task(
        func=mock_func,
        args=[1, 2, 3],
        kwargs={"a": 1, "b": 2},
    )
    
    # Execute the task
    with pytest.raises(ValueError, match="test error"):
        await task.execute()
    
    # Check that the task was executed correctly
    assert task.result is None
    assert task.status == TaskStatus.FAILED
    assert task.started_at is not None
    assert task.completed_at is not None
    assert task.error == "test error"
    
    # Check that the function was called with the correct arguments
    mock_func.assert_called_once_with(1, 2, 3, a=1, b=2)


@pytest.mark.asyncio
async def test_task_to_dict():
    """Test converting a task to a dictionary."""
    # Create a task
    task = Task(
        func=lambda: None,
        task_id="test-task",
        priority=5,
        timeout=10.0,
        retry_count=3,
        retry_delay=0.5,
        dependencies=["dep1", "dep2"],
    )
    
    # Convert the task to a dictionary
    task_dict = task.to_dict()
    
    # Check that the dictionary contains the correct values
    assert task_dict["task_id"] == "test-task"
    assert task_dict["status"] == "pending"
    assert task_dict["created_at"] is not None
    assert task_dict["started_at"] is None
    assert task_dict["completed_at"] is None
    assert task_dict["result"] is None
    assert task_dict["error"] is None
    assert task_dict["priority"] == 5
    assert task_dict["timeout"] == 10.0
    assert task_dict["retry_count"] == 3
    assert task_dict["retries_left"] == 3
    assert task_dict["dependencies"] == ["dep1", "dep2"]


@pytest.mark.asyncio
async def test_task_queue_start_stop(task_queue):
    """Test starting and stopping the task queue."""
    # Start the queue
    await task_queue.start()
    
    # Check that the queue is running
    assert task_queue.running
    assert len(task_queue.workers) == 2
    
    # Stop the queue
    await task_queue.stop()
    
    # Check that the queue is stopped
    assert not task_queue.running
    assert len(task_queue.workers) == 0


@pytest.mark.asyncio
async def test_task_queue_add_task(task_queue):
    """Test adding a task to the queue."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task
        task = await task_queue.add_task(
            func=lambda: "result",
            task_id="test-task",
            priority=5,
        )
        
        # Check that the task was added correctly
        assert task.task_id == "test-task"
        assert task.priority == 5
        assert task.future is not None
        assert task.task_id in task_queue.tasks
        assert task_queue.queue.qsize() == 1
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_get_task(task_queue):
    """Test getting a task from the queue."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task
        task = await task_queue.add_task(
            func=lambda: "result",
            task_id="test-task",
        )
        
        # Get the task
        retrieved_task = await task_queue.get_task("test-task")
        
        # Check that the task was retrieved correctly
        assert retrieved_task is task
        
        # Try to get a nonexistent task
        nonexistent_task = await task_queue.get_task("nonexistent")
        
        # Check that the task was not found
        assert nonexistent_task is None
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_cancel_task(task_queue):
    """Test cancelling a task in the queue."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task
        task = await task_queue.add_task(
            func=lambda: "result",
            task_id="test-task",
        )
        
        # Cancel the task
        result = await task_queue.cancel_task("test-task")
        
        # Check that the task was cancelled
        assert result is True
        assert task.status == TaskStatus.CANCELLED
        
        # Try to cancel a nonexistent task
        result = await task_queue.cancel_task("nonexistent")
        
        # Check that the task was not found
        assert result is False
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_wait_for_task(task_queue):
    """Test waiting for a task to complete."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task that completes immediately
        task = await task_queue.add_task(
            func=lambda: "result",
            task_id="test-task",
        )
        
        # Wait for the task to complete
        result = await task_queue.wait_for_task("test-task", timeout=1.0)
        
        # Check that the task completed
        assert result == "result"
        assert task.status == TaskStatus.COMPLETED
        
        # Try to wait for a nonexistent task
        result = await task_queue.wait_for_task("nonexistent", timeout=0.1)
        
        # Check that the task was not found
        assert result is None
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_wait_for_task_timeout(task_queue):
    """Test waiting for a task to complete with a timeout."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task that takes a long time to complete
        task = await task_queue.add_task(
            func=lambda: time.sleep(1.0) or "result",
            task_id="test-task",
        )
        
        # Wait for the task with a short timeout
        result = await task_queue.wait_for_task("test-task", timeout=0.1)
        
        # Check that the task timed out
        assert result is None
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_dependencies(task_queue):
    """Test task dependencies."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task
        task1 = await task_queue.add_task(
            func=lambda: "result1",
            task_id="task1",
        )
        
        # Add a task that depends on the first task
        task2 = await task_queue.add_task(
            func=lambda: "result2",
            task_id="task2",
            dependencies=["task1"],
        )
        
        # Wait for both tasks to complete
        await asyncio.gather(
            task_queue.wait_for_task("task1"),
            task_queue.wait_for_task("task2"),
        )
        
        # Check that both tasks completed
        assert task1.status == TaskStatus.COMPLETED
        assert task2.status == TaskStatus.COMPLETED
        assert task1.result == "result1"
        assert task2.result == "result2"
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_retry(task_queue):
    """Test task retry."""
    # Create a mock function that fails once then succeeds
    mock_func = MagicMock(side_effect=[ValueError("test error"), "result"])
    
    # Start the queue
    await task_queue.start()
    
    try:
        # Add a task with retry
        task = await task_queue.add_task(
            func=mock_func,
            task_id="test-task",
            retry_count=1,
            retry_delay=0.1,
        )
        
        # Wait for the task to complete
        result = await task_queue.wait_for_task("test-task", timeout=1.0)
        
        # Check that the task completed after retry
        assert result == "result"
        assert task.status == TaskStatus.COMPLETED
        assert task.retries_left == 0
        assert mock_func.call_count == 2
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_task_queue_get_queue_stats(task_queue):
    """Test getting queue statistics."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add some tasks
        await task_queue.add_task(
            func=lambda: "result1",
            task_id="task1",
        )
        
        await task_queue.add_task(
            func=lambda: "result2",
            task_id="task2",
        )
        
        # Get queue stats
        stats = await task_queue.get_queue_stats()
        
        # Check that the stats are correct
        assert stats["queue_size"] <= 2  # May be less if tasks have started
        assert stats["max_queue_size"] == 10
        assert stats["workers"] == 2
        assert stats["max_workers"] == 2
        assert stats["running"] is True
        assert stats["tasks"]["total"] == 2
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_global_task_queue_functions():
    """Test the global task queue functions."""
    # Get the default task queue
    queue = get_task_queue()
    
    # Start the queue
    await queue.start()
    
    try:
        # Add a task
        task = await add_task(
            func=lambda: "result",
            task_id="test-task",
        )
        
        # Get the task
        retrieved_task = await get_task("test-task")
        
        # Check that the task was retrieved correctly
        assert retrieved_task is task
        
        # Wait for the task to complete
        result = await wait_for_task("test-task", timeout=1.0)
        
        # Check that the task completed
        assert result == "result"
        
        # Get queue stats
        stats = await get_queue_stats()
        
        # Check that the stats are correct
        assert stats["tasks"]["total"] >= 1
        assert stats["tasks"]["completed"] >= 1
        
        # Add another task
        task2 = await add_task(
            func=lambda: "result2",
            task_id="test-task2",
        )
        
        # Cancel the task
        result = await cancel_task("test-task2")
        
        # Check that the task was cancelled
        assert result is True
    
    finally:
        # Stop the queue
        await queue.stop()
