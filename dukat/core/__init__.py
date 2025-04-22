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
from dukat.core.errors import (
    DukatError, ErrorCategory,
    NetworkError, TimeoutError, ResourceError,
    ValidationError, AuthenticationError, AuthorizationError, NotFoundError,
    DatabaseError, ApiError, ModelError, PluginError,
    CircuitBreaker, CircuitBreakerState, CircuitBreakerError,
    retry, classify_error, wrap_error, log_error
)
from dukat.core.settings import (
    Settings, SettingsScope, SettingsManager, SettingsError,
    ModelSettings, MemorySettings, UISettings, PluginSettings,
    LoggingSettings, SecuritySettings, NetworkSettings,
    get_settings, get_settings_manager, update_settings, reset_settings
)

__all__ = [
    # Assistant components
    "Assistant",
    "AsyncAssistant",
    "get_async_assistant",
    "ModelManager",
    "get_model_manager",
    "Memory",
    "get_memory",

    # Task queue components
    "Task",
    "TaskQueue",
    "TaskStatus",
    "add_task",
    "get_task",
    "cancel_task",
    "wait_for_task",
    "get_queue_stats",
    "get_task_queue",

    # Error handling components
    "DukatError",
    "ErrorCategory",
    "NetworkError",
    "TimeoutError",
    "ResourceError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "DatabaseError",
    "ApiError",
    "ModelError",
    "PluginError",
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerError",
    "retry",
    "classify_error",
    "wrap_error",
    "log_error",

    # Settings management components
    "Settings",
    "SettingsScope",
    "SettingsManager",
    "SettingsError",
    "ModelSettings",
    "MemorySettings",
    "UISettings",
    "PluginSettings",
    "LoggingSettings",
    "SecuritySettings",
    "NetworkSettings",
    "get_settings",
    "get_settings_manager",
    "update_settings",
    "reset_settings",
]
