import * as vscode from 'vscode';
import { McpServer, McpServerStatus } from './types';
import { McpServerManager } from './mcpServerManager';

/**
 * Health status of an MCP server
 */
export type ServerHealthStatus = 'healthy' | 'unhealthy' | 'unknown';

/**
 * Health information for an MCP server
 */
export interface ServerHealth {
  status: ServerHealthStatus;
  lastChecked: Date;
  error?: string;
}

/**
 * Monitor for MCP server health
 */
export class ServerHealthMonitor implements vscode.Disposable {
  private serverManager: McpServerManager;
  private intervalId: NodeJS.Timeout | undefined;
  private checkIntervalMs: number;
  private autoRecoveryEnabled: boolean;
  private _onDidUpdateHealth = new vscode.EventEmitter<string>();

  /**
   * Event that fires when a server's health is updated
   */
  public readonly onDidUpdateHealth = this._onDidUpdateHealth.event;

  /**
   * Create a new server health monitor
   * @param serverManager MCP server manager
   * @param checkIntervalMs Interval between health checks in milliseconds (default: 60000)
   * @param autoRecoveryEnabled Whether to automatically recover unhealthy servers (default: true)
   */
  constructor(
    serverManager: McpServerManager,
    checkIntervalMs: number = 60000,
    autoRecoveryEnabled: boolean = true
  ) {
    this.serverManager = serverManager;
    this.checkIntervalMs = checkIntervalMs;
    this.autoRecoveryEnabled = autoRecoveryEnabled;
  }

  /**
   * Start monitoring server health
   */
  public start(): void {
    // Stop any existing interval
    this.stop();

    // Start a new interval
    this.intervalId = setInterval(() => this.checkAllServersHealth(), this.checkIntervalMs);

    // Do an initial health check
    this.checkAllServersHealth();
  }

  /**
   * Stop monitoring server health
   */
  public stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  /**
   * Check the health of all running servers
   */
  private async checkAllServersHealth(): Promise<void> {
    const servers = this.serverManager.getServers();
    
    for (const server of servers) {
      if (server.status === McpServerStatus.Running) {
        await this.checkServerHealth(server.id);
      }
    }
  }

  /**
   * Check the health of a server
   * @param serverId Server ID
   */
  public async checkServerHealth(serverId: string): Promise<void> {
    try {
      const isHealthy = await this.serverManager.checkServerHealth(serverId);
      const server = this.serverManager.getServer(serverId);
      
      if (!server) {
        return;
      }

      // Notify listeners
      this._onDidUpdateHealth.fire(serverId);

      // If the server is unhealthy and auto-recovery is enabled, try to recover it
      if (!isHealthy && this.autoRecoveryEnabled && server.status === McpServerStatus.Running) {
        await this.recoverServer(serverId);
      }
    } catch (error) {
      console.error(`Error checking health for server ${serverId}:`, error);
    }
  }

  /**
   * Recover an unhealthy server
   * @param serverId Server ID
   */
  private async recoverServer(serverId: string): Promise<void> {
    try {
      const server = this.serverManager.getServer(serverId);
      if (!server) {
        return;
      }

      console.log(`Attempting to recover unhealthy server ${serverId}`);
      
      // Add log entry
      server.logs.push(`[${new Date().toISOString()}] Server is unhealthy, attempting recovery...`);
      
      // Restart the server
      await this.serverManager.restartServer(serverId);
      
      // Add log entry
      server.logs.push(`[${new Date().toISOString()}] Server recovery completed`);
      
      // Check health again after recovery
      setTimeout(() => this.checkServerHealth(serverId), 5000);
    } catch (error) {
      console.error(`Error recovering server ${serverId}:`, error);
      
      const server = this.serverManager.getServer(serverId);
      if (server) {
        server.logs.push(`[${new Date().toISOString()}] Error during server recovery: ${error}`);
      }
    }
  }

  /**
   * Set whether auto-recovery is enabled
   * @param enabled Whether auto-recovery is enabled
   */
  public setAutoRecoveryEnabled(enabled: boolean): void {
    this.autoRecoveryEnabled = enabled;
  }

  /**
   * Set the health check interval
   * @param intervalMs Interval between health checks in milliseconds
   */
  public setCheckInterval(intervalMs: number): void {
    this.checkIntervalMs = intervalMs;
    
    // Restart the interval with the new timing
    if (this.intervalId) {
      this.start();
    }
  }

  /**
   * Dispose of the health monitor
   */
  public dispose(): void {
    this.stop();
    this._onDidUpdateHealth.dispose();
  }
}
