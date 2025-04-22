"""Core components for the Dukat assistant.

This package contains the core components of the Dukat assistant,
including model management, memory systems, and prompt handling.

Version: 0.1.0
Created: 2025-04-22
"""

from dukat.core.assistant import Assistant
from dukat.core.async_assistant import AsyncAssistant, get_async_assistant
from dukat.core.model_manager import ModelManager, get_model_manager
from dukat.core.memory import Memory, get_memory
from dukat.core.task_queue import (
    Task, TaskQueue, TaskStatus,
    add_task, get_task, cancel_task, wait_for_task,
    get_queue_stats, get_task_queue
)

__all__ = [
    "Assistant",
    "AsyncAssistant",
    "get_async_assistant",
    "ModelManager",
    "get_model_manager",
    "Memory",
    "get_memory",
    "Task",
    "TaskQueue",
    "TaskStatus",
    "add_task",
    "get_task",
    "cancel_task",
    "wait_for_task",
    "get_queue_stats",
    "get_task_queue",
]
