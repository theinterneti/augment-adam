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
