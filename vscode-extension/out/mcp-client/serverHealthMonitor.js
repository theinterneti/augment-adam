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
exports.ServerHealthMonitor = void 0;
const vscode = __importStar(require("vscode"));
const types_1 = require("./types");
/**
 * Monitor for MCP server health
 */
class ServerHealthMonitor {
    /**
     * Create a new server health monitor
     * @param serverManager MCP server manager
     * @param checkIntervalMs Interval between health checks in milliseconds (default: 60000)
     * @param autoRecoveryEnabled Whether to automatically recover unhealthy servers (default: true)
     */
    constructor(serverManager, checkIntervalMs = 60000, autoRecoveryEnabled = true) {
        this._onDidUpdateHealth = new vscode.EventEmitter();
        /**
         * Event that fires when a server's health is updated
         */
        this.onDidUpdateHealth = this._onDidUpdateHealth.event;
        this.serverManager = serverManager;
        this.checkIntervalMs = checkIntervalMs;
        this.autoRecoveryEnabled = autoRecoveryEnabled;
    }
    /**
     * Start monitoring server health
     */
    start() {
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
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = undefined;
        }
    }
    /**
     * Check the health of all running servers
     */
    async checkAllServersHealth() {
        const servers = this.serverManager.getServers();
        for (const server of servers) {
            if (server.status === types_1.McpServerStatus.Running) {
                await this.checkServerHealth(server.id);
            }
        }
    }
    /**
     * Check the health of a server
     * @param serverId Server ID
     */
    async checkServerHealth(serverId) {
        try {
            const isHealthy = await this.serverManager.checkServerHealth(serverId);
            const server = this.serverManager.getServer(serverId);
            if (!server) {
                return;
            }
            // Notify listeners
            this._onDidUpdateHealth.fire(serverId);
            // If the server is unhealthy and auto-recovery is enabled, try to recover it
            if (!isHealthy && this.autoRecoveryEnabled && server.status === types_1.McpServerStatus.Running) {
                await this.recoverServer(serverId);
            }
        }
        catch (error) {
            console.error(`Error checking health for server ${serverId}:`, error);
        }
    }
    /**
     * Recover an unhealthy server
     * @param serverId Server ID
     */
    async recoverServer(serverId) {
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
        }
        catch (error) {
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
    setAutoRecoveryEnabled(enabled) {
        this.autoRecoveryEnabled = enabled;
    }
    /**
     * Set the health check interval
     * @param intervalMs Interval between health checks in milliseconds
     */
    setCheckInterval(intervalMs) {
        this.checkIntervalMs = intervalMs;
        // Restart the interval with the new timing
        if (this.intervalId) {
            this.start();
        }
    }
    /**
     * Dispose of the health monitor
     */
    dispose() {
        this.stop();
        this._onDidUpdateHealth.dispose();
    }
}
exports.ServerHealthMonitor = ServerHealthMonitor;
//# sourceMappingURL=serverHealthMonitor.js.map