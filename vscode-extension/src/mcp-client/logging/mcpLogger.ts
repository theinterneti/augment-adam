import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Log level
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR'
}

/**
 * Log entry
 */
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  serverId: string;
  message: string;
  data?: any;
}

/**
 * Logger for MCP servers
 */
export class McpLogger implements vscode.Disposable {
  private outputChannel: vscode.OutputChannel;
  private logDir: string;
  private maxLogSize: number;
  private maxLogFiles: number;
  private logEnabled: boolean;
  private fileLogEnabled: boolean;
  private _onDidLog = new vscode.EventEmitter<LogEntry>();

  /**
   * Event that fires when a log entry is added
   */
  public readonly onDidLog = this._onDidLog.event;

  /**
   * Create a new MCP logger
   * @param context Extension context
   * @param options Logger options
   */
  constructor(
    context: vscode.ExtensionContext,
    options: {
      logDir?: string;
      maxLogSize?: number;
      maxLogFiles?: number;
      logEnabled?: boolean;
      fileLogEnabled?: boolean;
    } = {}
  ) {
    this.outputChannel = vscode.window.createOutputChannel('MCP Servers');
    this.logDir = options.logDir || path.join(context.globalStorageUri.fsPath, 'logs');
    this.maxLogSize = options.maxLogSize || 5 * 1024 * 1024; // 5 MB
    this.maxLogFiles = options.maxLogFiles || 10;
    this.logEnabled = options.logEnabled !== false;
    this.fileLogEnabled = options.fileLogEnabled !== false;

    // Create log directory if it doesn't exist
    if (this.fileLogEnabled && !fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }

    // Register the logger with the extension context
    context.subscriptions.push(this);
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
    this._onDidLog.dispose();
  }

  /**
   * Log a message
   * @param level Log level
   * @param serverId Server ID
   * @param message Message
   * @param data Additional data
   */
  public log(level: LogLevel, serverId: string, message: string, data?: any): void {
    if (!this.logEnabled) {
      return;
    }

    const timestamp = new Date().toISOString();
    const entry: LogEntry = {
      timestamp,
      level,
      serverId,
      message,
      data
    };

    // Log to output channel
    this.logToOutputChannel(entry);

    // Log to file
    if (this.fileLogEnabled) {
      this.logToFile(entry);
    }

    // Fire event
    this._onDidLog.fire(entry);
  }

  /**
   * Log a debug message
   * @param serverId Server ID
   * @param message Message
   * @param data Additional data
   */
  public debug(serverId: string, message: string, data?: any): void {
    this.log(LogLevel.DEBUG, serverId, message, data);
  }

  /**
   * Log an info message
   * @param serverId Server ID
   * @param message Message
   * @param data Additional data
   */
  public info(serverId: string, message: string, data?: any): void {
    this.log(LogLevel.INFO, serverId, message, data);
  }

  /**
   * Log a warning message
   * @param serverId Server ID
   * @param message Message
   * @param data Additional data
   */
  public warning(serverId: string, message: string, data?: any): void {
    this.log(LogLevel.WARNING, serverId, message, data);
  }

  /**
   * Log an error message
   * @param serverId Server ID
   * @param message Message
   * @param data Additional data
   */
  public error(serverId: string, message: string, data?: any): void {
    this.log(LogLevel.ERROR, serverId, message, data);
  }

  /**
   * Show the log output channel
   */
  public show(): void {
    this.outputChannel.show();
  }

  /**
   * Get the log file path for a server
   * @param serverId Server ID
   * @returns Log file path
   */
  public getLogFilePath(serverId: string): string {
    return path.join(this.logDir, `${serverId}.log`);
  }

  /**
   * Get the log entries for a server
   * @param serverId Server ID
   * @param maxEntries Maximum number of entries to return
   * @returns Log entries
   */
  public getLogEntries(serverId: string, maxEntries: number = 100): LogEntry[] {
    if (!this.fileLogEnabled) {
      return [];
    }

    const logFilePath = this.getLogFilePath(serverId);
    if (!fs.existsSync(logFilePath)) {
      return [];
    }

    try {
      const logContent = fs.readFileSync(logFilePath, 'utf8');
      const lines = logContent.split('\n').filter(line => line.trim().length > 0);
      const entries: LogEntry[] = [];

      // Parse the most recent entries
      const startIndex = Math.max(0, lines.length - maxEntries);
      for (let i = startIndex; i < lines.length; i++) {
        try {
          const entry = JSON.parse(lines[i]) as LogEntry;
          entries.push(entry);
        } catch (error) {
          console.error(`Error parsing log entry: ${error}`);
        }
      }

      return entries;
    } catch (error) {
      console.error(`Error reading log file: ${error}`);
      return [];
    }
  }

  /**
   * Clear the logs for a server
   * @param serverId Server ID
   */
  public clearLogs(serverId: string): void {
    if (!this.fileLogEnabled) {
      return;
    }

    const logFilePath = this.getLogFilePath(serverId);
    if (fs.existsSync(logFilePath)) {
      fs.writeFileSync(logFilePath, '', 'utf8');
    }
  }

  /**
   * Log to the output channel
   * @param entry Log entry
   */
  private logToOutputChannel(entry: LogEntry): void {
    const { timestamp, level, serverId, message, data } = entry;
    let logMessage = `[${timestamp}] [${level}] [${serverId}] ${message}`;

    if (data !== undefined) {
      try {
        const dataStr = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        logMessage += `\n${dataStr}`;
      } catch (error) {
        logMessage += `\n[Error serializing data: ${error}]`;
      }
    }

    this.outputChannel.appendLine(logMessage);
  }

  /**
   * Log to a file
   * @param entry Log entry
   */
  private logToFile(entry: LogEntry): void {
    const { serverId } = entry;
    const logFilePath = this.getLogFilePath(serverId);

    try {
      // Check if log rotation is needed
      this.rotateLogFileIfNeeded(logFilePath);

      // Append the log entry to the file
      const logLine = JSON.stringify(entry) + '\n';
      fs.appendFileSync(logFilePath, logLine, 'utf8');
    } catch (error) {
      console.error(`Error writing to log file: ${error}`);
      this.outputChannel.appendLine(`[ERROR] Failed to write to log file: ${error}`);
    }
  }

  /**
   * Rotate the log file if needed
   * @param logFilePath Log file path
   */
  private rotateLogFileIfNeeded(logFilePath: string): void {
    if (!fs.existsSync(logFilePath)) {
      return;
    }

    try {
      const stats = fs.statSync(logFilePath);
      if (stats.size >= this.maxLogSize) {
        this.rotateLogFile(logFilePath);
      }
    } catch (error) {
      console.error(`Error checking log file size: ${error}`);
    }
  }

  /**
   * Rotate the log file
   * @param logFilePath Log file path
   */
  private rotateLogFile(logFilePath: string): void {
    try {
      // Delete the oldest log file if we have reached the maximum number of log files
      const baseLogPath = logFilePath;
      const rotatedLogPath = (index: number) => `${baseLogPath}.${index}`;

      // Check if we need to delete the oldest log file
      if (fs.existsSync(rotatedLogPath(this.maxLogFiles - 1))) {
        fs.unlinkSync(rotatedLogPath(this.maxLogFiles - 1));
      }

      // Shift all existing rotated log files
      for (let i = this.maxLogFiles - 2; i >= 0; i--) {
        const currentPath = rotatedLogPath(i);
        const nextPath = rotatedLogPath(i + 1);

        if (fs.existsSync(currentPath)) {
          fs.renameSync(currentPath, nextPath);
        }
      }

      // Rename the current log file
      fs.renameSync(baseLogPath, rotatedLogPath(0));

      // Create a new empty log file
      fs.writeFileSync(baseLogPath, '', 'utf8');
    } catch (error) {
      console.error(`Error rotating log file: ${error}`);
    }
  }
}
