# Streaming Examples

This directory contains examples demonstrating different streaming approaches for AI models and MCP servers.

## Basic Streaming Examples

1. **streaming_example.py** - A simple example showing how to use the ModelManager for streaming text generation.
2. **streaming_test.py** - A more advanced test script for streaming responses from different model backends.

## Model Context Protocol (MCP) Streaming Examples

3. **streamable_http_mcp_server.py** - Demonstrates how to implement an MCP server that supports both the new Streamable HTTP transport and the traditional SSE transport.
4. **streamable_http_mcp_client.py** - Shows how to connect to an MCP server using the Streamable HTTP transport.

## Transport Methods

The MCP specification supports different transport methods for communication between clients and servers:

### Server-Sent Events (SSE) Transport

The traditional transport method using two separate endpoints:
- One endpoint (e.g., `/sse`) for the client to receive streaming responses
- Another endpoint (e.g., `/sse/messages`) for the client to send requests

### Streamable HTTP Transport

A newer, more efficient transport method introduced in March 2025 that uses a single endpoint:
- One endpoint (e.g., `/mcp`) for both sending requests and receiving responses
- Supports automatic connection upgrades for streaming
- Provides better resumability and error handling
- Simplifies implementation and deployment

## Running the Examples

### Basic Streaming

```bash
# Run the basic streaming example
python examples/streaming_example.py

# Run the streaming test with different models
python examples/streaming_test.py --model_size medium
python examples/streaming_test.py --backend huggingface --model_size small
```

### MCP Server with Streamable HTTP

```bash
# Install required dependencies
pip install fastapi uvicorn mcp[cli]

# Run the MCP server
python examples/streamable_http_mcp_server.py

# In another terminal, run the client
python examples/streamable_http_mcp_client.py
```

## Additional Resources

For more information about Streamable HTTP transport and MCP:

1. See the detailed documentation in `docs/streamable_http_transport.md`
2. Visit the [Model Context Protocol website](https://modelcontextprotocol.io)
3. Check the [Python MCP SDK repository](https://github.com/modelcontextprotocol/python-sdk)
4. Read the [Cloudflare blog post](https://blog.cloudflare.com/streamable-http-mcp-servers-python/) about Streamable HTTP transport
