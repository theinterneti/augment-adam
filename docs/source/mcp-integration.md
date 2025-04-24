# Model Context Protocol (MCP) Integration Guide

This guide provides information on how to integrate and use the Model Context Protocol (MCP) in our project. Augment-Adam serves as an expert on all aspects of MCP, including client integration, server development, containerization, and ecosystem monitoring.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It acts like a "USB-C port for AI applications," providing a standardized way to connect AI models to different data sources and tools.

## Why Use MCP?

MCP offers several benefits for our project:

1. **Standardized Tool Access**: Provides a consistent way for AI models to access various tools and data sources
2. **Extensibility**: Easy to add new tools and capabilities as needed
3. **Security**: Helps maintain security by controlling what data and tools the AI model can access
4. **Interoperability**: Works with different AI models and platforms
5. **Community Support**: Large and growing ecosystem of tools and servers

## Available MCP Tools

Our project integrates with the Docker MCP server, which provides the following tools:

### Knowledge Graph Tools

- Create, read, update, and delete entities and relations in a knowledge graph
- Search for nodes and retrieve information from the knowledge graph
- Add observations to existing entities

### GitHub Integration Tools

- Create and update files in GitHub repositories
- Search for repositories, code, issues, and users
- Create and manage issues and pull requests
- Fork repositories and create branches

### Docker CLI Tool

- Execute Docker commands through the MCP server

## Setting Up MCP

To use MCP in your development environment:

1. Make sure you have the Docker MCP server running:

```bash
sudo docker exec -it augment-adam_devcontainer-dev-1 bash -c "chmod +x /usr/local/bin/mcp-connect.sh && /usr/local/bin/mcp-connect.sh initialize"
```

2. Configure your MCP client to connect to the server:

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "sudo",
      "args": [
        "docker",
        "exec",
        "-it",
        "augment-adam_devcontainer-dev-1",
        "bash",
        "-c",
        "/usr/local/bin/mcp-connect.sh"
      ]
    },
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server"],
      "env": {
        "SUPABASE_URL": "<YOUR_SUPABASE_URL>",
        "SUPABASE_KEY": "<YOUR_SUPABASE_KEY>"
      }
    }
  }
}
```

3. For VS Code integration, add to your settings.json:

```json
{
  "github.copilot.chat.mcpServers": {
    "docker-mcp": {
      "command": "sudo",
      "args": [
        "docker",
        "exec",
        "-it",
        "augment-adam_devcontainer-dev-1",
        "bash",
        "-c",
        "/usr/local/bin/mcp-connect.sh"
      ]
    }
  }
}
```

## Using MCP Tools in Code

Here's an example of how to use MCP tools in your code:

```python
from mcp_client import MCPClient

# Initialize the MCP client
client = MCPClient("docker-mcp")

# Use the knowledge graph tools
entities = [
    {
        "name": "Project Documentation",
        "entityType": "Document",
        "observations": [
            "Contains information about the project architecture",
            "Updated on 2025-04-28"
        ]
    }
]
client.call_tool("create_entities", {"entities": entities})

# Use the GitHub tools
client.call_tool("create_issue", {
    "owner": "theinterneti",
    "repo": "workspace",
    "title": "Update documentation with MCP information",
    "body": "Add information about MCP tools and integration to the project documentation."
})
```

## Best Practices

When using MCP in our project:

1. **Security First**: Only provide access to the tools and data that are necessary
2. **Document Tool Usage**: Clearly document which MCP tools are used and why
3. **Error Handling**: Implement robust error handling for MCP tool calls
4. **Testing**: Create mock MCP clients for testing to avoid making actual API calls
5. **Versioning**: Be aware of MCP server versions and tool compatibility

## Building and Containerizing MCP Servers

Augment-Adam can help you build and containerize custom MCP servers:

### 1. Server Development

```bash
# Create a new TypeScript MCP server project
npx create-mcp-server my-custom-server
cd my-custom-server

# Install dependencies
npm install

# Start the server for development
npm run dev
```

### 2. Containerization

Create a Dockerfile for your MCP server:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 8811

CMD ["npm", "start"]
```

Build and run the container:

```bash
# Build the container
docker build -t my-custom-mcp-server .

# Run the container
docker run -p 8811:8811 my-custom-mcp-server
```

### 3. Deployment

Deploy your containerized MCP server to various environments:

```bash
# Push to a container registry
docker tag my-custom-mcp-server username/my-custom-mcp-server:latest
docker push username/my-custom-mcp-server:latest

# Deploy with docker-compose
docker-compose up -d
```

## Staying Current with MCP Developments

Augment-Adam regularly monitors the MCP ecosystem for new developments:

1. **Daily Updates**: Tracking new MCP servers and tools released in the community
2. **Open Source Focus**: Prioritizing open-source and free/freemium services
3. **Integration Testing**: Evaluating new MCP servers for potential integration
4. **Best Practices**: Staying informed about evolving MCP development patterns

## Further Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/introduction)
- [Docker MCP Servers Repository](https://github.com/docker/mcp-servers)
- [MCP Tools Documentation](docs/docker-mcp-tools.md)
- [MCP Overview](docs/model-context-protocol.md)
- [Supabase MCP Documentation](https://supabase.com/docs/guides/getting-started/mcp)
- [VS Code MCP Integration](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

## Troubleshooting

If you encounter issues with MCP:

1. Make sure the Docker MCP server is running
2. Check that your MCP client is properly configured
3. Verify that you have the necessary permissions for the tools you're trying to use
4. Check the MCP server logs for error messages
5. Ensure you're using the correct input schema for the tools
