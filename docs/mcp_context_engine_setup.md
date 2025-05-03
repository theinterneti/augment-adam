# MCP Context Engine Setup

This document provides instructions for setting up and using the MCP Context Engine with the Augment Adam development environment.

## Architecture

The MCP Context Engine uses a microservices architecture with the following components:

1. **Redis Vector Database**: For high-speed vector similarity search
2. **Neo4j Graph Database**: For storing relationships and graph-aware context
3. **MCP Context Engine API**: FastAPI-based MCP server that exposes the context engine's capabilities

All services communicate on a closed internal network, with only the MCP Context Engine API exposed to the host when needed.

## Network Architecture

The services are organized in the following network architecture:

- **augment-network**: A closed internal network for communication between services
- **default**: The default Docker network, used for exposing the MCP Context Engine API to the host

This architecture ensures that:
- All microservices communicate on a closed internal network
- Only the MCP Context Engine API is exposed to the host
- The host doesn't need direct access to the supplemental services (Redis, Neo4j)

## Setup

### Prerequisites

- Docker and Docker Compose
- Augment Adam development environment

### Starting the Services

To start the MCP Context Engine services, use the provided management script:

```bash
./scripts/manage_mcp_context_engine.sh start
```

This will start all the required services in the background.

### Checking Service Status

To check the status of the MCP Context Engine services:

```bash
./scripts/manage_mcp_context_engine.sh status
```

### Viewing Logs

To view logs from all services:

```bash
./scripts/manage_mcp_context_engine.sh logs
```

To view logs from a specific service:

```bash
./scripts/manage_mcp_context_engine.sh logs mcp-context-engine
```

### Stopping the Services

To stop the MCP Context Engine services:

```bash
./scripts/manage_mcp_context_engine.sh stop
```

## Integration with Augment Adam

The MCP Context Engine is automatically integrated with the Augment Adam development environment. The integration is set up during the post-start process of the devcontainer.

### Environment Variables

The following environment variables are set up for integration:

- `MCP_ENGINE_URL`: The URL of the MCP Context Engine API
- `MCP_ENGINE_API_KEY`: The API key for authenticating with the MCP Context Engine API

### Testing the Integration

To test the integration, you can use the following command:

```bash
curl -H "Authorization: Bearer $MCP_ENGINE_API_KEY" "$MCP_ENGINE_URL/health"
```

If the integration is working correctly, you should see a response indicating that the MCP Context Engine is healthy.

## Troubleshooting

### MCP Context Engine Not Accessible

If the MCP Context Engine is not accessible from the devcontainer, check the following:

1. Make sure the MCP Context Engine services are running:
   ```bash
   ./scripts/manage_mcp_context_engine.sh status
   ```

2. Check the logs for any errors:
   ```bash
   ./scripts/manage_mcp_context_engine.sh logs
   ```

3. Verify that the Docker network is set up correctly:
   ```bash
   docker network ls | grep augment-network
   ```

4. Ensure that the MCP Context Engine container is connected to both networks:
   ```bash
   docker inspect mcp-context-engine | grep -A 10 "Networks"
   ```

### Docker Socket Permission Issues

If you encounter Docker socket permission issues, refer to the Docker socket permission fix documentation in the devcontainer setup.
