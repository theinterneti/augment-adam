"""Unit tests for the task persistence system.

This module contains tests for the task persistence system.

Version: 0.1.0
Created: 2025-04-25
"""

import asyncio
import json
import os
import pytest
import tempfile
import time
from unittest.mock import AsyncMock, MagicMock, patch

from dukat.core.task_queue import Task, TaskQueue, TaskStatus
from dukat.core.task_persistence import TaskPersistence


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def task_persistence(temp_dir):
    """Create a task persistence manager for testing."""
    persistence = TaskPersistence(
        persistence_dir=temp_dir,
        auto_save_interval=0.1,
        max_history_files=3,
    )
    return persistence


@pytest.fixture
def task_queue():
    """Create a task queue for testing."""
    queue = TaskQueue(
        max_workers=2,
        max_queue_size=10,
        enable_persistence=False,  # Disable persistence for testing
    )
    return queue


@pytest.mark.asyncio
async def test_task_persistence_init(temp_dir):
    """Test initializing the task persistence manager."""
    # Create a persistence manager
    persistence = TaskPersistence(
        persistence_dir=temp_dir,
        auto_save_interval=60.0,
        max_history_files=5,
    )
    
    # Check that the persistence directory was created
    assert os.path.exists(temp_dir)
    
    # Check that the persistence manager was initialized correctly
    assert persistence.persistence_dir == temp_dir
    assert persistence.auto_save_interval == 60.0
    assert persistence.max_history_files == 5
    assert persistence.last_save_time == 0


@pytest.mark.asyncio
async def test_get_persistence_file_path(task_persistence):
    """Test getting the path to a persistence file."""
    # Get a file path with a specific timestamp
    timestamp = 1234567890
    file_path = task_persistence.get_persistence_file_path(timestamp)
    
    # Check that the file path is correct
    assert file_path.endswith(f"tasks_{timestamp}.json")
    assert os.path.dirname(file_path) == task_persistence.persistence_dir
    
    # Get a file path with the current timestamp
    file_path = task_persistence.get_persistence_file_path()
    
    # Check that the file path is correct
    assert file_path.startswith(task_persistence.persistence_dir)
    assert file_path.endswith(".json")


@pytest.mark.asyncio
async def test_get_latest_persistence_file(task_persistence, temp_dir):
    """Test getting the latest persistence file."""
    # Create some test files
    for i in range(3):
        timestamp = 1000000 + i
        file_path = os.path.join(temp_dir, f"tasks_{timestamp}.json")
        with open(file_path, "w") as f:
            f.write("{}")
    
    # Get the latest file
    latest_file = task_persistence.get_latest_persistence_file()
    
    # Check that the latest file is correct
    assert latest_file.endswith("tasks_1000002.json")
    
    # Remove all files
    for i in range(3):
        timestamp = 1000000 + i
        file_path = os.path.join(temp_dir, f"tasks_{timestamp}.json")
        os.remove(file_path)
    
    # Get the latest file when no files exist
    latest_file = task_persistence.get_latest_persistence_file()
    
    # Check that no file was found
    assert latest_file is None


@pytest.mark.asyncio
async def test_cleanup_old_files(task_persistence, temp_dir):
    """Test cleaning up old persistence files."""
    # Create some test files
    for i in range(5):
        timestamp = 1000000 + i
        file_path = os.path.join(temp_dir, f"tasks_{timestamp}.json")
        with open(file_path, "w") as f:
            f.write("{}")
    
    # Clean up old files
    task_persistence.cleanup_old_files()
    
    # Check that only the most recent files were kept
    files = [
        f for f in os.listdir(temp_dir)
        if f.startswith("tasks_") and f.endswith(".json")
    ]
    assert len(files) == 3
    assert "tasks_1000002.json" in files
    assert "tasks_1000003.json" in files
    assert "tasks_1000004.json" in files


@pytest.mark.asyncio
async def test_save_queue(task_persistence, task_queue):
    """Test saving the task queue state."""
    # Start the queue
    await task_queue.start()
    
    try:
        # Add some tasks
        task1 = await task_queue.add_task(
            func=lambda: "result1",
            task_id="task1",
        )
        
        task2 = await task_queue.add_task(
            func=lambda: "result2",
            task_id="task2",
            dependencies=["task1"],
        )
        
        # Save the queue
        result = task_persistence.save_queue(task_queue)
        
        # Check that the save was successful
        assert result is True
        
        # Check that a file was created
        files = [
            f for f in os.listdir(task_persistence.persistence_dir)
            if f.startswith("tasks_") and f.endswith(".json")
        ]
        assert len(files) == 1
        
        # Check the file contents
        file_path = os.path.join(task_persistence.persistence_dir, files[0])
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Check that the data is correct
        assert "timestamp" in data
        assert data["max_workers"] == task_queue.max_workers
        assert data["max_queue_size"] == task_queue.max_queue_size
        assert "tasks" in data
        assert len(data["tasks"]) == 2
        assert "task1" in data["tasks"]
        assert "task2" in data["tasks"]
        assert data["tasks"]["task1"]["task_id"] == "task1"
        assert data["tasks"]["task2"]["task_id"] == "task2"
        assert data["tasks"]["task2"]["dependencies"] == ["task1"]
    
    finally:
        # Stop the queue
        await task_queue.stop()


@pytest.mark.asyncio
async def test_load_queue(task_persistence, task_queue, temp_dir):
    """Test loading the task queue state."""
    # Create a test file
    timestamp = int(time.time())
    file_path = os.path.join(temp_dir, f"tasks_{timestamp}.json")
    
    # Create test data
    data = {
        "timestamp": timestamp,
        "max_workers": 10,
        "max_queue_size": 50,
        "tasks": {
            "task1": {
                "task_id": "task1",
                "status": "pending",
                "created_at": timestamp - 100,
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None,
                "priority": 5,
                "timeout": 10.0,
                "retry_count": 3,
                "retries_left": 3,
                "dependencies": [],
                "func_name": "test_func",
                "func_module": "test_module",
            },
            "task2": {
                "task_id": "task2",
                "status": "running",
                "created_at": timestamp - 50,
                "started_at": timestamp - 25,
                "completed_at": None,
                "result": None,
                "error": None,
                "priority": 10,
                "timeout": None,
                "retry_count": 0,
                "retries_left": 0,
                "dependencies": ["task1"],
                "func_name": "test_func2",
                "func_module": "test_module",
            },
        },
    }
    
    # Write the data to the file
    with open(file_path, "w") as f:
        json.dump(data, f)
    
    # Load the queue
    result = task_persistence.load_queue(task_queue)
    
    # Check that the load was successful
    assert result is True
    
    # Check that the queue parameters were updated
    assert task_queue.max_workers == 10
    assert task_queue.max_queue_size == 50


@pytest.mark.asyncio
async def test_task_queue_with_persistence(temp_dir):
    """Test the task queue with persistence enabled."""
    # Create a task queue with persistence enabled
    queue = TaskQueue(
        max_workers=2,
        max_queue_size=10,
        enable_persistence=True,
        persistence_dir=temp_dir,
        auto_save_interval=0.1,
    )
    
    # Start the queue
    await queue.start()
    
    try:
        # Add some tasks
        task1 = await queue.add_task(
            func=lambda: "result1",
            task_id="task1",
        )
        
        task2 = await queue.add_task(
            func=lambda: "result2",
            task_id="task2",
            dependencies=["task1"],
        )
        
        # Wait for the tasks to complete
        await asyncio.gather(
            queue.wait_for_task("task1"),
            queue.wait_for_task("task2"),
        )
        
        # Wait for auto-save
        await asyncio.sleep(0.2)
        
        # Check that a persistence file was created
        files = [
            f for f in os.listdir(temp_dir)
            if f.startswith("tasks_") and f.endswith(".json")
        ]
        assert len(files) > 0
    
    finally:
        # Stop the queue
        await queue.stop()


@pytest.mark.asyncio
async def test_task_queue_auto_save(temp_dir):
    """Test the task queue auto-save functionality."""
    # Create a task queue with persistence enabled
    queue = TaskQueue(
        max_workers=2,
        max_queue_size=10,
        enable_persistence=True,
        persistence_dir=temp_dir,
        auto_save_interval=0.1,
    )
    
    # Mock the persistence.save_queue method
    with patch("dukat.core.task_persistence.TaskPersistence.save_queue") as mock_save:
        mock_save.return_value = True
        
        # Start the queue
        await queue.start()
        
        try:
            # Wait for auto-save to run
            await asyncio.sleep(0.2)
            
            # Check that save_queue was called
            assert mock_save.call_count >= 1
        
        finally:
            # Stop the queue
            await queue.stop()
