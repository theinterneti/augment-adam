# Augment Adam MCP Server

This directory contains the MCP (Machine Comprehension Protocol) server implementation for Augment Adam. The MCP server allows VS Code and other MCP clients to interact with Augment Adam's context engine and other functionality.

## Overview

The MCP server is a FastAPI-based server that exposes Augment Adam functionality as tools that can be called by MCP clients. The server is designed to be used with VS Code's MCP client, but can also be used with other MCP clients.

## Components

- `mcp_server.py`: Core MCP server implementation
- `mcp_client.py`: Client for interacting with MCP servers
- `run_mcp_server.py`: Executable script to run the MCP server
- `run_mcp_client.py`: Executable script to run the MCP client

## Usage

### Running the MCP Server

To run the MCP server:

```bash
python -m augment_adam.server.run_mcp_server --host 0.0.0.0 --port 8811
```

Options:
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8811)
- `--api-key`: API key for authentication (optional)
- `--debug`: Enable debug mode

### Running the MCP Client

To run the MCP client:

```bash
python -m augment_adam.server.run_mcp_client --url http://localhost:8811/mcp --list-tools
```

Options:
- `--url`: URL of the MCP server (default: http://localhost:8811/mcp)
- `--debug`: Enable debug mode
- `--list-tools`: List available tools
- `--call`: Call a tool
- `--params`: Parameters for the tool call (JSON)

Example:
```bash
python -m augment_adam.server.run_mcp_client --url http://localhost:8811/mcp --call vector_search --params '{"query": "function that prints hello world", "k": 10}'
```

## Connecting VS Code to the MCP Server

To connect VS Code to the MCP server, you need to:

1. Install the VS Code MCP extension
2. Configure the extension to connect to the MCP server
3. Run the MCP server

For more information, see the [VS Code MCP documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers).

### Docker Connection

If you're running the MCP server in a Docker container, you can use the following command to connect VS Code to the MCP server:

```bash
docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:8811
```

This command creates a bridge between your local machine and the Docker container, allowing VS Code to connect to the MCP server running in the container.

## Testing

To run the tests for the MCP server:

```bash
pytest tests/unit/server/test_mcp_server.py
pytest tests/unit/server/test_mcp_client.py
pytest tests/unit/context_engine/test_mcp_context_engine.py
```
