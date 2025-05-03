# Change Log

All notable changes to the "Qwen Coder Assistant" extension will be documented in this file.

## [0.1.0] - 2024-11-XX

### Added

- Integration with Qwen 3 API
  - Support for chat functionality
  - Support for thinking mode
  - Support for streaming responses
- Integration with MCP servers
  - MCP server management (add, start, stop, restart)
  - MCP server discovery from GitHub repositories
  - Tool execution on MCP servers
- Agent system
  - Agent coordinator for managing interactions between Qwen and MCP servers
  - Specialized agents for different tasks (development, testing, CI/CD, GitHub)
- UI improvements
  - Webview panels for displaying responses
  - MCP server tree view
  - Code insertion from generated code
- Error handling
  - Structured error details
  - User-friendly error messages
  - Retry functionality for retryable errors
- Testing improvements
  - Unit tests for core components (context engine, vector store, file indexer, API client, response formatter, context provider)
  - Test documentation and planning
  - TypeScript error tracking and documentation

## [0.0.1] - 2024-10-XX

### Initial Features

- Initial release
- Basic functionality for asking Qwen Coder questions
- Code explanation feature
- Code generation feature
- Mock API client for development
- Configuration options for API endpoint, API key, etc.
