"use strict";
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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const agentCoordinator_1 = require("./agents/agentCoordinator");
const commands_1 = require("./commands");
const configuration_1 = require("./configuration");
const containerManager_1 = require("./containers/containerManager");
const contextProvider_1 = require("./contextProvider");
const conversationHistory_1 = require("./conversationHistory");
const mcpClient_1 = require("./mcp/mcpClient");
const mockQwenApi_1 = require("./mockQwenApi");
const qwenApi_1 = require("./qwenApi");
function activate(context) {
    console.log('Qwen Coder Assistant is now active!');
    // Initialize the API client
    const config = (0, configuration_1.getConfiguration)();
    // Use mock API client for development, real client for production
    const isDevelopment = process.env.NODE_ENV === 'development' || !config.apiKey;
    const apiClient = isDevelopment
        ? new mockQwenApi_1.MockQwenApiClient(config)
        : new qwenApi_1.QwenApiClient(config);
    // Add status bar item to show which API client is being used
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = isDevelopment ? '$(beaker) Qwen: Mock API' : '$(cloud) Qwen: Live API';
    statusBarItem.tooltip = isDevelopment
        ? 'Using Mock Qwen API (for development)'
        : 'Using Live Qwen API';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // Initialize the container manager
    const containerManager = new containerManager_1.ContainerManager();
    context.subscriptions.push(containerManager);
    // Initialize the MCP client
    const mcpClient = new mcpClient_1.MCPClient(containerManager);
    context.subscriptions.push(mcpClient);
    // Initialize the agent coordinator
    const agentCoordinator = new agentCoordinator_1.AgentCoordinator();
    context.subscriptions.push(agentCoordinator);
    // Register commands
    (0, commands_1.registerCommands)(context, apiClient, agentCoordinator, mcpClient);
    // Register conversation history view
    (0, conversationHistory_1.registerConversationHistoryView)(context);
    // Initialize the context engine
    (0, contextProvider_1.initializeContextEngine)().catch(error => {
        console.error('Error initializing context engine:', error);
    });
    // Initialize the container manager
    containerManager.initialize().catch(error => {
        console.error('Error initializing container manager:', error);
    });
    // Initialize the MCP client after container manager is initialized
    containerManager.initialize().then(() => {
        mcpClient.initialize().catch(error => {
            console.error('Error initializing MCP client:', error);
        });
    }).catch(() => {
        // Container manager initialization failed, but we can still proceed
    });
    // Register configuration change listener
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('qwen-coder-assistant')) {
            const newConfig = (0, configuration_1.getConfiguration)();
            const newIsDevelopment = process.env.NODE_ENV === 'development' || !newConfig.apiKey;
            // Update API client
            if (apiClient instanceof mockQwenApi_1.MockQwenApiClient) {
                apiClient.updateConfig(newConfig);
            }
            else if (apiClient instanceof qwenApi_1.QwenApiClient) {
                apiClient.updateConfig(newConfig);
            }
            // Update status bar
            statusBarItem.text = newIsDevelopment ? '$(beaker) Qwen: Mock API' : '$(cloud) Qwen: Live API';
            statusBarItem.tooltip = newIsDevelopment
                ? 'Using Mock Qwen API (for development)'
                : 'Using Live Qwen API';
        }
    }));
    // Register commands for container management
    context.subscriptions.push(vscode.commands.registerCommand('qwenCoder.showContainerStatus', () => {
        const containerStatus = containerManager.getContainerStatus();
        const statusItems = Object.entries(containerStatus).map(([name, info]) => ({
            label: `$(docker) ${name}`,
            description: info.status,
            detail: info.status === 'running' ? `URL: ${info.url}` : info.error || '',
            containerName: name,
            status: info.status
        }));
        vscode.window.showQuickPick(statusItems, {
            placeHolder: 'Select a container to manage',
            matchOnDescription: true,
            matchOnDetail: true
        }).then(selected => {
            if (selected) {
                if (selected.status === 'running') {
                    vscode.window.showQuickPick(['Stop', 'Restart', 'View Schema'], {
                        placeHolder: `Action for ${selected.containerName}`
                    }).then(action => {
                        if (action === 'Stop') {
                            containerManager.stopContainer(selected.containerName).catch(error => {
                                vscode.window.showErrorMessage(`Error stopping container: ${error.message}`);
                            });
                        }
                        else if (action === 'Restart') {
                            containerManager.stopContainer(selected.containerName)
                                .then(() => containerManager.startContainer(selected.containerName))
                                .catch(error => {
                                vscode.window.showErrorMessage(`Error restarting container: ${error.message}`);
                            });
                        }
                        else if (action === 'View Schema') {
                            mcpClient.fetchToolSchema(selected.containerName)
                                .then(schema => {
                                const schemaDoc = JSON.stringify(schema, null, 2);
                                vscode.workspace.openTextDocument({ content: schemaDoc, language: 'json' })
                                    .then(doc => vscode.window.showTextDocument(doc));
                            })
                                .catch(error => {
                                vscode.window.showErrorMessage(`Error fetching schema: ${error.message}`);
                            });
                        }
                    });
                }
                else {
                    vscode.window.showQuickPick(['Start', 'Remove'], {
                        placeHolder: `Action for ${selected.containerName}`
                    }).then(action => {
                        if (action === 'Start') {
                            containerManager.startContainer(selected.containerName).catch(error => {
                                vscode.window.showErrorMessage(`Error starting container: ${error.message}`);
                            });
                        }
                    });
                }
            }
        });
    }));
    // Register command for DevOps guidance
    context.subscriptions.push(vscode.commands.registerCommand('qwenCoder.devops', async () => {
        const request = await vscode.window.showInputBox({
            prompt: 'What DevOps task do you need help with?',
            placeHolder: 'e.g., Set up CI/CD pipeline, Create Docker container, Configure GitHub workflow'
        });
        if (request) {
            const panel = vscode.window.createWebviewPanel('qwenCoderDevOps', 'DevOps Guidance', vscode.ViewColumn.One, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            panel.webview.html = getLoadingWebviewContent();
            try {
                const response = await agentCoordinator.processRequest(request);
                panel.webview.html = getWebviewContent(request, response);
            }
            catch (error) {
                panel.webview.html = getErrorWebviewContent(request, error.message);
            }
        }
    }));
}
async function deactivate() {
    // Clean up resources when the extension is deactivated
    console.log('Qwen Coder Assistant is now deactivated!');
    // Dispose the context engine
    await (0, contextProvider_1.disposeContextEngine)();
}
// Helper functions for webview content
function getLoadingWebviewContent() {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Guidance</title>
    <style>
      body {
        font-family: var(--vscode-font-family);
        color: var(--vscode-editor-foreground);
        background-color: var(--vscode-editor-background);
        padding: 20px;
      }
      .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
      }
      .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid var(--vscode-button-background);
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    </style>
  </head>
  <body>
    <div class="loading">
      <div class="spinner"></div>
      <h2>Processing your request...</h2>
      <p>The hierarchical agent system is working on your DevOps task.</p>
    </div>
  </body>
  </html>`;
}
function getWebviewContent(request, response) {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Guidance</title>
    <style>
      body {
        font-family: var(--vscode-font-family);
        color: var(--vscode-editor-foreground);
        background-color: var(--vscode-editor-background);
        padding: 20px;
        line-height: 1.5;
      }
      h1, h2, h3, h4, h5, h6 {
        color: var(--vscode-editor-foreground);
      }
      pre {
        background-color: var(--vscode-textCodeBlock-background);
        padding: 16px;
        border-radius: 4px;
        overflow: auto;
      }
      code {
        font-family: var(--vscode-editor-font-family);
        font-size: var(--vscode-editor-font-size);
      }
      .request {
        background-color: var(--vscode-input-background);
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-left: 4px solid var(--vscode-activityBarBadge-background);
      }
    </style>
  </head>
  <body>
    <div class="request">
      <strong>Your request:</strong> ${request}
    </div>
    <div class="response">
      ${markdownToHtml(response)}
    </div>
  </body>
  </html>`;
}
function getErrorWebviewContent(request, errorMessage) {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Guidance - Error</title>
    <style>
      body {
        font-family: var(--vscode-font-family);
        color: var(--vscode-editor-foreground);
        background-color: var(--vscode-editor-background);
        padding: 20px;
      }
      .request {
        background-color: var(--vscode-input-background);
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-left: 4px solid var(--vscode-activityBarBadge-background);
      }
      .error {
        background-color: var(--vscode-inputValidation-errorBackground);
        color: var(--vscode-inputValidation-errorForeground);
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-left: 4px solid var(--vscode-errorForeground);
      }
    </style>
  </head>
  <body>
    <div class="request">
      <strong>Your request:</strong> ${request}
    </div>
    <div class="error">
      <strong>Error:</strong> ${errorMessage}
    </div>
    <p>Please try again with a more specific request or check the extension logs for more details.</p>
  </body>
  </html>`;
}
function markdownToHtml(markdown) {
    // This is a very simple markdown to HTML converter
    // In a real implementation, we would use a proper markdown parser
    // Replace headers
    let html = markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // Replace code blocks
    html = html.replace(/```([a-z]*)\n([\s\S]*?)\n```/gim, '<pre><code class="language-$1">$2</code></pre>');
    // Replace inline code
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');
    // Replace lists
    html = html.replace(/^\s*\*\s(.*$)/gim, '<ul><li>$1</li></ul>');
    html = html.replace(/^\s*\d+\.\s(.*$)/gim, '<ol><li>$1</li></ol>');
    // Replace paragraphs
    html = html.replace(/^\s*(\n)?([^\n]+)\n/gim, '<p>$2</p>');
    // Fix consecutive lists
    html = html.replace(/<\/ul>\s*<ul>/gim, '');
    html = html.replace(/<\/ol>\s*<ol>/gim, '');
    return html;
}
//# sourceMappingURL=extension.js.map