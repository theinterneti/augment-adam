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
exports.McpServerManager = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const configuration_1 = require("../configuration");
const dockerContainerManager_1 = require("../container-manager/dockerContainerManager");
const githubRepoManager_1 = require("../github-integration/githubRepoManager");
const types_1 = require("./types");
/**
 * Manager for MCP servers
 */
class McpServerManager {
    /**
     * Create a new MCP server manager
     */
    constructor() {
        this.servers = new Map();
        this._onDidChangeServers = new vscode.EventEmitter();
        /**
         * Event that fires when the servers list changes
         */
        this.onDidChangeServers = this._onDidChangeServers.event;
        const config = (0, configuration_1.getConfiguration)();
        this.dockerManager = new dockerContainerManager_1.DockerContainerManager(config.mcpServers.dockerOptions);
        this.githubManager = new githubRepoManager_1.GitHubRepoManager(config.mcpServers.githubOptions);
        // Set up storage directory
        this.storageDir = this.getStorageDir(config.mcpServers.storagePath);
        this.configFile = path.join(this.storageDir, 'mcp-servers.json');
        // Create storage directory if it doesn't exist
        if (!fs.existsSync(this.storageDir)) {
            fs.mkdirSync(this.storageDir, { recursive: true });
        }
        // Load servers from config file
        this.loadServers();
    }
    /**
     * Get the storage directory
     * @param configPath Path from configuration
     * @returns Storage directory path
     */
    getStorageDir(configPath) {
        if (configPath) {
            return configPath;
        }
        // Use the extension's global storage path
        const context = vscode.extensions.getExtension('qwen-coder-assistant')?.extensionUri;
        if (context) {
            return path.join(context.fsPath, 'mcp-servers');
        }
        // Fallback to the workspace storage path
        if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
            return path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, '.vscode', 'mcp-servers');
        }
        throw new Error('Could not determine storage directory for MCP servers');
    }
    /**
     * Load servers from config file
     */
    loadServers() {
        try {
            if (fs.existsSync(this.configFile)) {
                const data = fs.readFileSync(this.configFile, 'utf8');
                const servers = JSON.parse(data);
                // Reset status for all servers
                for (const server of servers) {
                    server.status = types_1.McpServerStatus.Stopped;
                    server.logs = server.logs || [];
                    this.servers.set(server.id, server);
                }
                this._onDidChangeServers.fire();
            }
        }
        catch (error) {
            console.error('Error loading MCP servers:', error);
            vscode.window.showErrorMessage(`Error loading MCP servers: ${error}`);
        }
    }
    /**
     * Save servers to config file
     */
    saveServers() {
        try {
            const servers = Array.from(this.servers.values());
            fs.writeFileSync(this.configFile, JSON.stringify(servers, null, 2), 'utf8');
        }
        catch (error) {
            console.error('Error saving MCP servers:', error);
            vscode.window.showErrorMessage(`Error saving MCP servers: ${error}`);
        }
    }
    /**
     * Get all servers
     * @returns Array of MCP servers
     */
    getServers() {
        return Array.from(this.servers.values());
    }
    /**
     * Get a server by ID
     * @param id Server ID
     * @returns MCP server or undefined if not found
     */
    getServer(id) {
        return this.servers.get(id);
    }
    /**
     * Add a new server from a GitHub repository
     * @param repoUrl GitHub repository URL
     * @returns Promise that resolves to the new server
     */
    async addServerFromGitHub(repoUrl) {
        try {
            // Clone the repository
            const repoInfo = await this.githubManager.cloneRepository(repoUrl, this.storageDir);
            // Check if the repository has a Dockerfile
            if (!repoInfo.hasDockerfile) {
                throw new Error('Repository does not contain a Dockerfile');
            }
            // Check if the repository has an MCP schema file
            if (!repoInfo.hasMcpSchema) {
                throw new Error('Repository does not contain an MCP schema file');
            }
            // Read the schema file
            const schemaData = fs.readFileSync(repoInfo.schemaPath, 'utf8');
            let schema;
            // Parse the schema file based on its extension
            if (repoInfo.schemaPath.endsWith('.json')) {
                schema = JSON.parse(schemaData);
            }
            else if (repoInfo.schemaPath.endsWith('.yaml') || repoInfo.schemaPath.endsWith('.yml')) {
                // For YAML files, we would need a YAML parser
                // This is a placeholder - in a real implementation, you would use a YAML parser
                throw new Error('YAML schema files are not yet supported');
            }
            else {
                throw new Error('Unsupported schema file format');
            }
            // Validate the schema
            if (!schema.name || !schema.description || !schema.tools || !Array.isArray(schema.tools)) {
                throw new Error('Invalid MCP schema: missing required fields (name, description, tools)');
            }
            // Create a new server
            const server = {
                id: repoInfo.name,
                name: schema.name || repoInfo.name,
                description: schema.description || repoInfo.description || '',
                repoUrl,
                version: repoInfo.version || schema.version || '0.0.1',
                status: types_1.McpServerStatus.Stopped,
                type: types_1.McpServerType.Docker,
                autoStart: false,
                schema,
                logs: [],
                localPath: repoInfo.localPath,
                dockerfilePath: repoInfo.dockerfilePath
            };
            // Add the server to the list
            this.servers.set(server.id, server);
            // Save the servers
            this.saveServers();
            // Notify listeners
            this._onDidChangeServers.fire();
            // Add log entry
            server.logs.push(`[${new Date().toISOString()}] Server added from GitHub repository: ${repoUrl}`);
            return server;
        }
        catch (error) {
            console.error('Error adding server from GitHub:', error);
            throw error;
        }
    }
    /**
     * Remove a server
     * @param id Server ID
     * @returns Promise that resolves when the server is removed
     */
    async removeServer(id) {
        const server = this.servers.get(id);
        if (!server) {
            throw new Error(`Server ${id} not found`);
        }
        // Stop the server if it's running
        if (server.status === types_1.McpServerStatus.Running) {
            await this.stopServer(id);
        }
        // Remove the server from the list
        this.servers.delete(id);
        // Save the servers
        this.saveServers();
        // Notify listeners
        this._onDidChangeServers.fire();
    }
    /**
     * Start a server
     * @param id Server ID
     * @returns Promise that resolves when the server is started
     */
    async startServer(id) {
        const server = this.servers.get(id);
        if (!server) {
            throw new Error(`Server ${id} not found`);
        }
        // Update server status
        server.status = types_1.McpServerStatus.Starting;
        server.error = undefined;
        this._onDidChangeServers.fire();
        try {
            // Start the server based on its type
            if (server.type === types_1.McpServerType.Docker) {
                // Get the repository path
                const repoPath = server.localPath || path.join(this.storageDir, server.id);
                // Start the Docker container
                const containerId = await this.dockerManager.startContainer(server.id, repoPath, server.dockerfilePath);
                // Update server information
                server.containerId = containerId;
                server.status = types_1.McpServerStatus.Running;
                server.lastStarted = new Date();
                server.endpoint = await this.dockerManager.getContainerEndpoint(containerId);
                server.healthStatus = 'unknown';
                server.lastHealthCheck = new Date();
                // Add log entry
                server.logs.push(`[${new Date().toISOString()}] Server started with endpoint ${server.endpoint}`);
                // Check server health
                try {
                    const isHealthy = await this.checkServerHealth(server.id);
                    server.healthStatus = isHealthy ? 'healthy' : 'unhealthy';
                    if (!isHealthy) {
                        server.logs.push(`[${new Date().toISOString()}] Warning: Server health check failed`);
                    }
                    else {
                        server.logs.push(`[${new Date().toISOString()}] Server health check passed`);
                    }
                }
                catch (healthError) {
                    server.logs.push(`[${new Date().toISOString()}] Error checking server health: ${healthError}`);
                    server.healthStatus = 'unknown';
                }
                // Save the servers
                this.saveServers();
                // Notify listeners
                this._onDidChangeServers.fire();
            }
            else {
                throw new Error(`Unsupported server type: ${server.type}`);
            }
        }
        catch (error) {
            console.error(`Error starting server ${id}:`, error);
            // Update server status
            server.status = types_1.McpServerStatus.Error;
            server.error = `${error}`;
            // Add log entry
            server.logs.push(`[${new Date().toISOString()}] Error starting server: ${error}`);
            // Save the servers
            this.saveServers();
            // Notify listeners
            this._onDidChangeServers.fire();
            throw error;
        }
    }
    /**
     * Stop a server
     * @param id Server ID
     * @returns Promise that resolves when the server is stopped
     */
    async stopServer(id) {
        const server = this.servers.get(id);
        if (!server) {
            throw new Error(`Server ${id} not found`);
        }
        // Update server status
        server.status = types_1.McpServerStatus.Stopping;
        this._onDidChangeServers.fire();
        try {
            // Stop the server based on its type
            if (server.type === types_1.McpServerType.Docker) {
                // Stop the Docker container
                if (server.containerId) {
                    await this.dockerManager.stopContainer(server.containerId);
                }
                // Update server information
                server.status = types_1.McpServerStatus.Stopped;
                server.lastStopped = new Date();
                server.endpoint = undefined;
                // Add log entry
                server.logs.push(`[${new Date().toISOString()}] Server stopped`);
                // Save the servers
                this.saveServers();
                // Notify listeners
                this._onDidChangeServers.fire();
            }
            else {
                throw new Error(`Unsupported server type: ${server.type}`);
            }
        }
        catch (error) {
            console.error(`Error stopping server ${id}:`, error);
            // Update server status
            server.status = types_1.McpServerStatus.Error;
            server.error = `${error}`;
            // Add log entry
            server.logs.push(`[${new Date().toISOString()}] Error stopping server: ${error}`);
            // Save the servers
            this.saveServers();
            // Notify listeners
            this._onDidChangeServers.fire();
            throw error;
        }
    }
    /**
     * Restart a server
     * @param id Server ID
     * @returns Promise that resolves when the server is restarted
     */
    async restartServer(id) {
        await this.stopServer(id);
        await this.startServer(id);
    }
    /**
     * Get the logs for a server
     * @param id Server ID
     * @returns Server logs
     */
    getServerLogs(id) {
        const server = this.servers.get(id);
        if (!server) {
            throw new Error(`Server ${id} not found`);
        }
        return server.logs;
    }
    /**
     * Invoke a tool on a server
     * @param serverId Server ID
     * @param invocation Tool invocation
     * @param authHeaders Optional authentication headers
     * @returns Promise that resolves to the tool response
     */
    async invokeTool(serverId, invocation, authHeaders) {
        const server = this.servers.get(serverId);
        if (!server) {
            return {
                status: 'error',
                error: `Server ${serverId} not found`
            };
        }
        if (server.status !== types_1.McpServerStatus.Running) {
            return {
                status: 'error',
                error: `Server ${serverId} is not running (current status: ${server.status})`
            };
        }
        if (!server.endpoint) {
            return {
                status: 'error',
                error: `Server ${serverId} has no endpoint`
            };
        }
        try {
            // Log the invocation
            server.logs.push(`[${new Date().toISOString()}] Invoking tool ${invocation.tool} with parameters: ${JSON.stringify(invocation.parameters)}`);
            // Check server health before invoking the tool
            const isHealthy = await this.checkServerHealth(serverId);
            if (!isHealthy) {
                server.logs.push(`[${new Date().toISOString()}] Warning: Server health check failed before tool invocation`);
            }
            // Determine the correct endpoint URL
            let endpointUrl = `${server.endpoint}/tools/${invocation.tool}`;
            // Some MCP servers use a different endpoint format
            if (server.schema?.apiVersion === 'v2') {
                endpointUrl = `${server.endpoint}/v2/tools/${invocation.tool}`;
            }
            else if (server.schema?.apiVersion === 'v1') {
                endpointUrl = `${server.endpoint}/v1/tools/${invocation.tool}`;
            }
            // Prepare headers
            const headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            };
            // Add authentication headers if provided
            if (authHeaders) {
                Object.assign(headers, authHeaders);
                server.logs.push(`[${new Date().toISOString()}] Using authentication for tool invocation`);
            }
            // Invoke the tool on the server
            const response = await fetch(endpointUrl, {
                method: 'POST',
                headers,
                body: JSON.stringify(invocation.parameters),
                timeout: 30000 // 30 second timeout
            });
            if (!response.ok) {
                const errorText = await response.text();
                server.logs.push(`[${new Date().toISOString()}] Error invoking tool ${invocation.tool}: ${errorText}`);
                // Check for authentication errors
                if (response.status === 401 || response.status === 403) {
                    return {
                        status: 'error',
                        error: `Authentication error: ${errorText}`
                    };
                }
                return {
                    status: 'error',
                    error: `Error invoking tool: ${errorText}`
                };
            }
            const result = await response.json();
            // Log the result (truncated if too large)
            const resultStr = JSON.stringify(result);
            const truncatedResult = resultStr.length > 500 ? resultStr.substring(0, 500) + '...' : resultStr;
            server.logs.push(`[${new Date().toISOString()}] Tool ${invocation.tool} invocation successful. Result: ${truncatedResult}`);
            // Save the servers to persist the logs
            this.saveServers();
            return {
                status: 'success',
                result
            };
        }
        catch (error) {
            console.error(`Error invoking tool ${invocation.tool} on server ${serverId}:`, error);
            // Log the error
            server.logs.push(`[${new Date().toISOString()}] Error invoking tool ${invocation.tool}: ${error}`);
            // Save the servers to persist the logs
            this.saveServers();
            return {
                status: 'error',
                error: `${error}`
            };
        }
    }
    /**
     * Start all auto-start servers
     * @returns Promise that resolves when all auto-start servers are started
     */
    async startAutoStartServers() {
        const config = (0, configuration_1.getConfiguration)();
        // Get the list of servers to auto-start
        const autoStartList = config.mcpServers.autoStartList;
        // If auto-start is disabled, return
        if (!config.mcpServers.autoStart || autoStartList.length === 0) {
            return;
        }
        // Start each server in the list
        for (const serverId of autoStartList) {
            const server = this.servers.get(serverId);
            if (server && server.status === types_1.McpServerStatus.Stopped) {
                try {
                    await this.startServer(serverId);
                }
                catch (error) {
                    console.error(`Error auto-starting server ${serverId}:`, error);
                }
            }
        }
    }
    /**
     * Check the health of a server
     * @param id Server ID
     * @returns Promise that resolves to true if the server is healthy
     */
    async checkServerHealth(id) {
        const server = this.servers.get(id);
        if (!server) {
            throw new Error(`Server ${id} not found`);
        }
        if (server.status !== types_1.McpServerStatus.Running) {
            return false;
        }
        if (!server.endpoint) {
            return false;
        }
        try {
            // Try to fetch the server's health endpoint
            const response = await fetch(`${server.endpoint}/health`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                timeout: 5000 // 5 second timeout
            });
            // Update server health status
            server.healthStatus = response.ok ? 'healthy' : 'unhealthy';
            server.lastHealthCheck = new Date();
            // Save the servers
            this.saveServers();
            return response.ok;
        }
        catch (error) {
            console.error(`Error checking server health for ${id}:`, error);
            // Update server health status
            server.healthStatus = 'unhealthy';
            server.lastHealthCheck = new Date();
            // Save the servers
            this.saveServers();
            return false;
        }
    }
    /**
     * Check the health of all running servers
     * @returns Promise that resolves when all servers have been checked
     */
    async checkAllServersHealth() {
        for (const server of this.servers.values()) {
            if (server.status === types_1.McpServerStatus.Running) {
                try {
                    await this.checkServerHealth(server.id);
                }
                catch (error) {
                    console.error(`Error checking server health for ${server.id}:`, error);
                }
            }
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        // Stop all running servers
        for (const server of this.servers.values()) {
            if (server.status === types_1.McpServerStatus.Running) {
                try {
                    this.stopServer(server.id);
                }
                catch (error) {
                    console.error(`Error stopping server ${server.id} during disposal:`, error);
                }
            }
        }
        // Dispose of event emitter
        this._onDidChangeServers.dispose();
    }
}
exports.McpServerManager = McpServerManager;
//# sourceMappingURL=mcpServerManager.js.map