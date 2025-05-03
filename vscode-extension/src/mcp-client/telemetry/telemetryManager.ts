import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { McpServer } from '../types';

/**
 * Telemetry event type
 */
export enum TelemetryEventType {
  SERVER_START = 'server_start',
  SERVER_STOP = 'server_stop',
  SERVER_ERROR = 'server_error',
  TOOL_INVOCATION = 'tool_invocation',
  TOOL_ERROR = 'tool_error',
  HEALTH_CHECK = 'health_check',
  AUTHENTICATION = 'authentication'
}

/**
 * Telemetry event
 */
export interface TelemetryEvent {
  type: TelemetryEventType;
  timestamp: string;
  serverId: string;
  serverName: string;
  serverVersion: string;
  duration?: number;
  success?: boolean;
  errorMessage?: string;
  toolName?: string;
  toolParameters?: Record<string, any>;
  healthStatus?: string;
  authType?: string;
}

/**
 * Server usage statistics
 */
export interface ServerUsageStats {
  serverId: string;
  serverName: string;
  startCount: number;
  stopCount: number;
  errorCount: number;
  toolInvocations: number;
  toolErrors: number;
  healthChecks: number;
  uptime: number;
  lastStarted?: string;
  lastStopped?: string;
  lastError?: string;
  lastToolInvocation?: string;
  lastHealthCheck?: string;
  toolUsage: Record<string, number>;
}

/**
 * Telemetry manager for MCP servers
 */
export class TelemetryManager implements vscode.Disposable {
  private telemetryEnabled: boolean;
  private telemetryDir: string;
  private maxEventsPerFile: number;
  private events: Map<string, TelemetryEvent[]> = new Map();
  private stats: Map<string, ServerUsageStats> = new Map();
  private _onDidCollectTelemetry = new vscode.EventEmitter<TelemetryEvent>();

  /**
   * Event that fires when telemetry is collected
   */
  public readonly onDidCollectTelemetry = this._onDidCollectTelemetry.event;

  /**
   * Create a new telemetry manager
   * @param context Extension context
   * @param options Telemetry options
   */
  constructor(
    context: vscode.ExtensionContext,
    options: {
      telemetryEnabled?: boolean;
      telemetryDir?: string;
      maxEventsPerFile?: number;
    } = {}
  ) {
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
  public dispose(): void {
    this._onDidCollectTelemetry.dispose();

    // Save telemetry data
    this.saveTelemetry();
  }

  /**
   * Track a server start event
   * @param server Server
   */
  public trackServerStart(server: McpServer): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
  public trackServerStop(server: McpServer, duration: number): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
  public trackServerError(server: McpServer, errorMessage: string): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
  public trackToolInvocation(
    server: McpServer,
    toolName: string,
    toolParameters: Record<string, any>,
    success: boolean,
    errorMessage?: string,
    duration?: number
  ): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
      } else {
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
  public trackHealthCheck(server: McpServer, healthStatus: string): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
  public trackAuthentication(
    server: McpServer,
    authType: string,
    success: boolean,
    errorMessage?: string
  ): void {
    if (!this.telemetryEnabled) {
      return;
    }

    const event: TelemetryEvent = {
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
  public getUsageStats(): ServerUsageStats[] {
    return Array.from(this.stats.values());
  }

  /**
   * Get usage statistics for a server
   * @param serverId Server ID
   * @returns Server usage statistics
   */
  public getServerUsageStats(serverId: string): ServerUsageStats | undefined {
    return this.stats.get(serverId);
  }

  /**
   * Get telemetry events for a server
   * @param serverId Server ID
   * @param maxEvents Maximum number of events to return
   * @returns Telemetry events
   */
  public getServerEvents(serverId: string, maxEvents: number = 100): TelemetryEvent[] {
    const events = this.events.get(serverId) || [];
    return events.slice(-maxEvents);
  }

  /**
   * Clear telemetry data for a server
   * @param serverId Server ID
   */
  public clearServerTelemetry(serverId: string): void {
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
  public setTelemetryEnabled(enabled: boolean): void {
    this.telemetryEnabled = enabled;

    if (enabled) {
      // Create telemetry directory if it doesn't exist
      if (!fs.existsSync(this.telemetryDir)) {
        fs.mkdirSync(this.telemetryDir, { recursive: true });
      }

      // Load existing telemetry data
      this.loadTelemetry();
    } else {
      // Clear in-memory telemetry data
      this.events.clear();
      this.stats.clear();
    }
  }

  /**
   * Track a telemetry event
   * @param event Telemetry event
   */
  private trackEvent(event: TelemetryEvent): void {
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
  private updateStats(serverId: string, updater: (stats: ServerUsageStats) => void): void {
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
  private saveEvent(event: TelemetryEvent): void {
    if (!this.telemetryEnabled) {
      return;
    }

    try {
      const serverId = event.serverId;
      const eventsFilePath = this.getEventsFilePath(serverId);

      // Append the event to the file
      const eventLine = JSON.stringify(event) + '\n';
      fs.appendFileSync(eventsFilePath, eventLine, 'utf8');
    } catch (error) {
      console.error(`Error saving telemetry event: ${error}`);
    }
  }

  /**
   * Save server statistics to disk
   * @param serverId Server ID
   */
  private saveStats(serverId: string): void {
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
    } catch (error) {
      console.error(`Error saving telemetry stats: ${error}`);
    }
  }

  /**
   * Save all telemetry data to disk
   */
  private saveTelemetry(): void {
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
  private loadTelemetry(): void {
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
    } catch (error) {
      console.error(`Error loading telemetry data: ${error}`);
    }
  }

  /**
   * Load server statistics from disk
   * @param serverId Server ID
   */
  private loadStats(serverId: string): void {
    try {
      const statsFilePath = this.getStatsFilePath(serverId);
      if (!fs.existsSync(statsFilePath)) {
        return;
      }

      const statsJson = fs.readFileSync(statsFilePath, 'utf8');
      const stats = JSON.parse(statsJson) as ServerUsageStats;
      this.stats.set(serverId, stats);
    } catch (error) {
      console.error(`Error loading telemetry stats for ${serverId}: ${error}`);
    }
  }

  /**
   * Load telemetry events from disk
   * @param serverId Server ID
   */
  private loadEvents(serverId: string): void {
    try {
      const eventsFilePath = this.getEventsFilePath(serverId);
      if (!fs.existsSync(eventsFilePath)) {
        return;
      }

      const eventsContent = fs.readFileSync(eventsFilePath, 'utf8');
      const eventLines = eventsContent.split('\n').filter(line => line.trim().length > 0);
      const events: TelemetryEvent[] = [];

      // Parse the most recent events
      const startIndex = Math.max(0, eventLines.length - this.maxEventsPerFile);
      for (let i = startIndex; i < eventLines.length; i++) {
        try {
          const event = JSON.parse(eventLines[i]) as TelemetryEvent;
          events.push(event);
        } catch (error) {
          console.error(`Error parsing telemetry event: ${error}`);
        }
      }

      this.events.set(serverId, events);
    } catch (error) {
      console.error(`Error loading telemetry events for ${serverId}: ${error}`);
    }
  }

  /**
   * Get the events file path for a server
   * @param serverId Server ID
   * @returns Events file path
   */
  private getEventsFilePath(serverId: string): string {
    return path.join(this.telemetryDir, `${serverId}.events.jsonl`);
  }

  /**
   * Get the stats file path for a server
   * @param serverId Server ID
   * @returns Stats file path
   */
  private getStatsFilePath(serverId: string): string {
    return path.join(this.telemetryDir, `${serverId}.stats.json`);
  }
}
