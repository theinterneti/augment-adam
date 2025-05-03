# VS Code Extension Implementation

This document provides an overview of the implementation of the VS Code extension that integrates Qwen 3 with MCP servers.

## Architecture

The extension follows a modular architecture with the following components:

1. **Qwen API Client**: Handles communication with the Qwen 3 API.
2. **MCP Client**: Manages communication with MCP servers.
3. **Agent Coordinator**: Coordinates between Qwen and MCP servers.
4. **Context Engine**: Provides code understanding and context retrieval.
5. **UI Components**: Provides user interface for interacting with Qwen and MCP servers.

## Components

### Qwen API Client

The Qwen API client (`QwenApiClient`) is responsible for communicating with the Qwen 3 API. It provides methods for:

- Generating completions (`generateCompletion`)
- Streaming completions (`generateStreamingCompletion`)
- Chat with messages (`chat`)
- Streaming chat (`chatStream`)

The client supports thinking mode, which allows Qwen to show its reasoning process using `<think>` tags.

### MCP Client

The MCP client (`McpClient`) is responsible for communicating with MCP servers. It provides methods for:

- Getting available tools from all running servers (`getAllTools`)
- Invoking tools on servers (`invokeTool`)
- Finding tools by name (`findTool`)

### Agent Coordinator

The agent coordinator (`AgentCoordinator`) is the central component that coordinates between Qwen and MCP servers. It:

- Processes user requests (`processRequest`)
- Creates system prompts that include available tools (`createSystemPrompt`)
- Executes tools on MCP servers (`executeTool`)

The agent coordinator uses a hierarchical agent system with specialized agents for different tasks:

- Development Agent: For code generation, refactoring, and documentation
- Testing Agent: For test planning, generation, and execution
- CI/CD Agent: For build, deploy, and release management
- GitHub Agent: For PR management, issue tracking, and code reviews

### UI Components

The extension provides several UI components for interacting with Qwen and MCP servers:

- **MCP Server Tree View**: Displays available MCP servers and their status
- **Webview Panels**: Display responses from Qwen in a user-friendly way
  - Ask Qwen: For general questions
  - Explain Code: For code explanations
  - Generate Code: For code generation

## Commands

The extension provides the following commands:

- `qwen-coder-assistant.askQwen`: Ask general questions to Qwen
- `qwen-coder-assistant.explainCode`: Get explanations for selected code
- `qwen-coder-assistant.generateCode`: Generate code based on a description
- `qwen-coder-assistant.addMcpRepo`: Add an MCP server from a GitHub repository
- `qwen-coder-assistant.manageMcpServers`: Manage MCP servers
- `qwen-coder-assistant.startMcpServer`: Start an MCP server
- `qwen-coder-assistant.stopMcpServer`: Stop an MCP server
- `qwen-coder-assistant.restartMcpServer`: Restart an MCP server
- `qwen-coder-assistant.viewMcpServerLogs`: View logs for an MCP server
- `qwen-coder-assistant.viewMcpServerSchema`: View schema for an MCP server
- `qwen-coder-assistant.refreshMcpServers`: Refresh the MCP servers view

## Configuration

The extension provides the following configuration options:

- `qwen-coder-assistant.apiEndpoint`: API endpoint for the Qwen 3 coder model
- `qwen-coder-assistant.apiKey`: API key for the Qwen 3 coder model
- `qwen-coder-assistant.maxTokens`: Maximum number of tokens to generate
- `qwen-coder-assistant.temperature`: Temperature for the model's response generation
- `qwen-coder-assistant.mcpServers.storagePath`: Path to store MCP server repositories
- `qwen-coder-assistant.mcpServers.autoStart`: Whether to auto-start MCP servers
- `qwen-coder-assistant.mcpServers.autoStartList`: List of MCP servers to auto-start
- `qwen-coder-assistant.mcpServers.dockerOptions`: Docker options for MCP servers
- `qwen-coder-assistant.mcpServers.githubOptions`: GitHub options for MCP servers

## Error Handling

The extension provides robust error handling with:

- Structured error details (`ErrorDetails`)
- Error type classification (`ErrorType`)
- User-friendly error messages
- Retry functionality for retryable errors

## Testing

The extension uses a comprehensive testing approach with the following components:

### Unit Tests

Unit tests are implemented for core components to ensure they function correctly in isolation:

- **Context Engine Tests**: Test the context engine's ability to index, store, and retrieve code context
- **Vector Store Tests**: Test the vector store's ability to store and search for code chunks
- **File Indexer Tests**: Test the file indexer's ability to process and chunk code files
- **API Client Tests**: Test the Qwen API client's ability to communicate with the Qwen API
- **Response Formatter Tests**: Test the response formatter's ability to format and display responses
- **Context Provider Tests**: Test the context provider's ability to gather context from the editor

The tests use Mocha as the test runner and Sinon for mocking external dependencies.

### TypeScript Issues

The codebase currently has several TypeScript issues that need to be addressed:

- Naming convention issues (camelCase vs. PascalCase)
- Unused variables and parameters
- Type inference issues
- Missing type declarations
- Non-null assertions
- Case declarations in switch statements

These issues are tracked in the ISSUES.md file and are being addressed as part of the testing improvements.

### Planned Testing Improvements

1. **Complete Unit Tests**: Implement unit tests for remaining components
2. **Integration Tests**: Implement tests for component interactions
3. **End-to-End Tests**: Implement tests for complete user workflows
4. **TypeScript Error Fixes**: Address all TypeScript errors in the codebase
5. **Test Coverage**: Improve test coverage to at least 80%

## Future Improvements

1. **Enhanced Agent System**: Implement more specialized agents for different tasks
2. **Tool Execution**: Improve tool execution with better parameter validation and error handling
3. **Memory System**: Implement a memory system to remember previous conversations
4. **Workflow Management**: Implement workflow management for complex tasks
5. **Testing Framework**: Expand the testing framework to cover all components
