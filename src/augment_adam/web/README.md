# Augment Adam Web Interface

This directory contains the web interface for Augment Adam, providing a user-friendly way to interact with the system through a web browser.

## Overview

The web interface is built using:
- **FastAPI**: For the backend server
- **Gradio**: For the interactive UI components
- **Docker**: For containerization and deployment

## Components

- `interface.py`: Core web interface implementation using Gradio
- `server.py`: FastAPI server that serves the web interface
- `run_web_interface.py`: Script to launch the web interface

## Usage

### Running the Web Interface

You can run the web interface in several ways:

#### 1. Using Docker Compose

The easiest way is to use the provided Docker Compose configuration:

```bash
docker-compose up web-interface
```

This will start the web interface on port 8080.

#### 2. Running Directly

You can also run the web interface directly:

```bash
python -m augment_adam.web.run_web_interface
```

By default, this will start the web interface on port 8080. You can customize the port and other settings:

```bash
python -m augment_adam.web.run_web_interface --port 8888 --model llama3:70b
```

### Accessing the Web Interface

Once running, you can access the web interface at:

- http://localhost:8080 (when running in Docker)
- http://localhost:8081 (when running in the dev container)

## Features

The web interface provides:

1. **Chat Interface**: Interact with the Augment Adam assistant
2. **Context Engine**: Search and explore the context engine
3. **Memory System**: Store and retrieve memories

## Customization

You can customize the web interface by modifying:

- The theme (using Gradio themes)
- The title and description
- The model used by the assistant

## Development

To develop the web interface:

1. Start the dev container
2. Run the web interface in development mode:

```bash
python -m augment_adam.web.run_web_interface --debug
```

This will enable debug mode and hot-reloading for faster development.
