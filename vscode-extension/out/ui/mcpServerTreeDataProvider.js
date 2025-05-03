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
exports.McpServerTreeItem = exports.McpServerTreeDataProvider = void 0;
const vscode = __importStar(require("vscode"));
const types_1 = require("../mcp-client/types");
/**
 * Tree data provider for MCP servers
 */
class McpServerTreeDataProvider {
    /**
     * Create a new MCP server tree data provider
     * @param serverManager MCP server manager
     * @param healthMonitor Server health monitor
     */
    constructor(serverManager, healthMonitor) {
        this.serverManager = serverManager;
        this.healthMonitor = healthMonitor;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        /**
         * Event that fires when the tree data changes
         */
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        // Listen for server changes
        serverManager.onDidChangeServers(() => {
            this._onDidChangeTreeData.fire(undefined);
        });
        // Listen for health updates if health monitor is provided
        if (healthMonitor) {
            healthMonitor.onDidUpdateHealth(() => {
                this._onDidChangeTreeData.fire(undefined);
            });
        }
    }
    /**
     * Get the tree item for an element
     * @param element Tree item
     * @returns Tree item
     */
    getTreeItem(element) {
        return element;
    }
    /**
     * Get the children of an element
     * @param element Parent element
     * @returns Children of the element
     */
    getChildren(element) {
        if (!element) {
            // Root level - show all servers
            const servers = this.serverManager.getServers();
            return Promise.resolve(servers.map(server => new McpServerTreeItem(server)));
        }
        // No children for server items
        return Promise.resolve([]);
    }
    /**
     * Refresh the tree
     */
    refresh() {
        this._onDidChangeTreeData.fire(undefined);
    }
}
exports.McpServerTreeDataProvider = McpServerTreeDataProvider;
/**
 * Tree item for an MCP server
 */
class McpServerTreeItem extends vscode.TreeItem {
    /**
     * Create a new MCP server tree item
     * @param server MCP server
     */
    constructor(server) {
        super(server.name, vscode.TreeItemCollapsibleState.None);
        this.server = server;
        // Set the context value for context menu filtering
        this.contextValue = `mcpServer-${server.status}${server.healthStatus ? `-${server.healthStatus}` : ''}`;
        // Set the description
        this.description = server.healthStatus
            ? `${server.status} (${server.healthStatus})`
            : server.status;
        // Set the tooltip
        let tooltip = `${server.name} (${server.status})
${server.description}
Repository: ${server.repoUrl}
Version: ${server.version}`;
        // Add health information if available
        if (server.healthStatus) {
            tooltip += `
Health: ${server.healthStatus}`;
            if (server.lastHealthCheck) {
                tooltip += `
Last health check: ${server.lastHealthCheck.toLocaleString()}`;
            }
        }
        // Add endpoint information if available
        if (server.endpoint) {
            tooltip += `
Endpoint: ${server.endpoint}`;
        }
        this.tooltip = tooltip;
        // Set the icon
        this.iconPath = this.getIconPath(server.status, server.healthStatus);
    }
    /**
     * Get the icon path for a server status
     * @param status Server status
     * @param healthStatus Server health status
     * @returns Icon path
     */
    getIconPath(status, healthStatus) {
        // If the server is running and unhealthy, show a warning icon
        if (status === types_1.McpServerStatus.Running && healthStatus === 'unhealthy') {
            return new vscode.ThemeIcon('warning');
        }
        // Otherwise, show an icon based on the server status
        switch (status) {
            case types_1.McpServerStatus.Running:
                return new vscode.ThemeIcon('play');
            case types_1.McpServerStatus.Stopped:
                return new vscode.ThemeIcon('stop');
            case types_1.McpServerStatus.Starting:
                return new vscode.ThemeIcon('sync');
            case types_1.McpServerStatus.Stopping:
                return new vscode.ThemeIcon('sync');
            case types_1.McpServerStatus.Error:
                return new vscode.ThemeIcon('error');
            default:
                return new vscode.ThemeIcon('question');
        }
    }
}
exports.McpServerTreeItem = McpServerTreeItem;
//# sourceMappingURL=mcpServerTreeDataProvider.js.map