# Plugin System

This guide explains how to use and develop plugins for Augment Adam.

## Overview

The plugin system in Augment Adam allows you to extend the functionality of the assistant with custom capabilities. Plugins can:

1. Add new commands and tools
2. Integrate with external services
3. Provide access to additional data sources
4. Implement custom processing logic
5. Enhance the assistant's capabilities

## Using Plugins

### Loading Plugins

You can load plugins when creating an assistant:

```python
from augment_adam.core import Assistant
from augment_adam.plugins import FileManagerPlugin, WebSearchPlugin, SystemInfoPlugin

# Create an assistant with plugins
assistant = Assistant(
    plugins=[
        FileManagerPlugin(),
        WebSearchPlugin(api_key="your-api-key"),
        SystemInfoPlugin()
    ]
)

# Chat with the assistant
response = assistant.chat("Can you search for information about Python?")
```

### Using Plugin Commands

You can use plugin commands in your conversations:

```
User: Can you create a file called hello.txt with the content "Hello, World!"?
Assistant: I'll create that file for you.

Command: file_manager.create_file
Arguments: {"file_path": "hello.txt", "content": "Hello, World!"}
Result: File created successfully.

User: Can you search for information about Python?
Assistant: I'll search for information about Python.

Command: web_search.search
Arguments: {"query": "Python programming language"}
Result: Python is a high-level, interpreted programming language...
```

### Plugin Configuration

You can configure plugins when creating them:

```python
from augment_adam.plugins import WebSearchPlugin

# Create a web search plugin with custom configuration
web_search_plugin = WebSearchPlugin(
    api_key="your-api-key",
    search_engine="google",
    max_results=10,
    safe_search=True
)
```

## Built-in Plugins

Augment Adam comes with several built-in plugins:

### File Manager Plugin

The File Manager Plugin provides file operations:

```python
from augment_adam.plugins import FileManagerPlugin

# Create a file manager plugin
file_manager_plugin = FileManagerPlugin()

# Use the plugin
result = file_manager_plugin.execute("create_file", file_path="hello.txt", content="Hello, World!")
```

Available commands:
- `create_file`: Create a file
- `read_file`: Read a file
- `write_file`: Write to a file
- `append_file`: Append to a file
- `delete_file`: Delete a file
- `list_files`: List files in a directory
- `file_exists`: Check if a file exists
- `get_file_info`: Get information about a file

### Web Search Plugin

The Web Search Plugin provides web search capabilities:

```python
from augment_adam.plugins import WebSearchPlugin

# Create a web search plugin
web_search_plugin = WebSearchPlugin(api_key="your-api-key")

# Use the plugin
result = web_search_plugin.execute("search", query="Python programming language")
```

Available commands:
- `search`: Search the web
- `fetch_url`: Fetch content from a URL
- `summarize_url`: Summarize content from a URL

### System Info Plugin

The System Info Plugin provides system information:

```python
from augment_adam.plugins import SystemInfoPlugin

# Create a system info plugin
system_info_plugin = SystemInfoPlugin()

# Use the plugin
result = system_info_plugin.execute("get_cpu_info")
```

Available commands:
- `get_cpu_info`: Get CPU information
- `get_memory_info`: Get memory information
- `get_disk_info`: Get disk information
- `get_network_info`: Get network information
- `get_process_info`: Get process information
- `get_system_info`: Get system information

## Developing Custom Plugins

### Plugin Interface

To create a custom plugin, extend the `Plugin` base class:

```python
from augment_adam.plugins.base import Plugin
from typing import Dict, Any, List, Optional

class CustomPlugin(Plugin):
    """
    Custom plugin implementation.
    
    Args:
        config: Plugin configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the custom plugin."""
        super().__init__(name="custom_plugin", description="Custom plugin")
        self.config = config or {}
        # Initialize your custom plugin here
        
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute.
            **kwargs: Additional arguments for the command.
            
        Returns:
            Result of the command.
        """
        if command == "custom_command":
            return self._custom_command(**kwargs)
        else:
            raise ValueError(f"Unknown command: {command}")
        
    def _custom_command(self, arg1: str, arg2: int = 0) -> Dict[str, Any]:
        """
        Custom command implementation.
        
        Args:
            arg1: First argument.
            arg2: Second argument.
            
        Returns:
            Result of the command.
        """
        # Implement your custom command logic here
        return {
            "result": f"Custom command executed with arg1={arg1}, arg2={arg2}",
            "status": "success"
        }
        
    def get_commands(self) -> List[Dict[str, Any]]:
        """
        Get available commands.
        
        Returns:
            List of available commands.
        """
        return [
            {
                "name": "custom_command",
                "description": "Execute a custom command",
                "parameters": {
                    "arg1": {
                        "type": "string",
                        "description": "First argument"
                    },
                    "arg2": {
                        "type": "integer",
                        "description": "Second argument",
                        "default": 0
                    }
                }
            }
        ]
```

### Plugin Registration

You can register your custom plugin with Augment Adam:

```python
from augment_adam.plugins import register_plugin

# Register custom plugin
register_plugin("custom_plugin", CustomPlugin)
```

### Plugin Usage

You can use your custom plugin in your application:

```python
from augment_adam.core import Assistant
from augment_adam.plugins import get_plugin

# Get custom plugin
custom_plugin = get_plugin("custom_plugin", config={"key": "value"})

# Create an assistant with custom plugin
assistant = Assistant(plugins=[custom_plugin])

# Chat with the assistant
response = assistant.chat("Can you execute a custom command with arg1='hello'?")
```

## Plugin Configuration

Plugins can be configured using a configuration dictionary:

```python
from augment_adam.plugins import FileManagerPlugin

# Create a file manager plugin with custom configuration
file_manager_plugin = FileManagerPlugin(
    config={
        "base_dir": "./data/files",
        "allowed_extensions": [".txt", ".md", ".json"],
        "max_file_size": 1024 * 1024  # 1 MB
    }
)
```

## Plugin Validation

Plugins can validate their configuration and commands:

```python
from augment_adam.plugins.base import Plugin
from augment_adam.plugins.validation import validate_config, validate_command
from typing import Dict, Any, List, Optional

class ValidatedPlugin(Plugin):
    """
    Plugin with validation.
    
    Args:
        config: Plugin configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validated plugin."""
        super().__init__(name="validated_plugin", description="Plugin with validation")
        self.config = validate_config(config or {}, self.get_config_schema())
        # Initialize your plugin here
        
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command.
        
        Args:
            command: Command to execute.
            **kwargs: Additional arguments for the command.
            
        Returns:
            Result of the command.
        """
        if command == "validated_command":
            # Validate command arguments
            validated_args = validate_command(kwargs, self.get_command_schema(command))
            return self._validated_command(**validated_args)
        else:
            raise ValueError(f"Unknown command: {command}")
        
    def _validated_command(self, arg1: str, arg2: int = 0) -> Dict[str, Any]:
        """
        Validated command implementation.
        
        Args:
            arg1: First argument.
            arg2: Second argument.
            
        Returns:
            Result of the command.
        """
        # Implement your command logic here
        return {
            "result": f"Validated command executed with arg1={arg1}, arg2={arg2}",
            "status": "success"
        }
        
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema.
        
        Returns:
            Configuration schema.
        """
        return {
            "type": "object",
            "properties": {
                "key1": {
                    "type": "string",
                    "description": "First configuration key"
                },
                "key2": {
                    "type": "integer",
                    "description": "Second configuration key",
                    "default": 0
                }
            }
        }
        
    def get_command_schema(self, command: str) -> Dict[str, Any]:
        """
        Get command schema.
        
        Args:
            command: Command name.
            
        Returns:
            Command schema.
        """
        if command == "validated_command":
            return {
                "type": "object",
                "properties": {
                    "arg1": {
                        "type": "string",
                        "description": "First argument"
                    },
                    "arg2": {
                        "type": "integer",
                        "description": "Second argument",
                        "default": 0
                    }
                },
                "required": ["arg1"]
            }
        else:
            raise ValueError(f"Unknown command: {command}")
```

## Plugin Security

Plugins should implement security measures:

1. **Input Validation**: Validate all input to prevent injection attacks
2. **Permission Checking**: Check permissions before executing commands
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Sandboxing**: Sandbox plugin execution to prevent system access
5. **Logging**: Log plugin activity for auditing

## Best Practices

When developing plugins, follow these best practices:

1. **Follow the Interface**: Implement all required methods from the base class
2. **Add Documentation**: Document your plugin with docstrings
3. **Add Type Hints**: Use type hints for better code quality
4. **Add Tests**: Write tests for your plugin
5. **Handle Errors**: Implement proper error handling
6. **Be Consistent**: Follow the same patterns as the core plugins
7. **Be Modular**: Keep your plugin focused on a specific functionality
8. **Be Performant**: Optimize your plugin for performance

## Next Steps

After learning about plugins, check out the [Extending Guide](extending.md) to learn how to extend other parts of Augment Adam.
