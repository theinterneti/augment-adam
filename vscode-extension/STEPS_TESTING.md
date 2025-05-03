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
