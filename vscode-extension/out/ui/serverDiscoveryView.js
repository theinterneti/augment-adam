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
exports.ServerDiscoveryView = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Server discovery view for MCP servers
 */
class ServerDiscoveryView {
    /**
     * Create a new server discovery view
     * @param discovery Server discovery
     * @param serverManager MCP server manager
     */
    constructor(discovery, serverManager) {
        this.disposables = [];
        this.searchResults = [];
        this.discovery = discovery;
        this.serverManager = serverManager;
        // Listen for server discovery events
        this.disposables.push(this.discovery.onDidDiscoverServers(results => {
            this.searchResults = results;
            this.updateWebviewContent();
        }));
        // Listen for server manager events
        this.disposables.push(this.serverManager.onDidChangeServers(() => {
            this.updateWebviewContent();
        }));
    }
    /**
     * Create or show the server discovery view
     * @param extensionUri Extension URI
     */
    static createOrShow(extensionUri, discovery, serverManager) {
        const view = new ServerDiscoveryView(discovery, serverManager);
        view.createOrShowPanel(extensionUri);
        return view;
    }
    /**
     * Create or show the panel
     * @param extensionUri Extension URI
     */
    createOrShowPanel(extensionUri) {
        // If we already have a panel, show it
        if (this.panel) {
            this.panel.reveal();
            return;
        }
        // Create a new panel
        this.panel = vscode.window.createWebviewPanel('mcpServerDiscovery', 'MCP Server Discovery', vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [extensionUri]
        });
        // Set the webview's initial content
        this.panel.webview.html = this.getWebviewContent();
        // Handle messages from the webview
        this.panel.webview.onDidReceiveMessage(message => this.handleWebviewMessage(message), null, this.disposables);
        // Handle panel disposal
        this.panel.onDidDispose(() => {
            this.panel = undefined;
            this.disposeWebviewResources();
        }, null, this.disposables);
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
     */
    updateWebviewContent() {
        if (!this.panel) {
            return;
        }
        this.panel.webview.html = this.getWebviewContent();
    }
    /**
     * Get the webview content
     * @returns HTML content
     */
    getWebviewContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Server Discovery</title>
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
      margin-bottom: 20px;
    }
    .search-container {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }
    .search-input {
      flex: 1;
      background-color: var(--vscode-input-background);
      color: var(--vscode-input-foreground);
      border: 1px solid var(--vscode-input-border);
      padding: 6px 12px;
      border-radius: 2px;
    }
    .search-button {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 6px 12px;
      cursor: pointer;
      border-radius: 2px;
    }
    .search-button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    .filters {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
    }
    .filter-group {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .results-container {
      flex: 1;
      overflow-y: auto;
      background-color: var(--vscode-editor-background);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 2px;
    }
    .results-table {
      width: 100%;
      border-collapse: collapse;
    }
    .results-table th, .results-table td {
      text-align: left;
      padding: 8px;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    .results-table th {
      background-color: var(--vscode-editor-background);
      position: sticky;
      top: 0;
      z-index: 1;
    }
    .results-table tr:hover {
      background-color: var(--vscode-list-hoverBackground);
    }
    .server-name {
      font-weight: bold;
    }
    .server-description {
      color: var(--vscode-descriptionForeground);
      max-width: 300px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .server-version {
      font-family: var(--vscode-editor-font-family);
    }
    .server-source {
      text-transform: capitalize;
    }
    .server-official {
      color: var(--vscode-terminal-ansiGreen);
    }
    .server-actions {
      display: flex;
      gap: 5px;
    }
    .action-button {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 4px 8px;
      cursor: pointer;
      border-radius: 2px;
      font-size: 12px;
    }
    .action-button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    .action-button.installed {
      background-color: var(--vscode-badge-background);
      cursor: default;
    }
    .empty-results {
      text-align: center;
      padding: 20px;
      color: var(--vscode-descriptionForeground);
    }
    .loading {
      text-align: center;
      padding: 20px;
    }
    .spinner {
      width: 30px;
      height: 30px;
      border: 3px solid var(--vscode-button-background);
      border-top: 3px solid var(--vscode-editor-background);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 10px;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>MCP Server Discovery</h2>
    </div>
    
    <div class="search-container">
      <input type="text" id="search-input" class="search-input" placeholder="Search for MCP servers...">
      <button id="search-button" class="search-button">Search</button>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <input type="checkbox" id="filter-registry" checked>
        <label for="filter-registry">Registry</label>
      </div>
      <div class="filter-group">
        <input type="checkbox" id="filter-github" checked>
        <label for="filter-github">GitHub</label>
      </div>
      <div class="filter-group">
        <input type="checkbox" id="filter-local" checked>
        <label for="filter-local">Local</label>
      </div>
      <div class="filter-group">
        <input type="checkbox" id="filter-network" checked>
        <label for="filter-network">Network</label>
      </div>
      <div class="filter-group">
        <input type="checkbox" id="filter-official">
        <label for="filter-official">Official Only</label>
      </div>
    </div>
    
    <div class="results-container" id="results-container">
      ${this.renderSearchResults()}
    </div>
  </div>
  
  <script>
    (function() {
      const vscode = acquireVsCodeApi();
      const searchInput = document.getElementById('search-input');
      const searchButton = document.getElementById('search-button');
      const filterRegistry = document.getElementById('filter-registry');
      const filterGitHub = document.getElementById('filter-github');
      const filterLocal = document.getElementById('filter-local');
      const filterNetwork = document.getElementById('filter-network');
      const filterOfficial = document.getElementById('filter-official');
      const resultsContainer = document.getElementById('results-container');
      
      // Set up event listeners
      searchButton.addEventListener('click', () => {
        search();
      });
      
      searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          search();
        }
      });
      
      filterRegistry.addEventListener('change', () => {
        search();
      });
      
      filterGitHub.addEventListener('change', () => {
        search();
      });
      
      filterLocal.addEventListener('change', () => {
        search();
      });
      
      filterNetwork.addEventListener('change', () => {
        search();
      });
      
      filterOfficial.addEventListener('change', () => {
        search();
      });
      
      // Set up action button event listeners
      document.addEventListener('click', (event) => {
        if (event.target.classList.contains('action-button') && !event.target.classList.contains('installed')) {
          const serverId = event.target.dataset.serverId;
          const repoUrl = event.target.dataset.repoUrl;
          
          vscode.postMessage({
            command: 'addServer',
            repoUrl
          });
          
          // Show loading state
          event.target.textContent = 'Adding...';
          event.target.disabled = true;
        }
      });
      
      // Search function
      function search() {
        const query = searchInput.value.trim();
        const includeRegistry = filterRegistry.checked;
        const includeGitHub = filterGitHub.checked;
        const includeLocal = filterLocal.checked;
        const includeNetwork = filterNetwork.checked;
        const officialOnly = filterOfficial.checked;
        
        // Show loading state
        resultsContainer.innerHTML = \`
          <div class="loading">
            <div class="spinner"></div>
            <p>Searching for MCP servers...</p>
          </div>
        \`;
        
        vscode.postMessage({
          command: 'search',
          query,
          includeRegistry,
          includeGitHub,
          includeLocal,
          includeNetwork,
          officialOnly
        });
      }
      
      // Initial search
      search();
    })();
  </script>
</body>
</html>`;
    }
    /**
     * Render search results
     * @returns HTML content
     */
    renderSearchResults() {
        if (this.searchResults.length === 0) {
            return `
        <div class="empty-results">
          <p>No MCP servers found. Try a different search query or adjust the filters.</p>
        </div>
      `;
        }
        // Get installed servers
        const installedServers = this.serverManager.getServers();
        const installedRepoUrls = new Set(installedServers.map(server => server.repoUrl));
        return `
      <table class="results-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Version</th>
            <th>Source</th>
            <th>Official</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${this.searchResults.map(result => `
            <tr>
              <td class="server-name">${this.escapeHtml(result.name)}</td>
              <td class="server-description" title="${this.escapeHtml(result.description)}">${this.escapeHtml(result.description)}</td>
              <td class="server-version">${this.escapeHtml(result.version)}</td>
              <td class="server-source">${result.source}</td>
              <td class="server-official">${result.official ? '✓' : ''}</td>
              <td class="server-actions">
                ${result.installed
            ? `<button class="action-button installed" disabled>Installed</button>`
            : `<button class="action-button" data-repo-url="${this.escapeHtml(result.repoUrl)}">Add Server</button>`}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
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
    async handleWebviewMessage(message) {
        switch (message.command) {
            case 'search':
                await this.handleSearch(message);
                break;
            case 'addServer':
                await this.handleAddServer(message);
                break;
        }
    }
    /**
     * Handle a search message
     * @param message Message
     */
    async handleSearch(message) {
        try {
            const options = {
                includeRegistry: message.includeRegistry,
                includeGitHub: message.includeGitHub,
                includeLocal: message.includeLocal,
                includeNetwork: message.includeNetwork,
                searchQuery: message.query,
                maxResults: 100
            };
            // Discover servers
            const results = await this.discovery.discoverServers(options);
            // Filter by official if needed
            this.searchResults = message.officialOnly
                ? results.filter(result => result.official)
                : results;
            // Update the webview content
            this.updateWebviewContent();
        }
        catch (error) {
            console.error('Error searching for servers:', error);
            vscode.window.showErrorMessage(`Error searching for servers: ${error}`);
        }
    }
    /**
     * Handle an add server message
     * @param message Message
     */
    async handleAddServer(message) {
        try {
            const repoUrl = message.repoUrl;
            // Add the server
            await this.serverManager.addServerFromGitHub(repoUrl);
            // Show a success message
            vscode.window.showInformationMessage(`Added MCP server from ${repoUrl}`);
            // Update the search results
            const result = this.searchResults.find(r => r.repoUrl === repoUrl);
            if (result) {
                result.installed = true;
            }
            // Update the webview content
            this.updateWebviewContent();
        }
        catch (error) {
            console.error('Error adding server:', error);
            vscode.window.showErrorMessage(`Error adding server: ${error}`);
        }
    }
}
exports.ServerDiscoveryView = ServerDiscoveryView;
//# sourceMappingURL=serverDiscoveryView.js.map