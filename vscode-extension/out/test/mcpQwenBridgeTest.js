"use strict";
/**
 * Test file for MCP-Qwen Bridge
 *
 * This file contains a simple test for the MCP-Qwen Bridge.
 * It can be run manually to verify the implementation.
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
exports.runMcpQwenBridgeTest = runMcpQwenBridgeTest;
const vscode = __importStar(require("vscode"));
const configuration_1 = require("../configuration");
const containerManager_1 = require("../containers/containerManager");
const mcpClient_1 = require("../mcp/mcpClient");
const mcpQwenBridge_1 = require("../mcp/mcpQwenBridge");
const qwenApi_1 = require("../qwenApi");
/**
 * Run the test
 */
async function runMcpQwenBridgeTest() {
    try {
        // Get configuration
        const config = (0, configuration_1.getConfiguration)();
        // Create Qwen API client
        const qwenClient = new qwenApi_1.QwenApiClient(config);
        // Create container manager
        const containerManager = new containerManager_1.ContainerManager();
        // Create MCP client
        const mcpClient = new mcpClient_1.McpClient(containerManager);
        await mcpClient.initialize();
        // Create MCP-Qwen bridge
        const mcpQwenBridge = new mcpQwenBridge_1.McpQwenBridge(qwenClient, mcpClient);
        // Get available tools
        const tools = await mcpClient.getAllTools();
        console.log(`Found ${tools.length} tools`);
        // Process a test message
        if (tools.length > 0) {
            const response = await mcpQwenBridge.processMessage(`I need to use the following tools: ${tools.map(t => t.tool.name).join(', ')}. Please show me how to use them.`, {
                systemPrompt: 'You are a helpful assistant that can use MCP tools. When using tools, think step by step about what you need to do.',
                thinkingMode: 'auto',
                thinkingBudget: 1000
            });
            // Show the response
            vscode.window.showInformationMessage('Test completed successfully!');
            console.log('Response:', response);
            // Create output channel to show the response
            const outputChannel = vscode.window.createOutputChannel('MCP-Qwen Bridge Test');
            outputChannel.appendLine('Available Tools:');
            tools.forEach(tool => {
                outputChannel.appendLine(`- ${tool.serverId}.${tool.tool.name}: ${tool.tool.description}`);
            });
            outputChannel.appendLine('\nResponse:');
            outputChannel.appendLine(response);
            outputChannel.show();
        }
        else {
            console.log('No tools available for testing');
            vscode.window.showWarningMessage('No MCP tools available for testing. Please start some MCP servers first.');
        }
        // Clean up
        mcpQwenBridge.dispose();
        mcpClient.dispose();
    }
    catch (error) {
        console.error('Error running MCP-Qwen bridge test:', error);
    }
}
// Run the test if this file is executed directly
if (require.main === module) {
    runMcpQwenBridgeTest().then(() => {
        console.log('Test completed');
    });
}
//# sourceMappingURL=mcpQwenBridgeTest.js.map