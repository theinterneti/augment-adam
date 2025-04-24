"""Task queue persistence module.

This module provides functionality to save and load the task queue state.

Version: 0.1.0
Created: 2025-04-25
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Optional

from dukat.core.task_queue import Task, TaskStatus, TaskQueue

logger = logging.getLogger(__name__)


class TaskPersistence:
    """Task queue persistence manager.
    
    This class provides functionality to save and load the task queue state.
    """
    
    def __init__(
        self,
        persistence_dir: str = None,
        auto_save_interval: float = 60.0,
        max_history_files: int = 5,
    ):
        """Initialize the task persistence manager.
        
        Args:
            persistence_dir: Directory to store persistence files.
                If None, defaults to ~/.dukat/tasks
            auto_save_interval: Interval in seconds between auto-saves.
                Set to 0 to disable auto-saving.
            max_history_files: Maximum number of history files to keep.
        """
        # Set persistence directory
        if persistence_dir is None:
            home_dir = os.path.expanduser("~")
            persistence_dir = os.path.join(home_dir, ".dukat", "tasks")
        
        self.persistence_dir = persistence_dir
        self.auto_save_interval = auto_save_interval
        self.max_history_files = max_history_files
        self.last_save_time = 0
        
        # Create the persistence directory if it doesn't exist
        os.makedirs(self.persistence_dir, exist_ok=True)
    
    def get_persistence_file_path(self, timestamp: Optional[int] = None) -> str:
        """Get the path to a persistence file.
        
        Args:
            timestamp: Optional timestamp to include in the filename.
                If None, uses the current time.
                
        Returns:
            The path to the persistence file.
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        return os.path.join(
            self.persistence_dir,
            f"tasks_{timestamp}.json"
        )
    
    def get_latest_persistence_file(self) -> Optional[str]:
        """Get the path to the latest persistence file.
        
        Returns:
            The path to the latest persistence file, or None if no files exist.
        """
        try:
            files = [
                f for f in os.listdir(self.persistence_dir)
                if f.startswith("tasks_") and f.endswith(".json")
            ]
            
            if not files:
                return None
            
            # Sort files by timestamp (newest first)
            files.sort(reverse=True)
            
            return os.path.join(self.persistence_dir, files[0])
            
        except Exception as e:
            logger.error(f"Error getting latest persistence file: {str(e)}")
            return None
    
    def cleanup_old_files(self):
        """Remove old persistence files, keeping only the most recent ones."""
        try:
            files = [
                f for f in os.listdir(self.persistence_dir)
                if f.startswith("tasks_") and f.endswith(".json")
            ]
            
            if len(files) <= self.max_history_files:
                return
            
            # Sort files by timestamp (oldest first)
            files.sort()
            
            # Remove oldest files
            for f in files[:-self.max_history_files]:
                file_path = os.path.join(self.persistence_dir, f)
                os.remove(file_path)
                logger.debug(f"Removed old persistence file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error cleaning up old persistence files: {str(e)}")
    
    def save_queue(self, queue: TaskQueue) -> bool:
        """Save the task queue state to a file.
        
        Args:
            queue: The task queue to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the current time
            current_time = time.time()
            
            # Skip if auto-save interval hasn't elapsed
            if (
                self.auto_save_interval > 0 and
                current_time - self.last_save_time < self.auto_save_interval
            ):
                return True
            
            # Get the file path
            file_path = self.get_persistence_file_path()
            
            # Convert tasks to serializable format
            tasks_data = {}
            for task_id, task in queue.tasks.items():
                # Skip completed, failed, or cancelled tasks
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                    continue
                
                # Convert task to dictionary
                task_dict = task.to_dict()
                
                # Add function name for reconstruction
                if hasattr(task.func, "__name__"):
                    task_dict["func_name"] = task.func.__name__
                elif hasattr(task.func, "__qualname__"):
                    task_dict["func_name"] = task.func.__qualname__
                else:
                    task_dict["func_name"] = str(task.func)
                
                # Add module name if available
                if hasattr(task.func, "__module__"):
                    task_dict["func_module"] = task.func.__module__
                
                tasks_data[task_id] = task_dict
            
            # Create queue data
            queue_data = {
                "timestamp": current_time,
                "max_workers": queue.max_workers,
                "max_queue_size": queue.max_queue_size,
                "tasks": tasks_data,
            }
            
            # Save to file
            with open(file_path, "w") as f:
                json.dump(queue_data, f, indent=2)
            
            # Update last save time
            self.last_save_time = current_time
            
            # Cleanup old files
            self.cleanup_old_files()
            
            logger.info(f"Saved task queue state to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving task queue state: {str(e)}")
            return False
    
    def load_queue(self, queue: TaskQueue) -> bool:
        """Load the task queue state from a file.
        
        Args:
            queue: The task queue to load into.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the latest persistence file
            file_path = self.get_latest_persistence_file()
            
            if not file_path or not os.path.exists(file_path):
                logger.warning("No persistence file found")
                return False
            
            # Load from file
            with open(file_path, "r") as f:
                queue_data = json.load(f)
            
            # Update queue parameters
            queue.max_workers = queue_data.get("max_workers", queue.max_workers)
            queue.max_queue_size = queue_data.get("max_queue_size", queue.max_queue_size)
            
            # Load tasks
            tasks_data = queue_data.get("tasks", {})
            
            # We can't fully restore tasks since we can't serialize functions
            # But we can log the tasks that were pending
            for task_id, task_dict in tasks_data.items():
                logger.info(
                    f"Found persisted task: {task_id} "
                    f"(status: {task_dict.get('status')}, "
                    f"function: {task_dict.get('func_module')}.{task_dict.get('func_name')})"
                )
            
            logger.info(f"Loaded task queue state from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading task queue state: {str(e)}")
            return False
