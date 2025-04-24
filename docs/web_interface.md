# Web Interface in Dukat

This document describes the web interface in Dukat, including the interface architecture, error handling, and customization options.

## Overview

Dukat implements a web interface using Gradio that provides:

1. **Chat interface** for interacting with the assistant
2. **Plugin management** for managing plugins
3. **Settings management** for configuring the assistant
4. **Error handling** for robust user experience
5. **Customization options** for adapting the interface to different needs

## Interface Architecture

The web interface is implemented in `augment-adam.web.interface` and provides a Gradio-based interface for interacting with the assistant:

```python
from augment_adam.web.interface import WebInterface, create_web_interface, launch_web_interface

# Create a web interface
interface = create_web_interface(
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)

# Launch the interface
interface.launch(
    host="127.0.0.1",
    port=7860,
    share=False,
    debug=False,
)
```

### Key Features

- **Chat interface** for conversing with the assistant
- **System prompt configuration** for customizing the assistant's behavior
- **Model selection** for choosing different models
- **Conversation management** for saving and loading conversations
- **Plugin management** for managing plugins
- **Settings management** for configuring the assistant

### Interface Components

#### Chat Tab

The chat tab provides a chat interface for interacting with the assistant:

- **Chat history** for viewing the conversation
- **User input** for sending messages to the assistant
- **System prompt** for customizing the assistant's behavior
- **Model selection** for choosing different models
- **Conversation management** for saving and loading conversations

#### Plugin Tab

The plugin tab provides a plugin management interface:

- **Plugin list** for viewing available plugins
- **Plugin details** for viewing plugin information
- **Plugin execution** for executing plugins
- **Plugin management** for refreshing the plugin list

#### Settings Tab

The settings tab provides a settings management interface:

- **Settings list** for viewing available settings
- **Settings editor** for editing settings
- **Settings management** for saving and loading settings

## Error Handling

The web interface implements robust error handling using the Dukat error handling framework:

```python
from augment_adam.core.errors import (
    AugmentAdamError, ModelError, NetworkError, ResourceError, NotFoundError,
    wrap_error, log_error, ErrorCategory
)
```

### Error Classification

The web interface classifies errors into specific categories:

```python
# Wrap the exception in a ModelError
error = wrap_error(
    e,
    message=f"Error changing model to {model_name}",
    category=ErrorCategory.MODEL,
    details={
        "model_name": model_name,
        "current_model": self.model_name,
    },
)
```

### Error Logging

The web interface logs errors with appropriate context:

```python
# Log the error with context
log_error(
    error,
    logger=logger,
    context={
        "message_preview": message[:50] + "..." if len(message) > 50 else message,
        "system_prompt_preview": system_prompt[:50] + "..." if len(system_prompt) > 50 else system_prompt,
    },
)
```

### User Feedback

The web interface provides user feedback for errors:

```python
# Add an error message to the conversation history
error_message = {
    "role": "system",
    "content": f"Error: {str(error)}",
}
self.conversation_history.append(error_message)

# Update the history for Gradio
error_response = f"I'm sorry, but I encountered an error: {str(error)}"
history.append((message, error_response))
```

## Customization Options

The web interface provides several customization options:

### Theme

The web interface supports different Gradio themes:

```python
interface = create_web_interface(
    theme="soft",  # Options: soft, default, glass, etc.
)
```

### Title and Description

The web interface supports custom title and description:

```python
interface = create_web_interface(
    title="My Assistant",
    description="My custom assistant for personal automation.",
)
```

### CSS

The web interface supports custom CSS:

```python
def _get_css(self) -> str:
    """Get the CSS for the interface."""
    return """
    .conversation {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f9f9f9;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .user-message {
        align-self: flex-end;
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message {
        align-self: flex-start;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .system-message {
        align-self: center;
        background-color: #f0f0f0;
        padding: 5px 10px;
        border-radius: 10px;
        max-width: 80%;
        font-style: italic;
        color: #666;
    }
    
    .unknown-message {
        align-self: center;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
    }
    """
```

## Best Practices

1. **Handle errors gracefully**: Use the error handling framework to provide a good user experience.
2. **Provide user feedback**: Always provide feedback to the user when errors occur.
3. **Log errors with context**: Log errors with appropriate context for debugging.
4. **Use settings**: Use settings to configure the interface instead of hardcoding values.
5. **Customize the interface**: Customize the interface to match your needs.

## Example: Custom Web Interface

```python
from augment_adam.web.interface import WebInterface
from augment_adam.core.assistant import Assistant
from augment_adam.core.model_manager import ModelManager
from augment_adam.core.settings import get_settings

# Create a custom web interface
class CustomWebInterface(WebInterface):
    """Custom web interface for the Dukat assistant."""
    
    def __init__(
        self,
        model_name: str = "llama3:8b",
        theme: str = "soft",
        title: str = "Custom Assistant",
        description: str = "My custom assistant for personal automation.",
        version: str = "0.1.0",
    ):
        """Initialize the custom web interface."""
        super().__init__(
            model_name=model_name,
            theme=theme,
            title=title,
            description=description,
            version=version,
        )
        
        # Add custom initialization
        self.settings = get_settings()
        self.custom_setting = self.settings.ui.get("custom_setting", "default")
    
    def _get_css(self) -> str:
        """Get the CSS for the interface."""
        # Add custom CSS
        return super()._get_css() + """
        .custom-element {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
        }
        """
    
    def _user_input_callback(
        self,
        message: str,
        history: List[Tuple[str, str]],
        system_prompt: str,
    ) -> Tuple[str, List[Tuple[str, str]], str]:
        """Callback for user input."""
        try:
            # Add custom processing
            if message.startswith("/custom"):
                # Handle custom command
                result = self._handle_custom_command(message)
                
                # Add the result to the conversation history
                system_message = {"role": "system", "content": result}
                self.conversation_history.append(system_message)
                
                # Update the history for Gradio
                history.append((message, result))
                
                # Return the updated state
                return "", history, self._format_conversation(self.conversation_history)
            
            # Call the parent method for normal messages
            return super()._user_input_callback(message, history, system_prompt)
            
        except Exception as e:
            # Handle errors
            error = wrap_error(
                e,
                message="Error processing custom command",
                category=ErrorCategory.UNKNOWN,
                details={"message": message},
            )
            
            log_error(error, logger=logger)
            
            # Return an error message
            error_response = f"Error processing custom command: {str(error)}"
            history.append((message, error_response))
            
            return "", history, self._format_conversation(self.conversation_history)
    
    def _handle_custom_command(self, message: str) -> str:
        """Handle a custom command."""
        # Parse the command
        parts = message.split(" ")
        command = parts[0][1:]  # Remove the leading /
        args = parts[1:]
        
        # Handle different commands
        if command == "custom":
            if not args:
                return "Usage: /custom <arg>"
            
            # Process the command
            return f"Custom command executed with args: {' '.join(args)}"
        
        # Unknown command
        return f"Unknown command: {command}"
```

## Conclusion

Dukat's web interface provides a flexible and robust way to interact with the assistant. By using the interface architecture, error handling framework, and customization options, Dukat can provide a more powerful and reliable user experience.
