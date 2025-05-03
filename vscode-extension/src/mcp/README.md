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
