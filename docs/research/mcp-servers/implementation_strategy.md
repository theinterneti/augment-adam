# Implementation Strategy for VS Code Extension

## Overview

This document outlines the implementation strategy for enhancing our VS Code extension to integrate with MCP servers and Qwen 3. The strategy focuses on leveraging the official MCP repositories and Qwen-Agent framework to create a seamless experience for users.

## Current Extension Architecture

Our current VS Code extension has the following components:

1. **MCP Client**: Handles communication with MCP servers
2. **MCP Server Manager**: Manages MCP server lifecycle
3. **Docker Container Manager**: Manages Docker containers for MCP servers
4. **GitHub Repository Manager**: Manages GitHub repositories for MCP servers
5. **UI Components**: Provides user interface for interacting with MCP servers

## Enhancement Strategy

Based on our research of the official MCP repositories and Qwen 3 integration requirements, we propose the following enhancement strategy:

### 1. MCP Server Management Enhancements

#### 1.1 Server Discovery and Installation

Implement a robust server discovery and installation mechanism:

```typescript
// server-discovery.ts
import * as vscode from 'vscode';
import * as axios from 'axios';

export class ServerDiscovery {
  private readonly REGISTRY_URL = 'https://api.mcp-registry.com/servers';

  /**
   * Discover available MCP servers from the registry
   */
  public async discoverServers(): Promise<ServerInfo[]> {
    try {
      const response = await axios.get(this.REGISTRY_URL);
      return response.data.servers;
    } catch (error) {
      vscode.window.showErrorMessage(`Error discovering servers: ${error}`);
      return [];
    }
  }

  /**
   * Install an MCP server
   */
  public async installServer(server: ServerInfo): Promise<boolean> {
    // Implementation details
  }
}
```

#### 1.2 Server Configuration Management

Enhance the server configuration management:

```typescript
// server-config-manager.ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class ServerConfigManager {
  private readonly CONFIG_FILE = 'mcp-servers.json';
  private readonly CONFIG_DIR: string;

  constructor(storagePath: string) {
    this.CONFIG_DIR = storagePath;
    this.ensureConfigDir();
  }

  /**
   * Ensure the configuration directory exists
   */
  private ensureConfigDir(): void {
    if (!fs.existsSync(this.CONFIG_DIR)) {
      fs.mkdirSync(this.CONFIG_DIR, { recursive: true });
    }
  }

  /**
   * Get the server configuration
   */
  public getConfig(): ServerConfig {
    const configPath = path.join(this.CONFIG_DIR, this.CONFIG_FILE);
    if (!fs.existsSync(configPath)) {
      return { servers: [] };
    }

    try {
      const configData = fs.readFileSync(configPath, 'utf8');
      return JSON.parse(configData);
    } catch (error) {
      vscode.window.showErrorMessage(`Error reading config: ${error}`);
      return { servers: [] };
    }
  }

  /**
   * Save the server configuration
   */
  public saveConfig(config: ServerConfig): void {
    const configPath = path.join(this.CONFIG_DIR, this.CONFIG_FILE);
    try {
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
    } catch (error) {
      vscode.window.showErrorMessage(`Error saving config: ${error}`);
    }
  }
}
```

#### 1.3 Server Health Monitoring

Implement server health monitoring:

```typescript
// server-health-monitor.ts
import * as vscode from 'vscode';
import * as axios from 'axios';

export class ServerHealthMonitor {
  private servers: Map<string, ServerHealth> = new Map();
  private intervalId: NodeJS.Timeout | undefined;

  /**
   * Start monitoring server health
   */
  public start(servers: ServerInfo[]): void {
    this.servers.clear();
    servers.forEach(server => {
      this.servers.set(server.id, { status: 'unknown', lastChecked: new Date() });
    });

    this.intervalId = setInterval(() => this.checkHealth(), 60000);
  }

  /**
   * Stop monitoring server health
   */
  public stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  /**
   * Check the health of all servers
   */
  private async checkHealth(): Promise<void> {
    for (const [id, health] of this.servers.entries()) {
      try {
        const server = await this.getServerInfo(id);
        if (!server || !server.endpoint) {
          continue;
        }

        const response = await axios.get(`${server.endpoint}/health`);
        this.servers.set(id, {
          status: response.status === 200 ? 'healthy' : 'unhealthy',
          lastChecked: new Date()
        });
      } catch (error) {
        this.servers.set(id, {
          status: 'unhealthy',
          lastChecked: new Date(),
          error: `${error}`
        });
      }
    }
  }

  /**
   * Get server health information
   */
  public getServerHealth(id: string): ServerHealth | undefined {
    return this.servers.get(id);
  }

  /**
   * Get server information
   */
  private async getServerInfo(id: string): Promise<ServerInfo | undefined> {
    // Implementation details
    return undefined;
  }
}
```

### 2. Qwen Integration

#### 2.1 Qwen API Client

Implement a client for the Qwen API:

```typescript
// qwen-api-client.ts
import * as vscode from 'vscode';
import * as axios from 'axios';
import { getConfiguration } from './configuration';

export class QwenApiClient {
  private readonly apiEndpoint: string;
  private readonly apiKey: string;

  constructor() {
    const config = getConfiguration();
    this.apiEndpoint = config.apiEndpoint;
    this.apiKey = config.apiKey;
  }

  /**
   * Generate a response from Qwen
   */
  public async generateResponse(
    messages: ChatMessage[],
    options: GenerationOptions = {}
  ): Promise<ChatResponse> {
    try {
      const response = await axios.post(
        `${this.apiEndpoint}/chat/completions`,
        {
          model: options.model || 'Qwen3-30B-A3B',
          messages,
          temperature: options.temperature || 0.7,
          max_tokens: options.maxTokens || 1000,
          enable_thinking: options.enableThinking !== false,
          tools: options.tools || []
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      );

      return response.data;
    } catch (error) {
      vscode.window.showErrorMessage(`Error generating response: ${error}`);
      throw error;
    }
  }
}
```

#### 2.2 MCP-Qwen Bridge

Implement a bridge between MCP and Qwen:

```typescript
// mcp-qwen-bridge.ts
import * as vscode from 'vscode';
import { QwenApiClient } from './qwen-api-client';
import { McpClient } from './mcp-client/mcpClient';

export class McpQwenBridge {
  private qwenClient: QwenApiClient;
  private mcpClient: McpClient;

  constructor(qwenClient: QwenApiClient, mcpClient: McpClient) {
    this.qwenClient = qwenClient;
    this.mcpClient = mcpClient;
  }

  /**
   * Process a user message
   */
  public async processMessage(message: string): Promise<string> {
    try {
      // Get available tools
      const tools = await this.mcpClient.getAllTools();

      // Convert MCP tools to Qwen tool format
      const qwenTools = tools.map(tool => this.convertToolToQwenFormat(tool));

      // Generate response from Qwen
      const response = await this.qwenClient.generateResponse(
        [{ role: 'user', content: message }],
        { tools: qwenTools }
      );

      // Process tool calls
      if (response.tool_calls && response.tool_calls.length > 0) {
        return await this.processToolCalls(response.tool_calls);
      }

      return response.content;
    } catch (error) {
      vscode.window.showErrorMessage(`Error processing message: ${error}`);
      return `Error: ${error}`;
    }
  }

  /**
   * Convert MCP tool to Qwen tool format
   */
  private convertToolToQwenFormat(tool: { serverId: string; tool: McpTool }): any {
    // Implementation details
    return {
      type: 'function',
      function: {
        name: `${tool.serverId}.${tool.tool.name}`,
        description: tool.tool.description,
        parameters: {
          type: 'object',
          properties: tool.tool.parameters.reduce((acc, param) => {
            acc[param.name] = {
              type: param.type,
              description: param.description
            };
            return acc;
          }, {}),
          required: tool.tool.parameters
            .filter(param => param.required)
            .map(param => param.name)
        }
      }
    };
  }

  /**
   * Process tool calls
   */
  private async processToolCalls(toolCalls: any[]): Promise<string> {
    const results = [];

    for (const toolCall of toolCalls) {
      try {
        const [serverId, toolName] = toolCall.function.name.split('.');
        const args = JSON.parse(toolCall.function.arguments);

        const result = await this.mcpClient.invokeTool(serverId, toolName, args);
        results.push(`Tool: ${toolCall.function.name}\nResult: ${JSON.stringify(result)}`);
      } catch (error) {
        results.push(`Tool: ${toolCall.function.name}\nError: ${error}`);
      }
    }

    return results.join('\n\n');
  }
}
```

#### 2.3 Hierarchical Agent System

Implement a hierarchical agent system:

```typescript
// agent-system.ts
import * as vscode from 'vscode';
import { QwenApiClient } from './qwen-api-client';
import { McpClient } from './mcp-client/mcpClient';

export class AgentSystem {
  private qwenClient: QwenApiClient;
  private mcpClient: McpClient;

  constructor(qwenClient: QwenApiClient, mcpClient: McpClient) {
    this.qwenClient = qwenClient;
    this.mcpClient = mcpClient;
  }

  /**
   * Process a task
   */
  public async processTask(task: string): Promise<string> {
    try {
      // Analyze the task
      const taskAnalysis = await this.analyzeTask(task);

      // Select the appropriate agent
      const agent = this.selectAgent(taskAnalysis);

      // Execute the task with the selected agent
      return await agent.executeTask(task);
    } catch (error) {
      vscode.window.showErrorMessage(`Error processing task: ${error}`);
      return `Error: ${error}`;
    }
  }

  /**
   * Analyze a task
   */
  private async analyzeTask(task: string): Promise<TaskAnalysis> {
    // Implementation details
    return {
      complexity: 'medium',
      domain: 'development',
      subtasks: []
    };
  }

  /**
   * Select an agent based on task analysis
   */
  private selectAgent(analysis: TaskAnalysis): Agent {
    switch (analysis.domain) {
      case 'development':
        return new DevelopmentAgent(this.qwenClient, this.mcpClient);
      case 'testing':
        return new TestingAgent(this.qwenClient, this.mcpClient);
      case 'cicd':
        return new CiCdAgent(this.qwenClient, this.mcpClient);
      case 'github':
        return new GitHubAgent(this.qwenClient, this.mcpClient);
      default:
        return new GeneralAgent(this.qwenClient, this.mcpClient);
    }
  }
}

/**
 * Base agent class
 */
abstract class Agent {
  protected qwenClient: QwenApiClient;
  protected mcpClient: McpClient;

  constructor(qwenClient: QwenApiClient, mcpClient: McpClient) {
    this.qwenClient = qwenClient;
    this.mcpClient = mcpClient;
  }

  /**
   * Execute a task
   */
  public abstract executeTask(task: string): Promise<string>;
}

/**
 * Development agent
 */
class DevelopmentAgent extends Agent {
  /**
   * Execute a development task
   */
  public async executeTask(task: string): Promise<string> {
    // Implementation details
    return '';
  }
}

// Other agent implementations...
```

### 3. User Interface Enhancements

#### 3.1 Chat Interface

Implement a chat interface for interacting with Qwen:

```typescript
// chat-panel.ts
import * as vscode from 'vscode';
import { McpQwenBridge } from './mcp-qwen-bridge';

export class ChatPanel {
  public static readonly viewType = 'qwenChat';

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private readonly _bridge: McpQwenBridge;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, bridge: McpQwenBridge) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._bridge = bridge;

    this._update();

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    this._panel.webview.onDidReceiveMessage(
      async message => {
        switch (message.command) {
          case 'sendMessage':
            const response = await this._bridge.processMessage(message.text);
            this._panel.webview.postMessage({ command: 'receiveMessage', text: response });
            return;
        }
      },
      null,
      this._disposables
    );
  }

  /**
   * Create a new chat panel
   */
  public static createOrShow(extensionUri: vscode.Uri, bridge: McpQwenBridge): ChatPanel {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it
    if (ChatPanel.currentPanel) {
      ChatPanel.currentPanel._panel.reveal(column);
      return ChatPanel.currentPanel;
    }

    // Otherwise, create a new panel
    const panel = vscode.window.createWebviewPanel(
      ChatPanel.viewType,
      'Qwen Chat',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
      }
    );

    ChatPanel.currentPanel = new ChatPanel(panel, extensionUri, bridge);
    return ChatPanel.currentPanel;
  }

  private static currentPanel: ChatPanel | undefined;

  /**
   * Update the webview content
   */
  private _update() {
    const webview = this._panel.webview;
    this._panel.title = 'Qwen Chat';
    this._panel.webview.html = this._getHtmlForWebview(webview);
  }

  /**
   * Get the HTML for the webview
   */
  private _getHtmlForWebview(webview: vscode.Webview): string {
    // Implementation details
    return '';
  }

  /**
   * Dispose of the panel
   */
  public dispose() {
    ChatPanel.currentPanel = undefined;

    this._panel.dispose();

    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }
}
```

#### 3.2 Server Management UI

Enhance the server management UI:

```typescript
// server-management-view.ts
import * as vscode from 'vscode';
import { McpServerManager } from './mcp-client/mcpServerManager';
import { ServerHealthMonitor } from './server-health-monitor';

export class ServerManagementView {
  private readonly _view: vscode.TreeView<ServerTreeItem>;
  private readonly _treeDataProvider: ServerTreeDataProvider;

  constructor(
    context: vscode.ExtensionContext,
    serverManager: McpServerManager,
    healthMonitor: ServerHealthMonitor
  ) {
    this._treeDataProvider = new ServerTreeDataProvider(serverManager, healthMonitor);
    this._view = vscode.window.createTreeView('qwenMcpServers', {
      treeDataProvider: this._treeDataProvider,
      showCollapseAll: true
    });

    context.subscriptions.push(this._view);

    // Register commands
    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.refreshServers', () => {
        this._treeDataProvider.refresh();
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.addServer', async () => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.removeServer', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.startServer', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.stopServer', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.restartServer', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.viewServerLogs', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand('qwen-coder-assistant.viewServerSchema', async (item: ServerTreeItem) => {
        // Implementation details
      })
    );
  }

  /**
   * Refresh the view
   */
  public refresh(): void {
    this._treeDataProvider.refresh();
  }
}

/**
 * Tree data provider for MCP servers
 */
class ServerTreeDataProvider implements vscode.TreeDataProvider<ServerTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<ServerTreeItem | undefined>();
  public readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(
    private readonly serverManager: McpServerManager,
    private readonly healthMonitor: ServerHealthMonitor
  ) {
    // Listen for server changes
    serverManager.onDidChangeServers(() => {
      this._onDidChangeTreeData.fire(undefined);
    });
  }

  /**
   * Get the tree item for an element
   */
  public getTreeItem(element: ServerTreeItem): vscode.TreeItem {
    return element;
  }

  /**
   * Get the children of an element
   */
  public getChildren(element?: ServerTreeItem): Thenable<ServerTreeItem[]> {
    if (!element) {
      // Root level - show all servers
      const servers = this.serverManager.getServers();
      return Promise.resolve(
        servers.map(server => {
          const health = this.healthMonitor.getServerHealth(server.id);
          return new ServerTreeItem(server, health);
        })
      );
    }

    // No children for server items
    return Promise.resolve([]);
  }

  /**
   * Refresh the tree
   */
  public refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }
}

/**
 * Tree item for an MCP server
 */
class ServerTreeItem extends vscode.TreeItem {
  constructor(
    public readonly server: McpServer,
    public readonly health?: ServerHealth
  ) {
    super(server.name, vscode.TreeItemCollapsibleState.None);

    // Set the context value for context menu filtering
    this.contextValue = `mcpServer-${server.status}`;

    // Set the description
    this.description = `${server.status}${health ? ` (${health.status})` : ''}`;

    // Set the tooltip
    this.tooltip = `${server.name} (${server.status})
${server.description}
Repository: ${server.repoUrl}
Version: ${server.version}
${health ? `Health: ${health.status}
Last checked: ${health.lastChecked.toLocaleString()}` : ''}`;

    // Set the icon
    this.iconPath = this.getIconPath(server.status, health?.status);
  }

  /**
   * Get the icon path for a server status
   */
  private getIconPath(status: McpServerStatus, healthStatus?: string): vscode.ThemeIcon {
    if (healthStatus === 'unhealthy') {
      return new vscode.ThemeIcon('warning');
    }

    switch (status) {
      case McpServerStatus.Running:
        return new vscode.ThemeIcon('play');
      case McpServerStatus.Stopped:
        return new vscode.ThemeIcon('stop');
      case McpServerStatus.Starting:
        return new vscode.ThemeIcon('sync');
      case McpServerStatus.Stopping:
        return new vscode.ThemeIcon('sync');
      case McpServerStatus.Error:
        return new vscode.ThemeIcon('error');
      default:
        return new vscode.ThemeIcon('question');
    }
  }
}
```

### 4. Extension Activation

Update the extension activation to initialize all components:

```typescript
// extension.ts
import * as vscode from 'vscode';
import { QwenCoderConfig, registerConfigurationListener } from './configuration';
import { McpClient } from './mcp-client/mcpClient';
import { McpServerManager } from './mcp-client/mcpServerManager';
import { ServerHealthMonitor } from './server-health-monitor';
import { ServerManagementView } from './server-management-view';
import { QwenApiClient } from './qwen-api-client';
import { McpQwenBridge } from './mcp-qwen-bridge';
import { AgentSystem } from './agent-system';
import { ChatPanel } from './chat-panel';

// Global state
let mcpServerManager: McpServerManager | undefined;
let mcpClient: McpClient | undefined;
let serverHealthMonitor: ServerHealthMonitor | undefined;
let qwenApiClient: QwenApiClient | undefined;
let mcpQwenBridge: McpQwenBridge | undefined;
let agentSystem: AgentSystem | undefined;

/**
 * Activate the extension
 */
export async function activate(context: vscode.ExtensionContext) {
  console.log('Qwen Coder Assistant is now active!');

  // Initialize the MCP server manager
  mcpServerManager = new McpServerManager();

  // Initialize the MCP client
  mcpClient = new McpClient(mcpServerManager);

  // Initialize the server health monitor
  serverHealthMonitor = new ServerHealthMonitor();
  serverHealthMonitor.start(mcpServerManager.getServers());

  // Initialize the server management view
  const serverManagementView = new ServerManagementView(
    context,
    mcpServerManager,
    serverHealthMonitor
  );

  // Initialize the Qwen API client
  qwenApiClient = new QwenApiClient();

  // Initialize the MCP-Qwen bridge
  mcpQwenBridge = new McpQwenBridge(qwenApiClient, mcpClient);

  // Initialize the agent system
  agentSystem = new AgentSystem(qwenApiClient, mcpClient);

  // Register commands
  registerCommands(context);

  // Listen for configuration changes
  context.subscriptions.push(
    registerConfigurationListener(handleConfigurationChange)
  );

  // Start auto-start servers
  await mcpServerManager.startAutoStartServers();
}

/**
 * Register commands
 */
function registerCommands(context: vscode.ExtensionContext) {
  // Register the askQwen command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.askQwen', () => {
      if (mcpQwenBridge) {
        ChatPanel.createOrShow(context.extensionUri, mcpQwenBridge);
      }
    })
  );

  // Register the explainCode command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.explainCode', async () => {
      // Implementation details
    })
  );

  // Register the generateCode command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.generateCode', async () => {
      // Implementation details
    })
  );

  // Register the addMcpRepo command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.addMcpRepo', async () => {
      // Implementation details
    })
  );

  // Register the manageMcpServers command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.manageMcpServers', () => {
      vscode.commands.executeCommand('qwenMcpServers.focus');
    })
  );

  // Additional commands...
}

/**
 * Handle configuration changes
 */
function handleConfigurationChange(config: QwenCoderConfig) {
  console.log('Configuration changed:', config);

  // Update Qwen API client
  if (qwenApiClient) {
    qwenApiClient = new QwenApiClient();
  }

  // Update MCP-Qwen bridge
  if (mcpQwenBridge && qwenApiClient && mcpClient) {
    mcpQwenBridge = new McpQwenBridge(qwenApiClient, mcpClient);
  }

  // Update agent system
  if (agentSystem && qwenApiClient && mcpClient) {
    agentSystem = new AgentSystem(qwenApiClient, mcpClient);
  }
}

/**
 * Deactivate the extension
 */
export async function deactivate() {
  // Clean up resources when the extension is deactivated
  console.log('Qwen Coder Assistant is now deactivated!');

  // Stop the server health monitor
  if (serverHealthMonitor) {
    serverHealthMonitor.stop();
    serverHealthMonitor = undefined;
  }

  // Dispose the MCP server manager
  if (mcpServerManager) {
    mcpServerManager.dispose();
    mcpServerManager = undefined;
  }

  // Dispose the MCP client
  if (mcpClient) {
    mcpClient.dispose();
    mcpClient = undefined;
  }
}
```

## Implementation Timeline

We propose the following implementation timeline:

### Phase 1: MCP Server Management Enhancements (2 weeks)

1. Implement server discovery and installation
2. Enhance server configuration management
3. Implement server health monitoring
4. Update the server management UI

### Phase 2: Qwen Integration (2 weeks)

1. Implement Qwen API client
2. Implement MCP-Qwen bridge
3. Implement hierarchical agent system
4. Create chat interface

### Phase 3: Testing and Refinement (1 week)

1. Write unit tests
2. Perform integration testing
3. Refine the user interface
4. Update documentation

## Conclusion

This implementation strategy provides a comprehensive approach to enhancing our VS Code extension with MCP server integration and Qwen 3 capabilities. By leveraging the official MCP repositories and Qwen-Agent framework, we can create a seamless experience for users, enabling them to interact with a wide range of tools and data sources through natural language.

The strategy focuses on:

1. Robust MCP server management
2. Seamless Qwen integration
3. Intuitive user interface
4. Hierarchical agent system

By following this strategy, we can create a powerful VS Code extension that leverages the best of MCP and Qwen technologies.
