# Streamable HTTP Transport for Model Context Protocol (MCP)

## Introduction

The Model Context Protocol (MCP) is a standardized way for AI agents to communicate with services. As of March 26, 2025, the MCP specification introduced a new transport mechanism called **Streamable HTTP**, which simplifies how AI agents interact with services by using a single HTTP endpoint for bidirectional communication.

This document explains the Streamable HTTP transport, its benefits, and how to implement it in your Python applications.

## What is Streamable HTTP Transport?

Streamable HTTP is a new transport mechanism for MCP that:

1. **Uses a single endpoint** for all communication between clients and servers
2. **Supports bidirectional communication** allowing servers to send notifications and requests back to clients
3. **Enables automatic connection upgrades** from standard HTTP to streaming protocols like SSE when needed
4. **Simplifies implementation** for both clients and servers

## Comparison with Previous SSE Transport

| Feature | SSE Transport | Streamable HTTP Transport |
|---------|--------------|--------------------------|
| Endpoints | Two separate endpoints:<br>- `/sse` for receiving responses<br>- `/sse/messages` for sending requests | Single endpoint:<br>- `/mcp` for both sending requests and receiving responses |
| Connection Management | Requires keeping a persistent SSE connection open | Can use standard HTTP for short operations and upgrade to SSE for streaming |
| Implementation Complexity | Higher (managing two endpoints) | Lower (single endpoint) |
| Backward Compatibility | N/A | Can be implemented alongside SSE transport |
| Resumability | Limited | Built-in support for resuming interrupted operations |

## Benefits of Streamable HTTP Transport

1. **Simplified Architecture**: One endpoint handles all communication, reducing complexity.
2. **Improved Reliability**: Built-in support for resuming operations if connections drop.
3. **Better Scalability**: Stateless operations can use standard HTTP, while streaming operations can upgrade as needed.
4. **Reduced Resource Usage**: No need to maintain persistent connections for short operations.
5. **Future-Proof**: Designed to support advanced features like cancellability and session management.

## Implementing Streamable HTTP in Python

### Server Implementation

Using the Python MCP SDK, you can easily add Streamable HTTP support to your MCP server:

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("My App")

# Define your tools and resources
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

# Configure the server to support both transports
# 1. SSE transport (backward compatibility)
app.mount('/sse', mcp.serveSSE('/sse').fetch)

# 2. Streamable HTTP transport (new)
app.mount('/mcp', mcp.serve('/mcp').fetch)
```

### Client Implementation

Clients can connect to servers using the Streamable HTTP transport:

```python
from mcp import ClientSession
from mcp.client.http import http_client

async def main():
    # Connect to the server using Streamable HTTP
    async with http_client("https://example.com/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Call a tool
            result = await session.call_tool(
                "calculate_bmi", 
                arguments={"weight_kg": 70, "height_m": 1.75}
            )
            print(f"BMI: {result}")
```

## Advanced Features

The Streamable HTTP transport specification includes several advanced features that are being implemented:

1. **Resumability**: If a connection drops during a long-running operation, clients can resume exactly where they left off.
2. **Cancellability**: Clients can explicitly cancel operations, enabling cleaner termination of long-running processes.
3. **Session Management**: Secure session handling with unique session IDs that maintain state across multiple connections.

## Security Considerations

When implementing Streamable HTTP transport:

1. **CORS Protection**: Servers must implement proper CORS protection to prevent unauthorized cross-origin requests.
2. **DNS Rebinding Protection**: Implement protection against DNS rebinding attacks, especially for local MCP servers.
3. **Authentication**: Consider implementing OAuth 2.0 or other authentication mechanisms for protected resources.

## Conclusion

Streamable HTTP transport represents a significant improvement in how AI agents communicate with services through MCP. By simplifying the communication model to a single endpoint while supporting both immediate and streaming responses, it makes implementing MCP servers and clients more straightforward and reliable.

The examples in this repository demonstrate how to implement both server and client components using the Python MCP SDK, allowing you to take advantage of this new transport mechanism in your applications.

## References

1. [Cloudflare Blog: Streamable HTTP MCP Servers Python](https://blog.cloudflare.com/streamable-http-mcp-servers-python/)
2. [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
3. [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
