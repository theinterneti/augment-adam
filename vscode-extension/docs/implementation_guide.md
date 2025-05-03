# Implementation Guide for Current Priority Tasks

This guide provides detailed instructions for implementing the current priority tasks for the Qwen Coder Assistant VS Code extension.

## Configuration Setup

### Setting up Qwen API Endpoint and Key

1. **Verify Configuration Loading**:
   - The configuration is already defined in `src/configuration.ts`
   - The `QwenCoderConfig` interface includes `apiEndpoint` and `apiKey` properties
   - The `getConfiguration()` function loads these values from VS Code settings

2. **Test Configuration Loading**:
   - Create a simple command to display the current configuration
   - Add this to `src/commands.ts`:

   ```typescript
   export function registerShowConfigCommand(context: vscode.ExtensionContext): void {
     const disposable = vscode.commands.registerCommand('qwen-coder-assistant.showConfig', async () => {
       const config = getConfiguration();
       vscode.window.showInformationMessage(`API Endpoint: ${config.apiEndpoint}, API Key: ${config.apiKey ? '(Set)' : '(Not Set)'}`);
     });
     context.subscriptions.push(disposable);
   }
   ```

3. **Add Command to Package.json**:
   - Add the command to the `contributes.commands` section in `package.json`:

   ```json
   {
     "command": "qwen-coder-assistant.showConfig",
     "title": "Show Qwen API Configuration"
   }
   ```

4. **Verify API Client Initialization**:
   - Check that the `QwenApiClient` is properly initialized with the configuration
   - Ensure the client is updated when configuration changes

### Configuring MCP Server Storage Path

1. **Verify Storage Path Configuration**:
   - The `McpServersConfig` interface in `src/configuration.ts` includes a `storagePath` property
   - The `getConfiguration()` function loads this value from VS Code settings

2. **Add Storage Path Selection Command**:
   - Create a command to allow users to select a storage path
   - Add this to `src/commands.ts`:

   ```typescript
   export function registerSelectStoragePathCommand(context: vscode.ExtensionContext): void {
     const disposable = vscode.commands.registerCommand('qwen-coder-assistant.selectStoragePath', async () => {
       const options: vscode.OpenDialogOptions = {
         canSelectMany: false,
         canSelectFolders: true,
         canSelectFiles: false,
         openLabel: 'Select MCP Server Storage Path'
       };
       
       const folderUri = await vscode.window.showOpenDialog(options);
       if (folderUri && folderUri.length > 0) {
         const config = vscode.workspace.getConfiguration('qwen-coder-assistant');
         await config.update('mcpServers.storagePath', folderUri[0].fsPath, vscode.ConfigurationTarget.Global);
         vscode.window.showInformationMessage(`MCP Server storage path set to: ${folderUri[0].fsPath}`);
       }
     });
     context.subscriptions.push(disposable);
   }
   ```

3. **Add Command to Package.json**:
   - Add the command to the `contributes.commands` section in `package.json`:

   ```json
   {
     "command": "qwen-coder-assistant.selectStoragePath",
     "title": "Select MCP Server Storage Path"
   }
   ```

4. **Verify Storage Path Usage**:
   - Check that the `McpServerManager` is properly using the storage path
   - Ensure the storage path is created if it doesn't exist

## Basic Testing

### Testing Basic Qwen Interactions

1. **Test "askQwen" Command**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Ask Qwen Coder" command
   - Enter a simple coding question like "How do I read a file in Node.js?"
   - Verify that the response is displayed in a webview panel

2. **Test "explainCode" Command**:
   - Open a code file
   - Select a block of code
   - Right-click and select "Explain Code with Qwen" from the context menu
   - Verify that the explanation is displayed in a webview panel

3. **Test "generateCode" Command**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Generate Code with Qwen" command
   - Enter a description like "Create a function that sorts an array of objects by a property"
   - Verify that the generated code is displayed in a webview panel

### Testing MCP Server Management

1. **Test Adding a Server from GitHub**:
   - Open the command palette (Ctrl+Shift+P)
   - Run the "Add MCP Server from GitHub" command
   - Enter a GitHub repository URL like "https://github.com/modelcontextprotocol/servers"
   - Verify that the server is added to the MCP Servers view

2. **Test Starting and Stopping the Server**:
   - In the MCP Servers view, right-click on a server and select "Start MCP Server"
   - Verify that the server status changes to "Running"
   - Right-click on the server and select "Stop MCP Server"
   - Verify that the server status changes to "Stopped"

3. **Test Basic Tool Invocation**:
   - Start an MCP server
   - Open the command palette (Ctrl+Shift+P)
   - Run a command that uses an MCP tool
   - Verify that the tool is invoked and the result is displayed

## Troubleshooting

### Common Issues

1. **API Connection Issues**:
   - Check that the API endpoint is correct
   - Verify that the API key is set
   - Check network connectivity
   - Look for CORS issues if using a browser-based API

2. **MCP Server Issues**:
   - Check that Docker is running
   - Verify that the storage path exists and is writable
   - Check Docker logs for container errors
   - Verify that the GitHub token is set if using private repositories

3. **Extension Activation Issues**:
   - Check the VS Code Developer Tools console for errors
   - Verify that all dependencies are installed
   - Check that the extension is properly activated

### Debugging Tips

1. **Enable Extension Logging**:
   - Add logging statements to key functions
   - Use `console.log` for basic logging
   - Consider implementing a more robust logging system for production

2. **Use VS Code Developer Tools**:
   - Open Developer Tools with Help > Toggle Developer Tools
   - Check the Console tab for errors and log messages
   - Use the Network tab to monitor API requests

3. **Test with Mock API**:
   - Use the mock API client for testing without a real API
   - Set `NODE_ENV=development` to use the mock API
   - Verify that the mock API is returning expected responses
