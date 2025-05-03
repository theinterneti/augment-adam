import * as vscode from 'vscode';
import * as semver from 'semver';
import { McpServer } from '../types';
import { McpServerManager } from '../mcpServerManager';
import { GitHubRepoManager } from '../../github-integration/githubRepoManager';

/**
 * Update information
 */
export interface UpdateInfo {
  serverId: string;
  serverName: string;
  currentVersion: string;
  latestVersion: string;
  releaseUrl: string;
  releaseDate: string;
  releaseNotes: string;
  updateAvailable: boolean;
}

/**
 * Update history entry
 */
export interface UpdateHistoryEntry {
  serverId: string;
  serverName: string;
  fromVersion: string;
  toVersion: string;
  updateDate: string;
  success: boolean;
  errorMessage?: string;
}

/**
 * Update manager for MCP servers
 */
export class UpdateManager implements vscode.Disposable {
  private serverManager: McpServerManager;
  private githubManager: GitHubRepoManager;
  private updateHistory: UpdateHistoryEntry[] = [];
  private _onDidCheckForUpdates = new vscode.EventEmitter<UpdateInfo[]>();
  private _onDidUpdateServer = new vscode.EventEmitter<UpdateHistoryEntry>();

  /**
   * Event that fires when updates are checked
   */
  public readonly onDidCheckForUpdates = this._onDidCheckForUpdates.event;

  /**
   * Event that fires when a server is updated
   */
  public readonly onDidUpdateServer = this._onDidUpdateServer.event;

  /**
   * Create a new update manager
   * @param serverManager MCP server manager
   * @param githubManager GitHub repository manager
   */
  constructor(serverManager: McpServerManager, githubManager: GitHubRepoManager) {
    this.serverManager = serverManager;
    this.githubManager = githubManager;
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this._onDidCheckForUpdates.dispose();
    this._onDidUpdateServer.dispose();
  }

  /**
   * Check for updates for all servers
   * @returns Promise that resolves to update information for all servers
   */
  public async checkForUpdates(): Promise<UpdateInfo[]> {
    const servers = this.serverManager.getServers();
    const updateInfos: UpdateInfo[] = [];

    for (const server of servers) {
      try {
        const updateInfo = await this.checkForServerUpdate(server.id);
        if (updateInfo) {
          updateInfos.push(updateInfo);
        }
      } catch (error) {
        console.error(`Error checking for updates for server ${server.id}:`, error);
      }
    }

    // Notify listeners
    this._onDidCheckForUpdates.fire(updateInfos);

    return updateInfos;
  }

  /**
   * Check for updates for a server
   * @param serverId Server ID
   * @returns Promise that resolves to update information for the server
   */
  public async checkForServerUpdate(serverId: string): Promise<UpdateInfo | undefined> {
    const server = this.serverManager.getServer(serverId);
    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    try {
      // Get the latest release from GitHub
      const repoInfo = this.parseGitHubUrl(server.repoUrl);
      if (!repoInfo) {
        throw new Error(`Invalid GitHub URL: ${server.repoUrl}`);
      }

      const latestRelease = await this.githubManager.getLatestRelease(repoInfo.owner, repoInfo.repo);
      if (!latestRelease) {
        return undefined;
      }

      // Check if an update is available
      const currentVersion = server.version;
      const latestVersion = latestRelease.tag_name.startsWith('v')
        ? latestRelease.tag_name.substring(1)
        : latestRelease.tag_name;

      const updateAvailable = this.isUpdateAvailable(currentVersion, latestVersion);

      // Create update information
      const updateInfo: UpdateInfo = {
        serverId: server.id,
        serverName: server.name,
        currentVersion,
        latestVersion,
        releaseUrl: latestRelease.html_url,
        releaseDate: latestRelease.published_at,
        releaseNotes: latestRelease.body || '',
        updateAvailable
      };

      return updateInfo;
    } catch (error) {
      console.error(`Error checking for updates for server ${serverId}:`, error);
      return undefined;
    }
  }

  /**
   * Update a server
   * @param serverId Server ID
   * @returns Promise that resolves when the server is updated
   */
  public async updateServer(serverId: string): Promise<void> {
    const server = this.serverManager.getServer(serverId);
    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    // Check if an update is available
    const updateInfo = await this.checkForServerUpdate(serverId);
    if (!updateInfo || !updateInfo.updateAvailable) {
      throw new Error(`No update available for server ${serverId}`);
    }

    // Create an update history entry
    const historyEntry: UpdateHistoryEntry = {
      serverId: server.id,
      serverName: server.name,
      fromVersion: server.version,
      toVersion: updateInfo.latestVersion,
      updateDate: new Date().toISOString(),
      success: false
    };

    try {
      // Stop the server if it's running
      const wasRunning = server.status === 'running';
      if (wasRunning) {
        await this.serverManager.stopServer(serverId);
      }

      // Update the server
      await this.serverManager.updateServer(serverId);

      // Restart the server if it was running
      if (wasRunning) {
        await this.serverManager.startServer(serverId);
      }

      // Update the history entry
      historyEntry.success = true;

      // Add the entry to the update history
      this.updateHistory.push(historyEntry);

      // Notify listeners
      this._onDidUpdateServer.fire(historyEntry);
    } catch (error) {
      // Update the history entry
      historyEntry.success = false;
      historyEntry.errorMessage = `${error}`;

      // Add the entry to the update history
      this.updateHistory.push(historyEntry);

      // Notify listeners
      this._onDidUpdateServer.fire(historyEntry);

      // Re-throw the error
      throw error;
    }
  }

  /**
   * Get the update history
   * @returns Update history
   */
  public getUpdateHistory(): UpdateHistoryEntry[] {
    return [...this.updateHistory];
  }

  /**
   * Get the update history for a server
   * @param serverId Server ID
   * @returns Update history for the server
   */
  public getServerUpdateHistory(serverId: string): UpdateHistoryEntry[] {
    return this.updateHistory.filter(entry => entry.serverId === serverId);
  }

  /**
   * Clear the update history
   */
  public clearUpdateHistory(): void {
    this.updateHistory = [];
  }

  /**
   * Check if an update is available
   * @param currentVersion Current version
   * @param latestVersion Latest version
   * @returns True if an update is available
   */
  private isUpdateAvailable(currentVersion: string, latestVersion: string): boolean {
    try {
      // Clean the versions to ensure they are valid semver
      const cleanCurrentVersion = semver.valid(semver.coerce(currentVersion));
      const cleanLatestVersion = semver.valid(semver.coerce(latestVersion));

      if (!cleanCurrentVersion || !cleanLatestVersion) {
        // If we can't parse the versions, assume no update is available
        return false;
      }

      // Compare the versions
      return semver.gt(cleanLatestVersion, cleanCurrentVersion);
    } catch (error) {
      console.error('Error comparing versions:', error);
      return false;
    }
  }

  /**
   * Parse a GitHub URL
   * @param url GitHub URL
   * @returns Owner and repository
   */
  private parseGitHubUrl(url: string): { owner: string; repo: string } | undefined {
    try {
      // Parse the URL
      const parsedUrl = new URL(url);
      if (parsedUrl.hostname !== 'github.com') {
        return undefined;
      }

      // Extract the owner and repository
      const parts = parsedUrl.pathname.split('/').filter(part => part.length > 0);
      if (parts.length < 2) {
        return undefined;
      }

      return {
        owner: parts[0],
        repo: parts[1]
      };
    } catch (error) {
      console.error('Error parsing GitHub URL:', error);
      return undefined;
    }
  }
}
