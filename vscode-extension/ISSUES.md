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
