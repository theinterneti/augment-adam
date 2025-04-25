"""Core module for the Augment Adam assistant.

This module provides core functionality for the Augment Adam assistant,
including error handling, settings management, and other utilities.

Version: 0.1.0
Created: 2025-04-25
"""

from augment_adam.core.errors import (
    AugmentAdamError, ErrorCategory,
    ResourceError, DatabaseError,
    wrap_error, log_error
)
from augment_adam.core.settings import (
    get_settings, update_settings, reset_settings,
    SettingsScope
)

__all__ = [
    "AugmentAdamError",
    "ErrorCategory",
    "ResourceError",
    "DatabaseError",
    "wrap_error",
    "log_error",
    "get_settings",
    "update_settings",
    "reset_settings",
    "SettingsScope",
]