# VS Code Extension Integration

This document provides instructions for integrating Augment Adam with VS Code through the MCP (Machine Comprehension Protocol) server and creating a VS Code extension.

## Overview

Augment Adam can be integrated with VS Code in two ways:

1. **MCP Server Integration**: Using the built-in MCP server to connect to VS Code's MCP client
2. **Custom VS Code Extension**: Creating a dedicated VS Code extension for Augment Adam

## MCP Server Integration

For detailed instructions on using the MCP server with VS Code, see [VS Code Integration](vscode_integration.md).

## Creating a VS Code Extension for Augment Adam

If you want to create a dedicated VS Code extension for Augment Adam, follow these steps:

### Prerequisites

- Node.js and npm
- VS Code Extension Generator
- Augment Adam installed

### Setting Up the Extension Project

1. Install the VS Code Extension Generator:

```bash
npm install -g yo generator-code
```

2. Generate a new extension:

```bash
yo code
```

3. Select "New Extension (TypeScript)" and follow the prompts.

### Connecting to Augment Adam

The extension can connect to Augment Adam in two ways:

1. **Direct Integration**: Using the Augment Adam Python package directly
2. **MCP Server Integration**: Connecting to the Augment Adam MCP server

#### Direct Integration

For direct integration, you'll need to use the Node.js child process module to spawn a Python process:

```typescript
import * as cp from 'child_process';
import * as vscode from 'vscode';

export function activateAugmentAdam(context: vscode.ExtensionContext) {
    // Spawn the Augment Adam process
    const pythonProcess = cp.spawn('python', ['-m', 'augment_adam.cli']);
    
    // Handle process output
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Augment Adam: ${data}`);
    });
    
    // Handle process errors
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Augment Adam Error: ${data}`);
    });
    
    // Clean up when VS Code is closed
    context.subscriptions.push({
        dispose: () => {
            pythonProcess.kill();
        }
    });
}
```

#### MCP Server Integration

For MCP server integration, you'll need to connect to the Augment Adam MCP server:

```typescript
import * as vscode from 'vscode';
import axios from 'axios';

export class AugmentAdamClient {
    private baseUrl: string;
    
    constructor(baseUrl: string = 'http://localhost:8811/mcp') {
        this.baseUrl = baseUrl;
    }
    
    async getTools(): Promise<any[]> {
        const response = await axios.get(`${this.baseUrl}/tools`);
        return response.data;
    }
    
    async callTool(name: string, parameters: any): Promise<any> {
        const response = await axios.post(`${this.baseUrl}/call`, {
            name,
            parameters
        });
        return response.data.result;
    }
}

export function activateAugmentAdam(context: vscode.ExtensionContext) {
    const client = new AugmentAdamClient();
    
    // Register commands
    const disposable = vscode.commands.registerCommand('augment-adam.search', async () => {
        const query = await vscode.window.showInputBox({
            prompt: 'Enter search query'
        });
        
        if (query) {
            try {
                const results = await client.callTool('vector_search', {
                    query,
                    k: 10,
                    include_metadata: true
                });
                
                // Display results
                vscode.window.showInformationMessage(`Found ${results.total_results} results`);
                
                // Create a webview to display results
                const panel = vscode.window.createWebviewPanel(
                    'augmentAdamResults',
                    'Augment Adam Results',
                    vscode.ViewColumn.One,
                    {}
                );
                
                panel.webview.html = getResultsHtml(results);
            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
            }
        }
    });
    
    context.subscriptions.push(disposable);
}

function getResultsHtml(results: any): string {
    // Generate HTML to display results
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Augment Adam Results</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .result { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; }
                .score { color: #888; }
            </style>
        </head>
        <body>
            <h1>Search Results</h1>
            <p>Found ${results.total_results} results in ${results.query_time_ms.toFixed(2)}ms</p>
            <div class="results">
                ${results.results.map((result: any) => `
                    <div class="result">
                        <h3>${result.id}</h3>
                        <p class="score">Score: ${result.score.toFixed(4)}</p>
                        <pre>${result.text}</pre>
                        ${result.metadata ? `
                            <details>
                                <summary>Metadata</summary>
                                <pre>${JSON.stringify(result.metadata, null, 2)}</pre>
                            </details>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </body>
        </html>
    `;
}
```

### Extension Features

Consider implementing the following features in your VS Code extension:

1. **Context-Aware Code Completion**: Use Augment Adam's context engine to provide intelligent code completion
2. **Code Search**: Search for code snippets in the codebase
3. **Documentation Generation**: Generate documentation for code
4. **Code Explanation**: Explain code snippets
5. **Refactoring Suggestions**: Suggest code refactorings

### Publishing the Extension

Once your extension is ready, you can publish it to the VS Code Marketplace:

1. Create a publisher account on the [VS Code Marketplace](https://marketplace.visualstudio.com/vscode)
2. Install the VS Code Extension Manager:

```bash
npm install -g vsce
```

3. Package your extension:

```bash
vsce package
```

4. Publish your extension:

```bash
vsce publish
```

## Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code MCP Documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
- [Augment Adam MCP Server Documentation](../src/augment_adam/server/README.md)
