# Plugin System in Dukat

This document describes the plugin system in Dukat, including the plugin architecture, plugin registry, and built-in plugins.

## Overview

Dukat implements a flexible plugin system that provides:

1. **Plugin architecture** for extending functionality
2. **Plugin registry** for managing plugins
3. **Error handling** with retry and circuit breaker patterns
4. **Settings integration** for configurable plugin behavior
5. **Built-in plugins** for common tasks

## Plugin Architecture

The plugin architecture is based on the `Plugin` abstract base class in `augment-adam.plugins.base`:

```python
from augment_adam.plugins.base import Plugin

class MyPlugin(Plugin):
    """My custom plugin."""
    
    def __init__(
        self,
        name: str = "my_plugin",
        description: str = "My custom plugin",
        version: str = "0.1.0",
    ):
        """Initialize the plugin."""
        super().__init__(name=name, description=description, version=version)
    
    def execute(self, param1: str, param2: int = 0) -> dict:
        """Execute the plugin.
        
        Args:
            param1: A string parameter.
            param2: An integer parameter.
            
        Returns:
            The result of the plugin execution.
        """
        # Plugin implementation
        return {
            "result": f"Executed with {param1} and {param2}",
        }
```

### Key Features

- **Abstract base class** for defining plugins
- **Signature generation** for automatic documentation
- **Parameter validation** for type safety
- **Error handling** for robust execution

### Plugin Methods

#### `execute(**kwargs)`

Execute the plugin with the given arguments:

```python
result = my_plugin.execute(param1="test", param2=42)
```

#### `get_signature()`

Get the signature of the plugin:

```python
signature = my_plugin.get_signature()
```

## Plugin Registry

The plugin registry is implemented in `augment-adam.plugins.base.PluginManager` and provides a central registry for managing plugins:

```python
from augment_adam.plugins.base import PluginManager, get_plugin_manager

# Create a new registry
registry = PluginManager()

# Or get the default registry
registry = get_plugin_manager()
```

### Key Features

- **Plugin registration** for adding plugins
- **Plugin discovery** for finding plugins
- **Plugin execution** for running plugins
- **Error handling** with retry and circuit breaker patterns

### Registry Methods

#### `register(plugin)`

Register a plugin:

```python
registry.register(my_plugin)
```

#### `unregister(plugin_name)`

Unregister a plugin:

```python
registry.unregister("my_plugin")
```

#### `get_plugin(plugin_name)`

Get a plugin by name:

```python
plugin = registry.get_plugin("my_plugin")
```

#### `list_plugins()`

List all registered plugins:

```python
plugins = registry.list_plugins()
```

#### `execute_plugin(plugin_name, **kwargs)`

Execute a plugin:

```python
result = registry.execute_plugin("my_plugin", param1="test", param2=42)
```

## Error Handling

The plugin system implements robust error handling using the Dukat error handling framework:

```python
from augment_adam.core.errors import (
    PluginError, ValidationError, NotFoundError,
    wrap_error, log_error, retry, CircuitBreaker
)
```

### Retry Pattern

The plugin system uses the retry pattern for transient failures:

```python
@retry(max_attempts=2, delay=1.0)
def execute_plugin(self, plugin_name, **kwargs):
    # This method will be retried up to 2 times if it fails
    pass
```

### Circuit Breaker Pattern

The plugin system uses the circuit breaker pattern to prevent cascading failures:

```python
# Create a circuit breaker for plugin execution
_execute_circuit = CircuitBreaker(
    name="plugin_execution",
    failure_threshold=5,
    recovery_timeout=60.0,
)

@retry(max_attempts=2, delay=1.0)
@_execute_circuit
def execute_plugin(self, plugin_name, **kwargs):
    # This method is protected by the circuit breaker
    pass
```

### Error Classification

The plugin system classifies errors into specific categories:

```python
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
```

## Settings Integration

The plugin system integrates with the Dukat settings system:

```python
from augment_adam.core.settings import get_settings

# Get settings for plugin configuration
settings = get_settings()
plugin_settings = settings.plugins

# Use settings for plugin configuration
enabled_plugins = plugin_settings.enabled_plugins
plugin_timeout = plugin_settings.timeout
```

## Built-in Plugins

Dukat includes several built-in plugins for common tasks:

### File Manager Plugin

The file manager plugin provides file system operations:

```python
from augment_adam.plugins.file_manager import FileManagerPlugin

# Create the plugin
file_manager = FileManagerPlugin()

# Register the plugin
registry.register(file_manager)

# Execute the plugin
result = registry.execute_plugin(
    "file_manager",
    operation="read_file",
    path="/path/to/file.txt",
)
```

### System Info Plugin

The system info plugin provides system information:

```python
from augment_adam.plugins.system_info import SystemInfoPlugin

# Create the plugin
system_info = SystemInfoPlugin()

# Register the plugin
registry.register(system_info)

# Execute the plugin
result = registry.execute_plugin(
    "system_info",
    operation="get_cpu_info",
)
```

### Web Search Plugin

The web search plugin provides web search capabilities:

```python
from augment_adam.plugins.web_search import WebSearchPlugin

# Create the plugin
web_search = WebSearchPlugin()

# Register the plugin
registry.register(web_search)

# Execute the plugin
result = registry.execute_plugin(
    "web_search",
    query="Dukat assistant",
    num_results=5,
)
```

## Creating Custom Plugins

Creating a custom plugin involves subclassing the `Plugin` class and implementing the `execute` method:

```python
from augment_adam.plugins.base import Plugin, get_plugin_manager

class CalculatorPlugin(Plugin):
    """A simple calculator plugin."""
    
    def __init__(
        self,
        name: str = "calculator",
        description: str = "A simple calculator plugin",
        version: str = "0.1.0",
    ):
        """Initialize the plugin."""
        super().__init__(name=name, description=description, version=version)
    
    def execute(
        self,
        operation: str,
        a: float,
        b: float,
    ) -> dict:
        """Execute the calculator plugin.
        
        Args:
            operation: The operation to perform (add, subtract, multiply, divide).
            a: The first operand.
            b: The second operand.
            
        Returns:
            The result of the calculation.
        """
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "Division by zero"}
            result = a / b
        else:
            return {"error": f"Unknown operation: {operation}"}
        
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
        }

# Register the plugin
registry = get_plugin_manager()
registry.register(CalculatorPlugin())

# Execute the plugin
result = registry.execute_plugin(
    "calculator",
    operation="add",
    a=2,
    b=3,
)
```

## Best Practices

1. **Use descriptive names**: Use descriptive names for plugins and parameters.
2. **Add documentation**: Add docstrings to plugins and methods.
3. **Handle errors**: Handle errors gracefully to prevent cascading failures.
4. **Use settings**: Use settings to configure plugin behavior instead of hardcoding values.
5. **Test plugins**: Write tests for plugins to ensure they work correctly.

## Example: Using Plugins in an Assistant

```python
from augment_adam.core.assistant import Assistant
from augment_adam.plugins.base import get_plugin_manager
from augment_adam.plugins.file_manager import FileManagerPlugin
from augment_adam.plugins.system_info import SystemInfoPlugin
from augment_adam.plugins.web_search import WebSearchPlugin

# Create an assistant
assistant = Assistant()

# Get the plugin registry
registry = get_plugin_manager()

# Register plugins
registry.register(FileManagerPlugin())
registry.register(SystemInfoPlugin())
registry.register(WebSearchPlugin())

# Use plugins in the assistant
def process_user_query(query):
    """Process a user query using plugins."""
    if "file" in query:
        # Use the file manager plugin
        result = registry.execute_plugin(
            "file_manager",
            operation="list_files",
            path="/path/to/directory",
        )
        return f"Files in directory: {', '.join(result['files'])}"
    
    elif "system" in query:
        # Use the system info plugin
        result = registry.execute_plugin(
            "system_info",
            operation="get_system_info",
        )
        return f"System info: {result['system']} {result['release']}"
    
    elif "search" in query:
        # Use the web search plugin
        result = registry.execute_plugin(
            "web_search",
            query=query.replace("search", "").strip(),
            num_results=3,
        )
        return f"Search results: {result['results']}"
    
    else:
        # Use the assistant
        return assistant.generate_response(query)
```

## Conclusion

Dukat's plugin system provides a flexible and robust way to extend the functionality of the assistant. By using the plugin architecture, plugin registry, and error handling framework, Dukat can provide a more powerful and reliable experience.
