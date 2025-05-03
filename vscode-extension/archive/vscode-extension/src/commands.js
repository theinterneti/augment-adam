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
exports.registerCommands = registerCommands;
const vscode = __importStar(require("vscode"));
const configuration_1 = require("./configuration");
const contextProvider_1 = require("./contextProvider");
const errorHandler_1 = require("./errorHandler");
const responseFormatter_1 = require("./responseFormatter");
function registerCommands(context, apiClient, agentCoordinator, mcpClient) {
    // Register the "Ask Qwen" command
    const askQwenCommand = vscode.commands.registerCommand('qwen-coder-assistant.askQwen', async () => {
        const userPrompt = await vscode.window.showInputBox({
            prompt: 'What would you like to ask Qwen?',
            placeHolder: 'E.g., How do I implement a binary search in JavaScript?'
        });
        if (!userPrompt) {
            return; // User cancelled
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Asking Qwen...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const editorContext = await (0, contextProvider_1.getEditorContext)();
                let prompt = userPrompt;
                if (editorContext) {
                    prompt += `\n\nContext:\nFile: ${editorContext.fileName}\nLanguage: ${editorContext.language}\n`;
                    if (editorContext.selectedCode) {
                        prompt += `\nSelected code:\n\`\`\`${editorContext.language}\n${editorContext.selectedCode}\n\`\`\``;
                    }
                }
                progress.report({ increment: 30, message: 'Retrieving code context...' });
                // Get relevant context from the context engine
                const codeContext = await (0, contextProvider_1.getProjectContext)(userPrompt);
                if (codeContext) {
                    prompt += `\n\nRelevant code context:\n${codeContext}`;
                }
                progress.report({ increment: 50 });
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in helping with programming tasks. Provide clear, concise, and accurate responses to coding questions. Include code examples when appropriate.'
                };
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Explain Code" command
    const explainCodeCommand = vscode.commands.registerCommand('qwen-coder-assistant.explainCode', async () => {
        const editorContext = await (0, contextProvider_1.getEditorContext)();
        if (!editorContext || !editorContext.selectedCode) {
            vscode.window.showInformationMessage('Please select some code to explain.');
            return;
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Explaining code...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const prompt = `Please explain the following code in detail:\n\`\`\`${editorContext.language}\n${editorContext.selectedCode}\n\`\`\``;
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in explaining code. Provide clear, detailed explanations of how the code works, its purpose, and any important patterns or concepts it demonstrates.'
                };
                progress.report({ increment: 50 });
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Generate Code" command
    const generateCodeCommand = vscode.commands.registerCommand('qwen-coder-assistant.generateCode', async () => {
        const userPrompt = await vscode.window.showInputBox({
            prompt: 'What code would you like to generate?',
            placeHolder: 'E.g., Write a function to sort an array of objects by a property'
        });
        if (!userPrompt) {
            return; // User cancelled
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Generating code...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const editorContext = await (0, contextProvider_1.getEditorContext)();
                let prompt = `Generate code for: ${userPrompt}`;
                if (editorContext) {
                    prompt += `\n\nContext:\nFile: ${editorContext.fileName}\nLanguage: ${editorContext.language}\n`;
                    if (editorContext.visibleRangeText) {
                        prompt += `\nSurrounding code:\n\`\`\`${editorContext.language}\n${editorContext.visibleRangeText}\n\`\`\``;
                    }
                }
                progress.report({ increment: 30 });
                // Get project context for better code generation
                progress.report({ message: 'Retrieving code context...' });
                const projectContext = await (0, contextProvider_1.getProjectContext)(userPrompt);
                if (projectContext) {
                    prompt += `\n\nProject context (relevant files):\n${projectContext}`;
                }
                progress.report({ increment: 50 });
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in generating high-quality code. Generate code that is efficient, well-documented, and follows best practices for the given language and context.'
                };
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Clear Cache" command
    const clearCacheCommand = vscode.commands.registerCommand('qwen-coder-assistant.clearCache', async () => {
        try {
            apiClient.clearCache();
            vscode.window.showInformationMessage('Qwen Coder cache cleared successfully.');
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Refactor Code" command
    const refactorCodeCommand = vscode.commands.registerCommand('qwen-coder-assistant.refactorCode', async () => {
        const editorContext = await (0, contextProvider_1.getEditorContext)();
        if (!editorContext || !editorContext.selectedCode) {
            vscode.window.showInformationMessage('Please select some code to refactor.');
            return;
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Refactoring code...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const prompt = `Please refactor the following code to improve its readability, efficiency, and maintainability. Provide the refactored code and explain the improvements made:\n\`\`\`${editorContext.language}\n${editorContext.selectedCode}\n\`\`\``;
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in refactoring code. Provide clean, efficient, and well-structured code that follows best practices and design patterns. Explain the improvements you made.'
                };
                progress.report({ increment: 50 });
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Document Code" command
    const documentCodeCommand = vscode.commands.registerCommand('qwen-coder-assistant.documentCode', async () => {
        const editorContext = await (0, contextProvider_1.getEditorContext)();
        if (!editorContext || !editorContext.selectedCode) {
            vscode.window.showInformationMessage('Please select some code to document.');
            return;
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Documenting code...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const prompt = `Please add comprehensive documentation to the following code. Include function/method descriptions, parameter explanations, return value details, and any other relevant documentation:\n\`\`\`${editorContext.language}\n${editorContext.selectedCode}\n\`\`\``;
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in documenting code. Provide clear, comprehensive documentation that follows the conventions of the given programming language. Include function/method descriptions, parameter explanations, return value details, and usage examples where appropriate.'
                };
                progress.report({ increment: 50 });
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Fix Issues" command
    const fixIssuesCommand = vscode.commands.registerCommand('qwen-coder-assistant.fixIssues', async () => {
        const editorContext = await (0, contextProvider_1.getEditorContext)();
        if (!editorContext || !editorContext.selectedCode) {
            vscode.window.showInformationMessage('Please select some code to fix.');
            return;
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Fixing code issues...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const prompt = `Please identify and fix any issues in the following code. This could include bugs, syntax errors, performance issues, or security vulnerabilities. Provide the fixed code and explain the issues that were addressed:\n\`\`\`${editorContext.language}\n${editorContext.selectedCode}\n\`\`\``;
                const options = {
                    prompt,
                    systemPrompt: 'You are Qwen Coder, an AI assistant specialized in identifying and fixing code issues. Look for bugs, syntax errors, performance issues, security vulnerabilities, and other problems. Provide the fixed code and explain the issues that were addressed.'
                };
                progress.report({ increment: 50 });
                // Check if streaming is enabled in configuration
                const config = (0, configuration_1.getConfiguration)();
                if (config.streamingEnabled) {
                    // Use streaming API
                    progress.report({ message: 'Streaming response...' });
                    // Variable to accumulate the full response for history
                    let fullResponse = '';
                    (0, responseFormatter_1.showStreamingResponseInPanel)(context, (streamHandler) => {
                        apiClient.generateStreamingCompletion(options, (chunk, done) => {
                            // Accumulate the response
                            fullResponse += chunk;
                            // Pass to the original handler
                            streamHandler(chunk, done);
                            // When streaming is complete, save to history
                            if (done) {
                                saveToHistory(context, prompt, fullResponse, options.systemPrompt);
                            }
                        }).catch(error => {
                            errorHandler_1.ErrorHandler.handleError(error);
                        });
                    });
                    progress.report({ increment: 100 });
                }
                else {
                    // Use non-streaming API
                    const response = await apiClient.generateCompletion(options);
                    progress.report({ increment: 100 });
                    // Save to conversation history
                    saveToHistory(context, prompt, response.text, options.systemPrompt);
                    // Show response in panel
                    (0, responseFormatter_1.showResponseInPanel)(response.text, context);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "Hierarchical Agent" command
    const hierarchicalAgentCommand = vscode.commands.registerCommand('qwen-coder-assistant.hierarchicalAgent', async () => {
        if (!agentCoordinator) {
            vscode.window.showErrorMessage('Hierarchical agent system is not available.');
            return;
        }
        const userPrompt = await vscode.window.showInputBox({
            prompt: 'What would you like the hierarchical agent system to do?',
            placeHolder: 'E.g., Implement a feature, refactor a module, create tests for a function'
        });
        if (!userPrompt) {
            return; // User cancelled
        }
        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Processing with hierarchical agent system...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                // Create a webview panel to display the results
                const panel = vscode.window.createWebviewPanel('qwenCoderHierarchicalAgent', 'Hierarchical Agent', vscode.ViewColumn.One, {
                    enableScripts: true,
                    retainContextWhenHidden: true
                });
                // Show loading indicator
                panel.webview.html = getLoadingWebviewContent();
                progress.report({ increment: 30, message: 'Decomposing task...' });
                try {
                    // Process the request with the agent coordinator
                    progress.report({ increment: 50, message: 'Executing subtasks...' });
                    const response = await agentCoordinator.processRequest(userPrompt);
                    progress.report({ increment: 100, message: 'Aggregating results...' });
                    // Show the response in the panel
                    panel.webview.html = getWebviewContent(userPrompt, response);
                    // Save to conversation history
                    saveToHistory(context, userPrompt, response, 'Hierarchical Agent System');
                }
                catch (error) {
                    panel.webview.html = getErrorWebviewContent(userPrompt, error.message);
                    errorHandler_1.ErrorHandler.handleError(error);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Register the "MCP Tool" command
    const mcpToolCommand = vscode.commands.registerCommand('qwen-coder-assistant.mcpTool', async () => {
        if (!mcpClient) {
            vscode.window.showErrorMessage('MCP tools are not available.');
            return;
        }
        try {
            // Get available tools
            const availableTools = mcpClient.getAvailableTools();
            if (availableTools.length === 0) {
                vscode.window.showInformationMessage('No MCP tools are currently available. Please start some tools first.');
                return;
            }
            // Let the user select a tool
            const selectedTool = await vscode.window.showQuickPick(availableTools, {
                placeHolder: 'Select an MCP tool to use'
            });
            if (!selectedTool) {
                return; // User cancelled
            }
            // Get the tool schema
            const toolSchema = mcpClient.getToolSchema(selectedTool);
            if (!toolSchema) {
                vscode.window.showErrorMessage(`Schema for tool ${selectedTool} is not available.`);
                return;
            }
            // Let the user select a function
            const functionItems = toolSchema.functions.map(func => ({
                label: func.name,
                description: func.description,
                detail: `Parameters: ${Object.keys(func.parameters.properties).join(', ')}`,
                function: func
            }));
            const selectedFunction = await vscode.window.showQuickPick(functionItems, {
                placeHolder: 'Select a function to call'
            });
            if (!selectedFunction) {
                return; // User cancelled
            }
            // Collect parameters for the function
            const parameters = {};
            for (const paramName of selectedFunction.function.parameters.required) {
                const paramSchema = selectedFunction.function.parameters.properties[paramName];
                const paramValue = await vscode.window.showInputBox({
                    prompt: `Enter value for ${paramName}`,
                    placeHolder: paramSchema.description
                });
                if (paramValue === undefined) {
                    return; // User cancelled
                }
                // Convert value to appropriate type
                if (paramSchema.type === 'number') {
                    parameters[paramName] = Number(paramValue);
                }
                else if (paramSchema.type === 'boolean') {
                    parameters[paramName] = paramValue.toLowerCase() === 'true';
                }
                else {
                    parameters[paramName] = paramValue;
                }
            }
            // Call the function
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Calling ${selectedFunction.label} on ${selectedTool}...`,
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0 });
                const result = await mcpClient.callFunction(selectedTool, selectedFunction.label, parameters);
                progress.report({ increment: 100 });
                // Show the result
                if (result.status === 'success') {
                    // Create a webview panel to display the results
                    const panel = vscode.window.createWebviewPanel('qwenCoderMcpTool', `${selectedTool} - ${selectedFunction.label}`, vscode.ViewColumn.One, {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    });
                    // Show the result
                    panel.webview.html = `<!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${selectedTool} - ${selectedFunction.label}</title>
            <style>
              body {
                font-family: var(--vscode-font-family);
                color: var(--vscode-editor-foreground);
                background-color: var(--vscode-editor-background);
                padding: 20px;
              }
              pre {
                background-color: var(--vscode-textCodeBlock-background);
                padding: 16px;
                border-radius: 4px;
                overflow: auto;
              }
            </style>
          </head>
          <body>
            <h1>${selectedTool} - ${selectedFunction.label}</h1>
            <h2>Parameters</h2>
            <pre>${JSON.stringify(parameters, null, 2)}</pre>
            <h2>Result</h2>
            <pre>${JSON.stringify(result.result, null, 2)}</pre>
          </body>
          </html>`;
                }
                else {
                    vscode.window.showErrorMessage(`Error calling function: ${result.error}`);
                }
            });
        }
        catch (error) {
            errorHandler_1.ErrorHandler.handleError(error);
        }
    });
    // Add commands to subscriptions
    context.subscriptions.push(askQwenCommand, explainCodeCommand, generateCodeCommand, refactorCodeCommand, documentCodeCommand, fixIssuesCommand, clearCacheCommand, hierarchicalAgentCommand, mcpToolCommand);
}
// Helper function to get loading webview content
function getLoadingWebviewContent() {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Processing Request</title>
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
      <p>The hierarchical agent system is working on your task.</p>
    </div>
  </body>
  </html>`;
}
// Helper function to get webview content
function getWebviewContent(request, response) {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Response</title>
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
// Helper function to get error webview content
function getErrorWebviewContent(request, errorMessage) {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
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
// Helper function to convert markdown to HTML
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
//# sourceMappingURL=commands.js.map