import * as vscode from 'vscode';
import { AgentCoordinator } from './agents/agentCoordinator';
import { getConfiguration, QwenCoderConfig, registerConfigurationListener, verifyConfiguration } from './configuration';
import { AuthManager } from './mcp-client/authentication/authManager';
import { McpClient } from './mcp-client/mcpClient';
import { McpServerManager } from './mcp-client/mcpServerManager';
import { OfficialMcpServersManager } from './mcp-client/officialMcpServers';
import { ServerHealthMonitor } from './mcp-client/serverHealthMonitor';
import { QwenApiClient } from './qwenApi';
import { McpServerTreeDataProvider, McpServerTreeItem } from './ui/mcpServerTreeDataProvider';

// Global state
let mcpServerManager: McpServerManager | undefined;
let mcpClient: McpClient | undefined;
let mcpServerTreeDataProvider: McpServerTreeDataProvider | undefined;
let qwenApiClient: QwenApiClient | undefined;
let agentCoordinator: AgentCoordinator | undefined;
let serverHealthMonitor: ServerHealthMonitor | undefined;
let officialMcpServersManager: OfficialMcpServersManager | undefined;
let authManager: AuthManager | undefined;

/**
 * Activate the extension
 * @param context Extension context
 */
export async function activate(context: vscode.ExtensionContext) {
  console.log('Qwen Coder Assistant is now active!');

  // Get configuration
  const config = getConfiguration();

  // Initialize the MCP server manager
  mcpServerManager = new McpServerManager();

  // Initialize the authentication manager
  authManager = new AuthManager(context);
  context.subscriptions.push(authManager);

  // Initialize the MCP client
  mcpClient = new McpClient(mcpServerManager, authManager);

  // Initialize the server health monitor
  serverHealthMonitor = new ServerHealthMonitor(mcpServerManager);
  context.subscriptions.push(serverHealthMonitor);

  // Initialize the official MCP servers manager
  officialMcpServersManager = new OfficialMcpServersManager(mcpServerManager);

  // Initialize the MCP server tree data provider
  mcpServerTreeDataProvider = new McpServerTreeDataProvider(mcpServerManager, serverHealthMonitor);

  // Register the MCP server tree data provider
  vscode.window.registerTreeDataProvider('qwenMcpServers', mcpServerTreeDataProvider);

  // Initialize the Qwen API client
  qwenApiClient = new QwenApiClient(config);

  // Initialize the agent coordinator
  agentCoordinator = new AgentCoordinator(qwenApiClient, mcpClient, config);

  // Register commands
  registerCommands(context);

  // Listen for configuration changes
  context.subscriptions.push(
    registerConfigurationListener(handleConfigurationChange)
  );

  // Start the server health monitor
  serverHealthMonitor.start();

  // Start auto-start servers
  await mcpServerManager.startAutoStartServers();
}

/**
 * Register commands
 * @param context Extension context
 */
function registerCommands(context: vscode.ExtensionContext) {
  // Register the askQwen command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.askQwen', askQwen)
  );

  // Register the explainCode command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.explainCode', explainCode)
  );

  // Register the generateCode command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.generateCode', generateCode)
  );

  // Register the addMcpRepo command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.addMcpRepo', addMcpRepo)
  );

  // Register the manageMcpServers command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.manageMcpServers', manageMcpServers)
  );

  // Register the startMcpServer command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.startMcpServer', startMcpServer)
  );

  // Register the stopMcpServer command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.stopMcpServer', stopMcpServer)
  );

  // Register the restartMcpServer command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.restartMcpServer', restartMcpServer)
  );

  // Register the viewMcpServerLogs command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.viewMcpServerLogs', viewMcpServerLogs)
  );

  // Register the viewMcpServerSchema command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.viewMcpServerSchema', viewMcpServerSchema)
  );

  // Register the refreshMcpServers command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.refreshMcpServers', refreshMcpServers)
  );

  // Register the testApiConnection command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.testApiConnection', testApiConnection)
  );

  // Register the verifyConfiguration command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.verifyConfiguration', verifyExtensionConfiguration)
  );

  // Register the testMcpTool command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.testMcpTool', testMcpTool)
  );

  // Register the testMcpQwenBridge command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.testMcpQwenBridge', async () => {
      try {
        // Import the test module
        const { runMcpQwenBridgeTest } = await import('./test/mcpQwenBridgeTest');

        // Run the test
        await runMcpQwenBridgeTest();

        // Show success message
        vscode.window.showInformationMessage('MCP-Qwen bridge test completed. Check the console for results.');
      } catch (error) {
        vscode.window.showErrorMessage(`Error testing MCP-Qwen bridge: ${error}`);
      }
    })
  );

  // Register the testMcpQwenIntegration command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.testMcpQwenIntegration', async () => {
      try {
        // Import the test module
        const { runMcpQwenIntegrationTest } = await import('./test/mcpQwenIntegrationTest');

        // Run the test
        await runMcpQwenIntegrationTest();

        // Show success message
        vscode.window.showInformationMessage('MCP-Qwen integration test completed. Check the output channel for results.');
      } catch (error) {
        vscode.window.showErrorMessage(`Error testing MCP-Qwen integration: ${error}`);
      }
    })
  );

  // Register the configureMcpServer command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.configureMcpServer', (item?: McpServerTreeItem) => {
      try {
        if (!mcpServerManager || !officialMcpServersManager || !serverHealthMonitor) {
          throw new Error('MCP server manager, official servers manager, or health monitor not initialized');
        }

        // Get the server ID from the tree item
        const serverId = item?.server.id;

        // Create the configuration view
        McpServerConfigView.createOrShow(
          context.extensionUri,
          mcpServerManager,
          officialMcpServersManager,
          serverHealthMonitor,
          serverId
        );
      } catch (error) {
        vscode.window.showErrorMessage(`Error configuring MCP server: ${error}`);
      }
    })
  );

  // Register the addOfficialMcpServer command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.addOfficialMcpServer', async () => {
      try {
        if (!officialMcpServersManager) {
          throw new Error('Official MCP servers manager not initialized');
        }

        // Show a quick pick to select a server type
        const serverTypes = [
          { label: 'GitHub MCP Server', value: 'GITHUB' },
          { label: 'Docker MCP Server', value: 'DOCKER' },
          { label: 'Git MCP Server', value: 'GIT' },
          { label: 'Memory MCP Server', value: 'MEMORY' },
          { label: 'Filesystem MCP Server', value: 'FILESYSTEM' },
          { label: 'All Official MCP Servers', value: 'ALL' }
        ];

        const selectedType = await vscode.window.showQuickPick(serverTypes, {
          placeHolder: 'Select an official MCP server to add',
          title: 'Add Official MCP Server'
        });

        if (!selectedType) {
          return;
        }

        // Show a progress notification
        vscode.window.withProgress({
          location: vscode.ProgressLocation.Notification,
          title: `Adding ${selectedType.label}...`,
          cancellable: false
        }, async () => {
          try {
            if (selectedType.value === 'ALL') {
              const serverIds = await officialMcpServersManager.addAllOfficialServers();
              vscode.window.showInformationMessage(`Added ${serverIds.length} official MCP servers`);
            } else {
              let serverId: string;

              switch (selectedType.value) {
                case 'GITHUB':
                  serverId = await officialMcpServersManager.addGitHubServer();
                  break;
                case 'DOCKER':
                  serverId = await officialMcpServersManager.addDockerServer();
                  break;
                case 'GIT':
                  serverId = await officialMcpServersManager.addGitServer();
                  break;
                case 'MEMORY':
                  serverId = await officialMcpServersManager.addMemoryServer();
                  break;
                case 'FILESYSTEM':
                  serverId = await officialMcpServersManager.addFilesystemServer();
                  break;
                default:
                  throw new Error(`Unknown server type: ${selectedType.value}`);
              }

              vscode.window.showInformationMessage(`Added ${selectedType.label}`);
            }
          } catch (error) {
            vscode.window.showErrorMessage(`Error adding official MCP server: ${error}`);
          }
        });
      } catch (error) {
        vscode.window.showErrorMessage(`Error adding official MCP server: ${error}`);
      }
    })
  );

  // Register the checkMcpServerHealth command
  context.subscriptions.push(
    vscode.commands.registerCommand('qwen-coder-assistant.checkMcpServerHealth', async (item?: McpServerTreeItem) => {
      try {
        if (!serverHealthMonitor) {
          throw new Error('Server health monitor not initialized');
        }

        // If no item is provided, check all servers
        if (!item) {
          // Show a progress notification
          vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Checking all MCP servers health...',
            cancellable: false
          }, async () => {
            try {
              await serverHealthMonitor.checkAllServersHealth();
              vscode.window.showInformationMessage('All MCP servers health checked');
            } catch (error) {
              vscode.window.showErrorMessage(`Error checking MCP servers health: ${error}`);
            }
          });
          return;
        }

        // Check the health of the selected server
        const serverId = item.server.id;

        // Show a progress notification
        vscode.window.withProgress({
          location: vscode.ProgressLocation.Notification,
          title: `Checking MCP server health: ${item.server.name}...`,
          cancellable: false
        }, async () => {
          try {
            await serverHealthMonitor.checkServerHealth(serverId);
            const server = mcpServerManager?.getServer(serverId);
            if (server) {
              vscode.window.showInformationMessage(`MCP server ${server.name} health: ${server.healthStatus || 'unknown'}`);
            }
          } catch (error) {
            vscode.window.showErrorMessage(`Error checking MCP server health: ${error}`);
          }
        });
      } catch (error) {
        vscode.window.showErrorMessage(`Error checking MCP server health: ${error}`);
      }
    })
  );
}

/**
 * Handle configuration changes
 * @param config New configuration
 */
function handleConfigurationChange(config: QwenCoderConfig) {
  console.log('Configuration changed:', config);

  // Update the Qwen API client
  if (qwenApiClient) {
    qwenApiClient.updateConfig(config);
  }

  // Update the agent coordinator
  if (agentCoordinator) {
    agentCoordinator.updateConfig(config);
  }
}

/**
 * Ask Qwen
 */
async function askQwen() {
  // Get the input from the user
  const input = await vscode.window.showInputBox({
    prompt: 'What would you like to ask Qwen?',
    placeHolder: 'Enter your question...'
  });

  if (!input) {
    return;
  }

  // Create a webview panel to display the response
  const panel = vscode.window.createWebviewPanel(
    'qwenResponse',
    'Qwen Response',
    vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true
    }
  );

  // Set initial content
  panel.webview.html = getLoadingWebviewContent();

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Asking Qwen...',
    cancellable: false
  }, async () => {
    try {
      if (!agentCoordinator) {
        throw new Error('Agent coordinator not initialized');
      }

      // Process the request using the agent coordinator
      const response = await agentCoordinator.processRequest(input);

      // Update the webview with the response
      panel.webview.html = getResponseWebviewContent(input, response);
    } catch (error) {
      // Handle the error
      const errorDetails = error instanceof Error ? error.message : String(error);
      panel.webview.html = getErrorWebviewContent(input, errorDetails);
      vscode.window.showErrorMessage(`Error asking Qwen: ${errorDetails}`);
    }
  });
}

/**
 * Get loading webview content
 * @returns HTML content for the loading state
 */
function getLoadingWebviewContent(): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qwen Response</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
    }
    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }
    .spinner {
      width: 50px;
      height: 50px;
      border: 5px solid var(--vscode-button-background);
      border-top: 5px solid var(--vscode-editor-background);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 20px;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="loading">
    <div class="spinner"></div>
    <p>Asking Qwen...</p>
  </div>
</body>
</html>`;
}

/**
 * Get response webview content
 * @param question The user's question
 * @param answer The answer from Qwen
 * @returns HTML content for the response
 */
function getResponseWebviewContent(question: string, answer: string): string {
  // Convert the answer to HTML (replace newlines with <br>, etc.)
  const formattedAnswer = answer
    .replace(/\n/g, '<br>')
    .replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qwen Response</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .question {
      background-color: var(--vscode-input-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      border-left: 5px solid var(--vscode-button-background);
    }
    .answer {
      background-color: var(--vscode-editor-background);
      padding: 15px;
      border-radius: 5px;
    }
    pre {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code {
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Your Question</h2>
    <div class="question">
      ${question}
    </div>
    <h2>Qwen's Response</h2>
    <div class="answer">
      ${formattedAnswer}
    </div>
  </div>
</body>
</html>`;
}

/**
 * Get error webview content
 * @param question The user's question
 * @param error The error message
 * @returns HTML content for the error state
 */
function getErrorWebviewContent(question: string, error: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qwen Response</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .question {
      background-color: var(--vscode-input-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      border-left: 5px solid var(--vscode-button-background);
    }
    .error {
      background-color: var(--vscode-inputValidation-errorBackground);
      color: var(--vscode-inputValidation-errorForeground);
      padding: 15px;
      border-radius: 5px;
      border-left: 5px solid var(--vscode-errorForeground);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Your Question</h2>
    <div class="question">
      ${question}
    </div>
    <h2>Error</h2>
    <div class="error">
      <p>An error occurred while processing your request:</p>
      <p>${error}</p>
    </div>
  </div>
</body>
</html>`;
}

/**
 * Explain code
 */
async function explainCode() {
  // Get the active editor
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor');
    return;
  }

  // Get the selected text
  const selection = editor.selection;
  const text = editor.document.getText(selection);

  if (!text) {
    vscode.window.showErrorMessage('No text selected');
    return;
  }

  // Get the file path and language
  const filePath = editor.document.uri.fsPath;
  const fileName = filePath.split(/[\\/]/).pop() || '';
  const language = editor.document.languageId;

  // Create a webview panel to display the explanation
  const panel = vscode.window.createWebviewPanel(
    'qwenExplanation',
    `Explanation: ${fileName}`,
    vscode.ViewColumn.Beside,
    {
      enableScripts: true,
      retainContextWhenHidden: true
    }
  );

  // Set initial content
  panel.webview.html = getLoadingWebviewContent();

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Explaining code...',
    cancellable: false
  }, async () => {
    try {
      if (!agentCoordinator) {
        throw new Error('Agent coordinator not initialized');
      }

      // Create a prompt that includes the code and asks for an explanation
      const prompt = `Please explain the following ${language} code:

\`\`\`${language}
${text}
\`\`\`

Please provide a detailed explanation of what this code does, how it works, and any important patterns or concepts it demonstrates.`;

      // Process the request using the agent coordinator
      const response = await agentCoordinator.processRequest(prompt);

      // Update the webview with the explanation
      panel.webview.html = getExplanationWebviewContent(text, language, response);
    } catch (error) {
      // Handle the error
      const errorDetails = error instanceof Error ? error.message : String(error);
      panel.webview.html = getErrorExplanationWebviewContent(text, language, errorDetails);
      vscode.window.showErrorMessage(`Error explaining code: ${errorDetails}`);
    }
  });
}

/**
 * Get explanation webview content
 * @param code The code to explain
 * @param language The code language
 * @param explanation The explanation from Qwen
 * @returns HTML content for the explanation
 */
function getExplanationWebviewContent(code: string, language: string, explanation: string): string {
  // Convert the explanation to HTML (replace newlines with <br>, etc.)
  const formattedExplanation = explanation
    .replace(/\n/g, '<br>')
    .replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code Explanation</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .code {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      overflow-x: auto;
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
      white-space: pre;
    }
    .explanation {
      background-color: var(--vscode-editor-background);
      padding: 15px;
      border-radius: 5px;
    }
    pre {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code {
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Code</h2>
    <div class="code">
      <code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code>
    </div>
    <h2>Explanation</h2>
    <div class="explanation">
      ${formattedExplanation}
    </div>
  </div>
</body>
</html>`;
}

/**
 * Get error explanation webview content
 * @param code The code to explain
 * @param language The code language
 * @param error The error message
 * @returns HTML content for the error state
 */
function getErrorExplanationWebviewContent(code: string, language: string, error: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code Explanation</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .code {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      overflow-x: auto;
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
      white-space: pre;
    }
    .error {
      background-color: var(--vscode-inputValidation-errorBackground);
      color: var(--vscode-inputValidation-errorForeground);
      padding: 15px;
      border-radius: 5px;
      border-left: 5px solid var(--vscode-errorForeground);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Code</h2>
    <div class="code">
      <code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code>
    </div>
    <h2>Error</h2>
    <div class="error">
      <p>An error occurred while explaining the code:</p>
      <p>${error}</p>
    </div>
  </div>
</body>
</html>`;
}

/**
 * Generate code
 */
async function generateCode() {
  // Get the active editor
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor');
    return;
  }

  // Get the input from the user
  const input = await vscode.window.showInputBox({
    prompt: 'What code would you like to generate?',
    placeHolder: 'Enter your request...'
  });

  if (!input) {
    return;
  }

  // Get the language
  const language = editor.document.languageId;

  // Create a webview panel to display the generated code
  const panel = vscode.window.createWebviewPanel(
    'qwenCodeGeneration',
    'Generated Code',
    vscode.ViewColumn.Beside,
    {
      enableScripts: true,
      retainContextWhenHidden: true
    }
  );

  // Set initial content
  panel.webview.html = getLoadingWebviewContent();

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Generating code...',
    cancellable: false
  }, async () => {
    try {
      if (!agentCoordinator) {
        throw new Error('Agent coordinator not initialized');
      }

      // Create a prompt that asks for code generation
      const prompt = `Please generate ${language} code for the following request:

${input}

Please provide well-structured, efficient, and well-commented code that follows best practices for ${language}.`;

      // Process the request using the agent coordinator
      const response = await agentCoordinator.processRequest(prompt);

      // Update the webview with the generated code
      panel.webview.html = getGeneratedCodeWebviewContent(input, language, response);

      // Add a button to insert the code
      panel.webview.onDidReceiveMessage(async message => {
        if (message.command === 'insertCode') {
          try {
            // Extract the code from the response
            const codeMatch = response.match(/```(?:\w+)?\s*([\s\S]*?)```/);
            const codeToInsert = codeMatch ? codeMatch[1].trim() : response;

            // Insert the code at the current cursor position
            editor.edit(editBuilder => {
              editBuilder.insert(editor.selection.active, codeToInsert);
            });

            vscode.window.showInformationMessage('Code inserted successfully');
          } catch (error) {
            vscode.window.showErrorMessage(`Error inserting code: ${error}`);
          }
        }
      });

      // Enable messaging from the webview
      panel.webview.options = { enableScripts: true };
    } catch (error) {
      // Handle the error
      const errorDetails = error instanceof Error ? error.message : String(error);
      panel.webview.html = getErrorGeneratedCodeWebviewContent(input, language, errorDetails);
      vscode.window.showErrorMessage(`Error generating code: ${errorDetails}`);
    }
  });
}

/**
 * Get generated code webview content
 * @param request The user's request
 * @param language The code language
 * @param response The response from Qwen
 * @returns HTML content for the generated code
 */
function getGeneratedCodeWebviewContent(request: string, language: string, response: string): string {
  // Extract code blocks from the response
  const codeBlocks: string[] = [];
  const codeBlockRegex = /```(?:\w+)?\s*([\s\S]*?)```/g;
  let match;
  while ((match = codeBlockRegex.exec(response)) !== null) {
    codeBlocks.push(match[1].trim());
  }

  // Format the response
  let formattedResponse = response
    .replace(/\n/g, '<br>')
    .replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated Code</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .request {
      background-color: var(--vscode-input-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      border-left: 5px solid var(--vscode-button-background);
    }
    .response {
      background-color: var(--vscode-editor-background);
      padding: 15px;
      border-radius: 5px;
    }
    pre {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code {
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
    button {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 20px;
      font-size: var(--vscode-font-size);
    }
    button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Your Request</h2>
    <div class="request">
      ${request}
    </div>
    <h2>Generated Code</h2>
    <div class="response">
      ${formattedResponse}
    </div>
    <button id="insertButton">Insert Code</button>
  </div>
  <script>
    const vscode = acquireVsCodeApi();
    document.getElementById('insertButton').addEventListener('click', () => {
      vscode.postMessage({
        command: 'insertCode'
      });
    });
  </script>
</body>
</html>`;
}

/**
 * Get error generated code webview content
 * @param request The user's request
 * @param language The code language
 * @param error The error message
 * @returns HTML content for the error state
 */
function getErrorGeneratedCodeWebviewContent(request: string, language: string, error: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated Code</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      line-height: 1.5;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
    }
    .request {
      background-color: var(--vscode-input-background);
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
      border-left: 5px solid var(--vscode-button-background);
    }
    .error {
      background-color: var(--vscode-inputValidation-errorBackground);
      color: var(--vscode-inputValidation-errorForeground);
      padding: 15px;
      border-radius: 5px;
      border-left: 5px solid var(--vscode-errorForeground);
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Your Request</h2>
    <div class="request">
      ${request}
    </div>
    <h2>Error</h2>
    <div class="error">
      <p>An error occurred while generating code:</p>
      <p>${error}</p>
    </div>
  </div>
</body>
</html>`;
}

/**
 * Add an MCP server from a GitHub repository
 */
async function addMcpRepo() {
  // Get the repository URL from the user
  const repoUrl = await vscode.window.showInputBox({
    prompt: 'Enter the GitHub repository URL',
    placeHolder: 'https://github.com/username/repo',
    validateInput: (value) => {
      if (!value) {
        return 'Repository URL is required';
      }

      if (!value.startsWith('https://github.com/')) {
        return 'Repository URL must start with https://github.com/';
      }

      return null;
    }
  });

  if (!repoUrl) {
    return;
  }

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Adding MCP server...',
    cancellable: false
  }, async () => {
    try {
      // Add the server
      const server = await mcpServerManager?.addServerFromGitHub(repoUrl);

      // Show a success message
      vscode.window.showInformationMessage(`Added MCP server: ${server?.name}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Error adding MCP server: ${error}`);
    }
  });
}

/**
 * Manage MCP servers
 */
async function manageMcpServers() {
  // Focus the MCP servers view
  vscode.commands.executeCommand('qwenMcpServers.focus');
}

/**
 * Start an MCP server
 * @param item Server tree item
 */
async function startMcpServer(item?: McpServerTreeItem) {
  // If no item is provided, show a quick pick to select a server
  let serverId: string | undefined;

  if (item?.server?.id) {
    serverId = item.server.id;
  } else {
    const servers = mcpServerManager?.getServers() || [];
    const stoppedServers = servers.filter(s => s.status === 'stopped');

    if (stoppedServers.length === 0) {
      vscode.window.showInformationMessage('No stopped servers to start');
      return;
    }

    const items = stoppedServers.map(s => ({
      label: s.name,
      description: s.description,
      id: s.id
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: 'Select a server to start'
    });

    if (!selected) {
      return;
    }

    serverId = selected.id;
  }

  if (!serverId) {
    return;
  }

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Starting MCP server...',
    cancellable: false
  }, async () => {
    try {
      // Start the server
      if (mcpServerManager && serverId) {
        await mcpServerManager.startServer(serverId);
      }

      // Show a success message
      vscode.window.showInformationMessage(`Started MCP server: ${serverId}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Error starting MCP server: ${error}`);
    }
  });
}

/**
 * Stop an MCP server
 * @param item Server tree item
 */
async function stopMcpServer(item?: McpServerTreeItem) {
  // If no item is provided, show a quick pick to select a server
  let serverId: string | undefined;

  if (item?.server?.id) {
    serverId = item.server.id;
  } else {
    const servers = mcpServerManager?.getServers() || [];
    const runningServers = servers.filter(s => s.status === 'running');

    if (runningServers.length === 0) {
      vscode.window.showInformationMessage('No running servers to stop');
      return;
    }

    const items = runningServers.map(s => ({
      label: s.name,
      description: s.description,
      id: s.id
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: 'Select a server to stop'
    });

    if (!selected) {
      return;
    }

    serverId = selected.id;
  }

  if (!serverId) {
    return;
  }

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Stopping MCP server...',
    cancellable: false
  }, async () => {
    try {
      // Stop the server
      if (mcpServerManager && serverId) {
        await mcpServerManager.stopServer(serverId);
      }

      // Show a success message
      vscode.window.showInformationMessage(`Stopped MCP server: ${serverId}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Error stopping MCP server: ${error}`);
    }
  });
}

/**
 * Restart an MCP server
 * @param item Server tree item
 */
async function restartMcpServer(item?: McpServerTreeItem) {
  // If no item is provided, show a quick pick to select a server
  let serverId: string | undefined;

  if (item?.server?.id) {
    serverId = item.server.id;
  } else {
    const servers = mcpServerManager?.getServers() || [];
    const runningServers = servers.filter(s => s.status === 'running');

    if (runningServers.length === 0) {
      vscode.window.showInformationMessage('No running servers to restart');
      return;
    }

    const items = runningServers.map(s => ({
      label: s.name,
      description: s.description,
      id: s.id
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: 'Select a server to restart'
    });

    if (!selected) {
      return;
    }

    serverId = selected.id;
  }

  if (!serverId) {
    return;
  }

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Restarting MCP server...',
    cancellable: false
  }, async () => {
    try {
      // Restart the server
      if (mcpServerManager && serverId) {
        await mcpServerManager.restartServer(serverId);
      }

      // Show a success message
      vscode.window.showInformationMessage(`Restarted MCP server: ${serverId}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Error restarting MCP server: ${error}`);
    }
  });
}

/**
 * View the logs for an MCP server
 * @param item Server tree item
 */
async function viewMcpServerLogs(item?: McpServerTreeItem) {
  // If no item is provided, show a quick pick to select a server
  let serverId: string | undefined;

  if (item?.server?.id) {
    serverId = item.server.id;
  } else {
    const servers = mcpServerManager?.getServers() || [];

    if (servers.length === 0) {
      vscode.window.showInformationMessage('No servers available');
      return;
    }

    const items = servers.map(s => ({
      label: s.name,
      description: s.description,
      id: s.id
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: 'Select a server to view logs'
    });

    if (!selected) {
      return;
    }

    serverId = selected.id;
  }

  if (!serverId) {
    return;
  }

  try {
    // Get the server
    const server = mcpServerManager?.getServer(serverId);

    if (!server) {
      vscode.window.showErrorMessage(`Server ${serverId} not found`);
      return;
    }

    // Get the logs
    const logs = mcpServerManager?.getServerLogs(serverId);

    if (!logs || logs.length === 0) {
      vscode.window.showInformationMessage(`No logs available for server ${serverId}`);
      return;
    }

    // Create a new output channel
    const channel = vscode.window.createOutputChannel(`MCP Server: ${server.name}`);

    // Write the logs to the channel
    channel.appendLine(logs.join('\n'));

    // Show the channel
    channel.show();
  } catch (error) {
    vscode.window.showErrorMessage(`Error viewing logs: ${error}`);
  }
}

/**
 * View the schema for an MCP server
 * @param item Server tree item
 */
async function viewMcpServerSchema(item?: McpServerTreeItem) {
  // If no item is provided, show a quick pick to select a server
  let serverId: string | undefined;

  if (item?.server?.id) {
    serverId = item.server.id;
  } else {
    const servers = mcpServerManager?.getServers() || [];
    const runningServers = servers.filter(s => s.status === 'running');

    if (runningServers.length === 0) {
      vscode.window.showInformationMessage('No running servers to view schema');
      return;
    }

    const items = runningServers.map(s => ({
      label: s.name,
      description: s.description,
      id: s.id
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: 'Select a server to view schema'
    });

    if (!selected) {
      return;
    }

    serverId = selected.id;
  }

  if (!serverId) {
    return;
  }

  try {
    // Get the server
    const server = mcpServerManager?.getServer(serverId);

    if (!server) {
      vscode.window.showErrorMessage(`Server ${serverId} not found`);
      return;
    }

    // Get the schema
    const schema = server.schema;

    if (!schema) {
      vscode.window.showInformationMessage(`No schema available for server ${serverId}`);
      return;
    }

    // Create a new untitled document
    const document = await vscode.workspace.openTextDocument({
      content: JSON.stringify(schema, null, 2),
      language: 'json'
    });

    // Show the document
    await vscode.window.showTextDocument(document);
  } catch (error) {
    vscode.window.showErrorMessage(`Error viewing schema: ${error}`);
  }
}

/**
 * Refresh the MCP servers view
 */
async function refreshMcpServers() {
  mcpServerTreeDataProvider?.refresh();
}

/**
 * Test the API connection
 */
async function testApiConnection() {
  if (!qwenApiClient) {
    vscode.window.showErrorMessage('Qwen API client not initialized');
    return;
  }

  // Show a progress notification
  vscode.window.withProgress({
    location: vscode.ProgressLocation.Notification,
    title: 'Testing API connection...',
    cancellable: false
  }, async () => {
    try {
      // Create a simple test prompt
      const response = await qwenApiClient!.generateCompletion({
        prompt: 'Hello, can you respond with a simple "Hello, I am Qwen!" to test the connection?',
        maxTokens: 20,
        skipCache: true // Skip cache to ensure we're testing the actual API connection
      });

      // Show a success message
      vscode.window.showInformationMessage(`API connection successful! Response: ${response.text.substring(0, 50)}${response.text.length > 50 ? '...' : ''}`);
    } catch (error) {
      // Show an error message
      const errorMessage = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(`API connection failed: ${errorMessage}`);
    }
  });
}

/**
 * Verify the extension configuration
 */
async function verifyExtensionConfiguration() {
  // Get the current configuration
  const config = getConfiguration();

  // Verify the configuration
  const verificationResult = verifyConfiguration(config);

  if (verificationResult.isValid) {
    // Show a success message
    vscode.window.showInformationMessage('Configuration is valid');
  } else {
    // Show an error message with the issues
    const issuesMessage = verificationResult.issues.join('\n');
    vscode.window.showErrorMessage(`Configuration issues found:\n${issuesMessage}`);

    // Offer to open settings
    const openSettings = 'Open Settings';
    vscode.window.showWarningMessage('Would you like to update your settings?', openSettings)
      .then(selection => {
        if (selection === openSettings) {
          vscode.commands.executeCommand('workbench.action.openSettings', 'qwen-coder-assistant');
        }
      });
  }
}

/**
 * Test an MCP tool
 */
async function testMcpTool() {
  try {
    if (!mcpClient || !mcpServerManager) {
      throw new Error('MCP client or server manager not initialized');
    }

    // Get all running servers
    const servers = mcpServerManager.getServers().filter(s => s.status === 'running');

    if (servers.length === 0) {
      throw new Error('No running MCP servers found. Please start a server first.');
    }

    // Let the user select a server
    const serverItems = servers.map(s => ({
      label: s.name,
      description: s.description,
      detail: `Status: ${s.status}, Endpoint: ${s.endpoint || 'N/A'}`,
      server: s
    }));

    const selectedServer = await vscode.window.showQuickPick(serverItems, {
      placeHolder: 'Select an MCP server',
      title: 'Test MCP Tool'
    });

    if (!selectedServer) {
      return;
    }

    // Get all tools for the selected server
    const tools = selectedServer.server.schema?.tools || [];

    if (tools.length === 0) {
      throw new Error(`No tools found for server ${selectedServer.server.name}`);
    }

    // Let the user select a tool
    const toolItems = tools.map(t => ({
      label: t.name,
      description: t.description,
      detail: `Parameters: ${t.parameters.length}`,
      tool: t
    }));

    const selectedTool = await vscode.window.showQuickPick(toolItems, {
      placeHolder: 'Select a tool to test',
      title: 'Test MCP Tool'
    });

    if (!selectedTool) {
      return;
    }

    // Collect parameters for the tool
    const parameters: Record<string, any> = {};

    for (const param of selectedTool.tool.parameters) {
      const paramValue = await vscode.window.showInputBox({
        prompt: `Enter value for parameter '${param.name}'${param.required ? ' (required)' : ''}`,
        placeHolder: param.description,
        ignoreFocusOut: true,
        validateInput: value => {
          if (param.required && !value) {
            return 'This parameter is required';
          }
          return null;
        }
      });

      if (param.required && !paramValue) {
        return; // User cancelled
      }

      if (paramValue) {
        // Convert the value to the appropriate type
        if (param.type === 'number') {
          parameters[param.name] = Number(paramValue);
        } else if (param.type === 'boolean') {
          parameters[param.name] = paramValue.toLowerCase() === 'true';
        } else if (param.type === 'array' || param.type === 'object') {
          try {
            parameters[param.name] = JSON.parse(paramValue);
          } catch (error) {
            throw new Error(`Invalid JSON for parameter ${param.name}: ${error}`);
          }
        } else {
          parameters[param.name] = paramValue;
        }
      }
    }

    // Show a progress notification
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: `Invoking tool ${selectedTool.tool.name}...`,
      cancellable: false
    }, async () => {
      try {
        // Invoke the tool
        const result = await mcpClient!.invokeTool(
          selectedServer.server.id,
          selectedTool.tool.name,
          parameters
        );

        // Create a new untitled document to display the result
        const document = await vscode.workspace.openTextDocument({
          content: JSON.stringify(result, null, 2),
          language: 'json'
        });

        // Show the document
        await vscode.window.showTextDocument(document);

        // Show a success message
        if (result.status === 'success') {
          vscode.window.showInformationMessage(`Tool ${selectedTool.tool.name} invoked successfully`);
        } else {
          vscode.window.showErrorMessage(`Error invoking tool: ${result.error}`);
        }
      } catch (error) {
        vscode.window.showErrorMessage(`Error invoking tool: ${error}`);
      }
    });
  } catch (error) {
    vscode.window.showErrorMessage(`Error testing MCP tool: ${error}`);
  }
}

/**
 * Deactivate the extension
 */
export async function deactivate() {
  // Clean up resources when the extension is deactivated
  console.log('Qwen Coder Assistant is now deactivated!');

  // Dispose the agent coordinator
  if (agentCoordinator) {
    agentCoordinator.dispose();
    agentCoordinator = undefined;
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


