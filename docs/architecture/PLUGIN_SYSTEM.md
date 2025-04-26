# Plugin System

## Overview

This document describes the architecture of the Plugin System in Augment Adam. The Plugin System enables the extension of the assistant's capabilities through plugins, allowing it to perform a wide range of tasks beyond its core functionality.

## Architecture Diagram

The Plugin System architecture consists of several components that work together to provide a flexible and powerful plugin framework.

```
                  +----------------+
                  |  PluginManager |
                  +-------+--------+
                          |
          +---------------+---------------+
          |               |               |
+---------v------+ +------v-------+ +-----v--------+
|  PluginLoader  | | PluginRegistry| |PluginExecutor |
+-------+-------+ +------+-------+ +-----+--------+
        |                |               |
+-------v-------+ +------v-------+ +-----v--------+
|    Plugin     | |   Plugin     | |   Plugin     |
|  (Interface)  | |  Manifest    | |   Result     |
+---------------+ +--------------+ +--------------+
```

## Components

### Plugin Manager

The Plugin Manager is the central component of the Plugin System. It manages the loading, registration, and execution of plugins.

#### Responsibilities

- Load plugins from various sources
- Register plugins with the system
- Execute plugin actions
- Manage plugin lifecycle
- Handle plugin errors and exceptions

#### Interfaces

- `load_plugin(plugin_path: str) -> Plugin`: Load a plugin from a path.
- `register_plugin(plugin: Plugin) -> None`: Register a plugin with the system.
- `execute_plugin_action(plugin_name: str, action_name: str, **kwargs) -> Any`: Execute a plugin action.
- `get_plugin(plugin_name: str) -> Optional[Plugin]`: Get a plugin by name.
- `list_plugins() -> List[Plugin]`: List all registered plugins.

#### Implementation

The Plugin Manager is implemented as a class that coordinates the loading, registration, and execution of plugins:

```python
from typing import Dict, List, Any, Optional
import os
import importlib.util

from augment_adam.plugins.base import Plugin
from augment_adam.plugins.loader import PluginLoader
from augment_adam.plugins.registry import PluginRegistry
from augment_adam.plugins.executor import PluginExecutor

class PluginManager:
    """Manager for plugins."""
    
    def __init__(self, plugin_dir: str = "./plugins"):
        """Initialize the plugin manager.
        
        Args:
            plugin_dir: Directory containing plugins.
        """
        self.plugin_dir = plugin_dir
        self.loader = PluginLoader()
        self.registry = PluginRegistry()
        self.executor = PluginExecutor()
        
    def load_plugin(self, plugin_path: str) -> Plugin:
        """Load a plugin from a path.
        
        Args:
            plugin_path: Path to the plugin.
            
        Returns:
            The loaded plugin.
        """
        plugin = self.loader.load(plugin_path)
        self.register_plugin(plugin)
        return plugin
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the system.
        
        Args:
            plugin: Plugin to register.
        """
        self.registry.register(plugin)
    
    def execute_plugin_action(self, plugin_name: str, action_name: str, **kwargs) -> Any:
        """Execute a plugin action.
        
        Args:
            plugin_name: Name of the plugin.
            action_name: Name of the action to execute.
            **kwargs: Arguments for the action.
            
        Returns:
            Result of the action.
        """
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"Plugin '{plugin_name}' not found.")
        
        return self.executor.execute(plugin, action_name, **kwargs)
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin.
            
        Returns:
            The plugin, or None if not found.
        """
        return self.registry.get(plugin_name)
    
    def list_plugins(self) -> List[Plugin]:
        """List all registered plugins.
        
        Returns:
            List of registered plugins.
        """
        return self.registry.list()
    
    def load_plugins_from_directory(self) -> List[Plugin]:
        """Load all plugins from the plugin directory.
        
        Returns:
            List of loaded plugins.
        """
        plugins = []
        
        # Check if the plugin directory exists
        if not os.path.exists(self.plugin_dir):
            return plugins
        
        # Iterate through all subdirectories in the plugin directory
        for plugin_name in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            
            # Check if it's a directory and contains a plugin.py file
            if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "plugin.py")):
                try:
                    plugin = self.load_plugin(plugin_path)
                    plugins.append(plugin)
                except Exception as e:
                    print(f"Error loading plugin '{plugin_name}': {e}")
        
        return plugins
```

### Plugin Loader

The Plugin Loader is responsible for loading plugins from various sources, such as files, directories, or packages.

#### Responsibilities

- Load plugins from files
- Load plugins from directories
- Load plugins from packages
- Validate plugin structure
- Handle loading errors

#### Interfaces

- `load(plugin_path: str) -> Plugin`: Load a plugin from a path.

#### Implementation

The Plugin Loader is implemented as a class that loads plugins from various sources:

```python
from typing import Dict, Any, Optional
import os
import importlib.util
import sys

from augment_adam.plugins.base import Plugin

class PluginLoader:
    """Loader for plugins."""
    
    def load(self, plugin_path: str) -> Plugin:
        """Load a plugin from a path.
        
        Args:
            plugin_path: Path to the plugin.
            
        Returns:
            The loaded plugin.
        """
        # Check if the plugin path exists
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin path '{plugin_path}' does not exist.")
        
        # Check if it's a directory
        if os.path.isdir(plugin_path):
            return self._load_from_directory(plugin_path)
        
        # Check if it's a file
        if os.path.isfile(plugin_path):
            return self._load_from_file(plugin_path)
        
        raise ValueError(f"Plugin path '{plugin_path}' is not a file or directory.")
    
    def _load_from_directory(self, plugin_dir: str) -> Plugin:
        """Load a plugin from a directory.
        
        Args:
            plugin_dir: Directory containing the plugin.
            
        Returns:
            The loaded plugin.
        """
        # Check if the directory contains a plugin.py file
        plugin_file = os.path.join(plugin_dir, "plugin.py")
        if not os.path.exists(plugin_file):
            raise ValueError(f"Plugin directory '{plugin_dir}' does not contain a plugin.py file.")
        
        # Load the plugin from the file
        return self._load_from_file(plugin_file)
    
    def _load_from_file(self, plugin_file: str) -> Plugin:
        """Load a plugin from a file.
        
        Args:
            plugin_file: File containing the plugin.
            
        Returns:
            The loaded plugin.
        """
        # Get the plugin name from the file name
        plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
        
        # Load the module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if spec is None or spec.loader is None:
            raise ValueError(f"Failed to load plugin from '{plugin_file}'.")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        spec.loader.exec_module(module)
        
        # Find the plugin class
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                plugin_class = attr
                break
        
        if plugin_class is None:
            raise ValueError(f"No plugin class found in '{plugin_file}'.")
        
        # Create an instance of the plugin
        plugin = plugin_class()
        
        return plugin
```

### Plugin Registry

The Plugin Registry is responsible for registering and managing plugins. It provides a central repository for all plugins in the system.

#### Responsibilities

- Register plugins
- Retrieve plugins by name
- List all registered plugins
- Validate plugin compatibility
- Handle plugin conflicts

#### Interfaces

- `register(plugin: Plugin) -> None`: Register a plugin.
- `get(plugin_name: str) -> Optional[Plugin]`: Get a plugin by name.
- `list() -> List[Plugin]`: List all registered plugins.
- `unregister(plugin_name: str) -> None`: Unregister a plugin.

#### Implementation

The Plugin Registry is implemented as a class that manages registered plugins:

```python
from typing import Dict, List, Optional

from augment_adam.plugins.base import Plugin

class PluginRegistry:
    """Registry for plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins = {}
    
    def register(self, plugin: Plugin) -> None:
        """Register a plugin.
        
        Args:
            plugin: Plugin to register.
        """
        # Check if the plugin is already registered
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin '{plugin.name}' is already registered.")
        
        # Register the plugin
        self.plugins[plugin.name] = plugin
    
    def get(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin.
            
        Returns:
            The plugin, or None if not found.
        """
        return self.plugins.get(plugin_name)
    
    def list(self) -> List[Plugin]:
        """List all registered plugins.
        
        Returns:
            List of registered plugins.
        """
        return list(self.plugins.values())
    
    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin.
        
        Args:
            plugin_name: Name of the plugin to unregister.
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
```

### Plugin Executor

The Plugin Executor is responsible for executing plugin actions. It handles the invocation of plugin methods and the processing of results.

#### Responsibilities

- Execute plugin actions
- Handle action parameters
- Process action results
- Handle execution errors
- Validate action inputs and outputs

#### Interfaces

- `execute(plugin: Plugin, action_name: str, **kwargs) -> Any`: Execute a plugin action.

#### Implementation

The Plugin Executor is implemented as a class that executes plugin actions:

```python
from typing import Dict, Any

from augment_adam.plugins.base import Plugin

class PluginExecutor:
    """Executor for plugin actions."""
    
    def execute(self, plugin: Plugin, action_name: str, **kwargs) -> Any:
        """Execute a plugin action.
        
        Args:
            plugin: Plugin to execute the action on.
            action_name: Name of the action to execute.
            **kwargs: Arguments for the action.
            
        Returns:
            Result of the action.
        """
        # Check if the plugin has the action
        if not hasattr(plugin, action_name):
            raise ValueError(f"Plugin '{plugin.name}' does not have action '{action_name}'.")
        
        # Get the action
        action = getattr(plugin, action_name)
        
        # Check if the action is callable
        if not callable(action):
            raise ValueError(f"Action '{action_name}' of plugin '{plugin.name}' is not callable.")
        
        # Execute the action
        try:
            result = action(**kwargs)
            return result
        except Exception as e:
            # Handle execution errors
            if hasattr(plugin, "handle_error"):
                return plugin.handle_error(action_name, e, **kwargs)
            else:
                raise
```

### Plugin Interface

The Plugin Interface defines the contract that all plugins must follow. It provides methods for plugin initialization, execution, and cleanup.

#### Responsibilities

- Define the plugin contract
- Provide common functionality for all plugins
- Enable plugins to be used interchangeably
- Handle plugin lifecycle events

#### Interfaces

- `initialize() -> None`: Initialize the plugin.
- `cleanup() -> None`: Clean up the plugin.
- `get_manifest() -> Dict[str, Any]`: Get the plugin manifest.

#### Implementation

The Plugin Interface is implemented as an abstract base class that all plugins must inherit from:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.name = self.__class__.__name__
        self.description = "Base plugin implementation"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.actions = {}
        
        # Initialize the plugin
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize the plugin.
        
        This method is called when the plugin is loaded.
        Override this method to perform any initialization tasks.
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up the plugin.
        
        This method is called when the plugin is unloaded.
        Override this method to perform any cleanup tasks.
        """
        pass
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the plugin manifest.
        
        Returns:
            The plugin manifest.
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "actions": self.actions
        }
    
    def handle_error(self, action_name: str, error: Exception, **kwargs) -> Any:
        """Handle an error that occurred during action execution.
        
        Args:
            action_name: Name of the action that caused the error.
            error: The error that occurred.
            **kwargs: Arguments that were passed to the action.
            
        Returns:
            Result to return from the action.
        """
        # By default, re-raise the error
        raise error
```



## Interfaces

### Plugin System Interface

The Plugin System provides a simple interface for managing and using plugins.

```python
from typing import Dict, List, Any, Optional

from augment_adam.plugins.base import Plugin

class PluginSystemInterface:
    """Interface for the plugin system."""
    
    def load_plugin(self, plugin_path: str) -> Plugin:
        """Load a plugin from a path.
        
        Args:
            plugin_path: Path to the plugin.
            
        Returns:
            The loaded plugin.
        """
        pass
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the system.
        
        Args:
            plugin: Plugin to register.
        """
        pass
    
    def execute_plugin_action(self, plugin_name: str, action_name: str, **kwargs) -> Any:
        """Execute a plugin action.
        
        Args:
            plugin_name: Name of the plugin.
            action_name: Name of the action to execute.
            **kwargs: Arguments for the action.
            
        Returns:
            Result of the action.
        """
        pass
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin.
            
        Returns:
            The plugin, or None if not found.
        """
        pass
    
    def list_plugins(self) -> List[Plugin]:
        """List all registered plugins.
        
        Returns:
            List of registered plugins.
        """
        pass
```



## Workflows

### Loading a Plugin

The process of loading a plugin into the system.

#### Steps

1. Create a plugin manager
2. Specify the plugin path
3. Call the load_plugin method
4. The plugin is loaded and registered
5. The plugin is returned

#### Diagram

```
User -> PluginManager: load_plugin(plugin_path)
PluginManager -> PluginLoader: load(plugin_path)
PluginLoader -> Plugin: new Plugin()
Plugin -> PluginLoader: plugin
PluginLoader -> PluginManager: plugin
PluginManager -> PluginRegistry: register(plugin)
PluginRegistry -> PluginManager: None
PluginManager -> User: plugin
```

### Executing a Plugin Action

The process of executing a plugin action.

#### Steps

1. Create a plugin manager
2. Specify the plugin name and action name
3. Prepare the action parameters
4. Call the execute_plugin_action method
5. The action is executed and the result is returned

#### Diagram

```
User -> PluginManager: execute_plugin_action(plugin_name, action_name, **kwargs)
PluginManager -> PluginRegistry: get(plugin_name)
PluginRegistry -> PluginManager: plugin
PluginManager -> PluginExecutor: execute(plugin, action_name, **kwargs)
PluginExecutor -> Plugin: action(**kwargs)
Plugin -> PluginExecutor: result
PluginExecutor -> PluginManager: result
PluginManager -> User: result
```



## Examples

### Creating a Simple Plugin

Example of creating a simple plugin.

```python
from augment_adam.plugins.base import Plugin

class CalculatorPlugin(Plugin):
    """Plugin for performing calculations."""
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        self.name = "calculator"
        self.description = "Plugin for performing calculations"
        self.version = "1.0.0"
        self.author = "Augment Adam"
        self.actions = {
            "add": "Add two numbers",
            "subtract": "Subtract two numbers",
            "multiply": "Multiply two numbers",
            "divide": "Divide two numbers"
        }
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            Sum of the two numbers.
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            Difference of the two numbers.
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            Product of the two numbers.
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers.
        
        Args:
            a: First number.
            b: Second number.
            
        Returns:
            Quotient of the two numbers.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b
    
    def handle_error(self, action_name: str, error: Exception, **kwargs) -> Any:
        """Handle an error that occurred during action execution.
        
        Args:
            action_name: Name of the action that caused the error.
            error: The error that occurred.
            **kwargs: Arguments that were passed to the action.
            
        Returns:
            Result to return from the action.
        """
        if action_name == "divide" and isinstance(error, ValueError) and str(error) == "Cannot divide by zero.":
            return float("inf")
        raise error
```

### Using the Plugin System

Example of using the plugin system.

```python
from augment_adam.plugins import PluginManager

# Create a plugin manager
manager = PluginManager(plugin_dir="./plugins")

# Load all plugins from the plugin directory
plugins = manager.load_plugins_from_directory()
print(f"Loaded {len(plugins)} plugins.")

# List all plugins
for plugin in manager.list_plugins():
    print(f"Plugin: {plugin.name} - {plugin.description}")
    print(f"Version: {plugin.version}")
    print(f"Author: {plugin.author}")
    print(f"Actions: {plugin.actions}")
    print()

# Execute a plugin action
result = manager.execute_plugin_action("calculator", "add", a=2, b=3)
print(f"2 + 3 = {result}")

result = manager.execute_plugin_action("calculator", "subtract", a=5, b=2)
print(f"5 - 2 = {result}")

result = manager.execute_plugin_action("calculator", "multiply", a=4, b=3)
print(f"4 * 3 = {result}")

result = manager.execute_plugin_action("calculator", "divide", a=10, b=2)
print(f"10 / 2 = {result}")

# Handle errors
try:
    result = manager.execute_plugin_action("calculator", "divide", a=10, b=0)
    print(f"10 / 0 = {result}")
except Exception as e:
    print(f"Error: {e}")
```



## Integration with Other Components

### Assistant

The Plugin System integrates with the Assistant to provide extended capabilities.

```python
from augment_adam.core import Assistant
from augment_adam.plugins import PluginManager

# Create a plugin manager
manager = PluginManager(plugin_dir="./plugins")

# Load all plugins from the plugin directory
plugins = manager.load_plugins_from_directory()

# Create an assistant with the plugin manager
assistant = Assistant(plugin_manager=manager)

# Chat with the assistant
response = assistant.chat("What is 2 + 3?")
print(response)

response = assistant.chat("What is 5 - 2?")
print(response)

response = assistant.chat("What is 4 * 3?")
print(response)

response = assistant.chat("What is 10 / 2?")
print(response)
```

### Context Engine

The Plugin System integrates with the Context Engine to provide context-aware plugin execution.

```python
from augment_adam.plugins import PluginManager
from augment_adam.context_engine import ContextEngine

# Create a plugin manager
manager = PluginManager(plugin_dir="./plugins")

# Load all plugins from the plugin directory
plugins = manager.load_plugins_from_directory()

# Create a context engine
context_engine = ContextEngine()

# Add documents to the context engine
context_engine.add_document("The calculator plugin can perform basic arithmetic operations.")

# Execute a plugin action with context
context = context_engine.get_context("What can the calculator plugin do?")
print(f"Context: {context}")

# Use the context to determine which plugin to use
if "calculator" in context.lower():
    result = manager.execute_plugin_action("calculator", "add", a=2, b=3)
    print(f"2 + 3 = {result}")
```



## Future Enhancements

- **Plugin Versioning**: Add support for versioning plugins to ensure compatibility between different versions.
- **Plugin Dependencies**: Implement a dependency system for plugins to specify and resolve dependencies.
- **Plugin Permissions**: Add a permission system for plugins to control access to system resources.
- **Plugin Marketplace**: Create a marketplace for sharing and discovering plugins.
- **Plugin Testing Framework**: Develop a testing framework for plugins to ensure quality and reliability.
- **Plugin Documentation Generator**: Create a documentation generator for plugins to make it easier to understand and use them.
- **Plugin Hot Reloading**: Implement hot reloading for plugins to allow updates without restarting the system.
- **Plugin Configuration UI**: Develop a user interface for configuring plugins.

