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
exports.UpdateManager = void 0;
const vscode = __importStar(require("vscode"));
const semver = __importStar(require("semver"));
/**
 * Update manager for MCP servers
 */
class UpdateManager {
    /**
     * Create a new update manager
     * @param serverManager MCP server manager
     * @param githubManager GitHub repository manager
     */
    constructor(serverManager, githubManager) {
        this.updateHistory = [];
        this._onDidCheckForUpdates = new vscode.EventEmitter();
        this._onDidUpdateServer = new vscode.EventEmitter();
        /**
         * Event that fires when updates are checked
         */
        this.onDidCheckForUpdates = this._onDidCheckForUpdates.event;
        /**
         * Event that fires when a server is updated
         */
        this.onDidUpdateServer = this._onDidUpdateServer.event;
        this.serverManager = serverManager;
        this.githubManager = githubManager;
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this._onDidCheckForUpdates.dispose();
        this._onDidUpdateServer.dispose();
    }
    /**
     * Check for updates for all servers
     * @returns Promise that resolves to update information for all servers
     */
    async checkForUpdates() {
        const servers = this.serverManager.getServers();
        const updateInfos = [];
        for (const server of servers) {
            try {
                const updateInfo = await this.checkForServerUpdate(server.id);
                if (updateInfo) {
                    updateInfos.push(updateInfo);
                }
            }
            catch (error) {
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
    async checkForServerUpdate(serverId) {
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
            const updateInfo = {
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
        }
        catch (error) {
            console.error(`Error checking for updates for server ${serverId}:`, error);
            return undefined;
        }
    }
    /**
     * Update a server
     * @param serverId Server ID
     * @returns Promise that resolves when the server is updated
     */
    async updateServer(serverId) {
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
        const historyEntry = {
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
        }
        catch (error) {
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
    getUpdateHistory() {
        return [...this.updateHistory];
    }
    /**
     * Get the update history for a server
     * @param serverId Server ID
     * @returns Update history for the server
     */
    getServerUpdateHistory(serverId) {
        return this.updateHistory.filter(entry => entry.serverId === serverId);
    }
    /**
     * Clear the update history
     */
    clearUpdateHistory() {
        this.updateHistory = [];
    }
    /**
     * Check if an update is available
     * @param currentVersion Current version
     * @param latestVersion Latest version
     * @returns True if an update is available
     */
    isUpdateAvailable(currentVersion, latestVersion) {
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
        }
        catch (error) {
            console.error('Error comparing versions:', error);
            return false;
        }
    }
    /**
     * Parse a GitHub URL
     * @param url GitHub URL
     * @returns Owner and repository
     */
    parseGitHubUrl(url) {
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
        }
        catch (error) {
            console.error('Error parsing GitHub URL:', error);
            return undefined;
        }
    }
}
exports.UpdateManager = UpdateManager;
//# sourceMappingURL=updateManager.js.map