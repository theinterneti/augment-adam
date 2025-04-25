# Plugin System

## Overview

This module provides a flexible plugin system that allows users to extend and customize the assistant with plugins for various functionalities. It includes features for plugin registry, loading, execution, validation, and configuration.

## Components

### Interface

The interface module provides the core interfaces and classes for plugins:

- **Plugin**: Base class for plugins
- **PluginMetadata**: Metadata for plugins
- **PluginType**: Enum for plugin types (AGENT, CONTEXT, MEMORY, TOOL, UTILITY, INTEGRATION, OTHER)
- **PluginCategory**: Enum for plugin categories (CORE, EXTENSION, THIRD_PARTY, USER)
- **PluginHook**: Enum for plugin hooks (INIT, PRE_PROCESS, PROCESS, POST_PROCESS, CLEANUP)

### Registry

The registry module provides the registry for plugins:

- **PluginRegistry**: Registry for tracking available plugins and their capabilities

### Loader

The loader module provides the loader for plugins:

- **PluginLoader**: Loader for discovering and loading plugins
- **PluginDiscovery**: Base class for plugin discovery
- **EntryPointDiscovery**: Discover plugins from entry points
- **DirectoryDiscovery**: Discover plugins from a directory

### Execution

The execution module provides the executor for plugins:

- **PluginExecutor**: Executor for handling plugin execution and lifecycle
- **PluginContext**: Context for plugin execution
- **PluginResult**: Result of plugin execution

### Validation

The validation module provides validation for plugins:

- **PluginValidator**: Base class for plugin validators
- **SecurityValidator**: Validator for plugin security
- **CompatibilityValidator**: Validator for plugin compatibility

### Config

The config module provides configuration for plugins:

- **PluginConfig**: Configuration for plugins
- **PluginConfigSchema**: Schema for plugin configuration

### Samples

The samples module provides sample plugins:

- **HelloWorldPlugin**: Simple Hello World plugin
- **TextProcessorPlugin**: Plugin for processing text
- **LoggerPlugin**: Plugin for logging context data

## Usage

### Creating a Plugin

```python
from augment_adam.plugins.interface import Plugin, PluginMetadata, PluginType, PluginCategory, PluginHook

class MyPlugin(Plugin):
    """
    My custom plugin.
    
    This plugin does something useful.
    """
    
    metadata = PluginMetadata(
        name="my_plugin",
        description="A useful plugin",
        version="0.1.0",
        author="Your Name",
        plugin_type=PluginType.UTILITY,
        category=PluginCategory.USER,
        hooks={PluginHook.PROCESS},
        tags=["useful", "custom"],
    )
    
    def _initialize(self) -> None:
        """Initialize the plugin."""
        # Get configuration options
        self.option1 = self.config.get("option1", "default")
        self.option2 = self.config.get("option2", 42)
    
    def _cleanup(self) -> None:
        """Clean up the plugin."""
        # Clean up resources
        pass
    
    def _execute(self, hook: PluginHook, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            hook: The hook to execute.
            context: The context for execution.
            
        Returns:
            The updated context.
        """
        # Process the context
        if "input" in context:
            context["output"] = context["input"] + " processed by MyPlugin"
        
        return context
```

### Registering a Plugin

```python
from augment_adam.plugins.registry import PluginRegistry

# Get the plugin registry
registry = PluginRegistry()

# Register a plugin
registry.register(MyPlugin)

# Get a plugin by name
plugin_class = registry.get_plugin("my_plugin")

# Get plugins by type
utility_plugins = registry.get_plugins_by_type(PluginType.UTILITY)

# Get plugins by hook
process_plugins = registry.get_plugins_by_hook(PluginHook.PROCESS)
```

### Loading Plugins

```python
from augment_adam.plugins.loader import PluginLoader, DirectoryDiscovery

# Create a plugin loader
loader = PluginLoader()

# Add a custom discovery
loader.discoveries.append(DirectoryDiscovery("/path/to/plugins"))

# Load plugins
loaded_plugins = loader.load_plugins()

# Load a specific plugin
plugin_class = loader.load_plugin("my_module:MyPlugin")

# Load a plugin from a file
plugin_class = loader.load_plugin_from_file("/path/to/plugin.py")
```

### Executing Plugins

```python
from augment_adam.plugins.execution import PluginExecutor, PluginContext

# Create a plugin executor
executor = PluginExecutor()

# Initialize a plugin
executor.initialize_plugin("my_plugin", {"option1": "value", "option2": 123})

# Execute a plugin
context = PluginContext(input_data={"input": "Hello"})
result = executor.execute_plugin("my_plugin", PluginHook.PROCESS, context)

# Execute all plugins for a hook
results = executor.execute_plugins(PluginHook.PROCESS, context)

# Execute a pipeline of plugins
result = executor.execute_pipeline(PluginHook.PROCESS, context)

# Clean up a plugin
executor.cleanup_plugin("my_plugin")

# Clean up all plugins
executor.cleanup_all_plugins()
```

### Validating Plugins

```python
from augment_adam.plugins.validation import SecurityValidator, CompatibilityValidator

# Create validators
security_validator = SecurityValidator()
compatibility_validator = CompatibilityValidator()

# Validate a plugin
is_secure = security_validator.validate(MyPlugin)
is_compatible = compatibility_validator.validate(MyPlugin)

# Get validation errors
security_errors = security_validator.get_validation_errors(MyPlugin)
compatibility_errors = compatibility_validator.get_validation_errors(MyPlugin)
```

### Configuring Plugins

```python
from augment_adam.plugins.config import PluginConfig, PluginConfigSchema

# Create a config schema
schema = PluginConfigSchema()
schema.add_property("option1", "string", "First option", required=True)
schema.add_property("option2", "integer", "Second option", default=42)

# Create a config
config = PluginConfig(schema=schema, config={"option1": "value"})

# Get a config value
value1 = config.get("option1")
value2 = config.get("option2")  # Returns default value (42)

# Set a config value
config.set("option2", 123)

# Validate the config
errors = config.validate()

# Save the config to a file
config.save("config.json")

# Load the config from a file
config.load("config.json")
```

## TODOs

- Add plugin marketplace for sharing plugins (Issue #11)
- Implement plugin versioning and compatibility checking (Issue #11)
- Add plugin analytics to track usage and performance (Issue #11)
- Implement plugin dependencies management (Issue #11)
- Add support for remote plugins (Issue #11)
- Add support for plugin validation (Issue #11)
- Implement plugin analytics (Issue #11)
- Add support for context validation (Issue #11)
- Implement context analytics (Issue #11)
- Add support for result validation (Issue #11)
- Implement result analytics (Issue #11)
- Add support for schema validation (Issue #11)
- Implement schema analytics (Issue #11)
- Add support for config validation (Issue #11)
- Implement config analytics (Issue #11)
