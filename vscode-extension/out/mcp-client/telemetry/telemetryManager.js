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
exports.TelemetryManager = exports.TelemetryEventType = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Telemetry event type
 */
var TelemetryEventType;
(function (TelemetryEventType) {
    TelemetryEventType["SERVER_START"] = "server_start";
    TelemetryEventType["SERVER_STOP"] = "server_stop";
    TelemetryEventType["SERVER_ERROR"] = "server_error";
    TelemetryEventType["TOOL_INVOCATION"] = "tool_invocation";
    TelemetryEventType["TOOL_ERROR"] = "tool_error";
    TelemetryEventType["HEALTH_CHECK"] = "health_check";
    TelemetryEventType["AUTHENTICATION"] = "authentication";
})(TelemetryEventType || (exports.TelemetryEventType = TelemetryEventType = {}));
/**
 * Telemetry manager for MCP servers
 */
class TelemetryManager {
    /**
     * Create a new telemetry manager
     * @param context Extension context
     * @param options Telemetry options
     */
    constructor(context, options = {}) {
        this.events = new Map();
        this.stats = new Map();
        this._onDidCollectTelemetry = new vscode.EventEmitter();
        /**
         * Event that fires when telemetry is collected
         */
        this.onDidCollectTelemetry = this._onDidCollectTelemetry.event;
        this.telemetryEnabled = options.telemetryEnabled !== false;
        this.telemetryDir = options.telemetryDir || path.join(context.globalStorageUri.fsPath, 'telemetry');
        this.maxEventsPerFile = options.maxEventsPerFile || 1000;
        // Create telemetry directory if it doesn't exist
        if (this.telemetryEnabled && !fs.existsSync(this.telemetryDir)) {
            fs.mkdirSync(this.telemetryDir, { recursive: true });
        }
        // Load existing telemetry data
        this.loadTelemetry();
        // Register the telemetry manager with the extension context
        context.subscriptions.push(this);
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this._onDidCollectTelemetry.dispose();
        // Save telemetry data
        this.saveTelemetry();
    }
    /**
     * Track a server start event
     * @param server Server
     */
    trackServerStart(server) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: TelemetryEventType.SERVER_START,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version
        };
        this.trackEvent(event);
        this.updateStats(server.id, stats => {
            stats.startCount++;
            stats.lastStarted = event.timestamp;
        });
    }
    /**
     * Track a server stop event
     * @param server Server
     * @param duration Duration in milliseconds
     */
    trackServerStop(server, duration) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: TelemetryEventType.SERVER_STOP,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version,
            duration
        };
        this.trackEvent(event);
        this.updateStats(server.id, stats => {
            stats.stopCount++;
            stats.lastStopped = event.timestamp;
            stats.uptime += duration;
        });
    }
    /**
     * Track a server error event
     * @param server Server
     * @param errorMessage Error message
     */
    trackServerError(server, errorMessage) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: TelemetryEventType.SERVER_ERROR,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version,
            errorMessage
        };
        this.trackEvent(event);
        this.updateStats(server.id, stats => {
            stats.errorCount++;
            stats.lastError = event.timestamp;
        });
    }
    /**
     * Track a tool invocation event
     * @param server Server
     * @param toolName Tool name
     * @param toolParameters Tool parameters
     * @param success Whether the invocation was successful
     * @param errorMessage Error message if the invocation failed
     * @param duration Duration in milliseconds
     */
    trackToolInvocation(server, toolName, toolParameters, success, errorMessage, duration) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: success ? TelemetryEventType.TOOL_INVOCATION : TelemetryEventType.TOOL_ERROR,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version,
            toolName,
            toolParameters,
            success,
            errorMessage,
            duration
        };
        this.trackEvent(event);
        this.updateStats(server.id, stats => {
            if (success) {
                stats.toolInvocations++;
                stats.lastToolInvocation = event.timestamp;
            }
            else {
                stats.toolErrors++;
            }
            // Update tool usage
            stats.toolUsage[toolName] = (stats.toolUsage[toolName] || 0) + 1;
        });
    }
    /**
     * Track a health check event
     * @param server Server
     * @param healthStatus Health status
     */
    trackHealthCheck(server, healthStatus) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: TelemetryEventType.HEALTH_CHECK,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version,
            healthStatus
        };
        this.trackEvent(event);
        this.updateStats(server.id, stats => {
            stats.healthChecks++;
            stats.lastHealthCheck = event.timestamp;
        });
    }
    /**
     * Track an authentication event
     * @param server Server
     * @param authType Authentication type
     * @param success Whether the authentication was successful
     * @param errorMessage Error message if the authentication failed
     */
    trackAuthentication(server, authType, success, errorMessage) {
        if (!this.telemetryEnabled) {
            return;
        }
        const event = {
            type: TelemetryEventType.AUTHENTICATION,
            timestamp: new Date().toISOString(),
            serverId: server.id,
            serverName: server.name,
            serverVersion: server.version,
            authType,
            success,
            errorMessage
        };
        this.trackEvent(event);
    }
    /**
     * Get usage statistics for all servers
     * @returns Server usage statistics
     */
    getUsageStats() {
        return Array.from(this.stats.values());
    }
    /**
     * Get usage statistics for a server
     * @param serverId Server ID
     * @returns Server usage statistics
     */
    getServerUsageStats(serverId) {
        return this.stats.get(serverId);
    }
    /**
     * Get telemetry events for a server
     * @param serverId Server ID
     * @param maxEvents Maximum number of events to return
     * @returns Telemetry events
     */
    getServerEvents(serverId, maxEvents = 100) {
        const events = this.events.get(serverId) || [];
        return events.slice(-maxEvents);
    }
    /**
     * Clear telemetry data for a server
     * @param serverId Server ID
     */
    clearServerTelemetry(serverId) {
        this.events.delete(serverId);
        this.stats.delete(serverId);
        // Delete telemetry files
        const eventsFilePath = this.getEventsFilePath(serverId);
        const statsFilePath = this.getStatsFilePath(serverId);
        if (fs.existsSync(eventsFilePath)) {
            fs.unlinkSync(eventsFilePath);
        }
        if (fs.existsSync(statsFilePath)) {
            fs.unlinkSync(statsFilePath);
        }
    }
    /**
     * Enable or disable telemetry
     * @param enabled Whether telemetry is enabled
     */
    setTelemetryEnabled(enabled) {
        this.telemetryEnabled = enabled;
        if (enabled) {
            // Create telemetry directory if it doesn't exist
            if (!fs.existsSync(this.telemetryDir)) {
                fs.mkdirSync(this.telemetryDir, { recursive: true });
            }
            // Load existing telemetry data
            this.loadTelemetry();
        }
        else {
            // Clear in-memory telemetry data
            this.events.clear();
            this.stats.clear();
        }
    }
    /**
     * Track a telemetry event
     * @param event Telemetry event
     */
    trackEvent(event) {
        // Add the event to the in-memory store
        const serverId = event.serverId;
        const serverEvents = this.events.get(serverId) || [];
        serverEvents.push(event);
        // Limit the number of events in memory
        if (serverEvents.length > this.maxEventsPerFile) {
            serverEvents.shift();
        }
        this.events.set(serverId, serverEvents);
        // Save the event to disk
        this.saveEvent(event);
        // Fire the event
        this._onDidCollectTelemetry.fire(event);
    }
    /**
     * Update server statistics
     * @param serverId Server ID
     * @param updater Function to update the statistics
     */
    updateStats(serverId, updater) {
        // Get or create the server stats
        const stats = this.stats.get(serverId) || {
            serverId,
            serverName: '',
            startCount: 0,
            stopCount: 0,
            errorCount: 0,
            toolInvocations: 0,
            toolErrors: 0,
            healthChecks: 0,
            uptime: 0,
            toolUsage: {}
        };
        // Update the stats
        updater(stats);
        // Store the updated stats
        this.stats.set(serverId, stats);
        // Save the stats to disk
        this.saveStats(serverId);
    }
    /**
     * Save a telemetry event to disk
     * @param event Telemetry event
     */
    saveEvent(event) {
        if (!this.telemetryEnabled) {
            return;
        }
        try {
            const serverId = event.serverId;
            const eventsFilePath = this.getEventsFilePath(serverId);
            // Append the event to the file
            const eventLine = JSON.stringify(event) + '\n';
            fs.appendFileSync(eventsFilePath, eventLine, 'utf8');
        }
        catch (error) {
            console.error(`Error saving telemetry event: ${error}`);
        }
    }
    /**
     * Save server statistics to disk
     * @param serverId Server ID
     */
    saveStats(serverId) {
        if (!this.telemetryEnabled) {
            return;
        }
        try {
            const stats = this.stats.get(serverId);
            if (!stats) {
                return;
            }
            const statsFilePath = this.getStatsFilePath(serverId);
            fs.writeFileSync(statsFilePath, JSON.stringify(stats, null, 2), 'utf8');
        }
        catch (error) {
            console.error(`Error saving telemetry stats: ${error}`);
        }
    }
    /**
     * Save all telemetry data to disk
     */
    saveTelemetry() {
        if (!this.telemetryEnabled) {
            return;
        }
        // Save all server stats
        for (const serverId of this.stats.keys()) {
            this.saveStats(serverId);
        }
    }
    /**
     * Load telemetry data from disk
     */
    loadTelemetry() {
        if (!this.telemetryEnabled || !fs.existsSync(this.telemetryDir)) {
            return;
        }
        try {
            // Get all server IDs from the telemetry directory
            const files = fs.readdirSync(this.telemetryDir);
            const statsFiles = files.filter(file => file.endsWith('.stats.json'));
            const serverIds = statsFiles.map(file => file.replace('.stats.json', ''));
            // Load stats for each server
            for (const serverId of serverIds) {
                this.loadStats(serverId);
                this.loadEvents(serverId);
            }
        }
        catch (error) {
            console.error(`Error loading telemetry data: ${error}`);
        }
    }
    /**
     * Load server statistics from disk
     * @param serverId Server ID
     */
    loadStats(serverId) {
        try {
            const statsFilePath = this.getStatsFilePath(serverId);
            if (!fs.existsSync(statsFilePath)) {
                return;
            }
            const statsJson = fs.readFileSync(statsFilePath, 'utf8');
            const stats = JSON.parse(statsJson);
            this.stats.set(serverId, stats);
        }
        catch (error) {
            console.error(`Error loading telemetry stats for ${serverId}: ${error}`);
        }
    }
    /**
     * Load telemetry events from disk
     * @param serverId Server ID
     */
    loadEvents(serverId) {
        try {
            const eventsFilePath = this.getEventsFilePath(serverId);
            if (!fs.existsSync(eventsFilePath)) {
                return;
            }
            const eventsContent = fs.readFileSync(eventsFilePath, 'utf8');
            const eventLines = eventsContent.split('\n').filter(line => line.trim().length > 0);
            const events = [];
            // Parse the most recent events
            const startIndex = Math.max(0, eventLines.length - this.maxEventsPerFile);
            for (let i = startIndex; i < eventLines.length; i++) {
                try {
                    const event = JSON.parse(eventLines[i]);
                    events.push(event);
                }
                catch (error) {
                    console.error(`Error parsing telemetry event: ${error}`);
                }
            }
            this.events.set(serverId, events);
        }
        catch (error) {
            console.error(`Error loading telemetry events for ${serverId}: ${error}`);
        }
    }
    /**
     * Get the events file path for a server
     * @param serverId Server ID
     * @returns Events file path
     */
    getEventsFilePath(serverId) {
        return path.join(this.telemetryDir, `${serverId}.events.jsonl`);
    }
    /**
     * Get the stats file path for a server
     * @param serverId Server ID
     * @returns Stats file path
     */
    getStatsFilePath(serverId) {
        return path.join(this.telemetryDir, `${serverId}.stats.json`);
    }
}
exports.TelemetryManager = TelemetryManager;
//# sourceMappingURL=telemetryManager.js.map