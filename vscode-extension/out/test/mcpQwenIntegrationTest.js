"use strict";
/**
 * Test for MCP-Qwen integration
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.runMcpQwenIntegrationTest = runMcpQwenIntegrationTest;
exports.registerMcpQwenIntegrationTestCommand = registerMcpQwenIntegrationTestCommand;
const vscode = __importStar(require("vscode"));
const qwenApi_1 = require("../qwenApi");
const mcpClient_1 = require("../mcp/mcpClient");
const mcpQwenBridge_1 = require("../mcp/mcpQwenBridge");
const containerManager_1 = require("../containers/containerManager");
const configuration_1 = require("../configuration");
/**
 * Run the MCP-Qwen integration test
 */
async function runMcpQwenIntegrationTest() {
    // Create output channel
    const outputChannel = vscode.window.createOutputChannel('MCP-Qwen Integration Test');
    outputChannel.show();
    try {
        outputChannel.appendLine('Starting MCP-Qwen integration test...');
        // Get configuration
        const config = (0, configuration_1.getConfiguration)();
        outputChannel.appendLine(`Using API endpoint: ${config.apiEndpoint}`);
        // Create Qwen API client
        const qwenClient = new qwenApi_1.QwenApiClient(config);
        outputChannel.appendLine('Created Qwen API client');
        // Create container manager
        const containerManager = new containerManager_1.ContainerManager();
        outputChannel.appendLine('Created container manager');
        // Create MCP client
        const mcpClient = new mcpClient_1.McpClient(containerManager);
        await mcpClient.initialize();
        outputChannel.appendLine('Initialized MCP client');
        // Create MCP-Qwen bridge
        const mcpQwenBridge = new mcpQwenBridge_1.McpQwenBridge(qwenClient, mcpClient);
        outputChannel.appendLine('Created MCP-Qwen bridge');
        // Get available tools
        const tools = await mcpClient.getAllTools();
        outputChannel.appendLine(`Found ${tools.length} tools:`);
        tools.forEach(tool => {
            outputChannel.appendLine(`- ${tool.serverId}.${tool.tool.name}: ${tool.tool.description}`);
        });
        // Test message processing
        outputChannel.appendLine('\nTesting message processing...');
        const message = 'What files are in the current workspace?';
        // Process message
        const response = await mcpQwenBridge.processMessage(message, {
            systemPrompt: 'You are a helpful assistant that can use tools to answer questions.',
            thinkingMode: 'auto',
            gatherContext: true
        });
        outputChannel.appendLine('\nResponse:');
        outputChannel.appendLine(response);
        // Test streaming message processing
        outputChannel.appendLine('\nTesting streaming message processing...');
        const streamingMessage = 'What is the current git branch?';
        // Process message with streaming
        let streamingResponse = '';
        await mcpQwenBridge.processMessageStream(streamingMessage, {
            systemPrompt: 'You are a helpful assistant that can use tools to answer questions.',
            thinkingMode: 'auto',
            gatherContext: true
        }, (chunk, done) => {
            if (chunk) {
                outputChannel.append(chunk);
                streamingResponse += chunk;
            }
            if (done) {
                outputChannel.appendLine('\n\nStreaming complete');
            }
        });
        outputChannel.appendLine('\nTest completed successfully');
    }
    catch (error) {
        outputChannel.appendLine(`\nError: ${error}`);
    }
}
/**
 * Register the MCP-Qwen integration test command
 */
function registerMcpQwenIntegrationTestCommand(context) {
    const disposable = vscode.commands.registerCommand('qwen-coder-assistant.testMcpQwenIntegration', async () => {
        await runMcpQwenIntegrationTest();
    });
    context.subscriptions.push(disposable);
}
//# sourceMappingURL=mcpQwenIntegrationTest.js.map