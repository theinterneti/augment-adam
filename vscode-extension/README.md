# Qwen Coder Assistant

A VS Code extension that acts as an MCP client hub, connecting Qwen with containerized MCP servers to provide AI-assisted coding capabilities.

## Features

- **Ask Qwen**: Ask general coding questions and get detailed answers
- **Explain Code**: Select code in your editor and get an explanation of what it does
- **Generate Code**: Describe what you want to implement and get code generated for you
- **MCP Server Management**: Add, start, stop, and restart MCP servers from GitHub repositories
- **Tool Integration**: Use Qwen with tools provided by MCP servers
- **Container Management**: Automatic building and management of Docker containers for MCP servers
- **GitHub Integration**: Clone and manage MCP server repositories from GitHub
- **Authentication Support**: Secure authentication for MCP servers with multiple methods
- **Logging and Telemetry**: Comprehensive logging and usage statistics for MCP servers
- **Server Updates**: Automatic version checking and updates for MCP servers
- **Server Discovery**: Find and install MCP servers from multiple sources

## Requirements

- VS Code 1.80.0 or higher
- Access to a Qwen 3 coder model API endpoint (local or remote)

## Extension Settings

This extension contributes the following settings:

- `qwen-coder-assistant.apiEndpoint`: API endpoint for the Qwen 3 coder model
- `qwen-coder-assistant.apiKey`: API key for the Qwen 3 coder model (if required)
- `qwen-coder-assistant.maxTokens`: Maximum number of tokens to generate
- `qwen-coder-assistant.temperature`: Temperature for the model's response generation
- `qwen-coder-assistant.mcpServers.storagePath`: Path to store MCP server data
- `qwen-coder-assistant.mcpServers.autoStart`: Automatically start MCP servers on extension activation
- `qwen-coder-assistant.mcpServers.autoStartList`: List of MCP server IDs to auto-start
- `qwen-coder-assistant.mcpServers.dockerOptions`: Docker configuration for MCP servers
- `qwen-coder-assistant.mcpServers.githubOptions`: GitHub configuration for MCP servers

## Getting Started

1. Install the extension
2. Configure the API endpoint in the settings
3. Configure the API key in the settings (if required)
4. Set the MCP server storage path in the settings
5. Use the commands from the command palette or context menu:
   - `Ask Qwen Coder`: Ask general coding questions
   - `Explain Code with Qwen`: Get explanations for selected code
   - `Generate Code with Qwen`: Generate code based on your description
   - `Add MCP Server from GitHub`: Add an MCP server from a GitHub repository
   - `Add Official MCP Server`: Add an official MCP server from the registry
   - `Discover MCP Servers`: Find and install MCP servers from multiple sources
   - `Manage MCP Servers`: View and manage MCP servers
   - `View MCP Server Logs`: View logs for a specific MCP server
   - `Check for MCP Server Updates`: Check for updates to installed MCP servers

## Official MCP Servers

The extension supports the following official MCP servers:

1. **GitHub MCP Server**: Interact with GitHub repositories, issues, pull requests, and more
2. **Docker MCP Server**: Manage Docker containers, images, volumes, and networks
3. **Git MCP Server**: Perform Git operations on local repositories
4. **Memory MCP Server**: Store and retrieve persistent memory for AI assistants
5. **Filesystem MCP Server**: Perform secure file operations with configurable access controls

For detailed documentation on using these servers, see:

- [Official MCP Server Integration Guide](./docs/research/mcp-servers/official_mcp_server_integration.md)
- [GitHub MCP Server Examples](./docs/examples/mcp-servers/github_examples.md)
- [Docker MCP Server Examples](./docs/examples/mcp-servers/docker_examples.md)

## Current Development Priorities

### Qwen-MCP Integration Enhancements (High Priority)

- Implement dynamic agent selection based on task complexity
- Create result aggregation for multi-agent responses
- Add support for parallel tool invocation
- Implement error handling and recovery for Qwen-MCP integration

### User Experience Improvements (Medium Priority)

- Create a welcome/onboarding experience
- Add keyboard shortcuts for common commands
- Enhance context menu integration
- Create context visualization panel

### Advanced Features (Medium Priority)

- Implement code actions integration
- Add diagnostics integration
- Create multi-file operation support
- Implement custom prompt templates

## Development Approach

We follow a test-driven development (TDD) approach:

1. **Write Tests First**: We define clear test cases that specify expected behavior before implementing features
2. **Implement to Pass Tests**: We write code to make the tests pass, focusing on functionality first
3. **Refactor**: We refine and optimize code while ensuring tests continue to pass
4. **Document**: We document features and update relevant documentation files

See the [TASKS.md](./TASKS.md) file for more details on current development tasks and the [PLANNING.md](./PLANNING.md) file for the overall project roadmap.

## Running Locally

To run this extension locally:

1. Clone the repository
2. Run `npm install` to install dependencies
3. Press F5 to start debugging

## License

MIT
