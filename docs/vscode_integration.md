# VS Code Integration with Augment Adam

This document describes how to integrate Augment Adam with VS Code using the MCP (Machine Comprehension Protocol) server.

## Overview

Augment Adam provides a context engine that can be used by VS Code to provide intelligent code assistance. The integration is done through the MCP server, which exposes Augment Adam's functionality as tools that can be called by VS Code.

## Prerequisites

- VS Code with the MCP extension installed
- Augment Adam installed in development mode (`pip install -e .`)
- Python 3.9 or higher

## Running the MCP Server

To run the MCP server:

```bash
# From the project root
./scripts/run_mcp_server.py
```

Or:

```bash
python -m augment_adam.server.run_mcp_server
```

By default, the server runs on `0.0.0.0:8811`. You can customize the host and port:

```bash
./scripts/run_mcp_server.py --host 127.0.0.1 --port 8812
```

## Connecting VS Code to the MCP Server

### Direct Connection

If the MCP server is running on the same machine as VS Code, you can connect directly:

1. Open VS Code
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "MCP: Connect to Server"
4. Enter the URL: `http://localhost:8811/mcp`

### Docker Connection

If you're running the MCP server in a Docker container, you can use socat to create a bridge:

```bash
docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:8811
```

Then in VS Code:

1. Open the Command Palette (Ctrl+Shift+P)
2. Type "MCP: Connect to Server"
3. Enter the URL: `stdio://<path-to-socat>`

### WSL Connection

If you're running VS Code on Windows and the MCP server in WSL, you can use socat:

```bash
docker run -i --rm alpine/socat STDIO TCP:host.docker.internal:8811
```

## Available Tools

The MCP server exposes the following tools:

- `vector_store`: Store a vector in the context engine
- `vector_search`: Search for vectors in the context engine
- `code_index`: Index code in the context engine
- `create_relationship`: Create a relationship between vectors
- `get_related_vectors`: Get vectors related to a given vector

## Testing the Integration

You can test the integration by running:

```bash
python -m augment_adam.server.run_mcp_client --url http://localhost:8811/mcp --list-tools
```

This will list all the available tools on the MCP server.

## Troubleshooting

### Connection Issues

If VS Code can't connect to the MCP server:

1. Make sure the MCP server is running
2. Check the host and port settings
3. Check if there's a firewall blocking the connection
4. Try using socat to create a bridge

### Tool Errors

If a tool call fails:

1. Check the MCP server logs for error messages
2. Make sure the tool parameters are correct
3. Try calling the tool using the MCP client for debugging

## Further Reading

- [VS Code MCP Documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [Augment Adam MCP Server Documentation](../src/augment_adam/server/README.md)
