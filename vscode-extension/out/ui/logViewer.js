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
exports.LogViewer = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Log viewer for MCP servers
 */
class LogViewer {
    /**
     * Create a new log viewer
     * @param logger MCP logger
     */
    constructor(logger) {
        this.disposables = [];
        this.logger = logger;
    }
    /**
     * Show the log viewer for a server
     * @param server Server
     */
    show(server) {
        const serverId = server.id;
        this.currentServerId = serverId;
        // Create or show the panel
        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel('mcpServerLogs', `Logs: ${server.name}`, vscode.ViewColumn.Two, {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: []
            });
            // Handle panel disposal
            this.panel.onDidDispose(() => {
                this.panel = undefined;
                this.disposeWebviewResources();
            }, null, this.disposables);
            // Handle messages from the webview
            this.panel.webview.onDidReceiveMessage(message => this.handleWebviewMessage(message), null, this.disposables);
            // Listen for log events
            this.logger.onDidLog(entry => {
                if (this.panel && entry.serverId === this.currentServerId) {
                    this.panel.webview.postMessage({ type: 'newLog', entry });
                }
            }, null, this.disposables);
        }
        else {
            // Update the panel title
            this.panel.title = `Logs: ${server.name}`;
            this.currentServerId = serverId;
        }
        // Update the webview content
        this.updateWebviewContent(server);
        // Show the panel
        this.panel.reveal();
    }
    /**
     * Dispose of resources
     */
    dispose() {
        if (this.panel) {
            this.panel.dispose();
            this.panel = undefined;
        }
        this.disposeWebviewResources();
    }
    /**
     * Dispose of webview resources
     */
    disposeWebviewResources() {
        this.disposables.forEach(d => d.dispose());
        this.disposables = [];
    }
    /**
     * Update the webview content
     * @param server Server
     */
    updateWebviewContent(server) {
        if (!this.panel) {
            return;
        }
        // Get the log entries for the server
        const logEntries = this.logger.getLogEntries(server.id, 1000);
        // Set the webview content
        this.panel.webview.html = this.getWebviewContent(server, logEntries);
    }
    /**
     * Get the webview content
     * @param server Server
     * @param logEntries Log entries
     * @returns HTML content
     */
    getWebviewContent(server, logEntries) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Server Logs: ${server.name}</title>
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
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .server-info {
      margin-bottom: 10px;
    }
    .server-info table {
      border-collapse: collapse;
      width: 100%;
    }
    .server-info th, .server-info td {
      text-align: left;
      padding: 8px;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    .log-controls {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
    }
    .log-controls button {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 6px 12px;
      cursor: pointer;
      border-radius: 2px;
    }
    .log-controls button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    .log-controls select {
      background-color: var(--vscode-dropdown-background);
      color: var(--vscode-dropdown-foreground);
      border: 1px solid var(--vscode-dropdown-border);
      padding: 5px;
    }
    .log-container {
      flex: 1;
      overflow-y: auto;
      background-color: var(--vscode-editor-background);
      border: 1px solid var(--vscode-panel-border);
      padding: 10px;
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
    }
    .log-entry {
      margin-bottom: 5px;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .log-entry.DEBUG {
      color: var(--vscode-debugIcon-startForeground);
    }
    .log-entry.INFO {
      color: var(--vscode-foreground);
    }
    .log-entry.WARNING {
      color: var(--vscode-editorWarning-foreground);
    }
    .log-entry.ERROR {
      color: var(--vscode-editorError-foreground);
    }
    .log-timestamp {
      color: var(--vscode-descriptionForeground);
      margin-right: 10px;
    }
    .log-level {
      font-weight: bold;
      margin-right: 10px;
    }
    .log-message {
      margin-right: 10px;
    }
    .log-data {
      color: var(--vscode-textPreformat-foreground);
      background-color: var(--vscode-textCodeBlock-background);
      padding: 5px;
      margin-top: 5px;
      border-radius: 3px;
      font-family: var(--vscode-editor-font-family);
      white-space: pre;
      overflow-x: auto;
    }
    .empty-logs {
      text-align: center;
      padding: 20px;
      color: var(--vscode-descriptionForeground);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>MCP Server Logs: ${server.name}</h2>
    </div>
    
    <div class="server-info">
      <table>
        <tr>
          <th>Server ID</th>
          <td>${server.id}</td>
          <th>Status</th>
          <td>${server.status}</td>
        </tr>
        <tr>
          <th>Version</th>
          <td>${server.version}</td>
          <th>Health</th>
          <td>${server.healthStatus || 'unknown'}</td>
        </tr>
      </table>
    </div>
    
    <div class="log-controls">
      <button id="refresh-logs">Refresh</button>
      <button id="clear-logs">Clear Logs</button>
      <select id="log-level">
        <option value="DEBUG">Debug</option>
        <option value="INFO" selected>Info</option>
        <option value="WARNING">Warning</option>
        <option value="ERROR">Error</option>
      </select>
      <button id="export-logs">Export Logs</button>
    </div>
    
    <div class="log-container" id="log-container">
      ${this.renderLogEntries(logEntries)}
    </div>
  </div>
  
  <script>
    (function() {
      const vscode = acquireVsCodeApi();
      const logContainer = document.getElementById('log-container');
      const refreshButton = document.getElementById('refresh-logs');
      const clearButton = document.getElementById('clear-logs');
      const logLevelSelect = document.getElementById('log-level');
      const exportButton = document.getElementById('export-logs');
      
      // Store the current log entries
      let logEntries = ${JSON.stringify(logEntries)};
      
      // Set up event listeners
      refreshButton.addEventListener('click', () => {
        vscode.postMessage({ command: 'refresh' });
      });
      
      clearButton.addEventListener('click', () => {
        vscode.postMessage({ command: 'clear' });
      });
      
      logLevelSelect.addEventListener('change', () => {
        filterLogs();
      });
      
      exportButton.addEventListener('click', () => {
        vscode.postMessage({ command: 'export' });
      });
      
      // Handle messages from the extension
      window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.type) {
          case 'refreshLogs':
            logEntries = message.entries;
            renderLogs();
            break;
          case 'newLog':
            logEntries.push(message.entry);
            // Limit the number of entries to prevent performance issues
            if (logEntries.length > 1000) {
              logEntries.shift();
            }
            renderLogs();
            break;
          case 'clearLogs':
            logEntries = [];
            renderLogs();
            break;
        }
      });
      
      // Render the logs
      function renderLogs() {
        // Filter logs by level
        const filteredLogs = filterLogs();
        
        // Render the logs
        logContainer.innerHTML = filteredLogs.length > 0
          ? filteredLogs.map(entry => renderLogEntry(entry)).join('')
          : '<div class="empty-logs">No logs to display</div>';
        
        // Scroll to the bottom
        logContainer.scrollTop = logContainer.scrollHeight;
      }
      
      // Filter logs by level
      function filterLogs() {
        const selectedLevel = logLevelSelect.value;
        const levelPriority = {
          'DEBUG': 0,
          'INFO': 1,
          'WARNING': 2,
          'ERROR': 3
        };
        
        return logEntries.filter(entry => {
          return levelPriority[entry.level] >= levelPriority[selectedLevel];
        });
      }
      
      // Render a log entry
      function renderLogEntry(entry) {
        const timestamp = new Date(entry.timestamp).toLocaleTimeString();
        let html = \`
          <div class="log-entry \${entry.level}">
            <span class="log-timestamp">\${timestamp}</span>
            <span class="log-level">\${entry.level}</span>
            <span class="log-message">\${escapeHtml(entry.message)}</span>
        \`;
        
        if (entry.data) {
          let dataStr;
          try {
            dataStr = typeof entry.data === 'string'
              ? entry.data
              : JSON.stringify(entry.data, null, 2);
          } catch (error) {
            dataStr = \`[Error serializing data: \${error}]\`;
          }
          
          html += \`<div class="log-data">\${escapeHtml(dataStr)}</div>\`;
        }
        
        html += '</div>';
        return html;
      }
      
      // Escape HTML
      function escapeHtml(str) {
        return str
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#039;');
      }
    })();
  </script>
</body>
</html>`;
    }
    /**
     * Render log entries
     * @param entries Log entries
     * @returns HTML content
     */
    renderLogEntries(entries) {
        if (entries.length === 0) {
            return '<div class="empty-logs">No logs to display</div>';
        }
        return entries.map(entry => {
            const timestamp = new Date(entry.timestamp).toLocaleTimeString();
            let html = `
        <div class="log-entry ${entry.level}">
          <span class="log-timestamp">${timestamp}</span>
          <span class="log-level">${entry.level}</span>
          <span class="log-message">${this.escapeHtml(entry.message)}</span>
      `;
            if (entry.data) {
                let dataStr;
                try {
                    dataStr = typeof entry.data === 'string'
                        ? entry.data
                        : JSON.stringify(entry.data, null, 2);
                }
                catch (error) {
                    dataStr = `[Error serializing data: ${error}]`;
                }
                html += `<div class="log-data">${this.escapeHtml(dataStr)}</div>`;
            }
            html += '</div>';
            return html;
        }).join('');
    }
    /**
     * Escape HTML
     * @param str String to escape
     * @returns Escaped string
     */
    escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    /**
     * Handle a message from the webview
     * @param message Message
     */
    handleWebviewMessage(message) {
        if (!this.currentServerId) {
            return;
        }
        switch (message.command) {
            case 'refresh':
                this.refreshLogs();
                break;
            case 'clear':
                this.clearLogs();
                break;
            case 'export':
                this.exportLogs();
                break;
        }
    }
    /**
     * Refresh the logs
     */
    refreshLogs() {
        if (!this.panel || !this.currentServerId) {
            return;
        }
        const server = this.getServerById(this.currentServerId);
        if (!server) {
            return;
        }
        const logEntries = this.logger.getLogEntries(this.currentServerId, 1000);
        this.panel.webview.postMessage({ type: 'refreshLogs', entries: logEntries });
    }
    /**
     * Clear the logs
     */
    clearLogs() {
        if (!this.currentServerId) {
            return;
        }
        this.logger.clearLogs(this.currentServerId);
        if (this.panel) {
            this.panel.webview.postMessage({ type: 'clearLogs' });
        }
    }
    /**
     * Export the logs
     */
    async exportLogs() {
        if (!this.currentServerId) {
            return;
        }
        const server = this.getServerById(this.currentServerId);
        if (!server) {
            return;
        }
        // Get the log entries
        const logEntries = this.logger.getLogEntries(this.currentServerId, 10000);
        // Format the logs
        const formattedLogs = logEntries.map(entry => {
            const timestamp = new Date(entry.timestamp).toISOString();
            let line = `[${timestamp}] [${entry.level}] ${entry.message}`;
            if (entry.data) {
                try {
                    const dataStr = typeof entry.data === 'string'
                        ? entry.data
                        : JSON.stringify(entry.data, null, 2);
                    line += `\n${dataStr}`;
                }
                catch (error) {
                    line += `\n[Error serializing data: ${error}]`;
                }
            }
            return line;
        }).join('\n');
        // Show a save dialog
        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(`${server.name}_logs.txt`),
            filters: {
                'Text Files': ['txt'],
                'All Files': ['*']
            }
        });
        if (uri) {
            // Write the logs to the file
            await vscode.workspace.fs.writeFile(uri, Buffer.from(formattedLogs, 'utf8'));
            vscode.window.showInformationMessage(`Logs exported to ${uri.fsPath}`);
        }
    }
    /**
     * Get a server by ID
     * @param serverId Server ID
     * @returns Server or undefined
     */
    getServerById(serverId) {
        // This is a placeholder - in a real implementation, you would get the server from the MCP server manager
        // For now, we'll just return a dummy server
        return {
            id: serverId,
            name: 'Unknown Server',
            description: '',
            repoUrl: '',
            version: '',
            status: 'unknown',
            type: 'docker',
            autoStart: false,
            logs: []
        };
    }
}
exports.LogViewer = LogViewer;
//# sourceMappingURL=logViewer.js.map