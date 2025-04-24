"""Core module for the Augment Adam assistant.

This module provides core functionality for the Augment Adam assistant,
including error handling, settings management, and other utilities.

Version: 0.1.0
Created: 2025-04-25
Updated: 2025-04-24
"""

from augment_adam.core.agent import Agent
from augment_adam.core.assistant import Assistant
from augment_adam.core.async_assistant import AsyncAssistant
from augment_adam.core.circuit_breaker import CircuitBreaker
from augment_adam.core.errors import (
    AugmentAdamError, ErrorCategory,
    ResourceError, DatabaseError,
    wrap_error, log_error
)
from augment_adam.core.memory import MemoryManager
from augment_adam.core.model_manager import ModelManager
from augment_adam.core.parallel_executor import ParallelExecutor
from augment_adam.core.progress import ProgressTracker, ProgressCallback
from augment_adam.core.prompt_manager import PromptManager, PromptTemplate
from augment_adam.core.settings import (
    get_settings, update_settings, reset_settings,
    SettingsScope
)
from augment_adam.core.task_persistence import TaskPersistence
from augment_adam.core.task_queue import TaskQueue, Task, TaskStatus
from augment_adam.core.task_scheduler import TaskScheduler

__all__ = [
    "Agent",
    "Assistant",
    "AsyncAssistant",
    "CircuitBreaker",
    "AugmentAdamError",
    "ErrorCategory",
    "ResourceError",
    "DatabaseError",
    "wrap_error",
    "log_error",
    "MemoryManager",
    "ModelManager",
    "ParallelExecutor",
    "ProgressTracker",
    "ProgressCallback",
    "PromptManager",
    "PromptTemplate",
    "get_settings",
    "update_settings",
    "reset_settings",
    "SettingsScope",
    "TaskPersistence",
    "TaskQueue",
    "Task",
    "TaskStatus",
    "TaskScheduler",
]