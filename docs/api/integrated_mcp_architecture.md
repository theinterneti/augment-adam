# Integrated MCP Architecture

This document describes an integrated architecture that combines all three MCP integration approaches to provide a comprehensive solution for exposing services as both MCP tools and RESTful APIs.

## Overview

The Integrated MCP Architecture combines the strengths of all three MCP integration approaches:

1. **FastAPI with FastAPI-MCP**: Direct API-to-MCP conversion
2. **FastAPI with open-webui-mcp**: Secure, proxied MCP access
3. **FastMCP with FastAPI Generation**: MCP-first design

By integrating these approaches, we can create a flexible, robust system that meets a wide range of requirements and use cases.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Integrated MCP Architecture                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Main FastAPI Application                    │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  Direct API     │    │  Native API     │    │  Proxy API   │ │
│  │  (/direct/*)    │    │  (/native/*)    │    │  (/proxy/*)  │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬───────┘ │
└───────────┼─────────────────────┼─────────────────────┼─────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  FastAPI-MCP      │  │  FastMCP          │  │  open-webui-mcp   │
│  (Port 8001)      │  │  (Port 8002)      │  │  (Port 8003)      │
└───────────────────┘  └───────────────────┘  └───────────────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  Shared Service       │
                      │  Implementation       │
                      └───────────────────────┘
```

## Components

### 1. Main FastAPI Application

The main FastAPI application serves as the entry point for all HTTP requests. It uses middleware to route requests to the appropriate sub-application based on the URL path:

- `/direct/*` → Direct API (FastAPI-MCP)
- `/native/*` → Native API (FastMCP)
- `/proxy/*` → Proxy API (open-webui-mcp)

### 2. Shared Service Implementation

A shared service implementation provides the core business logic for all three approaches. This ensures consistency across all interfaces and avoids code duplication.

### 3. Direct API (FastAPI-MCP)

The Direct API uses FastAPI with FastAPI-MCP to provide a simple, direct conversion of API endpoints to MCP tools. This approach is ideal for:

- Simple services with straightforward API-to-MCP mapping
- Development and testing scenarios
- Internal services where security is less of a concern

### 4. Native API (FastMCP)

The Native API uses FastMCP to define MCP tools and resources first, then generates a FastAPI application from them. This approach is ideal for:

- MCP-first design where the MCP interface is the primary concern
- Services that need fine-grained control over both interfaces
- Advanced MCP features like resources and prompts

### 5. Proxy API (open-webui-mcp)

The Proxy API uses FastAPI with open-webui-mcp to provide a secure, proxied MCP access. This approach is ideal for:

- Production environments where security is a concern
- Exposing existing APIs as MCP without modifying them
- Adding authentication and authorization to MCP tools

## Implementation

The implementation of the Integrated MCP Architecture involves:

1. Creating a shared service implementation
2. Setting up three separate MCP servers (one for each approach)
3. Creating a main FastAPI application that routes requests to the appropriate sub-application
4. Starting all servers in a coordinated way

See the [example implementation](../examples/memory_service_integrated.py) for a complete working example.

## Benefits

The Integrated MCP Architecture provides several benefits:

1. **Flexibility**: Different clients can use different interfaces based on their needs
2. **Security**: Sensitive operations can be restricted to specific interfaces
3. **Compatibility**: Support for a wide range of clients and use cases
4. **Scalability**: Each component can be scaled independently
5. **Resilience**: Failure in one component doesn't affect the others

## Use Cases

### 1. Multi-Tenant System

In a multi-tenant system, different tenants may have different requirements:

- Tenant A needs direct, high-performance access → Direct API
- Tenant B needs secure, authenticated access → Proxy API
- Tenant C needs advanced MCP features → Native API

### 2. Staged Deployment

In a staged deployment scenario:

- Development environment uses Direct API for simplicity
- Testing environment uses Native API for comprehensive testing
- Production environment uses Proxy API for security

### 3. Hybrid System

In a hybrid system:

- Internal services use Direct API for performance
- External services use Proxy API for security
- Advanced clients use Native API for full feature set

## Conclusion

The Integrated MCP Architecture provides a comprehensive solution for exposing services as both MCP tools and RESTful APIs. By combining the strengths of all three approaches, it offers flexibility, security, and compatibility for a wide range of use cases.

To implement this architecture, use the provided template and example:

- Template: `templates/code/python/integrated_mcp_service.py.j2`
- Example: `examples/memory_service_integrated.py`

This architecture is particularly well-suited for the Memory Service, as it allows different clients to access the service in different ways based on their specific requirements.
