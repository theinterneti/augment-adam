import * as vscode from 'vscode';
import { McpServerManager } from '../mcp-client/mcpServerManager';
import { ServerHealthMonitor } from '../mcp-client/serverHealthMonitor';
import { McpServer, McpServerStatus } from '../mcp-client/types';

/**
 * Tree data provider for MCP servers
 */
export class McpServerTreeDataProvider implements vscode.TreeDataProvider<McpServerTreeItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<McpServerTreeItem | undefined>();

  /**
   * Event that fires when the tree data changes
   */
  public readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  /**
   * Create a new MCP server tree data provider
   * @param serverManager MCP server manager
   * @param healthMonitor Server health monitor
   */
  constructor(
    private serverManager: McpServerManager,
    private healthMonitor?: ServerHealthMonitor
  ) {
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
  public getTreeItem(element: McpServerTreeItem): vscode.TreeItem {
    return element;
  }

  /**
   * Get the children of an element
   * @param element Parent element
   * @returns Children of the element
   */
  public getChildren(element?: McpServerTreeItem): Thenable<McpServerTreeItem[]> {
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
  public refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }
}

/**
 * Tree item for an MCP server
 */
export class McpServerTreeItem extends vscode.TreeItem {
  /**
   * Create a new MCP server tree item
   * @param server MCP server
   */
  constructor(public readonly server: McpServer) {
    super(server.name, vscode.TreeItemCollapsibleState.None);

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
  private getIconPath(status: McpServerStatus, healthStatus?: string): vscode.ThemeIcon {
    // If the server is running and unhealthy, show a warning icon
    if (status === McpServerStatus.Running && healthStatus === 'unhealthy') {
      return new vscode.ThemeIcon('warning');
    }

    // Otherwise, show an icon based on the server status
    switch (status) {
      case McpServerStatus.Running:
        return new vscode.ThemeIcon('play');
      case McpServerStatus.Stopped:
        return new vscode.ThemeIcon('stop');
      case McpServerStatus.Starting:
        return new vscode.ThemeIcon('sync');
      case McpServerStatus.Stopping:
        return new vscode.ThemeIcon('sync');
      case McpServerStatus.Error:
        return new vscode.ThemeIcon('error');
      default:
        return new vscode.ThemeIcon('question');
    }
  }
}
