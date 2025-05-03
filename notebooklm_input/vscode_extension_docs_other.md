# VS Code Extension: Docs Other



---

### File: `TASKS.md`

```markdown
# VS Code Extension Development Tasks

This file tracks the tasks related to the development of the Qwen Coder Assistant VS Code extension.

## Current Priority Tasks

### Testing Improvements (High Priority)

- [x] Create unit tests for core components:
  - [x] Context Engine
  - [x] Vector Store
  - [x] File Indexer
  - [x] API Client
  - [x] Response Formatter
  - [x] Context Provider
- [ ] Fix TypeScript errors in the codebase:
  - [ ] Fix naming convention issues
  - [ ] Fix unused variables and parameters
  - [ ] Fix type inference issues
  - [ ] Fix missing type declarations
  - [ ] Fix non-null assertions
  - [ ] Fix case declarations in switch statements
- [ ] Create unit tests for remaining components:
  - [ ] Symbol Extractor
  - [ ] Embedding Service
  - [ ] Conversation History
  - [ ] Error Handler
  - [ ] MCP Client
  - [ ] MCP-Qwen Bridge
  - [ ] Commands

### Incremental Improvements (Medium Priority)

- [ ] Refine agent implementations based on real-world usage
- [ ] Add more specialized agents as needed (Testing, CI/CD, GitHub)
- [ ] Improve error handling for specific scenarios
- [x] Implement resource monitoring for MCP servers

### Documentation & Usability (Low Priority)

- [ ] Add more detailed documentation for personal reference
- [ ] Improve UI based on usage patterns
- [ ] Create a simple onboarding experience
- [ ] Add keyboard shortcuts for common operations

## Previous Tasks

### UI Enhancements

- [ ] Add custom webview styling to match VS Code themes
- [ ] Implement a welcome/onboarding experience
- [ ] Add keyboard shortcuts for common commands
- [ ] Enhance context menu integration
- [ ] Create context visualization panel
- [ ] Add settings UI for context engine configuration
- [ ] Implement progress indicators for indexing operations

### API Integration

- [ ] Implement rate limiting and throttling
- [ ] Create adapter for different API formats
- [ ] Add support for Augment API integration

### Testing

- [x] Write unit tests for context engine
- [x] Write unit tests for vector store
- [x] Write unit tests for file indexer
- [x] Write unit tests for API client
- [x] Write unit tests for response formatter
- [x] Write unit tests for context provider
- [ ] Write unit tests for symbol extractor
- [ ] Write unit tests for embedding service
- [ ] Write unit tests for conversation history
- [ ] Write unit tests for error handler
- [ ] Write unit tests for MCP client
- [ ] Write unit tests for MCP-Qwen bridge
- [ ] Write unit tests for commands
- [ ] Write integration tests for extension activation
- [ ] Create test fixtures for mock responses
- [ ] Implement end-to-end tests for user workflows
- [ ] Add tests for context engine integration

#### TypeScript Error Fixing Tasks

- [ ] Fix naming convention issues (camelCase vs. PascalCase)
- [ ] Fix unused variables and parameters
- [ ] Fix type inference issues
- [ ] Fix missing type declarations
- [ ] Fix non-null assertions
- [ ] Fix case declarations in switch statements

### Documentation

- [ ] Create comprehensive user guide
- [ ] Add inline code documentation
- [ ] Create API documentation
- [ ] Add screenshots and GIFs to README
- [ ] Create usage examples for context engine

### Personal Deployment

- [ ] Create personal installation script
- [ ] Set up local backup system for configurations
- [ ] Create personal settings sync mechanism
- [ ] Implement personal usage logging (optional)

### Performance Optimization

- [ ] Implement lazy loading for extension components
- [ ] Optimize memory usage for large codebases
- [ ] Implement incremental context updates

### Advanced Context Engine

- [ ] Add support for custom context filters
- [ ] Create context visualization tool
- [ ] Implement persistent storage for embeddings
- [ ] Add parallel processing for indexing and embedding generation
- [ ] Improve dependency analysis between files
- [ ] Add support for semantic code search
- [ ] Implement context-aware code completion

### Security

- [ ] Implement secure storage for API keys
- [ ] Add data sanitization for API requests
- [ ] Create privacy policy
- [ ] Implement content filtering options
- [ ] Add user consent prompts for data collection

### MCP Client Hub Implementation

- [x] Create basic structure for MCP client hub
- [x] Implement configuration for MCP servers
- [x] Create types for MCP servers and tools
- [x] Implement McpServerManager for managing MCP servers
- [x] Implement DockerContainerManager for managing Docker containers
- [x] Implement GitHubRepoManager for cloning and managing GitHub repositories
- [x] Implement McpClient for interacting with MCP servers
- [x] Implement UI for MCP servers
- [x] Implement commands for managing MCP servers
- [x] Implement Qwen API integration with MCP tools
- [x] Add support for tool invocation through Qwen
- [x] Implement context gathering from MCP servers
- [x] Add support for streaming responses from MCP servers
- [x] Implement error handling and recovery for MCP servers
- [x] Add support for authentication for MCP servers
- [x] Implement logging and telemetry for MCP servers
- [x] Add support for updating MCP servers
- [x] Implement MCP server discovery
- [x] Add support for MCP server configuration

### Official MCP Server Integration

- [x] Implement integration with official GitHub MCP server
- [x] Implement integration with official Docker MCP server
- [x] Add support for official Git MCP server
- [x] Integrate with Memory MCP server for persistent memory
- [x] Add support for Filesystem MCP server
- [x] Implement health monitoring for official MCP servers
- [x] Create configuration UI for official MCP servers
- [x] Add documentation for official MCP server integration
- [x] Implement error handling for official MCP servers
- [x] Create examples for using official MCP servers

### Hierarchical Agent System

- [ ] Implement additional specialized agents (Testing, CI/CD, GitHub)
- [ ] Create visualization panel for agent activities
- [ ] Add settings UI for agent configuration
- [ ] Implement agent testing framework

### Qwen-MCP Integration

- [x] Create Qwen API client with support for function calling
- [x] Implement MCP-Qwen bridge for tool invocation
- [x] Add support for hybrid thinking modes in Qwen integration
- [ ] Implement dynamic agent selection based on task complexity
- [ ] Create result aggregation for multi-agent responses
- [ ] Add support for parallel tool invocation
- [ ] Implement error handling and recovery for Qwen-MCP integration
- [ ] Create documentation for Qwen-MCP integration
- [ ] Add examples for using Qwen with MCP tools
- [ ] Implement resource monitoring and throttling

### Advanced Features (Next Phase)

- [ ] Implement code actions integration
- [ ] Add diagnostics integration
- [ ] Create multi-file operation support
- [ ] Implement custom prompt templates
- [ ] Add support for project-specific settings
- [ ] Create team collaboration features
- [ ] Implement version control integration
- [ ] Add support for code review assistance
- [ ] Implement AI-assisted debugging
- [ ] Add support for code generation with tests

## Completed Tasks History

### MCP Server Testing Completed

- [x] Enhanced MCP server management with a simple MCP server:
  - [x] Improved adding servers from GitHub with better validation
  - [x] Enhanced server starting and stopping functionality with health checks
  - [x] Implemented robust tool invocation with parameter validation
  - [x] Added server health monitoring
  - [x] Improved error handling for MCP server operations
  - [x] Added detailed logging for MCP server operations

### Configuration Setup Completed

- [x] Set up Qwen API endpoint in extension settings (default: `http://localhost:8000/v1`)
- [x] Configure Qwen API key in extension settings
- [x] Configure MCP server storage path in extension settings
- [x] Verify configuration is properly loaded and applied to API client
- [x] Implement configuration verification command
- [x] Implement API connection test command

### Basic Testing Completed

- [x] Test basic Qwen interactions:
  - [x] Test "askQwen" command with simple coding questions
  - [x] Test "explainCode" command with selected code
  - [x] Test "generateCode" command with requirements description
  - [x] Test "testApiConnection" command to verify API connectivity

### Hierarchical Agent System Completed

- [x] Implement agent coordination framework using Qwen 3 MoE
- [x] Develop task decomposition system with thinking mode
- [x] Create agent selection algorithm based on task complexity
- [x] Design result aggregation mechanism for multi-agent responses
- [x] Implement resource monitoring and dynamic throttling
- [x] Create specialized agents with appropriate model sizes
- [x] Develop agent communication protocol
- [x] Implement error handling and recovery for agents

### MCP Tool Integration Completed

- [x] Research and identify existing MCP tool repositories
- [x] Create Dockerfiles for containerizing MCP tools
- [x] Implement container registry for MCP tools
- [x] Develop container download and instantiation system
- [x] Set up container health monitoring with automatic restart
- [x] Create container lifecycle management
- [x] Implement persistent configuration storage
- [x] Develop unified tool invocation interface
- [x] Create tool discovery mechanism
- [x] Implement error handling and recovery for containerized tools

### API Integration Completed (Advanced)

- [x] Add support for multiple model options
- [x] Integrate Qwen 3 MoE models (Qwen3-30B-A3B, Qwen3-235B-A22B)
- [x] Implement hybrid thinking mode control
- [x] Create dynamic thinking budget allocation system
- [x] Develop model sharing across agents

### Core Functionality Completed

- [x] Create basic extension structure
- [x] Implement configuration management
- [x] Create Qwen API client interface
- [x] Implement mock API client for development
- [x] Create context provider for gathering code from editor
- [x] Implement response formatter for displaying AI responses
- [x] Create webview panel for interactive responses
- [x] Add syntax highlighting for code blocks in responses
- [x] Implement caching mechanism for API responses

### Commands Completed

- [x] Implement "Ask Qwen" command
- [x] Implement "Explain Code" command
- [x] Implement "Generate Code" command
- [x] Add "Refactor Code" command
- [x] Add "Document Code" command
- [x] Add "Fix Issues" command for error correction

### UI Enhancements Completed

- [x] Create status bar indicator for API mode
- [x] Implement progress notifications during API calls
- [x] Create a sidebar view for conversation history

### API Integration Completed

- [x] Create mock API for development
- [x] Implement proper error handling for API failures
- [x] Add support for streaming responses

### Testing Completed

- [x] Set up basic test framework
- [x] Write unit tests for symbol extractor

### Documentation Completed

- [x] Create basic README.md
- [x] Add CHANGELOG.md
- [x] Document context engine architecture
- [x] Update testing documentation
- [x] Create detailed component documentation

### Packaging and Distribution Completed

- [x] Create packaging script

### Performance Optimization Completed

- [x] Optimize context gathering for large files
- [x] Add caching for frequently used contexts
- [x] Optimize webview rendering for large responses
- [x] Implement background processing for heavy operations

### Advanced Context Engine Completed

- [x] Implement file indexer and chunker
- [x] Create embedding service for semantic search
- [x] Build vector store for code chunks
- [x] Implement symbol extraction and analysis
- [x] Create dependency graph for code relationships
- [x] Build context composer for relevant code retrieval
- [x] Add support for multi-language parsing (15+ languages)
- [x] Implement incremental indexing for large codebases
- [x] Add language-specific chunking strategies
- [x] Implement binary file detection and skipping

## References

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Qwen API Documentation](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- [Qwen3 Blog Post](https://qwenlm.github.io/blog/qwen3/)
- [Qwen Documentation](https://qwen.readthedocs.io/)
- [Qwen-Agent GitHub Repository](https://github.com/QwenLM/Qwen-Agent)
- [Function Calling Documentation](https://qwen.readthedocs.io/en/latest/framework/function_call.html)
- [Qwen-Agent Documentation](https://qwen.readthedocs.io/en/latest/framework/qwen_agent.html)
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Augment API Documentation](https://docs.augment.dev)
- [Docker SDK for Node.js](https://github.com/apocas/dockerode)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [Model Context Protocol Servers Repository](https://github.com/modelcontextprotocol/servers)
- [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Internal Research: Qwen API Capabilities](/docs/research/qwen-api/qwen_api_capabilities.md)
- [Internal Research: Hierarchical Agent Implementation](/docs/research/qwen-api/hierarchical_agent_implementation.md)
- [Internal Research: Containerizing MCP Tools](/docs/research/qwen-api/containerizing_mcp_tools.md)
- [Internal Research: Qwen MoE Architecture](/docs/research/qwen-api/qwen_moe_architecture.md)
- [Internal Research: MCP Servers Overview](/docs/research/mcp-servers/mcp_servers_overview.md)
- [Internal Research: MCP-Qwen Integration](/docs/research/mcp-servers/mcp_qwen_integration.md)
- [Internal Research: Implementation Strategy](/docs/research/mcp-servers/implementation_strategy.md)
- [Official MCP Server Integration Guide](/docs/research/mcp-servers/official_mcp_server_integration.md)
- [GitHub MCP Server Examples](/docs/examples/mcp-servers/github_examples.md)
- [Docker MCP Server Examples](/docs/examples/mcp-servers/docker_examples.md)

```


---

### File: `package.json.new`




---

### File: `TESTING.md`

```markdown
# Testing Documentation for VS Code Extension

This document outlines the testing strategy, current status, and future plans for testing the Qwen Coder Assistant VS Code extension.

## Testing Strategy

### Types of Tests

1. **Unit Tests**
   - Test individual components in isolation
   - Mock dependencies and external services
   - Focus on specific functionality

2. **Integration Tests**
   - Test interactions between components
   - Verify correct communication between modules
   - Test extension activation and command registration

3. **End-to-End Tests**
   - Test complete user workflows
   - Simulate user interactions with the extension
   - Verify expected outcomes

### Test Environment

- Tests run in a special VS Code extension host
- Uses Mocha as the test runner
- Uses the VS Code Extension Testing API

## Current Test Coverage

| Component | Unit Tests | Integration Tests | E2E Tests |
|-----------|------------|-------------------|-----------|
| Extension Activation | ✅ | ✅ | ❌ |
| Commands | ❌ | ❌ | ❌ |
| API Client | ✅ | ❌ | ❌ |
| Context Provider | ✅ | ❌ | ❌ |
| Response Formatter | ✅ | ❌ | ❌ |
| Webview Panel | ❌ | ❌ | ❌ |
| Configuration | ❌ | ❌ | ❌ |
| Symbol Extractor | ✅ | ❌ | ❌ |
| File Indexer | ✅ | ❌ | ❌ |
| Vector Store | ✅ | ❌ | ❌ |
| Context Engine | ✅ | ❌ | ❌ |
| Agent Selector | ✅ | ❌ | ❌ |
| MCP Client | ❌ | ❌ | ❌ |
| MCP-Qwen Bridge | ❌ | ❌ | ❌ |

## Test Issues and Priorities

### Current Issues

- Many TypeScript errors in the codebase need to be fixed
- Unit tests have been created for core components but need to be run and fixed
- Need to create proper mocks for VS Code API
- Need to implement test fixtures for API responses
- Need to add tests for MCP integration components

### Testing Priorities

1. Fix TypeScript errors in the codebase
   - Fix naming convention issues
   - Fix unused variables and parameters
   - Fix type inference issues
   - Fix missing type declarations
   - Fix non-null assertions
   - Fix case declarations in switch statements

2. Complete unit tests for remaining components
   - Symbol Extractor
   - Embedding Service
   - Conversation History
   - Error Handler
   - MCP Client
   - MCP-Qwen Bridge

3. Implement integration tests for commands
   - Test command registration
   - Test command execution with mock responses
   - Test context engine integration with commands

4. Implement end-to-end tests for user workflows
   - Test asking a question
   - Test explaining code
   - Test generating code
   - Test context-aware code generation
   - Test MCP tool integration

## Running Tests

### Prerequisites

- Node.js and npm installed
- VS Code Extension Testing API

### Commands

```bash
# Run all tests
npm test

# Run tests with coverage report
npm run test:coverage

# Run specific test file
npm test -- --grep "Extension Activation"
```

## Continuous Integration

### Future CI Setup

- Automated tests on pull requests
- Test matrix for different VS Code versions
- Coverage reporting and thresholds

## Manual Testing Checklist

Before releasing a new version, perform the following manual tests:

- [ ] Extension activates correctly
- [ ] Commands are registered and appear in the command palette
- [ ] "Ask Qwen" command opens input box and returns a response
- [ ] "Explain Code" command works with selected code
- [ ] "Generate Code" command produces valid code
- [ ] Configuration changes are applied correctly
- [ ] Status bar indicator shows the correct API mode
- [ ] Webview panel displays responses with proper formatting
- [ ] Copy and insert buttons in the webview work correctly

## References

- [VS Code Extension Testing](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Mocha Documentation](https://mochajs.org/)
- [VS Code Extension Samples - Testing](https://github.com/microsoft/vscode-extension-samples/tree/main/helloworld-test-sample)

```


---

### File: `.augment-guidelines.yaml`

# Augment Guidelines for VS Code Extension Project
# This file provides guidelines for Augment Code when working with this project

# Reference files that should be consulted when working on this project
REFERENCES:
  - vscode-extension/PLANNING.md
  - vscode-extension/TASKS.md
  - vscode-extension/TESTING.md
  - vscode-extension/STEPS.md
  - vscode-extension/STEPS_TESTING.md
  - vscode-extension/ISSUES.md
  - vscode-extension/IMPLEMENTATION.md
  - vscode-extension/CHANGELOG.md
  - vscode-extension/README.md

# VS Code Extension specific guidelines
VSCODE_EXTENSION:
  # Guidelines for working with VS Code Extension API
  API_USAGE:
    - Always use the VS Code Extension API as documented in the official VS Code API documentation
    - Use the appropriate VS Code namespaces (vscode, window, workspace, etc.)
    - Follow VS Code extension activation patterns and lifecycle management
    - Use VS Code's built-in UI components (webviews, tree views, etc.) rather than custom implementations
    - Respect VS Code's theming and styling guidelines

  # Guidelines for testing VS Code extensions
  TESTING:
    - Use the VS Code Extension Testing API for all tests
    - Follow the test structure in src/test/suite/
    - Use Mocha as the test runner with the TDD (Test-Driven Development) UI
    - Use Sinon for mocking external dependencies
    - Test extension activation, command registration, and other core functionality
    - Create proper mocks for VS Code API components

  # Guidelines for working with MCP (Model Context Protocol)
  MCP_INTEGRATION:
    - Follow the Model Context Protocol specification
    - Use the official MCP TypeScript SDK for integration
    - Implement proper error handling for MCP server communication
    - Follow the container-based approach for MCP tools
    - Use the MCP server discovery mechanism for finding available servers

# Problem-solving approach guidelines
PROBLEM_SOLVING:
  # Priority order for solving problems
  PRIORITY_ORDER:
    1: "WORKSPACE_CODE: Always look at existing code in the workspace first"
    2: "INSTALLED_LIBRARIES: Check installed libraries and dependencies before writing new code"
    3: "OPEN_SOURCE_REPOS: Reference open source repositories only when necessary"
    4: "CUSTOM_CODE: Write custom code only as a last resort"

  # Guidelines for working with tests
  TEST_APPROACH:
    - Never modify tests just to make them pass - fix the underlying code instead
    - Understand the test requirements before implementing solutions
    - Follow test-driven development: write tests first, then implement code to pass them
    - Use the VS Code Extension Testing API rather than creating standalone test implementations
    - Fix root causes of problems rather than symptoms
    - Document unfixed issues as GitHub issues tagged with TODO

  # Guidelines for implementing features
  IMPLEMENTATION_APPROACH:
    - Follow the modular architecture described in IMPLEMENTATION.md
    - Implement features incrementally, focusing on one component at a time
    - Use TypeScript best practices and follow the project's coding style
    - Fix TypeScript errors as described in ISSUES.md before adding new features
    - Document all new features in the appropriate reference files

# TypeScript specific guidelines
TYPESCRIPT:
  # Guidelines for fixing TypeScript errors
  ERROR_FIXING:
    - Fix naming convention issues by following consistent naming patterns
    - Remove or use unused variables and parameters
    - Fix type inference issues by removing redundant type annotations
    - Add missing type declarations for external libraries
    - Replace non-null assertions with proper null checks
    - Fix case declarations in switch statements by moving them outside case blocks

  # Guidelines for writing TypeScript code
  BEST_PRACTICES:
    - Use strong typing and avoid 'any' type when possible
    - Follow the TypeScript naming conventions (camelCase for variables, PascalCase for classes)
    - Use interfaces for defining complex types
    - Use enums for defining constants
    - Use async/await for asynchronous code
    - Use proper error handling with try/catch blocks

# Documentation guidelines
DOCUMENTATION:
  # Guidelines for updating documentation
  UPDATE_APPROACH:
    - Update all relevant reference files when implementing new features
    - Keep TASKS.md updated with current development tasks
    - Update TESTING.md with new test coverage information
    - Update CHANGELOG.md with notable changes
    - Update IMPLEMENTATION.md with architectural changes
    - Use consistent formatting across all documentation files



---

### File: `README.md`

```markdown
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

```


---

### File: `STEPS.md`

```markdown
# Next Steps for VS Code Extension Development

This document outlines the next steps for further development of the Qwen Coder Assistant VS Code extension. STEPS are things we aren't certain we want to do just yet. They might become TASKS if we decide to do them.

## Immediate Next Steps

### 1. Enhance the Hierarchical Agent System

- **Specialized Agents**: Implement additional specialized agents (Testing, CI/CD, GitHub, etc.)
- **Agent UI**: Create a visualization panel for agent activities and resource usage
- **Agent Testing**: Write comprehensive tests for the agent system
- **Agent Documentation**: Create detailed documentation for the agent system

### 2. Improve MCP Tool Integration

- **Local MCP Tools**: Create local implementations of MCP tools for personal use
- **Container UI**: Enhance the container management UI with more features
- **Tool Testing**: Write tests for the MCP tool integration
- **Tool Documentation**: Create personal documentation for the MCP tool integration

### 3. Enhance the Context Engine

- ✅ **Multi-Language Support**: Improve the symbol extractor to better handle more programming languages
- ✅ **Incremental Indexing**: Optimize the indexing process for large codebases
- **Custom Context Filters**: Allow users to specify which files or directories to include/exclude
- **Context Visualization**: Add a way for users to see what context is being used
- **Persistent Storage**: Store embeddings on disk to avoid re-indexing on restart

### 4. Improve User Experience

- ✅ **Custom Webview Styling**: Match the VS Code theme for a more integrated experience (Completed)
- ✅ **Keyboard Shortcuts**: Add customizable keyboard shortcuts for common commands (Completed)
- ✅ **Context Menu Integration**: Enhance the context menu options for different file types (Completed)
- **Welcome/Onboarding Experience**: Create a guided tour for new users

### 5. Add Advanced Features

- **Code Actions**: Integrate with VS Code's code actions for inline suggestions
- **Diagnostics Integration**: Use VS Code's diagnostics API to suggest fixes for errors
- **Multi-File Operations**: Support operations that span multiple files
- **Custom Prompts**: Allow users to create and save custom prompts for common tasks

### 6. Testing and Documentation

- ✅ **Unit Tests for Core Components**: Create unit tests for context engine, vector store, file indexer, API client, response formatter, and context provider (Completed)
- **TypeScript Error Fixes**: Address TypeScript errors in the codebase
  - Fix naming convention issues
  - Fix unused variables and parameters
  - Fix type inference issues
  - Fix missing type declarations
  - Fix non-null assertions
  - Fix case declarations in switch statements
- **Additional Unit Tests**: Create unit tests for remaining components
  - Symbol Extractor
  - Embedding Service
  - Conversation History
  - Error Handler
  - MCP Client
  - MCP-Qwen Bridge
  - Commands
- **Integration Tests**: Add simple integration tests for personal validation
- **Personal Guide**: Create notes and documentation for personal reference
- **Code Documentation**: Add inline documentation to make future maintenance easier

### 7. Performance Optimization

- **Lazy Loading**: Implement lazy loading for extension components
- **Memory Management**: Optimize memory usage for large codebases
- **Caching Strategies**: Improve caching for frequently used contexts
- **Background Processing**: Move more operations to background threads

## Long-Term Vision

### 1. Advanced AI Capabilities

- ✅ **Multi-Model Support**: Add support for different AI models (Completed with Qwen 3 MoE models)
- ✅ **Code Generation Workflows**: Create specialized workflows for different types of code generation (Partially completed with hierarchical agent system)
- **Fine-Tuning Options**: Allow users to fine-tune the model for their specific codebase
- **Learning from Feedback**: Implement a feedback system to improve responses over time

### 2. Personal Productivity Features

- **Personal Knowledge Base**: Build a personal knowledge base from past conversations
- **Project Templates**: Create templates for common project structures
- **Learning Assistant**: Use the system to help learn new technologies and concepts
- **Personal Workflow Automation**: Customize the system to match your personal workflow

### 3. Integration with Development Workflow

- ✅ **Git Integration**: Integrate with Git for commit message generation, PR descriptions, etc. (Partially completed with MCP tool integration)
- ✅ **CI/CD Integration**: Help with writing tests, fixing CI failures, etc. (Partially completed with hierarchical agent system)
- **Issue Tracker Integration**: Connect with issue trackers for context-aware assistance
- **Documentation Generation**: Automatically generate documentation for code

## Conclusion

The VS Code extension has made significant progress with the implementation of core features, error handling, streaming responses, conversation history, an advanced context engine, hierarchical agent system, and MCP tool integration. The next steps focus on enhancing these features for personal use, improving the user experience, adding advanced capabilities, and ensuring the extension is maintainable with basic testing and documentation.

The hierarchical agent system and MCP tool integration represent major advancements in the extension's capabilities, allowing for more sophisticated and specialized AI assistance for personal development. The Qwen 3 MoE models provide state-of-the-art performance for various tasks, and the container-based approach to MCP tools ensures flexibility and scalability even in a personal development environment.

By following this roadmap, we aim to create a powerful personal AI coding assistant that enhances your individual productivity and learning, leveraging the power of the Qwen 3 model, our advanced context engine, hierarchical agent system, and MCP tool integration - all while keeping the project private and focused on your personal needs.

```


---

### File: `STEPS_TESTING.md`

```markdown
# Testing Steps for VS Code Extension

This document outlines the detailed steps for testing the VS Code extension, including fixing TypeScript errors, implementing unit tests, and running tests.

## 1. TypeScript Error Fixing

### Step 1: Address Naming Convention Issues

- [ ] Fix enum member naming in `src/agents/types.ts`
- [ ] Fix object property naming in `src/context/symbolExtractor.ts`
- [ ] Fix variable naming in `src/agents/agentSelector.ts` and `src/agents/dynamicAgentSelector.ts`
- [ ] Fix class property naming in `src/context/contextComposer.ts`
- [ ] Fix HTTP header naming in `src/context/embeddingService.ts` and `src/qwenApi.ts`

### Step 2: Fix Unused Variables and Parameters

- [ ] Remove or use unused variables in `src/containers/containerManager.ts`
- [ ] Remove or use unused parameters in `src/context/fileIndexer.ts`
- [ ] Remove or use unused imports in `src/mcp-client/officialMcpServers.ts`
- [ ] Remove or use unused variables in `src/mcp/contextGatherer.ts`
- [ ] Remove or use unused variables in `src/test/mcpQwenIntegrationTest.ts`

### Step 3: Fix Type Inference Issues

- [ ] Remove redundant type annotations in `src/cache.ts`
- [ ] Remove redundant type annotations in `src/context/contextComposer.ts`
- [ ] Remove redundant type annotations in `src/context/contextEngine.ts`
- [ ] Remove redundant type annotations in `src/context/persistentVectorStore.ts`
- [ ] Remove redundant type annotations in `src/contextProvider.ts`

### Step 4: Fix Missing Type Declarations

- [ ] Add type declarations for `sqlite3` and `sqlite` in `src/context/persistentVectorStore.ts`
- [ ] Add type declarations for `simple-git` in `src/github-integration/githubRepoManager.ts`
- [ ] Add type declarations for `fetch` in `src/mcp-client/authentication/authManager.ts`
- [ ] Add type declarations for `fetch` in `src/mcp-client/discovery/serverDiscovery.ts`
- [ ] Add type declarations for `fetch` in `src/mcp-client/mcpServerManager.ts`

### Step 5: Fix Non-null Assertions

- [ ] Replace non-null assertions in `src/agents/agentSelector.ts` and `src/agents/dynamicAgentSelector.ts`
- [ ] Replace non-null assertions in `src/context/dependencyGraph.ts`
- [ ] Replace non-null assertions in `src/context/vectorStore.ts`
- [ ] Replace non-null assertions in `src/extension.ts`
- [ ] Replace non-null assertions in `src/mcp-client/mcpServerManager.ts`

### Step 6: Fix Case Declarations in Switch Statements

- [ ] Move case declarations outside case blocks in `src/agents/agentCoordinator.ts`
- [ ] Move case declarations outside case blocks in `src/errorHandler.ts`
- [ ] Move case declarations outside case blocks in `src/mcp-client/authentication/authManager.ts`
- [ ] Move case declarations outside case blocks in `src/ui/mcpServerConfigView.ts`

## 2. Unit Test Implementation

### Step 1: Implement Tests for Symbol Extractor

- [ ] Create test file `src/test/suite/symbolExtractor.test.ts`
- [ ] Implement tests for extracting symbols from TypeScript files
- [ ] Implement tests for extracting symbols from JavaScript files
- [ ] Implement tests for extracting symbols from Python files
- [ ] Implement tests for handling unsupported file types

### Step 2: Implement Tests for Embedding Service

- [ ] Create test file `src/test/suite/embeddingService.test.ts`
- [ ] Implement tests for getting embeddings from text
- [ ] Implement tests for handling API errors
- [ ] Implement tests for caching embeddings
- [ ] Implement tests for batch embedding requests

### Step 3: Implement Tests for Conversation History

- [ ] Create test file `src/test/suite/conversationHistory.test.ts`
- [ ] Implement tests for adding messages to history
- [ ] Implement tests for retrieving conversation history
- [ ] Implement tests for clearing conversation history
- [ ] Implement tests for serializing and deserializing history

### Step 4: Implement Tests for Error Handler

- [ ] Create test file `src/test/suite/errorHandler.test.ts`
- [ ] Implement tests for handling API errors
- [ ] Implement tests for handling network errors
- [ ] Implement tests for handling authentication errors
- [ ] Implement tests for handling unknown errors

### Step 5: Implement Tests for MCP Client

- [ ] Create test file `src/test/suite/mcpClient.test.ts`
- [ ] Implement tests for getting available tools
- [ ] Implement tests for invoking tools
- [ ] Implement tests for handling tool errors
- [ ] Implement tests for streaming tool results

### Step 6: Implement Tests for MCP-Qwen Bridge

- [ ] Create test file `src/test/suite/mcpQwenBridge.test.ts`
- [ ] Implement tests for converting MCP tools to Qwen format
- [ ] Implement tests for converting Qwen tool calls to MCP format
- [ ] Implement tests for handling tool results
- [ ] Implement tests for streaming tool results

### Step 7: Implement Tests for Commands

- [ ] Create test file `src/test/suite/commands.test.ts`
- [ ] Implement tests for the "Ask Qwen" command
- [ ] Implement tests for the "Explain Code" command
- [ ] Implement tests for the "Generate Code" command
- [ ] Implement tests for MCP server management commands

## 3. Running Tests

### Step 1: Run Existing Tests

- [ ] Run `npm test` to run all tests
- [ ] Fix any failing tests
- [ ] Verify that all tests pass

### Step 2: Run Tests with Coverage

- [ ] Run `npm run test:coverage` to run tests with coverage
- [ ] Identify areas with low coverage
- [ ] Add tests to improve coverage

### Step 3: Run Specific Tests

- [ ] Run `npm test -- --grep "Context Engine"` to run context engine tests
- [ ] Run `npm test -- --grep "Vector Store"` to run vector store tests
- [ ] Run `npm test -- --grep "File Indexer"` to run file indexer tests
- [ ] Run `npm test -- --grep "API Client"` to run API client tests
- [ ] Run `npm test -- --grep "Response Formatter"` to run response formatter tests
- [ ] Run `npm test -- --grep "Context Provider"` to run context provider tests

## 4. Integration Tests

### Step 1: Implement Integration Tests for Context Engine

- [ ] Create test file `src/test/suite/contextEngineIntegration.test.ts`
- [ ] Implement tests for context engine with file indexer
- [ ] Implement tests for context engine with vector store
- [ ] Implement tests for context engine with embedding service
- [ ] Implement tests for context engine with symbol extractor

### Step 2: Implement Integration Tests for Commands

- [ ] Create test file `src/test/suite/commandsIntegration.test.ts`
- [ ] Implement tests for commands with context provider
- [ ] Implement tests for commands with API client
- [ ] Implement tests for commands with response formatter
- [ ] Implement tests for commands with MCP client

## 5. End-to-End Tests

### Step 1: Implement End-to-End Tests for User Workflows

- [ ] Create test file `src/test/suite/e2e.test.ts`
- [ ] Implement tests for the "Ask Qwen" workflow
- [ ] Implement tests for the "Explain Code" workflow
- [ ] Implement tests for the "Generate Code" workflow
- [ ] Implement tests for MCP tool integration workflow

## References

- [VS Code Extension Testing](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Mocha Documentation](https://mochajs.org/)
- [Sinon Documentation](https://sinonjs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [ESLint Documentation](https://eslint.org/docs/user-guide/getting-started)

```


---

### File: `PLANNING.md`

```markdown
# VS Code Extension Planning Document

This document outlines the planning, architecture, and roadmap for the Augment Coder Assistant VS Code extension.

## Project Overview

The Augment Coder Assistant is a VS Code extension that integrates with AI models (including Qwen 3 and Augment API) to provide comprehensive AI-assisted coding and DevOps capabilities. The extension aims to enhance developer productivity by offering features like code generation, explanation, refactoring, and end-to-end DevOps guidance through natural language interactions and a hierarchical agent system.

## End-to-End DevOps Process Checklist

This section provides a detailed checklist for implementing the complete DevOps process within the extension.

### 1. Project Setup and Version Control

- [ ] **Repository Structure**
  - [ ] Create standardized directory structure
  - [ ] Set up .gitignore and .editorconfig
  - [ ] Configure linting and formatting rules
  - [ ] Create README.md with setup instructions

- [ ] **Git Workflow**
  - [ ] Implement branch strategy (main, develop, feature/*, bugfix/*, release/*)
  - [ ] Set up commit message templates
  - [ ] Configure pre-commit hooks
  - [ ] Document pull request process

- [ ] **GitHub Integration**
  - [ ] Set up issue templates
  - [ ] Create pull request templates
  - [ ] Configure branch protection rules
  - [ ] Set up project boards for task tracking

### 2. Development Environment

- [ ] **Containerization**
  - [ ] Create development container with VS Code integration
  - [ ] Set up Docker Compose for multi-container development
  - [ ] Implement volume caching for faster builds
  - [ ] Configure BuildKit optimizations

- [x] **MCP Integration**
  - [x] Identify and integrate with official MCP server repositories (GitHub, Docker, Git)
  - [x] Implement integration with Memory MCP server for persistent memory
  - [x] Add support for Filesystem MCP server for secure file operations
  - [x] Set up container health monitoring with automatic restart
  - [x] Create container lifecycle management
  - [x] Implement persistent configuration storage
  - [x] Develop server discovery and installation mechanism
  - [x] Create configuration UI for MCP servers
  - [x] Add authentication support for MCP servers
  - [x] Implement logging and telemetry for MCP servers
  - [x] Add support for updating MCP servers
  - [x] Create comprehensive documentation for MCP server integration
  - [x] Develop examples for using MCP servers

- [ ] **Local Testing Environment**
  - [ ] Set up automated test environment
  - [ ] Configure test data generation
  - [ ] Implement test result visualization
  - [ ] Create test coverage reporting

### 3. Continuous Integration

- [ ] **Build Pipeline**
  - [ ] Set up GitHub Actions workflow
  - [ ] Configure build matrix for multiple platforms
  - [ ] Implement caching for faster builds
  - [ ] Create build artifacts

- [ ] **Testing Pipeline**
  - [ ] Configure unit test automation
  - [ ] Set up integration test workflow
  - [ ] Implement end-to-end test suite
  - [ ] Create performance test benchmarks

- [ ] **Code Quality**
  - [ ] Set up code linting in CI
  - [ ] Configure static code analysis
  - [ ] Implement security scanning
  - [ ] Set up dependency vulnerability checking

### 4. Continuous Deployment

- [ ] **Release Management**
  - [ ] Create semantic versioning strategy
  - [ ] Set up changelog generation
  - [ ] Implement release notes automation
  - [ ] Configure version tagging

- [ ] **Deployment Pipeline**
  - [ ] Set up automated VS Code extension packaging
  - [ ] Configure marketplace deployment
  - [ ] Implement staged rollout strategy
  - [ ] Create rollback procedures

- [ ] **Monitoring**
  - [ ] Set up usage analytics
  - [ ] Implement error tracking
  - [ ] Configure performance monitoring
  - [ ] Create user feedback collection

### 5. Hierarchical Agent System

- [ ] **Agent Framework**
  - [ ] Design agent hierarchy and coordination system
  - [ ] Implement agent instantiation and lifecycle management
  - [ ] Create agent communication protocol
  - [ ] Set up agent resource monitoring and throttling

- [ ] **DevOps Agents**
  - [ ] Implement Development Agent (coding, refactoring, documentation)
  - [ ] Create Testing Agent (unit tests, integration tests, test planning)
  - [ ] Set up CI/CD Agent (build, deploy, release management)
  - [ ] Implement GitHub Agent (PR management, issue tracking, code reviews)

- [ ] **Specialized Agents**
  - [ ] Create Architecture Agent (system design, component planning)
  - [ ] Implement Security Agent (vulnerability scanning, secure coding practices)
  - [ ] Set up Performance Agent (optimization, benchmarking)
  - [ ] Create Documentation Agent (user guides, API docs, examples)

- [ ] **Agent Coordination**
  - [ ] Implement task decomposition system
  - [ ] Create agent selection algorithm
  - [ ] Set up result aggregation mechanism
  - [ ] Implement error handling and recovery

## Architecture

### Component Diagram

```ascii
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                VS Code Extension                                         │
│                                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌──────────────┐    ┌───────────────────┐   │
│  │   Commands    │    │  API Clients  │    │    Webview    │    │  Agent System     │   │
│  │               │    │               │    │    Panels     │    │                   │   │
│  │ - Ask         │    │ - QwenAPI     │    │               │    │ - Coordinator     │   │
│  │ - Explain Code│◄───┤ - AugmentAPI  │◄───┤ - Responses   │◄───┤ - Task Decomposer │   │
│  │ - Generate    │    │ - MockAPI     │    │ - Interactive │    │ - Agent Selector  │   │
│  │ - DevOps      │    │ - MCPAPI      │    │ - Dashboard   │    │ - Result Aggregator│  │
│  └───────┬───────┘    └───────┬───────┘    └──────┬───────┘    └─────────┬─────────┘   │
│          │                    │                    │                      │             │
│          ▼                    ▼                    ▼                      ▼             │
│  ┌───────────────┐    ┌───────────────┐    ┌──────────────┐    ┌───────────────────┐   │
│  │    Context    │    │ Configuration │    │   Response    │    │ Container Manager │   │
│  │    Engine     │    │   Manager     │    │  Formatter    │    │                   │   │
│  └───────────────┘    └───────────────┘    └──────────────┘    └───────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                │                     │                                    │
                ▼                     ▼                                    ▼
    ┌───────────────────┐   ┌───────────────────────┐   ┌───────────────────────────────┐
    │   AI Model APIs   │   │  Containerized MCP    │   │     Specialized Agents         │
    │                   │   │       Tools           │   │                               │
    │ - Qwen 3 Coder    │   │ - Docker MCP          │   │ - Development Agent           │
    │ - Augment API     │   │ - GitHub MCP          │   │ - Testing Agent               │
    │ - Local Models    │   │ - Knowledge Graph     │   │ - CI/CD Agent                 │
    │                   │   │ - Custom Tools        │   │ - GitHub Agent                │
    └───────────────────┘   └───────────────────────┘   └───────────────────────────────┘
```

### Hierarchical Agent System Architecture

```ascii
┌─────────────────────────────────────────────────────────────┐
│                   Agent Coordinator                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Resource Manager                        ││
│  │  - System monitoring                                    ││
│  │  - Agent instantiation/termination                      ││
│  │  - Resource allocation                                  ││
│  └─────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Task Decomposer                            │
│  - Breaks down user requests into subtasks                   │
│  - Creates execution plan                                    │
│  - Manages dependencies between tasks                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Selector                             │
│  - Chooses appropriate agents for each subtask               │
│  - Balances workload across agents                          │
│  - Handles agent specialization                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Pool                                 │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ DevOps Agents│  │ Domain Agents│  │Support Agents│      │
│  │              │  │              │  │              │      │
│  │ - Dev Agent  │  │ - Code Agent │  │ - UI Agent   │      │
│  │ - Test Agent │  │ - Docs Agent │  │ - Help Agent │      │
│  │ - CI/CD Agent│  │ - Arch Agent │  │ - Debug Agent│      │
│  │ - GitHub     │  │ - Sec Agent  │  │ - Review     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Result Aggregator                          │
│  - Collects results from all agents                          │
│  - Resolves conflicts                                        │
│  - Formats final response                                    │
└─────────────────────────────────────────────────────────────┘
```

### MCP Container Architecture

```ascii
┌─────────────────────────────────────────────────────────────┐
│                VS Code Extension                             │
│                                                             │
│  ┌───────────────────────┐      ┌───────────────────────┐   │
│  │  Container Registry   │      │  Container Manager    │   │
│  │  - Tool metadata      │      │  - Download           │   │
│  │  - Version tracking   │◄────►│  - Instantiation      │   │
│  │  - Dependency info    │      │  - Lifecycle          │   │
│  └───────────────────────┘      └───────────────────────┘   │
│                                           │                  │
└───────────────────────────────────────────┼──────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Docker Engine                                 │
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │
│  │  MCP Tool 1   │  │  MCP Tool 2   │  │  MCP Tool 3   │    │
│  │  Container    │  │  Container    │  │  Container    │    │
│  │               │  │               │  │               │    │
│  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │    │
│  │ │MCP Server │ │  │ │MCP Server │ │  │ │MCP Server │ │    │
│  │ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │    │
│  │       │       │  │       │       │  │       │       │    │
│  └───────┼───────┘  └───────┼───────┘  └───────┼───────┘    │
│          │                  │                  │            │
└──────────┼──────────────────┼──────────────────┼────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                MCP Client (Extension)                        │
│                                                             │
│  ┌───────────────────────┐      ┌───────────────────────┐   │
│  │  Tool Discovery       │      │  Tool Invocation      │   │
│  │  - Tool listing       │      │  - Parameter handling │   │
│  │  - Schema validation  │◄────►│  - Result processing  │   │
│  │  - Documentation      │      │  - Error handling     │   │
│  └───────────────────────┘      └───────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Commands**: Entry points for user interactions
   - Ask: General-purpose coding assistance
   - Explain Code: Detailed code explanations
   - Generate Code: Create new code based on requirements
   - Refactor Code: Improve existing code
   - Document Code: Add documentation to code
   - Fix Issues: Identify and fix code problems
   - DevOps: End-to-end development operations guidance

2. **API Clients**: Handle communication with AI models
   - QwenAPI: Interface for Qwen 3 coder model
   - AugmentAPI: Interface for Augment's API
   - MockAPI: Simulated responses for development
   - MCPAPI: Interface for MCP tools

3. **Context Engine**: Advanced code understanding system
   - File Indexer: Processes and chunks code files
   - Embedding Service: Generates vector embeddings for code
   - Vector Store: Stores and retrieves code chunks
   - Symbol Extractor: Identifies code symbols and relationships
   - Dependency Graph: Maps relationships between code components
   - Context Composer: Assembles relevant context for queries
   - Semantic Search: Finds semantically related code

4. **Configuration Manager**: Handles user settings
   - API configuration
   - Model parameters
   - Context engine settings
   - UI preferences
   - Agent system configuration
   - Container management settings

5. **Webview Panels**: Display interactive AI responses
   - Syntax highlighting
   - Interactive elements
   - Conversation history
   - DevOps dashboard
   - Agent activity visualization

6. **Response Formatter**: Formats AI responses for display
   - Code block formatting
   - Markdown rendering
   - Streaming support
   - Multi-agent response aggregation

7. **Agent System**: Manages hierarchical agent coordination using Qwen 3 MoE architecture
   - Coordinator: Orchestrates agent activities using Qwen3-30B-A3B with thinking mode
   - Task Decomposer: Breaks down complex tasks into manageable subtasks
   - Agent Selector: Chooses appropriate agents based on task complexity and available resources
   - Model Manager: Handles model sharing and thinking mode selection
   - Result Aggregator: Combines outputs from multiple agents into coherent responses
   - Resource Manager: Monitors system resources and implements dynamic throttling
   - Thinking Budget Allocator: Distributes computational resources based on task complexity

8. **Container Manager**: Handles MCP tool containerization with existing repositories
   - Container Registry: Tracks available MCP tools and their versions
   - Container Downloader: Fetches container images from registry or builds from source
   - Container Lifecycle: Manages container instantiation, auto-start, and graceful termination
   - Health Monitor: Tracks container status and automatically restarts crashed containers
   - Configuration Manager: Stores and manages persistent tool configurations
   - Resource Monitor: Tracks and optimizes resource usage across containers
   - Tool Discovery: Automatically discovers available tools and their capabilities
   - MCP Client: Communicates with containerized tools using the MCP protocol

## Development Roadmap

### Phase 1: Core Functionality (Completed)

- Basic extension structure
- Command implementation (Ask, Explain, Generate, Refactor, Document, Fix)
- Mock API for development
- Response display with syntax highlighting
- Conversation history sidebar
- Streaming responses
- Context provider for editor content

### Phase 2: Advanced Context Engine (Completed)

- File indexer and chunker
- Embedding service for semantic search
- Vector store for code chunks
- Symbol extraction and analysis
- Dependency graph for code relationships
- Context composer for relevant code retrieval
- Multi-language parsing support
- Incremental indexing for large codebases
- Language-specific chunking strategies
- Binary file detection and skipping

### Phase 3: Enhanced Features (Completed)

- Custom webview styling to match VS Code themes
- Welcome/onboarding experience
- Keyboard shortcuts for common commands
- Enhanced context menu integration
- Support for multiple model options
- Integration with Qwen 3 MoE models
- Hybrid thinking mode control
- Dynamic thinking budget allocation

### Phase 4: Current Priority Tasks

#### Configuration Setup (High Priority)

- Set up Qwen API endpoint in extension settings
- Configure Qwen API key in extension settings
- Configure MCP server storage path in extension settings
- Verify configuration is properly loaded and applied to API client

#### Basic Testing (High Priority)

- Test basic Qwen interactions (askQwen, explainCode, generateCode)
- Test MCP server management with a simple MCP server (Completed)

#### Incremental Improvements (Medium Priority)

- Refine agent implementations based on real-world usage
- Add more specialized agents as needed (Testing, CI/CD, GitHub)
- Improve error handling for specific scenarios
- Implement resource monitoring for MCP servers

#### Documentation & Usability (Low Priority)

- Add more detailed documentation for personal reference
- Improve UI based on usage patterns
- Create a simple onboarding experience
- Add keyboard shortcuts for common operations

### Phase 5: Advanced Features (Future)

- Context visualization panel
- Settings UI for context engine configuration
- Rate limiting and throttling
- Adapter for different API formats
- Augment API integration

### Phase 6: DevOps Integration (Future)

- End-to-end DevOps command implementation (Partially Completed)
- Hierarchical agent system for DevOps guidance (Completed)
- GitHub workflow integration
- Branch and PR management
- Commit message formatting
- CI/CD pipeline visualization
- Project structure guidance
- Development environment setup
- Testing workflow automation
- Documentation generation
- Release management

### Phase 7: MCP Containerization (Completed)

- Create Dockerfiles for GitHub and Docker MCP tools (Completed)
- Implement container registry for MCP tools (Completed)
- Set up automatic container download and caching (Completed)
- Develop container instantiation system with auto-start on extension activation (Completed)
- Implement container health monitoring with automatic restart (Completed)
- Create persistent configuration storage for MCP tools (Completed)
- Optimize resource usage for multiple containers (Completed)
- Develop unified tool invocation interface (Completed)
- Implement result processing and formatting (Completed)
- Create robust error handling and recovery (Completed)
- Implement tool invocation testing and validation (Completed)
- Design container lifecycle management with graceful shutdown (Completed)
- Add authentication support for MCP servers (Completed)
- Implement logging and telemetry for MCP servers (Completed)
- Add support for updating MCP servers (Completed)
- Implement MCP server discovery (Completed)
- Create comprehensive documentation for MCP server integration (Completed)
- Develop examples for using MCP servers (Completed)
- Create local implementations of MCP tools (Completed)
- Implement personal MCP tool configurations (Completed)

### Phase 8: Hierarchical Agent System (Completed)

- Implement agent coordination framework using Qwen 3 MoE architecture (Completed)
- Develop task decomposition system with thinking mode for complex planning (Completed)
- Create agent selection algorithm based on task complexity and available resources (Completed)
- Implement model sharing across agents with appropriate thinking mode selection (Completed)
- Design result aggregation mechanism for multi-agent responses (Completed)
- Develop resource monitoring and dynamic throttling based on system load (Completed)
- Create dynamic thinking budget allocation system (Completed)
- Implement Development agent using Qwen3-30B-A3B with thinking mode (Completed)

### Phase 9: Specialized Agents (Future)

- Implement DevOps agent using Qwen3-30B-A3B with thinking mode
- Create Testing agent using Qwen3-14B with thinking mode
- Develop CI/CD agent using Qwen3-8B with non-thinking mode
- Implement GitHub agent using Qwen3-4B with non-thinking mode
- Design additional specialized agents with appropriate model size and thinking mode

### Phase 10: Advanced Features (Future)

- Context-aware suggestions
- Code actions integration
- Diagnostics integration
- Multi-file operation support
- Custom prompt templates
- Project-specific settings
- Persistent storage for embeddings
- Parallel processing for indexing
- Semantic code search
- Context-aware code completion

### Phase 11: Personal Productivity Features (Future)

- Personal knowledge base from conversations
- Project templates for common structures
- Learning assistant for new technologies
- Personal workflow automation
- Custom model fine-tuning for personal projects
- Personal code style enforcement
- Automated personal code reviews
- Personal development environment optimization
- Learning progress tracking
- Personal coding analytics

## Integration Strategy

### Model Integration

The extension will support multiple AI models and deployment options:

1. **Qwen 3 Coder Model**
   - Local Deployment: Running the model locally using tools like llama.cpp or vLLM
   - Self-hosted API: Connecting to a self-hosted API endpoint
   - Cloud API: Connecting to a cloud-based API service
   - MoE Architecture: Leveraging Qwen3-30B-A3B and Qwen3-235B-A22B for efficient agent system

2. **Augment API Integration**
   - Cloud API: Connecting to Augment's cloud-based API service
   - Enterprise Deployment: Support for enterprise-specific deployments
   - Custom Models: Support for custom fine-tuned models

### Qwen 3 MoE Architecture

The extension will leverage Qwen 3's Mixture of Experts (MoE) architecture for the hierarchical agent system:

1. **MoE Models**
   - Qwen3-30B-A3B: 30B total parameters with 3B activated (10%)
   - Qwen3-235B-A22B: 235B total parameters with 22B activated (~9.4%)
   - Efficient resource usage with performance comparable to much larger dense models

2. **Hybrid Thinking Modes**
   - Thinking Mode: Step-by-step reasoning for complex tasks
   - Non-Thinking Mode: Quick responses for simpler tasks
   - Dynamic control via `/think` and `/no_think` directives
   - Thinking budget allocation based on task complexity

3. **Agent-Specific Model Selection**
   - Coordinator Agent: Qwen3-30B-A3B with thinking mode
   - Development Agent: Qwen3-30B-A3B with thinking mode
   - Testing Agent: Qwen3-14B with thinking mode
   - CI/CD Agent: Qwen3-8B with non-thinking mode
   - GitHub Agent: Qwen3-4B with non-thinking mode

### Qwen-MCP Integration

The extension will integrate Qwen with MCP servers using the Qwen-Agent framework:

1. **Qwen-Agent Framework**
   - Native support for MCP
   - Tool registration via Python decorators
   - Automatic handling of MCP protocol
   - Built-in agent capabilities

2. **Integration Approaches**
   - Direct API Integration: Full control over the Qwen model
   - OpenAI-Compatible API Server: Compatibility with existing tools
   - Qwen-Agent Integration: Simplified integration with native MCP support

3. **MCP-Qwen Bridge**
   - Tool discovery and schema parsing
   - Parameter handling and validation
   - Result processing and formatting
   - Error handling and recovery

4. **Dynamic Resource Allocation**
   - Model selection based on task complexity
   - Thinking mode control for efficient resource usage
   - Parallel processing for independent tasks
   - Resource monitoring and throttling

### MCP Tool Integration

The extension will integrate with official MCP servers from the Model Context Protocol repository:

1. **GitHub MCP Server**
   - Use the official GitHub MCP server
   - Repository management (clone, fork, create)
   - Branch operations (create, merge, delete)
   - Pull request management (create, review, merge)
   - Issue tracking (create, update, close)

2. **Docker MCP Server**
   - Use the official Docker MCP server
   - Image management (build, pull, push)
   - Container lifecycle (create, start, stop, remove)
   - Volume management
   - Network configuration

3. **Git MCP Server**
   - Use the official Git MCP server
   - Repository operations (clone, init)
   - Branch management
   - Commit operations
   - File operations

4. **Memory MCP Server**
   - Knowledge graph-based persistent memory
   - Entity and relationship management
   - Query capabilities
   - Context management

5. **Filesystem MCP Server**
   - Secure file operations
   - Directory listing
   - File reading and writing
   - Path manipulation
   - Access control

### API Requirements

The AI model APIs should support:

- Chat completions endpoint
- Context window of at least 32K tokens (128K preferred for MoE models)
- JSON mode for structured outputs
- Streaming responses
- Function calling capabilities
- Tool use capabilities
- Thinking mode control

## User Experience Goals

1. **Seamless Integration**: The extension should feel like a natural part of VS Code
   - Native UI components
   - Consistent with VS Code design patterns
   - Keyboard-friendly interactions

2. **Low Latency**: Responses should be quick, with appropriate loading indicators
   - Streaming responses for immediate feedback
   - Background processing for heavy operations
   - Caching for frequently used contexts
   - Incremental indexing for large codebases

3. **High Quality**: AI responses should be accurate and helpful
   - Context-aware responses using the advanced context engine
   - Code-specific formatting and syntax highlighting
   - Relevant code references from the codebase
   - Language-specific understanding and generation

4. **Customizable**: Users should be able to configure the extension to their preferences
   - Model selection and parameters
   - Context engine configuration
   - UI customization options
   - Custom prompt templates

5. **Privacy-focused**: Minimal data collection, with clear user consent
   - Local processing where possible
   - Transparent data handling
   - Opt-in telemetry
   - Data sanitization for API requests

6. **Context-aware**: The extension should understand the user's code context
   - Multi-file awareness
   - Symbol understanding across the codebase
   - Dependency analysis
   - Semantic code search capabilities

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
   - Symbol extractor tests (✅ Existing)
   - File indexer tests (✅ Implemented)
   - Vector store tests (✅ Implemented)
   - API client tests (✅ Implemented)
   - Response formatter tests (✅ Implemented)
   - Context provider tests (✅ Implemented)
   - Context engine tests (✅ Implemented)
   - Agent selector tests (✅ Existing)
   - MCP client tests (⏳ Planned)
   - MCP-Qwen bridge tests (⏳ Planned)
   - Command handler tests (⏳ Planned)
   - Embedding service tests (⏳ Planned)
   - Conversation history tests (⏳ Planned)
   - Error handler tests (⏳ Planned)

2. **Integration Tests**: Test component interactions
   - Context engine integration tests
   - API client with response formatter tests
   - Command with context provider tests
   - Webview panel integration tests
   - MCP tool integration tests

3. **TypeScript Error Fixing**: Address existing TypeScript errors
   - Fix naming convention issues (camelCase vs. PascalCase)
   - Fix unused variables and parameters
   - Fix type inference issues
   - Fix missing type declarations
   - Fix non-null assertions
   - Fix case declarations in switch statements

4. **End-to-End Tests**: Test complete user workflows
   - Ask command workflow
   - Explain code workflow
   - Generate code workflow
   - Refactor code workflow
   - Document code workflow
   - Fix issues workflow

5. **Performance Tests**: Evaluate system performance
   - Large codebase indexing performance
   - Context retrieval latency
   - Memory usage optimization
   - Response time benchmarks

6. **User Testing**: Gather feedback from real users
   - Beta testing program
   - Usability studies
   - Feature validation
   - Error case handling

## Success Metrics

1. **User Adoption**: Number of active installations
   - Installation growth rate
   - Retention rate
   - Cross-IDE adoption (if expanded)

2. **User Engagement**: Frequency of command usage
   - Commands used per session
   - Session duration
   - Feature usage distribution
   - Context engine utilization

3. **User Satisfaction**: Ratings and feedback
   - Marketplace ratings
   - Net Promoter Score
   - Feature satisfaction surveys
   - Support ticket analysis

4. **Code Quality Impact**: Improvements in development speed and code quality
   - Time saved metrics
   - Code quality improvements
   - Bug reduction
   - Documentation improvements

5. **Context Engine Performance**: Effectiveness of code understanding
   - Context relevance scores
   - Query-context match rate
   - Symbol extraction accuracy
   - Dependency graph correctness

## References

- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code Extension Best Practices](https://code.visualstudio.com/api/references/extension-guidelines)
- [Qwen API Documentation](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- [Qwen3 Blog Post](https://qwenlm.github.io/blog/qwen3/)
- [Qwen Documentation](https://qwen.readthedocs.io/)
- [Qwen-Agent GitHub Repository](https://github.com/QwenLM/Qwen-Agent)
- [Function Calling Documentation](https://qwen.readthedocs.io/en/latest/framework/function_call.html)
- [Qwen-Agent Documentation](https://qwen.readthedocs.io/en/latest/framework/qwen_agent.html)
- [Augment API Documentation](https://docs.augment.dev)
- [Vector Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Docker SDK for Node.js](https://github.com/apocas/dockerode)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [Model Context Protocol Servers Repository](https://github.com/modelcontextprotocol/servers)
- [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Internal Research: Qwen API Capabilities](/docs/research/qwen-api/qwen_api_capabilities.md)
- [Internal Research: Hierarchical Agent Implementation](/docs/research/qwen-api/hierarchical_agent_implementation.md)
- [Internal Research: Containerizing MCP Tools](/docs/research/qwen-api/containerizing_mcp_tools.md)
- [Internal Research: Qwen MoE Architecture](/docs/research/qwen-api/qwen_moe_architecture.md)
- [Internal Research: MCP Servers Overview](/docs/research/mcp-servers/mcp_servers_overview.md)
- [Internal Research: MCP-Qwen Integration](/docs/research/mcp-servers/mcp_qwen_integration.md)
- [Internal Research: Implementation Strategy](/docs/research/mcp-servers/implementation_strategy.md)
- [Official MCP Server Integration Guide](/docs/research/mcp-servers/official_mcp_server_integration.md)
- [GitHub MCP Server Examples](/docs/examples/mcp-servers/github_examples.md)
- [Docker MCP Server Examples](/docs/examples/mcp-servers/docker_examples.md)

```


---

### File: `ISSUES.md`

```markdown
# VS Code Extension Issues

This file tracks the current issues in the VS Code extension that need to be addressed.

## TypeScript Errors

### Issue: Multiple TypeScript errors in the codebase

**Priority**: High

**Description**:
There are numerous TypeScript errors in the codebase that need to be fixed. These errors are preventing the tests from running properly and could lead to runtime issues.

**Categories of Errors**:
1. Naming convention issues (camelCase vs. PascalCase)
2. Unused variables and parameters
3. Type inference issues
4. Missing type declarations
5. Non-null assertions
6. Case declarations in switch statements

**Files with Errors**:
- src/agents/agentCoordinator.ts
- src/agents/agentSelector.ts
- src/agents/developmentAgent.ts
- src/agents/dynamicAgentSelector.ts
- src/agents/types.ts
- src/cache.ts
- src/commands.ts
- src/container-manager/dockerContainerManager.ts
- src/containers/containerManager.ts
- src/context/contextComposer.ts
- src/context/contextEngine.ts
- src/context/dependencyGraph.ts
- src/context/embeddingService.ts
- src/context/fileIndexer.ts
- src/context/persistentVectorStore.ts
- src/context/semanticSearch.ts
- src/context/symbolExtractor.ts
- src/context/vectorStore.ts
- src/contextProvider.ts
- src/conversationHistory.ts
- src/errorHandler.ts
- src/extension.ts
- src/github-integration/githubRepoManager.ts
- src/mcp-client/authentication/authManager.ts
- src/mcp-client/discovery/serverDiscovery.ts
- src/mcp-client/logging/mcpLogger.ts
- src/mcp-client/mcpClient.ts
- src/mcp-client/mcpServerManager.ts
- src/mcp-client/officialMcpServers.ts
- src/mcp-client/serverHealthMonitor.ts
- src/mcp-client/telemetry/telemetryManager.ts
- src/mcp-client/types.ts
- src/mcp-client/updates/updateManager.ts
- src/mcp/contextGatherer.ts
- src/mcp/mcpClient.ts
- src/mcp/mcpQwenBridge.ts
- src/mcp/mcpTypes.ts
- src/mockQwenApi.ts
- src/qwenApi.ts
- src/responseFormatter.ts
- src/test/mcpQwenIntegrationTest.ts
- src/test/suite/dynamicAgentSelector.test.ts
- src/ui/logViewer.ts
- src/ui/mcpServerConfigView.ts
- src/ui/serverDiscoveryView.ts
- src/webview/panel.ts

**Steps to Reproduce**:
1. Run `npm run lint` to see the linting errors
2. Run `npm test` to see the TypeScript compilation errors

**Proposed Solution**:
1. Fix naming convention issues by updating variable and property names to follow consistent conventions
2. Remove or use unused variables and parameters
3. Fix type inference issues by removing redundant type annotations
4. Add missing type declarations for external libraries
5. Replace non-null assertions with proper null checks
6. Fix case declarations in switch statements by moving them outside the case blocks

**Related Tasks**:
- Update TASKS.md with TypeScript error fixing tasks
- Update TESTING.md with current testing status
- Create unit tests for core components

**Assignee**: TBD

**Due Date**: TBD

## Testing Issues

### Issue: Incomplete test coverage for core components

**Priority**: Medium

**Description**:
While basic tests have been set up, many core components lack proper test coverage. This makes it difficult to ensure the reliability of the extension.

**Components Needing Tests**:
- Symbol Extractor
- Embedding Service
- Conversation History
- Error Handler
- MCP Client
- MCP-Qwen Bridge
- Commands

**Proposed Solution**:
1. Create unit tests for each component
2. Use proper mocking for VS Code API and external services
3. Implement test fixtures for API responses
4. Add integration tests for key workflows

**Related Tasks**:
- Fix TypeScript errors to enable proper test execution
- Update TESTING.md with current testing status
- Create a test plan for each component

**Assignee**: TBD

**Due Date**: TBD

```


---

### File: `CHANGELOG.md`

```markdown
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

```


---

### File: `IMPLEMENTATION.md`

```markdown
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

```


---

### File: `docs/implementation_guide.md`

```markdown
# Implementation Guide for Current Priority Tasks

This guide provides detailed instructions for implementing the current priority tasks for the Qwen Coder Assistant VS Code extension.

## Configuration Setup

### Setting up Qwen API Endpoint and Key

1. **Verify Configuration Loading**:
   - The configuration is already defined in `src/configuration.ts`
   - The `QwenCoderConfig` interface includes `apiEndpoint` and `apiKey` properties
   - The `getConfiguration()` function loads these values from VS Code settings

2. **Test Configuration Loading**:
   - Create a simple command to display the current configuration
   - Add this to `src/commands.ts`:

   ```typescript
   export function registerShowConfigCommand(context: vscode.ExtensionContext): void {
     const disposable = vscode.commands.registerCommand('qwen-coder-assistant.showConfig', async () => {
       const config = getConfiguration();
       vscode.window.showInformationMessage(`API Endpoint: ${config.apiEndpoint}, API Key: ${config.apiKey ? '(Set)' : '(Not Set)'}`);
     });
     context.subscriptions.push(disposable);
   }
   ```

3. **Add Command to Package.json**:
   - Add the command to the `contributes.commands` section in `package.json`:

   ```json
   {
     "command": "qwen-coder-assistant.showConfig",
     "title": "Show Qwen API Configuration"
   }
   ```

4. **Verify API Client Initialization**:
   - Check that the `QwenApiClient` is properly initialized with the configuration
   - Ensure the client is updated when configuration changes

### Configuring MCP Server Storage Path

1. **Verify Storage Path Configuration**:
   - The `McpServersConfig` interface in `src/configuration.ts` includes a `storagePath` property
   - The `getConfiguration()` function loads this value from VS Code settings

2. **Add Storage Path Selection Command**:
   - Create a command to allow users to select a storage path
   - Add this to `src/commands.ts`:

   ```typescript
   export function registerSelectStoragePathCommand(context: vscode.ExtensionContext): void {
     const disposable = vscode.commands.registerCommand('qwen-coder-assistant.selectStoragePath', async () => {
       const options: vscode.OpenDialogOptions = {
         canSelectMany: false,
         canSelectFolders: true,
         canSelectFiles: false,
         openLabel: 'Select MCP Server Storage Path'
       };
       
       const folderUri = await vscode.window.showOpenDialog(options);
       if (folderUri && folderUri.length > 0) {
         const config = vscode.workspace.getConfiguration('qwen-coder-assistant');
         await config.update('mcpServers.storagePath', folderUri[0].fsPath, vscode.ConfigurationTarget.Global);
         vscode.window.showInformationMessage(`MCP Server storage path set to: ${folderUri[0].fsPath}`);
       }
     });
     context.subscriptions.push(disposable);
   }
   ```

3. **Add Command to Package.json**:
   - Add the command to the `contributes.commands` section in `package.json`:

   ```json
   {
     "command": "qwen-coder-assistant.selectStoragePath",
     "title": "Select MCP Server Storage Path"
   }
   ```

4. **Verify Storage Path Usage**:
   - Check that the `McpServerManager` is properly using the storage path
   - Ensure the storage path is created if it doesn't exist

## Basic Testing

### Testing Basic Qwen Interactions

1. **Test "askQwen" Command**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Ask Qwen Coder" command
   - Enter a simple coding question like "How do I read a file in Node.js?"
   - Verify that the response is displayed in a webview panel

2. **Test "explainCode" Command**:
   - Open a code file
   - Select a block of code
   - Right-click and select "Explain Code with Qwen" from the context menu
   - Verify that the explanation is displayed in a webview panel

3. **Test "generateCode" Command**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Generate Code with Qwen" command
   - Enter a description like "Create a function that sorts an array of objects by a property"
   - Verify that the generated code is displayed in a webview panel

### Testing MCP Server Management

1. **Test Adding a Server from GitHub**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Add MCP Server from GitHub" command
   - Enter a GitHub repository URL like "https://github.com/modelcontextprotocol/servers"
   - Verify that the server is added to the MCP Servers view

2. **Test Starting and Stopping the Server**:
   - In the MCP Servers view, right-click on a server and select "Start MCP Server"
   - Verify that the server status changes to "Running"
   - Right-click on the server and select "Stop MCP Server"
   - Verify that the server status changes to "Stopped"

3. **Test Basic Tool Invocation**:
   - Start an MCP server
   - Open the command palette (Ctrl+Shift+P)
   - Run a command that uses an MCP tool
   - Verify that the tool is invoked and the result is displayed

## Troubleshooting

### Common Issues

1. **API Connection Issues**:
   - Check that the API endpoint is correct
   - Verify that the API key is set
   - Check network connectivity
   - Look for CORS issues if using a browser-based API

2. **MCP Server Issues**:
   - Check that Docker is running
   - Verify that the storage path exists and is writable
   - Check Docker logs for container errors
   - Verify that the GitHub token is set if using private repositories

3. **Extension Activation Issues**:
   - Check the VS Code Developer Tools console for errors
   - Verify that all dependencies are installed
   - Check that the extension is properly activated

### Debugging Tips

1. **Enable Extension Logging**:
   - Add logging statements to key functions
   - Use `console.log` for basic logging
   - Consider implementing a more robust logging system for production

2. **Use VS Code Developer Tools**:
   - Open Developer Tools with Help > Toggle Developer Tools
   - Check the Console tab for errors and log messages
   - Use the Network tab to monitor API requests

3. **Test with Mock API**:
   - Use the mock API client for testing without a real API
   - Set `NODE_ENV=development` to use the mock API
   - Verify that the mock API is returning expected responses

```


---

### File: `archive/vscode-extension/src/context/README.md`

```markdown
# Context Engine for VS Code Extension

This directory contains the implementation of the advanced context engine for the Qwen Coder Assistant VS Code extension. The context engine is designed to provide relevant code context to the Qwen 3 model, enabling it to generate more accurate and contextually aware responses.

## Architecture

The context engine consists of several components that work together to provide a comprehensive understanding of the codebase:

### 1. File Indexer and Chunker (`fileIndexer.ts`)

- Scans the workspace for code files
- Splits files into manageable chunks
- Handles file changes, additions, and deletions
- Updates the index incrementally

### 2. Embedding Service (`embeddingService.ts`)

- Generates vector embeddings for code chunks
- Uses the Qwen 3 embedding model
- Supports batch embedding generation
- Handles API communication for embeddings

### 3. Vector Store (`vectorStore.ts`)

- Stores code chunks and their embeddings
- Provides semantic search capabilities
- Calculates similarity between queries and code
- Manages the lifecycle of stored chunks

### 4. Symbol Extractor (`symbolExtractor.ts`)

- Extracts symbols (functions, classes, variables) from code
- Identifies imports and dependencies
- Supports multiple programming languages
- Provides language-specific extraction strategies

### 5. Dependency Graph (`dependencyGraph.ts`)

- Builds a graph of code dependencies
- Tracks relationships between files
- Identifies related files for a given file
- Supports traversal of the dependency graph

### 6. Semantic Search (`semanticSearch.ts`)

- Provides advanced search capabilities
- Combines exact and semantic matching
- Searches for symbols across the codebase
- Ranks results by relevance

### 7. Context Composer (`contextComposer.ts`)

- Composes relevant context from code chunks
- Manages token limits for context
- Organizes context by file and relevance
- Provides summaries of symbols and imports

### 8. Context Engine (`contextEngine.ts`)

- Coordinates all components
- Provides a unified API for context retrieval
- Handles initialization and cleanup
- Manages the lifecycle of the context system

## Usage

The context engine is used by the VS Code extension to provide relevant code context to the Qwen 3 model. It is initialized when the extension is activated and is used by the various commands to retrieve context for the current task.

### Basic Usage

```typescript
import { getProjectContext } from './contextProvider';

// Get context for a query
const context = await getProjectContext('How do I implement a binary search?');

// Use the context in a prompt
const prompt = `${userQuery}\n\nRelevant code context:\n${context}`;
```

### Advanced Usage

```typescript
import { getContextForFile, getContextForSymbol } from './contextProvider';

// Get context for a specific file
const fileContext = await getContextForFile('/path/to/file.ts');

// Get context for a specific symbol
const symbolContext = await getContextForSymbol('BinarySearch');
```

## Performance Considerations

The context engine is designed to be efficient and scalable, but there are some performance considerations to keep in mind:

- **Indexing**: The initial indexing of a large codebase can take some time. Progress is shown in the status bar.
- **Memory Usage**: The vector store keeps embeddings in memory, which can use significant RAM for large codebases.
- **API Calls**: The embedding service makes API calls to generate embeddings, which can incur costs and latency.

## Current Status and Future Improvements

### Implemented Features

- ✅ **Multi-Language Support**: Enhanced symbol extractor with support for 15+ programming languages
- ✅ **Incremental Indexing**: Optimized indexing process with batching and background processing
- ✅ **Language-Specific Chunking**: Intelligent chunking strategies based on language semantics
- ✅ **Binary File Detection**: Automatic detection and skipping of binary files

### Planned Improvements

- **Custom Context Filters**: Allow users to specify which files or directories to include/exclude
- **Context Visualization**: Add a way for users to see what context is being used
- **Persistent Storage**: Store embeddings on disk to avoid re-indexing on restart
- **Parallel Processing**: Use worker threads for indexing and embedding generation
- **Improved Dependency Analysis**: Better detection of relationships between files

## Contributing

Contributions to the context engine are welcome! Please follow these guidelines:

1. Write tests for new functionality
2. Document your code with JSDoc comments
3. Follow the existing code style
4. Consider performance implications for large codebases

```


---

### File: `src/mcp/README.md`

```markdown
# MCP-Qwen Integration

This directory contains the implementation of the MCP-Qwen integration, which allows Qwen to use MCP tools.

## Components

### McpClient

The `McpClient` class is responsible for interacting with MCP servers. It provides methods for:

- Fetching tool schemas
- Getting available tools
- Calling functions on tools

### McpQwenBridge

The `McpQwenBridge` class bridges the gap between Qwen and MCP. It provides methods for:

- Converting MCP tools to Qwen tool format
- Processing user messages with MCP tools
- Executing tool calls and getting final responses

### QwenApiClient

The `QwenApiClient` class (in the parent directory) has been enhanced with function calling support:

- `chatWithTools`: Method to chat with function calling support
- `chatStreamWithTools`: Method for streaming responses with function calling
- Enhanced thinking mode support with `thinkingMode` and `thinkingBudget` options

## Usage

To use the MCP-Qwen integration:

1. Initialize the MCP client and Qwen API client
2. Create an instance of the McpQwenBridge
3. Process user messages with the bridge

Example:

```typescript
// Initialize clients
const qwenClient = new QwenApiClient(config);
const mcpClient = new McpClient(containerManager);
await mcpClient.initialize();

// Create bridge
const mcpQwenBridge = new McpQwenBridge(qwenClient, mcpClient);

// Process a message
const response = await mcpQwenBridge.processMessage(
  "Can you help me with GitHub?",
  {
    systemPrompt: "You are a helpful assistant that can use MCP tools.",
    thinkingMode: "auto"
  }
);
```

## Testing

You can test the MCP-Qwen integration using the `testMcpQwenBridge` command in VS Code. This command will:

1. Initialize the MCP client and Qwen API client
2. Create an instance of the McpQwenBridge
3. Get available tools
4. Process a test message
5. Display the response in an output channel

## Thinking Modes

The MCP-Qwen integration supports three thinking modes:

- `auto`: Qwen will use thinking mode for complex problems and respond directly for simple tasks
- `always`: Qwen will always use thinking mode for all problems
- `never`: Qwen will never use thinking mode

You can also specify a `thinkingBudget` to limit the number of tokens used for thinking.

```


---

### File: `src/context/README.md`

```markdown
# Context Engine for VS Code Extension

This directory contains the implementation of the advanced context engine for the Qwen Coder Assistant VS Code extension. The context engine is designed to provide relevant code context to the Qwen 3 model, enabling it to generate more accurate and contextually aware responses.

## Architecture

The context engine consists of several components that work together to provide a comprehensive understanding of the codebase:

### 1. File Indexer and Chunker (`fileIndexer.ts`)

- Scans the workspace for code files
- Splits files into manageable chunks
- Handles file changes, additions, and deletions
- Updates the index incrementally

### 2. Embedding Service (`embeddingService.ts`)

- Generates vector embeddings for code chunks
- Uses the Qwen 3 embedding model
- Supports batch embedding generation
- Handles API communication for embeddings

### 3. Vector Store (`vectorStore.ts`)

- Stores code chunks and their embeddings
- Provides semantic search capabilities
- Calculates similarity between queries and code
- Manages the lifecycle of stored chunks

### 4. Symbol Extractor (`symbolExtractor.ts`)

- Extracts symbols (functions, classes, variables) from code
- Identifies imports and dependencies
- Supports multiple programming languages
- Provides language-specific extraction strategies

### 5. Dependency Graph (`dependencyGraph.ts`)

- Builds a graph of code dependencies
- Tracks relationships between files
- Identifies related files for a given file
- Supports traversal of the dependency graph

### 6. Semantic Search (`semanticSearch.ts`)

- Provides advanced search capabilities
- Combines exact and semantic matching
- Searches for symbols across the codebase
- Ranks results by relevance

### 7. Context Composer (`contextComposer.ts`)

- Composes relevant context from code chunks
- Manages token limits for context
- Organizes context by file and relevance
- Provides summaries of symbols and imports

### 8. Context Engine (`contextEngine.ts`)

- Coordinates all components
- Provides a unified API for context retrieval
- Handles initialization and cleanup
- Manages the lifecycle of the context system

## Usage

The context engine is used by the VS Code extension to provide relevant code context to the Qwen 3 model. It is initialized when the extension is activated and is used by the various commands to retrieve context for the current task.

### Basic Usage

```typescript
import { getProjectContext } from './contextProvider';

// Get context for a query
const context = await getProjectContext('How do I implement a binary search?');

// Use the context in a prompt
const prompt = `${userQuery}\n\nRelevant code context:\n${context}`;
```

### Advanced Usage

```typescript
import { getContextForFile, getContextForSymbol } from './contextProvider';

// Get context for a specific file
const fileContext = await getContextForFile('/path/to/file.ts');

// Get context for a specific symbol
const symbolContext = await getContextForSymbol('BinarySearch');
```

## Performance Considerations

The context engine is designed to be efficient and scalable, but there are some performance considerations to keep in mind:

- **Indexing**: The initial indexing of a large codebase can take some time. Progress is shown in the status bar.
- **Memory Usage**: The vector store keeps embeddings in memory, which can use significant RAM for large codebases.
- **API Calls**: The embedding service makes API calls to generate embeddings, which can incur costs and latency.

## Current Status and Future Improvements

### Implemented Features

- ✅ **Multi-Language Support**: Enhanced symbol extractor with support for 15+ programming languages
- ✅ **Incremental Indexing**: Optimized indexing process with batching and background processing
- ✅ **Language-Specific Chunking**: Intelligent chunking strategies based on language semantics
- ✅ **Binary File Detection**: Automatic detection and skipping of binary files

### Planned Improvements

- **Custom Context Filters**: Allow users to specify which files or directories to include/exclude
- **Context Visualization**: Add a way for users to see what context is being used
- **Persistent Storage**: Store embeddings on disk to avoid re-indexing on restart
- **Parallel Processing**: Use worker threads for indexing and embedding generation
- **Improved Dependency Analysis**: Better detection of relationships between files

## Contributing

Contributions to the context engine are welcome! Please follow these guidelines:

1. Write tests for new functionality
2. Document your code with JSDoc comments
3. Follow the existing code style
4. Consider performance implications for large codebases

```


---

### File: `media/mcpServerConfig.css`

body {
  padding: 0;
  margin: 0;
  font-family: var(--vscode-font-family);
  color: var(--vscode-foreground);
  background-color: var(--vscode-editor-background);
}

h1 {
  font-size: 1.5em;
  margin-bottom: 1em;
  border-bottom: 1px solid var(--vscode-panel-border);
  padding-bottom: 0.5em;
}

h2 {
  font-size: 1.2em;
  margin-top: 1.5em;
  margin-bottom: 1em;
}

h3 {
  font-size: 1.1em;
  margin-top: 1.2em;
  margin-bottom: 0.8em;
}

#app {
  padding: 1em;
  max-width: 800px;
  margin: 0 auto;
}

#server-selector {
  margin-bottom: 1.5em;
}

#server-select {
  width: 100%;
  padding: 0.5em;
  font-size: 1em;
  background-color: var(--vscode-input-background);
  color: var(--vscode-input-foreground);
  border: 1px solid var(--vscode-input-border);
  border-radius: 2px;
}

.form-group {
  margin-bottom: 1em;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.3em;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group textarea {
  padding: 0.5em;
  font-size: 1em;
  background-color: var(--vscode-input-background);
  color: var(--vscode-input-foreground);
  border: 1px solid var(--vscode-input-border);
  border-radius: 2px;
}

.form-group textarea {
  min-height: 5em;
  resize: vertical;
}

.button-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
  margin-top: 1.5em;
  margin-bottom: 1.5em;
}

button {
  padding: 0.5em 1em;
  font-size: 1em;
  background-color: var(--vscode-button-background);
  color: var(--vscode-button-foreground);
  border: none;
  border-radius: 2px;
  cursor: pointer;
}

button:hover {
  background-color: var(--vscode-button-hoverBackground);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-running {
  color: var(--vscode-testing-iconPassed);
}

.status-stopped {
  color: var(--vscode-testing-iconQueued);
}

.status-starting, .status-stopping {
  color: var(--vscode-testing-iconUnset);
}

.status-error, .status-unknown {
  color: var(--vscode-testing-iconFailed);
}

.health-healthy {
  color: var(--vscode-testing-iconPassed);
}

.health-unhealthy {
  color: var(--vscode-testing-iconFailed);
}

.health-unknown {
  color: var(--vscode-testing-iconUnset);
}

.tools-container {
  margin-top: 2em;
  border-top: 1px solid var(--vscode-panel-border);
  padding-top: 1em;
}

.tools-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tool-item {
  margin-bottom: 1em;
  padding: 0.8em;
  background-color: var(--vscode-editor-inactiveSelectionBackground);
  border-radius: 4px;
}

.tool-item h4 {
  margin-top: 0;
  margin-bottom: 0.5em;
}

.tool-item p {
  margin: 0;
  font-size: 0.9em;
}

#official-servers {
  margin-top: 2em;
  border-top: 1px solid var(--vscode-panel-border);
  padding-top: 1em;
}



---

### File: `media/styles.css`

/* Base styles for the webview */
body {
  padding: 20px;
  line-height: 1.6;
  font-family: var(--vscode-font-family);
  color: var(--vscode-editor-foreground);
  background-color: var(--vscode-editor-background);
  font-size: var(--vscode-font-size);
}

h1, h2, h3, h4, h5, h6 {
  color: var(--vscode-editor-foreground);
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

h1 {
  font-size: 2em;
  border-bottom: 1px solid var(--vscode-panel-border);
  padding-bottom: 0.3em;
}

h2 {
  font-size: 1.5em;
  border-bottom: 1px solid var(--vscode-panel-border);
  padding-bottom: 0.3em;
}

h3 {
  font-size: 1.25em;
}

p {
  margin-top: 0;
  margin-bottom: 16px;
}

ul, ol {
  margin-top: 0;
  margin-bottom: 16px;
  padding-left: 2em;
}

li {
  margin-bottom: 0.25em;
}

a {
  color: var(--vscode-textLink-foreground);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

code {
  font-family: var(--vscode-editor-font-family, 'Consolas, "Courier New", monospace');
  font-size: var(--vscode-editor-font-size);
  padding: 0.2em 0.4em;
  margin: 0;
  border-radius: 3px;
  background-color: var(--vscode-textCodeBlock-background);
}

pre {
  font-family: var(--vscode-editor-font-family, 'Consolas, "Courier New", monospace');
  font-size: var(--vscode-editor-font-size);
  padding: 16px;
  overflow: auto;
  line-height: 1.45;
  background-color: var(--vscode-textCodeBlock-background);
  border-radius: 3px;
  margin-top: 0;
  margin-bottom: 16px;
  word-wrap: normal;
}

pre code {
  background-color: transparent;
  padding: 0;
  margin: 0;
  font-size: 100%;
  word-break: normal;
  white-space: pre;
  border: 0;
}

.code-block-container {
  position: relative;
  margin-bottom: 16px;
}

.copy-button, .insert-button {
  position: absolute;
  top: 5px;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 500;
  line-height: 20px;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  background-color: var(--vscode-button-background);
  color: var(--vscode-button-foreground);
  z-index: 1;
}

.copy-button {
  right: 5px;
}

.insert-button {
  right: 70px;
}

.copy-button:hover, .insert-button:hover {
  background-color: var(--vscode-button-hoverBackground);
}

.response-container {
  max-width: 100%;
  overflow-x: auto;
}

/* Syntax highlighting */
.hljs-keyword {
  color: var(--vscode-symbolIcon-keywordForeground, #569cd6);
}

.hljs-string {
  color: var(--vscode-symbolIcon-stringForeground, #ce9178);
}

.hljs-comment {
  color: var(--vscode-symbolIcon-textForeground, #6a9955);
}

.hljs-operator {
  color: var(--vscode-symbolIcon-operatorForeground, #d4d4d4);
}

.hljs-symbol {
  color: var(--vscode-symbolIcon-operatorForeground, #d4d4d4);
}

/* Dark theme adjustments */
.vscode-dark .hljs-keyword {
  color: #569cd6;
}

.vscode-dark .hljs-string {
  color: #ce9178;
}

.vscode-dark .hljs-comment {
  color: #6a9955;
}

.vscode-dark .hljs-operator {
  color: #d4d4d4;
}

.vscode-dark .hljs-symbol {
  color: #d4d4d4;
}

/* Light theme adjustments */
.vscode-light .hljs-keyword {
  color: #0000ff;
}

.vscode-light .hljs-string {
  color: #a31515;
}

.vscode-light .hljs-comment {
  color: #008000;
}

.vscode-light .hljs-operator {
  color: #000000;
}

.vscode-light .hljs-symbol {
  color: #000000;
}

