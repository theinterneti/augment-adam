"""Base plugin system for the Augment Adam assistant.

This module provides the base classes and interfaces for
creating plugins for the Augment Adam assistant.

Version: 0.1.0
Created: 2025-04-22
Updated: 2025-04-24
"""

from typing import Dict, Any, List, Optional, Callable, Type
import logging
import inspect
import time
from abc import ABC, abstractmethod

from augment_adam.core.errors import (
    PluginError, ValidationError, NotFoundError, ErrorCategory,
    wrap_error, log_error, retry, CircuitBreaker
)
from augment_adam.core.settings import get_settings

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base class for all Augment Adam plugins.

    This abstract class defines the interface that all plugins must implement.

    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "0.1.0",
    ):
        """Initialize the plugin.

        Args:
            name: The name of the plugin.
            description: A description of the plugin.
            version: The version of the plugin.
        """
        self.name = name
        self.description = description
        self.version = version

        logger.info(f"Initialized plugin: {name} v{version}")

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the plugin with the given arguments.

        Args:
            **kwargs: Arguments for the plugin.

        Returns:
            The result of the plugin execution.

        Raises:
            PluginError: If there is an error executing the plugin.
            ValidationError: If the arguments are invalid.
        """
        pass

    def get_signature(self) -> Dict[str, Any]:
        """Get the signature of the plugin.

        Returns:
            A dictionary describing the plugin's signature.
        """
        # Get the signature of the execute method
        sig = inspect.signature(self.execute)

        # Extract parameter information
        parameters = {}
        for name, param in sig.parameters.items():
            if name != "self":
                parameters[name] = {
                    "name": name,
                    "required": param.default == inspect.Parameter.empty,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": None if param.default == inspect.Parameter.empty else param.default,
                }

        # Return the signature
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": parameters,
        }


class PluginManager:
    """Manager for Augment Adam plugins.

    This class manages the registration and discovery of plugins.

    Attributes:
        plugins: Dictionary of registered plugins.
    """

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Plugin] = {}
        logger.info("Initialized plugin manager")

    def register(self, plugin: Plugin) -> bool:
        """Register a plugin.

        Args:
            plugin: The plugin to register.

        Returns:
            True if successful, False otherwise.

        Raises:
            ValidationError: If the plugin is not a valid Plugin instance.
        """
        try:
            if not isinstance(plugin, Plugin):
                error = ValidationError(
                    message=f"Cannot register {plugin}: not a Plugin instance",
                    details={
                        "plugin_type": type(plugin).__name__,
                    },
                )
                log_error(error, logger=logger)
                return False

            if plugin.name in self.plugins:
                logger.warning(
                    f"Plugin {plugin.name} already registered, overwriting")

            self.plugins[plugin.name] = plugin
            logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
            return True

        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error registering plugin: {getattr(plugin, 'name', 'unknown')}",
                category=ErrorCategory.PLUGIN,
                details={
                    "plugin_name": getattr(plugin, "name", "unknown"),
                    "plugin_type": type(plugin).__name__,
                },
            )
            log_error(error, logger=logger)
            return False

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_name: The name of the plugin to unregister.

        Returns:
            True if successful, False otherwise.

        Raises:
            NotFoundError: If the plugin is not found.
        """
        try:
            if plugin_name not in self.plugins:
                error = NotFoundError(
                    message=f"Plugin {plugin_name} not registered",
                    details={
                        "plugin_name": plugin_name,
                    },
                )
                log_error(error, logger=logger, level=logging.WARNING)
                return False

            del self.plugins[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
            return True

        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error unregistering plugin: {plugin_name}",
                category=ErrorCategory.PLUGIN,
                details={
                    "plugin_name": plugin_name,
                },
            )
            log_error(error, logger=logger)
            return False

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            plugin_name: The name of the plugin to get.

        Returns:
            The plugin, or None if not found.

        Raises:
            NotFoundError: If the plugin is not found and raise_error is True.
        """
        try:
            plugin = self.plugins.get(plugin_name)

            if plugin is None:
                logger.debug(f"Plugin {plugin_name} not found")

            return plugin

        except Exception as e:
            error = wrap_error(
                e,
                message=f"Error getting plugin: {plugin_name}",
                category=ErrorCategory.PLUGIN,
                details={
                    "plugin_name": plugin_name,
                },
            )
            log_error(error, logger=logger)
            return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins.

        Returns:
            A list of plugin signatures.

        Raises:
            PluginError: If there is an error getting the plugin signatures.
        """
        try:
            signatures = []
            for plugin in self.plugins.values():
                try:
                    signatures.append(plugin.get_signature())
                except Exception as e:
                    error = wrap_error(
                        e,
                        message=f"Error getting signature for plugin: {plugin.name}",
                        category=ErrorCategory.PLUGIN,
                        details={
                            "plugin_name": plugin.name,
                            "plugin_type": type(plugin).__name__,
                        },
                    )
                    log_error(error, logger=logger)
                    # Skip this plugin but continue with others
                    continue

            return signatures

        except Exception as e:
            error = wrap_error(
                e,
                message="Error listing plugins",
                category=ErrorCategory.PLUGIN,
            )
            log_error(error, logger=logger)
            return []

    # Create a circuit breaker for plugin execution
    _execute_circuit = CircuitBreaker(
        name="plugin_execution",
        failure_threshold=5,
        recovery_timeout=60.0,
    )

    @retry(max_attempts=2, delay=1.0)
    @_execute_circuit
    def execute_plugin(
        self,
        plugin_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a plugin.

        Args:
            plugin_name: The name of the plugin to execute.
            **kwargs: Arguments for the plugin.

        Returns:
            The result of the plugin execution.

        Raises:
            NotFoundError: If the plugin is not found.
            PluginError: If there is an error executing the plugin.
            CircuitBreakerError: If the circuit breaker is open due to too many failures.
        """
        try:
            # Get the plugin
            plugin = self.get_plugin(plugin_name)
            if plugin is None:
                error = NotFoundError(
                    message=f"Plugin {plugin_name} not found",
                    details={
                        "plugin_name": plugin_name,
                    },
                )
                log_error(error, logger=logger)
                return {"error": f"Plugin {plugin_name} not found"}

            # Execute the plugin
            start_time = time.time()
            result = plugin.execute(**kwargs)
            execution_time = time.time() - start_time

            logger.debug(
                f"Executed plugin {plugin_name} in {execution_time:.2f}s")
            return result

        except Exception as e:
            # Wrap the exception in a PluginError
            error = wrap_error(
                e,
                message=f"Error executing plugin {plugin_name}",
                category=ErrorCategory.PLUGIN,
                details={
                    "plugin_name": plugin_name,
                    "kwargs": kwargs,
                },
            )

            # Log the error with context
            log_error(
                error,
                logger=logger,
                context={
                    "plugin_name": plugin_name,
                    "kwargs_keys": list(kwargs.keys()),
                },
            )

            # Return an error result
            return {"error": f"Error executing plugin {plugin_name}: {str(e)}", "details": error.details}


# Singleton instance for easy access
default_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create the default plugin manager.

    Returns:
        The default plugin manager.

    Raises:
        PluginError: If there is an error creating the plugin manager.
    """
    global default_manager

    try:
        if default_manager is None:
            # Get settings for plugin configuration
            settings = get_settings()
            plugin_settings = settings.plugins

            # Create the plugin manager
            default_manager = PluginManager()

        return default_manager

    except Exception as e:
        # Wrap the exception in a PluginError
        error = wrap_error(
            e,
            message="Error creating plugin manager",
            category=ErrorCategory.PLUGIN,
        )

        # Log the error with context
        log_error(error, logger=logger)

        # Re-raise the wrapped error
        raise error
