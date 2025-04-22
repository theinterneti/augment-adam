// The module 'vscode' contains the VS Code extensibility API
const vscode = require('vscode');

// Import additional modules for Docker, WSL, and devcontainer functionality
const dockerode = require('dockerode');
const yaml = require('yaml');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Import Python bridge for model inference
const PythonBridge = require('./utils/python_bridge');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Dukat: Development Environment Assistant is now active!');

    // Initialize the Python bridge
    const pythonBridge = new PythonBridge(context);

    // Initialize Docker client if available
    let docker;
    try {
        docker = new dockerode();
    } catch (error) {
        console.log('Docker not available:', error.message);
    }

    // Register the askQuestion command
    let askQuestionDisposable = vscode.commands.registerCommand('dukat.askQuestion', async function () {
        const question = await vscode.window.showInputBox({
            placeHolder: 'Ask about Docker, WSL, or devcontainers...',
            prompt: 'What would you like to know about development environments?'
        });

        if (question) {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating response...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20 });

                // Call the model through Python bridge
                try {
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Provide clear, concise, and accurate information.";
                    const response = await pythonBridge.generateResponse(question, systemPrompt);

                    progress.report({ increment: 80 });

                    // Create and show a new webview panel
                    const panel = vscode.window.createWebviewPanel(
                        'dukat-assistant',
                        'Dukat Assistant',
                        vscode.ViewColumn.Beside,
                        {
                            enableScripts: true
                        }
                    );

                    panel.webview.html = getWebviewContent(question, response);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating response: ${error.message}`);
                }

                return null;
            });
        }
    });

    // Register the explainDockerCommand command
    let explainDockerCommandDisposable = vscode.commands.registerCommand('dukat.explainDockerCommand', async function () {
        const command = await vscode.window.showInputBox({
            placeHolder: 'Enter a Docker command...',
            prompt: 'Which Docker command would you like explained?'
        });

        if (command) {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating explanation...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20 });

                try {
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Explain Docker commands in detail, including options, use cases, and examples.";
                    const response = await pythonBridge.generateResponse(`Explain the Docker command: ${command}`, systemPrompt);

                    progress.report({ increment: 80 });

                    // Create and show a new webview panel
                    const panel = vscode.window.createWebviewPanel(
                        'dukat-assistant',
                        'Docker Command Explanation',
                        vscode.ViewColumn.Beside,
                        {
                            enableScripts: true
                        }
                    );

                    panel.webview.html = getWebviewContent(`Docker command: ${command}`, response);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating explanation: ${error.message}`);
                }

                return null;
            });
        }
    });

    // Register the generateDockerfile command
    let generateDockerfileDisposable = vscode.commands.registerCommand('dukat.generateDockerfile', async function () {
        const requirements = await vscode.window.showInputBox({
            placeHolder: 'Describe your application requirements...',
            prompt: 'What kind of Dockerfile do you need?'
        });

        if (requirements) {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating Dockerfile...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20 });

                try {
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Generate a well-commented Dockerfile based on the user's requirements. Include best practices and optimizations.";
                    const response = await pythonBridge.generateResponse(`Generate a Dockerfile for: ${requirements}`, systemPrompt);

                    progress.report({ increment: 60 });

                    // Extract the Dockerfile content from the response (assuming it's in a markdown code block)
                    const dockerfileContent = extractCodeBlock(response, 'dockerfile');

                    if (dockerfileContent) {
                        // Get the workspace folder
                        const workspaceFolders = vscode.workspace.workspaceFolders;
                        if (workspaceFolders) {
                            const workspacePath = workspaceFolders[0].uri.fsPath;
                            const dockerfilePath = path.join(workspacePath, 'Dockerfile');

                            // Check if Dockerfile already exists
                            if (fs.existsSync(dockerfilePath)) {
                                const overwrite = await vscode.window.showWarningMessage(
                                    'Dockerfile already exists. Do you want to overwrite it?',
                                    'Yes', 'No'
                                );

                                if (overwrite !== 'Yes') {
                                    return null;
                                }
                            }

                            // Write the Dockerfile
                            fs.writeFileSync(dockerfilePath, dockerfileContent);

                            // Open the Dockerfile
                            const document = await vscode.workspace.openTextDocument(dockerfilePath);
                            await vscode.window.showTextDocument(document);

                            vscode.window.showInformationMessage('Dockerfile generated successfully!');
                        }
                    } else {
                        // Show the full response in a webview if we couldn't extract the Dockerfile
                        const panel = vscode.window.createWebviewPanel(
                            'dukat-assistant',
                            'Dockerfile Generator',
                            vscode.ViewColumn.Beside,
                            {
                                enableScripts: true
                            }
                        );

                        panel.webview.html = getWebviewContent(`Generate Dockerfile for: ${requirements}`, response);
                    }

                    progress.report({ increment: 20 });
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating Dockerfile: ${error.message}`);
                }

                return null;
            });
        }
    });

    // Register the generateDevcontainer command
    let generateDevcontainerDisposable = vscode.commands.registerCommand('dukat.generateDevcontainer', async function () {
        const requirements = await vscode.window.showInputBox({
            placeHolder: 'Describe your development environment requirements...',
            prompt: 'What kind of devcontainer do you need?'
        });

        if (requirements) {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating devcontainer configuration...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20 });

                try {
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Generate a well-configured devcontainer.json and related files based on the user's requirements. Include volume mounts, extensions, and other best practices.";
                    const response = await pythonBridge.generateResponse(`Generate a devcontainer configuration for: ${requirements}`, systemPrompt);

                    progress.report({ increment: 60 });

                    // Get the workspace folder
                    const workspaceFolders = vscode.workspace.workspaceFolders;
                    if (workspaceFolders) {
                        const workspacePath = workspaceFolders[0].uri.fsPath;
                        const devcontainerDir = path.join(workspacePath, '.devcontainer');

                        // Create .devcontainer directory if it doesn't exist
                        if (!fs.existsSync(devcontainerDir)) {
                            fs.mkdirSync(devcontainerDir, { recursive: true });
                        }

                        // Extract the devcontainer.json content
                        const devcontainerJsonContent = extractCodeBlock(response, 'json');
                        if (devcontainerJsonContent) {
                            const devcontainerJsonPath = path.join(devcontainerDir, 'devcontainer.json');
                            fs.writeFileSync(devcontainerJsonPath, devcontainerJsonContent);
                        }

                        // Extract the Dockerfile content
                        const dockerfileContent = extractCodeBlock(response, 'dockerfile');
                        if (dockerfileContent) {
                            const dockerfilePath = path.join(devcontainerDir, 'Dockerfile');
                            fs.writeFileSync(dockerfilePath, dockerfileContent);
                        }

                        // Extract the docker-compose.yml content
                        const dockerComposeContent = extractCodeBlock(response, 'yaml');
                        if (dockerComposeContent) {
                            const dockerComposePath = path.join(devcontainerDir, 'docker-compose.yml');
                            fs.writeFileSync(dockerComposePath, dockerComposeContent);
                        }

                        // Open the devcontainer.json file
                        if (fs.existsSync(path.join(devcontainerDir, 'devcontainer.json'))) {
                            const document = await vscode.workspace.openTextDocument(path.join(devcontainerDir, 'devcontainer.json'));
                            await vscode.window.showTextDocument(document);

                            vscode.window.showInformationMessage('Devcontainer configuration generated successfully!');
                        } else {
                            // Show the full response in a webview if we couldn't extract the files
                            const panel = vscode.window.createWebviewPanel(
                                'dukat-assistant',
                                'Devcontainer Generator',
                                vscode.ViewColumn.Beside,
                                {
                                    enableScripts: true
                                }
                            );

                            panel.webview.html = getWebviewContent(`Generate devcontainer for: ${requirements}`, response);
                        }
                    }

                    progress.report({ increment: 20 });
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating devcontainer configuration: ${error.message}`);
                }

                return null;
            });
        }
    });

    // Register the setupWSL command
    let setupWSLDisposable = vscode.commands.registerCommand('dukat.setupWSL', async function () {
        const requirements = await vscode.window.showInputBox({
            placeHolder: 'Describe your WSL setup requirements...',
            prompt: 'What kind of WSL environment do you need?'
        });

        if (requirements) {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Generating WSL setup guide...",
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 20 });

                try {
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Provide detailed instructions for setting up WSL based on the user's requirements. Include commands, configuration files, and best practices.";
                    const response = await pythonBridge.generateResponse(`Setup WSL environment for: ${requirements}`, systemPrompt);

                    progress.report({ increment: 80 });

                    // Create and show a new webview panel
                    const panel = vscode.window.createWebviewPanel(
                        'dukat-assistant',
                        'WSL Setup Guide',
                        vscode.ViewColumn.Beside,
                        {
                            enableScripts: true
                        }
                    );

                    panel.webview.html = getWebviewContent(`WSL setup for: ${requirements}`, response);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error generating WSL setup guide: ${error.message}`);
                }

                return null;
            });
        }
    });

    // Register the optimizeVolumes command
    let optimizeVolumesDisposable = vscode.commands.registerCommand('dukat.optimizeVolumes', async function () {
        if (!docker) {
            vscode.window.showErrorMessage('Docker is not available. Please make sure Docker is installed and running.');
            return;
        }

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing Docker volumes...",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 20 });

            try {
                // Get all volumes
                const volumes = await docker.listVolumes();

                if (volumes && volumes.Volumes) {
                    const volumeNames = volumes.Volumes.map(v => v.Name);
                    progress.report({ increment: 40 });

                    // Generate optimization recommendations
                    const systemPrompt = "You are Dukat, a specialized Linux assistant for Docker, WSL, and devcontainer development environments. Analyze the list of Docker volumes and provide optimization recommendations. Consider volume naming, usage patterns, and potential improvements.";
                    const response = await pythonBridge.generateResponse(`Analyze and optimize these Docker volumes: ${JSON.stringify(volumeNames)}`, systemPrompt);

                    progress.report({ increment: 40 });

                    // Create and show a new webview panel
                    const panel = vscode.window.createWebviewPanel(
                        'dukat-assistant',
                        'Docker Volume Optimization',
                        vscode.ViewColumn.Beside,
                        {
                            enableScripts: true
                        }
                    );

                    panel.webview.html = getWebviewContent('Docker Volume Optimization', response);
                } else {
                    vscode.window.showInformationMessage('No Docker volumes found.');
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Error analyzing Docker volumes: ${error.message}`);
            }

            return null;
        });
    });

    // Register all commands
    context.subscriptions.push(askQuestionDisposable);
    context.subscriptions.push(explainDockerCommandDisposable);
    context.subscriptions.push(generateDockerfileDisposable);
    context.subscriptions.push(generateDevcontainerDisposable);
    context.subscriptions.push(setupWSLDisposable);
    context.subscriptions.push(optimizeVolumesDisposable);

    // Register Docker file watcher
    const dockerfileWatcher = vscode.workspace.createFileSystemWatcher('**/Dockerfile');
    const devcontainerWatcher = vscode.workspace.createFileSystemWatcher('**/.devcontainer/**');

    context.subscriptions.push(dockerfileWatcher);
    context.subscriptions.push(devcontainerWatcher);
}

/**
 * Extract code block from markdown response
 * @param {string} markdown - Markdown text
 * @param {string} language - Language of the code block to extract
 * @returns {string|null} - Extracted code or null if not found
 */
function extractCodeBlock(markdown, language) {
    const regex = new RegExp(`\\`\\`\\`(?:${language})?\n([\\s\\S]*?)\n\\`\\`\\``, 'i');
    const match = markdown.match(regex);
    return match ? match[1].trim() : null;
}

/**
 * Generate HTML content for the webview
 * @param {string} question - User question
 * @param {string} answer - Model response
 * @returns {string} - HTML content
 */
function getWebviewContent(question, answer) {
    // Convert markdown in the answer to HTML
    const markdownAnswer = answer.replace(/```(\w*)\n([\s\S]*?)\n```/g, '<pre><code class="language-$1">$2</code></pre>');

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dukat Assistant</title>
        <style>
            body {
                font-family: var(--vscode-font-family);
                padding: 20px;
                color: var(--vscode-foreground);
                line-height: 1.5;
            }
            .question {
                font-weight: bold;
                margin-bottom: 20px;
                padding: 15px;
                background-color: var(--vscode-editor-background);
                border-left: 4px solid var(--vscode-activityBarBadge-background);
                border-radius: 4px;
            }
            .answer {
                margin-top: 20px;
                padding: 15px;
                background-color: var(--vscode-editor-background);
                border-left: 4px solid var(--vscode-button-background);
                border-radius: 4px;
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
            h1, h2, h3, h4, h5, h6 {
                color: var(--vscode-titleBar-activeForeground);
            }
            a {
                color: var(--vscode-textLink-foreground);
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }
            th, td {
                border: 1px solid var(--vscode-panel-border);
                padding: 8px 12px;
                text-align: left;
            }
            th {
                background-color: var(--vscode-titleBar-activeBackground);
            }
        </style>
    </head>
    <body>
        <h2>Dukat: Development Environment Assistant</h2>
        <div class="question">
            <p>Q: ${question}</p>
        </div>
        <div class="answer">
            ${markdownAnswer}
        </div>
    </body>
    </html>`;
}

/**
 * Called when the extension is deactivated
 */
function deactivate() {
    // Clean up resources
    console.log('Dukat: Development Environment Assistant is deactivated');
}

module.exports = {
    activate,
    deactivate
}
