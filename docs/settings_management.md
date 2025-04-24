# Settings Management in Dukat

This document describes the settings management system in Dukat, including settings models, scopes, and the settings manager.

## Overview

Dukat implements a flexible settings management system that provides:

1. **Settings models** for type-safe settings
2. **Settings scopes** for different levels of configuration
3. **Settings persistence** for saving and loading settings
4. **Settings validation** for ensuring settings are valid
5. **Settings UI** for configuring settings in the web interface

## Settings Models

Settings in Dukat are defined using Pydantic models, which provide type safety and validation:

```python
from pydantic import BaseModel, Field

class ModelSettings(BaseModel):
    """Settings for language models."""
    
    default_model: str = "llama3:8b"
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    top_k: int = 40
    stop_sequences: List[str] = []
    repetition_penalty: float = 1.1

class Settings(BaseModel):
    """Main settings container."""
    
    model: ModelSettings = ModelSettings()
    memory: MemorySettings = MemorySettings()
    logging: LoggingSettings = LoggingSettings()
    network: NetworkSettings = NetworkSettings()
    security: SecuritySettings = SecuritySettings()
    ui: UISettings = UISettings()
    plugins: PluginSettings = PluginSettings()
    custom: Dict[str, Any] = {}
```

## Settings Scopes

Dukat supports different scopes for settings:

| Scope | Description |
|-------|-------------|
| `GLOBAL` | Global settings that apply to all users |
| `USER` | User-specific settings |
| `SESSION` | Session-specific settings (not persisted) |

Settings from different scopes are merged to form the effective settings, with more specific scopes taking precedence:

```
GLOBAL < USER < SESSION
```

## Settings Manager

The `SettingsManager` class manages settings for different scopes:

```python
from augment_adam.core.settings import SettingsManager, SettingsScope

# Create a settings manager
manager = SettingsManager(config_dir="/path/to/config")

# Get settings for a specific scope
global_settings = manager.get_settings(SettingsScope.GLOBAL)
user_settings = manager.get_settings(SettingsScope.USER)
session_settings = manager.get_settings(SettingsScope.SESSION)

# Get effective settings (merged from all scopes)
effective_settings = manager.get_effective_settings()

# Update settings
manager.update_settings(
    {"model": {"temperature": 0.8}},
    scope=SettingsScope.USER,
)

# Reset settings to defaults
manager.reset_settings(scope=SettingsScope.USER)

# Save settings
manager.save_settings(scope=SettingsScope.USER)

# Load settings
manager.load_settings(scope=SettingsScope.USER)
```

## Global Functions

Dukat provides global functions for working with settings:

```python
from augment_adam.core.settings import (
    get_settings, get_settings_manager, update_settings, reset_settings
)

# Get the default settings manager
manager = get_settings_manager()

# Get effective settings
settings = get_settings()

# Update settings
update_settings(
    {"model": {"temperature": 0.8}},
    scope=SettingsScope.USER,
)

# Reset settings
reset_settings(scope=SettingsScope.USER)
```

## Settings Persistence

Settings are persisted as JSON files in the configuration directory:

- `global_settings.json`: Global settings
- `user_settings.json`: User settings

Session settings are not persisted and are only stored in memory.

## Settings Validation

Settings are validated using Pydantic's validation system. If a setting is invalid, a `ValidationError` is raised:

```python
try:
    update_settings(
        {"model": {"temperature": "invalid"}},  # Should be a float
        scope=SettingsScope.USER,
    )
except ValidationError as e:
    # Handle validation error
    pass
```

## Settings UI

Dukat provides a web interface for configuring settings:

```python
from augment_adam.web.settings_manager import SettingsManagerUI

# Create a settings manager UI
settings_ui = SettingsManagerUI(settings_manager)

# Create the UI components
ui_components = settings_ui.create_ui()
```

## Best Practices

1. **Use settings models**: Define settings using Pydantic models for type safety and validation.
2. **Use appropriate scopes**: Use the appropriate scope for settings (GLOBAL, USER, SESSION).
3. **Provide defaults**: Always provide sensible defaults for settings.
4. **Validate settings**: Validate settings before using them.
5. **Handle errors**: Handle settings errors gracefully.

## Example: Model Manager

The model manager in Dukat uses the settings system to configure models:

```python
from augment_adam.core.settings import get_settings

class ModelManager:
    def __init__(
        self,
        model_name: str = None,
        ollama_host: str = None,
        api_key: str = None,
    ):
        # Get settings
        settings = get_settings()
        model_settings = settings.model
        
        # Use provided values or defaults from settings
        self.model_name = model_name or model_settings.default_model
        self.ollama_host = ollama_host or "http://localhost:11434"
        self.api_key = api_key or ""
        
        # Load the model
        self.lm = self._load_model(self.model_name, self.ollama_host, self.api_key)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        # Get settings
        settings = get_settings()
        model_settings = settings.model
        
        # Apply settings if not overridden in kwargs
        if "temperature" not in kwargs:
            kwargs["temperature"] = model_settings.temperature
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = model_settings.max_tokens
        
        # Generate response
        return self.lm(prompt, **kwargs)
```

## Testing Settings

Dukat provides utilities for testing settings:

```python
import tempfile
from pathlib import Path
from augment_adam.core.settings import SettingsManager, SettingsScope

def test_settings():
    # Create a temporary directory for settings
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        
        # Create a settings manager
        manager = SettingsManager(config_dir=config_dir)
        
        # Update settings
        manager.update_settings(
            {"model": {"temperature": 0.8}},
            scope=SettingsScope.USER,
        )
        
        # Get settings
        user_settings = manager.get_settings(SettingsScope.USER)
        assert user_settings.model.temperature == 0.8
        
        # Reset settings
        manager.reset_settings(scope=SettingsScope.USER)
        
        # Check that settings were reset
        user_settings = manager.get_settings(SettingsScope.USER)
        assert user_settings.model.temperature == 0.7  # Default value
```

## Conclusion

Dukat's settings management system provides a flexible and type-safe way to configure the application. By using Pydantic models, different scopes, and persistence, Dukat can handle settings in a robust and user-friendly way.
