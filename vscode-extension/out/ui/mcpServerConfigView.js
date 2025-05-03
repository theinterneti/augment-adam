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
exports.McpServerConfigView = void 0;
const vscode = __importStar(require("vscode"));
/**
 * WebView panel for configuring MCP servers
 */
class McpServerConfigView {
    /**
     * Create a new MCP server configuration view
     * @param extensionUri Extension URI
     * @param serverManager MCP server manager
     * @param officialServersManager Official MCP servers manager
     * @param healthMonitor Server health monitor
     * @param serverId Optional server ID to configure
     */
    constructor(extensionUri, serverManager, officialServersManager, healthMonitor, serverId) {
        this._disposables = [];
        this._extensionUri = extensionUri;
        this._serverManager = serverManager;
        this._officialServersManager = officialServersManager;
        this._healthMonitor = healthMonitor;
        // Create the webview panel
        this._panel = vscode.window.createWebviewPanel(McpServerConfigView.viewType, 'MCP Server Configuration', vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
        });
        // Set the webview's initial html content
        this._panel.webview.html = this._getHtmlForWebview(this._panel.webview);
        // Set the current server if provided
        if (serverId) {
            this._currentServer = this._serverManager.getServer(serverId);
        }
        // Update the webview content
        this._updateWebview();
        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'saveConfig':
                    this._saveServerConfig(message.serverId, message.config);
                    return;
                case 'startServer':
                    this._startServer(message.serverId);
                    return;
                case 'stopServer':
                    this._stopServer(message.serverId);
                    return;
                case 'restartServer':
                    this._restartServer(message.serverId);
                    return;
                case 'checkHealth':
                    this._checkServerHealth(message.serverId);
                    return;
                case 'viewLogs':
                    this._viewServerLogs(message.serverId);
                    return;
                case 'addOfficialServer':
                    this._addOfficialServer(message.serverType);
                    return;
            }
        }, null, this._disposables);
        // Listen for server changes
        this._serverManager.onDidChangeServers(() => {
            // Update the current server if it's still valid
            if (this._currentServer) {
                this._currentServer = this._serverManager.getServer(this._currentServer.id);
            }
            this._updateWebview();
        }, null, this._disposables);
        // Listen for health updates
        this._healthMonitor.onDidUpdateHealth(serverId => {
            if (this._currentServer && this._currentServer.id === serverId) {
                this._updateWebview();
            }
        }, null, this._disposables);
    }
    /**
     * Create and show a new MCP server configuration view
     * @param extensionUri Extension URI
     * @param serverManager MCP server manager
     * @param officialServersManager Official MCP servers manager
     * @param healthMonitor Server health monitor
     * @param serverId Optional server ID to configure
     * @returns The created view
     */
    static createOrShow(extensionUri, serverManager, officialServersManager, healthMonitor, serverId) {
        return new McpServerConfigView(extensionUri, serverManager, officialServersManager, healthMonitor, serverId);
    }
    /**
     * Get the HTML for the webview
     * @param webview Webview
     * @returns HTML string
     */
    _getHtmlForWebview(webview) {
        // Local path to script and css for the webview
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'mcpServerConfig.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'mcpServerConfig.css'));
        // Use a nonce to only allow specific scripts to be run
        const nonce = getNonce();
        return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link href="${styleUri}" rel="stylesheet">
      <title>MCP Server Configuration</title>
    </head>
    <body>
      <div id="app">
        <h1>MCP Server Configuration</h1>
        <div id="server-selector"></div>
        <div id="server-config"></div>
        <div id="official-servers">
          <h2>Add Official MCP Servers</h2>
          <div class="button-container">
            <button id="add-github">Add GitHub MCP Server</button>
            <button id="add-docker">Add Docker MCP Server</button>
            <button id="add-git">Add Git MCP Server</button>
            <button id="add-memory">Add Memory MCP Server</button>
            <button id="add-filesystem">Add Filesystem MCP Server</button>
            <button id="add-all">Add All Official Servers</button>
          </div>
        </div>
      </div>
      <script nonce="${nonce}" src="${scriptUri}"></script>
    </body>
    </html>`;
    }
    /**
     * Update the webview content
     */
    _updateWebview() {
        if (!this._panel.visible) {
            return;
        }
        // Get all servers
        const servers = this._serverManager.getServers();
        // Send the servers to the webview
        this._panel.webview.postMessage({
            command: 'updateServers',
            servers,
            currentServerId: this._currentServer?.id
        });
    }
    /**
     * Save server configuration
     * @param serverId Server ID
     * @param config Server configuration
     */
    async _saveServerConfig(serverId, config) {
        try {
            const server = this._serverManager.getServer(serverId);
            if (!server) {
                throw new Error(`Server ${serverId} not found`);
            }
            // Update server properties
            server.name = config.name || server.name;
            server.description = config.description || server.description;
            server.autoStart = config.autoStart !== undefined ? config.autoStart : server.autoStart;
            // Save the servers
            this._serverManager.saveServers();
            // Show a success message
            vscode.window.showInformationMessage(`Server ${server.name} configuration saved`);
            // Update the webview
            this._updateWebview();
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error saving server configuration: ${error}`);
        }
    }
    /**
     * Start a server
     * @param serverId Server ID
     */
    async _startServer(serverId) {
        try {
            await this._serverManager.startServer(serverId);
            vscode.window.showInformationMessage(`Server ${serverId} started`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error starting server: ${error}`);
        }
    }
    /**
     * Stop a server
     * @param serverId Server ID
     */
    async _stopServer(serverId) {
        try {
            await this._serverManager.stopServer(serverId);
            vscode.window.showInformationMessage(`Server ${serverId} stopped`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error stopping server: ${error}`);
        }
    }
    /**
     * Restart a server
     * @param serverId Server ID
     */
    async _restartServer(serverId) {
        try {
            await this._serverManager.restartServer(serverId);
            vscode.window.showInformationMessage(`Server ${serverId} restarted`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error restarting server: ${error}`);
        }
    }
    /**
     * Check server health
     * @param serverId Server ID
     */
    async _checkServerHealth(serverId) {
        try {
            await this._healthMonitor.checkServerHealth(serverId);
            const server = this._serverManager.getServer(serverId);
            if (server) {
                vscode.window.showInformationMessage(`Server ${serverId} health: ${server.healthStatus || 'unknown'}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error checking server health: ${error}`);
        }
    }
    /**
     * View server logs
     * @param serverId Server ID
     */
    _viewServerLogs(serverId) {
        try {
            const server = this._serverManager.getServer(serverId);
            if (!server) {
                throw new Error(`Server ${serverId} not found`);
            }
            // Create a new untitled document with the logs
            vscode.workspace.openTextDocument({
                content: server.logs.join('\n'),
                language: 'log'
            }).then(doc => {
                vscode.window.showTextDocument(doc);
            });
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error viewing server logs: ${error}`);
        }
    }
    /**
     * Add an official MCP server
     * @param serverType Server type
     */
    async _addOfficialServer(serverType) {
        try {
            let serverId;
            switch (serverType.toUpperCase()) {
                case 'GITHUB':
                    serverId = await this._officialServersManager.addGitHubServer();
                    break;
                case 'DOCKER':
                    serverId = await this._officialServersManager.addDockerServer();
                    break;
                case 'GIT':
                    serverId = await this._officialServersManager.addGitServer();
                    break;
                case 'MEMORY':
                    serverId = await this._officialServersManager.addMemoryServer();
                    break;
                case 'FILESYSTEM':
                    serverId = await this._officialServersManager.addFilesystemServer();
                    break;
                case 'ALL':
                    const serverIds = await this._officialServersManager.addAllOfficialServers();
                    vscode.window.showInformationMessage(`Added ${serverIds.length} official MCP servers`);
                    return;
                default:
                    throw new Error(`Unknown server type: ${serverType}`);
            }
            // Set the current server to the newly added server
            this._currentServer = this._serverManager.getServer(serverId);
            // Show a success message
            vscode.window.showInformationMessage(`Added ${serverType} MCP server`);
            // Update the webview
            this._updateWebview();
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error adding ${serverType} MCP server: ${error}`);
        }
    }
    /**
     * Dispose of the view
     */
    dispose() {
        // Clean up resources
        this._panel.dispose();
        // Dispose of all disposables
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.McpServerConfigView = McpServerConfigView;
McpServerConfigView.viewType = 'qwenMcpServerConfig';
/**
 * Get a nonce string
 * @returns Random nonce string
 */
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=mcpServerConfigView.js.map