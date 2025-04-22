"""Settings management for Dukat.

This module provides a settings management system for the Dukat assistant,
allowing for configuration of various components and features.

Version: 0.1.0
Created: 2025-04-25
"""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, cast

from pydantic import BaseModel, Field, ValidationError

from dukat.core.errors import DukatError, ErrorCategory, ValidationError as DukatValidationError

logger = logging.getLogger(__name__)


class SettingsError(DukatError):
    """Exception raised for settings-related errors."""
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            original_error=original_error,
            details=details,
        )


class SettingsScope(str, Enum):
    """Scope of settings."""
    
    GLOBAL = "global"  # Global settings for all users
    USER = "user"  # User-specific settings
    SESSION = "session"  # Session-specific settings (temporary)


class ModelSettings(BaseModel):
    """Settings for AI models."""
    
    default_model: str = Field(
        default="llama3:8b",
        description="Default model to use for text generation",
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for text generation (0.0 to 1.0)",
    )
    
    max_tokens: int = Field(
        default=1024,
        gt=0,
        description="Maximum number of tokens to generate",
    )
    
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter (0.0 to 1.0)",
    )
    
    top_k: int = Field(
        default=40,
        ge=0,
        description="Top-k sampling parameter",
    )
    
    stop_sequences: List[str] = Field(
        default=[],
        description="Sequences that will stop text generation",
    )
    
    repetition_penalty: float = Field(
        default=1.1,
        ge=1.0,
        description="Penalty for token repetition",
    )


class MemorySettings(BaseModel):
    """Settings for memory systems."""
    
    working_memory_size: int = Field(
        default=10,
        gt=0,
        description="Number of messages to keep in working memory",
    )
    
    semantic_memory_enabled: bool = Field(
        default=True,
        description="Whether semantic memory is enabled",
    )
    
    episodic_memory_enabled: bool = Field(
        default=True,
        description="Whether episodic memory is enabled",
    )
    
    max_episodic_memories: int = Field(
        default=100,
        gt=0,
        description="Maximum number of episodic memories to store",
    )


class UISettings(BaseModel):
    """Settings for the user interface."""
    
    theme: str = Field(
        default="light",
        description="UI theme (light, dark, etc.)",
    )
    
    font_size: int = Field(
        default=14,
        gt=0,
        description="Font size in pixels",
    )
    
    show_timestamps: bool = Field(
        default=True,
        description="Whether to show timestamps in messages",
    )
    
    show_typing_animation: bool = Field(
        default=True,
        description="Whether to show typing animation",
    )
    
    code_highlighting: bool = Field(
        default=True,
        description="Whether to highlight code in messages",
    )


class PluginSettings(BaseModel):
    """Settings for plugins."""
    
    enabled_plugins: List[str] = Field(
        default=[],
        description="List of enabled plugins",
    )
    
    auto_enable_plugins: bool = Field(
        default=False,
        description="Whether to automatically enable new plugins",
    )
    
    plugin_timeout: float = Field(
        default=30.0,
        gt=0.0,
        description="Timeout for plugin execution in seconds",
    )


class LoggingSettings(BaseModel):
    """Settings for logging."""
    
    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    
    file_logging_enabled: bool = Field(
        default=True,
        description="Whether to log to a file",
    )
    
    log_file_path: Optional[str] = Field(
        default=None,
        description="Path to the log file",
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Format for log messages",
    )
    
    max_log_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        gt=0,
        description="Maximum size of log file in bytes",
    )
    
    backup_count: int = Field(
        default=3,
        ge=0,
        description="Number of backup log files to keep",
    )


class SecuritySettings(BaseModel):
    """Settings for security."""
    
    enable_authentication: bool = Field(
        default=False,
        description="Whether authentication is required",
    )
    
    session_timeout: int = Field(
        default=3600,  # 1 hour
        gt=0,
        description="Session timeout in seconds",
    )
    
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="List of allowed hosts",
    )
    
    enable_cors: bool = Field(
        default=False,
        description="Whether to enable CORS",
    )
    
    cors_origins: List[str] = Field(
        default=[],
        description="List of allowed CORS origins",
    )


class NetworkSettings(BaseModel):
    """Settings for network connections."""
    
    request_timeout: float = Field(
        default=30.0,
        gt=0.0,
        description="Timeout for network requests in seconds",
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retries for network requests",
    )
    
    retry_delay: float = Field(
        default=1.0,
        ge=0.0,
        description="Delay between retries in seconds",
    )
    
    proxy_enabled: bool = Field(
        default=False,
        description="Whether to use a proxy",
    )
    
    proxy_url: Optional[str] = Field(
        default=None,
        description="URL of the proxy server",
    )


class Settings(BaseModel):
    """Main settings class for Dukat."""
    
    model: ModelSettings = Field(
        default_factory=ModelSettings,
        description="Settings for AI models",
    )
    
    memory: MemorySettings = Field(
        default_factory=MemorySettings,
        description="Settings for memory systems",
    )
    
    ui: UISettings = Field(
        default_factory=UISettings,
        description="Settings for the user interface",
    )
    
    plugins: PluginSettings = Field(
        default_factory=PluginSettings,
        description="Settings for plugins",
    )
    
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Settings for logging",
    )
    
    security: SecuritySettings = Field(
        default_factory=SecuritySettings,
        description="Settings for security",
    )
    
    network: NetworkSettings = Field(
        default_factory=NetworkSettings,
        description="Settings for network connections",
    )
    
    # Custom settings that don't fit into the above categories
    custom: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom settings",
    )


class SettingsManager:
    """Manager for Dukat settings."""
    
    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        auto_save: bool = True,
    ):
        """Initialize the settings manager.
        
        Args:
            config_dir: Directory to store settings files. If None, uses the default.
            auto_save: Whether to automatically save settings when they are updated.
        """
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.auto_save = auto_save
        
        # Create settings for each scope
        self._settings: Dict[SettingsScope, Settings] = {
            SettingsScope.GLOBAL: Settings(),
            SettingsScope.USER: Settings(),
            SettingsScope.SESSION: Settings(),
        }
        
        # Track which settings have been loaded
        self._loaded_scopes: Set[SettingsScope] = set()
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load global and user settings
        self.load_settings(SettingsScope.GLOBAL)
        self.load_settings(SettingsScope.USER)
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory.
        
        Returns:
            The default configuration directory.
        """
        if os.name == "nt":  # Windows
            base_dir = Path(os.environ.get("APPDATA", ""))
        else:  # Unix/Linux/Mac
            base_dir = Path(os.environ.get("XDG_CONFIG_HOME", "")) or Path.home() / ".config"
        
        return base_dir / "dukat"
    
    def _get_settings_path(self, scope: SettingsScope) -> Path:
        """Get the path to the settings file for a scope.
        
        Args:
            scope: The settings scope.
            
        Returns:
            The path to the settings file.
        """
        if scope == SettingsScope.GLOBAL:
            return self.config_dir / "global_settings.json"
        elif scope == SettingsScope.USER:
            return self.config_dir / "user_settings.json"
        else:
            # Session settings are not persisted
            raise ValueError(f"Cannot get path for scope: {scope}")
    
    def load_settings(self, scope: SettingsScope) -> None:
        """Load settings from a file.
        
        Args:
            scope: The settings scope to load.
            
        Raises:
            SettingsError: If there is an error loading the settings.
        """
        if scope == SettingsScope.SESSION:
            # Session settings are not persisted
            return
        
        settings_path = self._get_settings_path(scope)
        
        if not settings_path.exists():
            # Create default settings file
            self.save_settings(scope)
            self._loaded_scopes.add(scope)
            return
        
        try:
            with open(settings_path, "r") as f:
                settings_dict = json.load(f)
            
            # Update settings with loaded values
            self._settings[scope] = Settings.model_validate(settings_dict)
            self._loaded_scopes.add(scope)
            
            logger.info(f"Loaded settings from {settings_path}")
        except (json.JSONDecodeError, ValidationError) as e:
            raise SettingsError(
                f"Error loading settings from {settings_path}",
                original_error=e,
                details={"path": str(settings_path)},
            )
    
    def save_settings(self, scope: SettingsScope) -> None:
        """Save settings to a file.
        
        Args:
            scope: The settings scope to save.
            
        Raises:
            SettingsError: If there is an error saving the settings.
        """
        if scope == SettingsScope.SESSION:
            # Session settings are not persisted
            return
        
        settings_path = self._get_settings_path(scope)
        
        try:
            settings_dict = self._settings[scope].model_dump()
            
            with open(settings_path, "w") as f:
                json.dump(settings_dict, f, indent=2)
            
            logger.info(f"Saved settings to {settings_path}")
        except (OSError, TypeError) as e:
            raise SettingsError(
                f"Error saving settings to {settings_path}",
                original_error=e,
                details={"path": str(settings_path)},
            )
    
    def get_settings(self, scope: SettingsScope) -> Settings:
        """Get settings for a specific scope.
        
        Args:
            scope: The settings scope.
            
        Returns:
            The settings for the specified scope.
        """
        return self._settings[scope]
    
    def get_effective_settings(self) -> Settings:
        """Get the effective settings by merging all scopes.
        
        The precedence order is: GLOBAL < USER < SESSION.
        
        Returns:
            The effective settings.
        """
        # Start with global settings
        global_dict = self._settings[SettingsScope.GLOBAL].model_dump()
        
        # Merge with user settings
        user_dict = self._settings[SettingsScope.USER].model_dump()
        merged_dict = self._deep_merge(global_dict, user_dict)
        
        # Merge with session settings
        session_dict = self._settings[SettingsScope.SESSION].model_dump()
        merged_dict = self._deep_merge(merged_dict, session_dict)
        
        # Create a new Settings object with the merged values
        return Settings.model_validate(merged_dict)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: The base dictionary.
            override: The dictionary to override values in the base.
            
        Returns:
            The merged dictionary.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override or add the value
                result[key] = value
        
        return result
    
    def update_settings(
        self,
        scope: SettingsScope,
        settings_dict: Dict[str, Any],
        save: Optional[bool] = None,
    ) -> None:
        """Update settings for a specific scope.
        
        Args:
            scope: The settings scope to update.
            settings_dict: Dictionary of settings to update.
            save: Whether to save the settings to disk. If None, uses the auto_save value.
            
        Raises:
            SettingsError: If there is an error updating the settings.
        """
        try:
            # Get current settings
            current_settings = self._settings[scope]
            
            # Create a merged dictionary
            current_dict = current_settings.model_dump()
            merged_dict = self._deep_merge(current_dict, settings_dict)
            
            # Validate and update settings
            self._settings[scope] = Settings.model_validate(merged_dict)
            
            # Save settings if requested
            should_save = save if save is not None else self.auto_save
            if should_save and scope != SettingsScope.SESSION:
                self.save_settings(scope)
                
        except ValidationError as e:
            raise DukatValidationError(
                f"Invalid settings: {str(e)}",
                original_error=e,
                details={"settings": settings_dict},
            )
    
    def reset_settings(
        self,
        scope: SettingsScope,
        save: Optional[bool] = None,
    ) -> None:
        """Reset settings for a specific scope to defaults.
        
        Args:
            scope: The settings scope to reset.
            save: Whether to save the settings to disk. If None, uses the auto_save value.
        """
        # Create new default settings
        self._settings[scope] = Settings()
        
        # Save settings if requested
        should_save = save if save is not None else self.auto_save
        if should_save and scope != SettingsScope.SESSION:
            self.save_settings(scope)


# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager(
    config_dir: Optional[Union[str, Path]] = None,
    auto_save: bool = True,
) -> SettingsManager:
    """Get the global settings manager instance.
    
    Args:
        config_dir: Directory to store settings files. If None, uses the default.
        auto_save: Whether to automatically save settings when they are updated.
        
    Returns:
        The global settings manager instance.
    """
    global _settings_manager
    
    if _settings_manager is None:
        _settings_manager = SettingsManager(config_dir=config_dir, auto_save=auto_save)
    
    return _settings_manager


def get_settings(scope: Optional[SettingsScope] = None) -> Settings:
    """Get settings for a specific scope or the effective settings.
    
    Args:
        scope: The settings scope. If None, returns the effective settings.
        
    Returns:
        The settings for the specified scope or the effective settings.
    """
    manager = get_settings_manager()
    
    if scope is None:
        return manager.get_effective_settings()
    else:
        return manager.get_settings(scope)


def update_settings(
    settings_dict: Dict[str, Any],
    scope: SettingsScope = SettingsScope.USER,
    save: Optional[bool] = None,
) -> None:
    """Update settings for a specific scope.
    
    Args:
        settings_dict: Dictionary of settings to update.
        scope: The settings scope to update.
        save: Whether to save the settings to disk. If None, uses the auto_save value.
    """
    manager = get_settings_manager()
    manager.update_settings(scope=scope, settings_dict=settings_dict, save=save)


def reset_settings(
    scope: SettingsScope = SettingsScope.USER,
    save: Optional[bool] = None,
) -> None:
    """Reset settings for a specific scope to defaults.
    
    Args:
        scope: The settings scope to reset.
        save: Whether to save the settings to disk. If None, uses the auto_save value.
    """
    manager = get_settings_manager()
    manager.reset_settings(scope=scope, save=save)
