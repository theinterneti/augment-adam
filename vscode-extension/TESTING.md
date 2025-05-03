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
