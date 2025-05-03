/**
 * Test file for MCP-Qwen Bridge
 *
 * This file contains a simple test for the MCP-Qwen Bridge.
 * It can be run manually to verify the implementation.
 */

import * as vscode from 'vscode';
import { getConfiguration } from '../configuration';
import { ContainerManager } from '../containers/containerManager';
import { McpClient } from '../mcp/mcpClient';
import { McpQwenBridge } from '../mcp/mcpQwenBridge';
import { QwenApiClient } from '../qwenApi';

/**
 * Run the test
 */
export async function runMcpQwenBridgeTest(): Promise<void> {
  try {
    // Get configuration
    const config = getConfiguration();

    // Create Qwen API client
    const qwenClient = new QwenApiClient(config);

    // Create container manager
    const containerManager = new ContainerManager();

    // Create MCP client
    const mcpClient = new McpClient(containerManager);
    await mcpClient.initialize();

    // Create MCP-Qwen bridge
    const mcpQwenBridge = new McpQwenBridge(qwenClient, mcpClient);

    // Get available tools
    const tools = await mcpClient.getAllTools();
    console.log(`Found ${tools.length} tools`);

    // Process a test message
    if (tools.length > 0) {
      const response = await mcpQwenBridge.processMessage(
        `I need to use the following tools: ${tools.map(t => t.tool.name).join(', ')}. Please show me how to use them.`,
        {
          systemPrompt: 'You are a helpful assistant that can use MCP tools. When using tools, think step by step about what you need to do.',
          thinkingMode: 'auto',
          thinkingBudget: 1000
        }
      );

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
    } else {
      console.log('No tools available for testing');
      vscode.window.showWarningMessage('No MCP tools available for testing. Please start some MCP servers first.');
    }

    // Clean up
    mcpQwenBridge.dispose();
    mcpClient.dispose();
  } catch (error) {
    console.error('Error running MCP-Qwen bridge test:', error);
  }
}

// Run the test if this file is executed directly
if (require.main === module) {
  runMcpQwenBridgeTest().then(() => {
    console.log('Test completed');
  });
}
