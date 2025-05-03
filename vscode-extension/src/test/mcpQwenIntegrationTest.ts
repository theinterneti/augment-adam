/**
 * Test for MCP-Qwen integration
 */

import * as vscode from 'vscode';
import { QwenApiClient } from '../qwenApi';
import { McpClient } from '../mcp/mcpClient';
import { McpQwenBridge } from '../mcp/mcpQwenBridge';
import { ContainerManager } from '../containers/containerManager';
import { getConfiguration } from '../configuration';

/**
 * Run the MCP-Qwen integration test
 */
export async function runMcpQwenIntegrationTest(): Promise<void> {
  // Create output channel
  const outputChannel = vscode.window.createOutputChannel('MCP-Qwen Integration Test');
  outputChannel.show();
  
  try {
    outputChannel.appendLine('Starting MCP-Qwen integration test...');
    
    // Get configuration
    const config = getConfiguration();
    outputChannel.appendLine(`Using API endpoint: ${config.apiEndpoint}`);
    
    // Create Qwen API client
    const qwenClient = new QwenApiClient(config);
    outputChannel.appendLine('Created Qwen API client');
    
    // Create container manager
    const containerManager = new ContainerManager();
    outputChannel.appendLine('Created container manager');
    
    // Create MCP client
    const mcpClient = new McpClient(containerManager);
    await mcpClient.initialize();
    outputChannel.appendLine('Initialized MCP client');
    
    // Create MCP-Qwen bridge
    const mcpQwenBridge = new McpQwenBridge(qwenClient, mcpClient);
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
    await mcpQwenBridge.processMessageStream(
      streamingMessage,
      {
        systemPrompt: 'You are a helpful assistant that can use tools to answer questions.',
        thinkingMode: 'auto',
        gatherContext: true
      },
      (chunk, done) => {
        if (chunk) {
          outputChannel.append(chunk);
          streamingResponse += chunk;
        }
        
        if (done) {
          outputChannel.appendLine('\n\nStreaming complete');
        }
      }
    );
    
    outputChannel.appendLine('\nTest completed successfully');
  } catch (error) {
    outputChannel.appendLine(`\nError: ${error}`);
  }
}

/**
 * Register the MCP-Qwen integration test command
 */
export function registerMcpQwenIntegrationTestCommand(context: vscode.ExtensionContext): void {
  const disposable = vscode.commands.registerCommand('qwen-coder-assistant.testMcpQwenIntegration', async () => {
    await runMcpQwenIntegrationTest();
  });
  
  context.subscriptions.push(disposable);
}
