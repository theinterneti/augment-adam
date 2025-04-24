# Dukat Web API Reference v0.1.0

_Last updated: 2025-04-25_

This document provides reference information for the web interface API of Dukat.

## WebInterface

The `WebInterface` class provides a web interface for the Dukat assistant using Gradio.

```python
from augment_adam.web import WebInterface, create_web_interface, launch_web_interface

# Create a new instance
interface = WebInterface(
    assistant=None,  # Optional, will create a new one if not provided
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)

# Create the interface
interface.create_interface()

# Launch the interface
interface.launch(
    host="127.0.0.1",
    port=7860,
    share=False,
    debug=False,
)

# Or use the convenience functions
interface = create_web_interface(
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)

launch_web_interface(
    host="127.0.0.1",
    port=7860,
    share=False,
    debug=False,
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)
```

### Parameters

- `assistant` (Assistant, optional): The assistant to use. If None, a new one will be created. Default: None
- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `theme` (str, optional): The theme to use for the interface. Default: "soft"
- `title` (str, optional): The title of the interface. Default: "Dukat Assistant"
- `description` (str, optional): The description of the interface. Default: "An open-source AI assistant focused on personal automation."
- `version` (str, optional): The version of the interface. Default: "0.1.0"

### Methods

#### `create_interface()`

Create the Gradio interface.

```python
interface = web_interface.create_interface()
```

**Returns:**

- `gr.Blocks`: The Gradio interface.

#### `launch(host="127.0.0.1", port=7860, share=False, debug=False, **kwargs)`

Launch the web interface.

```python
web_interface.launch(
    host="127.0.0.1",
    port=7860,
    share=False,
    debug=False,
)
```

**Parameters:**

- `host` (str, optional): The host to bind to. Default: "127.0.0.1"
- `port` (int, optional): The port to bind to. Default: 7860
- `share` (bool, optional): Whether to create a public link. Default: False
- `debug` (bool, optional): Whether to enable debug mode. Default: False
- `**kwargs`: Additional arguments to pass to Gradio.

## Helper Functions

### `create_web_interface(model_name="llama3:8b", theme="soft", title="Dukat Assistant", description="An open-source AI assistant focused on personal automation.", version="0.1.0")`

Create a web interface.

```python
interface = create_web_interface(
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)
```

**Parameters:**

- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `theme` (str, optional): The theme to use for the interface. Default: "soft"
- `title` (str, optional): The title of the interface. Default: "Dukat Assistant"
- `description` (str, optional): The description of the interface. Default: "An open-source AI assistant focused on personal automation."
- `version` (str, optional): The version of the interface. Default: "0.1.0"

**Returns:**

- `WebInterface`: The web interface.

### `launch_web_interface(host="127.0.0.1", port=7860, share=False, debug=False, model_name="llama3:8b", theme="soft", title="Dukat Assistant", description="An open-source AI assistant focused on personal automation.", version="0.1.0", **kwargs)`

Launch a web interface.

```python
launch_web_interface(
    host="127.0.0.1",
    port=7860,
    share=False,
    debug=False,
    model_name="llama3:8b",
    theme="soft",
    title="Dukat Assistant",
    description="An open-source AI assistant focused on personal automation.",
    version="0.1.0",
)
```

**Parameters:**

- `host` (str, optional): The host to bind to. Default: "127.0.0.1"
- `port` (int, optional): The port to bind to. Default: 7860
- `share` (bool, optional): Whether to create a public link. Default: False
- `debug` (bool, optional): Whether to enable debug mode. Default: False
- `model_name` (str, optional): The name of the model to use. Default: "llama3:8b"
- `theme` (str, optional): The theme to use for the interface. Default: "soft"
- `title` (str, optional): The title of the interface. Default: "Dukat Assistant"
- `description` (str, optional): The description of the interface. Default: "An open-source AI assistant focused on personal automation."
- `version` (str, optional): The version of the interface. Default: "0.1.0"
- `**kwargs`: Additional arguments to pass to Gradio.
