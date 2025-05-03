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
exports.McpLogger = exports.LogLevel = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Log level
 */
var LogLevel;
(function (LogLevel) {
    LogLevel["DEBUG"] = "DEBUG";
    LogLevel["INFO"] = "INFO";
    LogLevel["WARNING"] = "WARNING";
    LogLevel["ERROR"] = "ERROR";
})(LogLevel || (exports.LogLevel = LogLevel = {}));
/**
 * Logger for MCP servers
 */
class McpLogger {
    /**
     * Create a new MCP logger
     * @param context Extension context
     * @param options Logger options
     */
    constructor(context, options = {}) {
        this._onDidLog = new vscode.EventEmitter();
        /**
         * Event that fires when a log entry is added
         */
        this.onDidLog = this._onDidLog.event;
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
    dispose() {
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
    log(level, serverId, message, data) {
        if (!this.logEnabled) {
            return;
        }
        const timestamp = new Date().toISOString();
        const entry = {
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
    debug(serverId, message, data) {
        this.log(LogLevel.DEBUG, serverId, message, data);
    }
    /**
     * Log an info message
     * @param serverId Server ID
     * @param message Message
     * @param data Additional data
     */
    info(serverId, message, data) {
        this.log(LogLevel.INFO, serverId, message, data);
    }
    /**
     * Log a warning message
     * @param serverId Server ID
     * @param message Message
     * @param data Additional data
     */
    warning(serverId, message, data) {
        this.log(LogLevel.WARNING, serverId, message, data);
    }
    /**
     * Log an error message
     * @param serverId Server ID
     * @param message Message
     * @param data Additional data
     */
    error(serverId, message, data) {
        this.log(LogLevel.ERROR, serverId, message, data);
    }
    /**
     * Show the log output channel
     */
    show() {
        this.outputChannel.show();
    }
    /**
     * Get the log file path for a server
     * @param serverId Server ID
     * @returns Log file path
     */
    getLogFilePath(serverId) {
        return path.join(this.logDir, `${serverId}.log`);
    }
    /**
     * Get the log entries for a server
     * @param serverId Server ID
     * @param maxEntries Maximum number of entries to return
     * @returns Log entries
     */
    getLogEntries(serverId, maxEntries = 100) {
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
            const entries = [];
            // Parse the most recent entries
            const startIndex = Math.max(0, lines.length - maxEntries);
            for (let i = startIndex; i < lines.length; i++) {
                try {
                    const entry = JSON.parse(lines[i]);
                    entries.push(entry);
                }
                catch (error) {
                    console.error(`Error parsing log entry: ${error}`);
                }
            }
            return entries;
        }
        catch (error) {
            console.error(`Error reading log file: ${error}`);
            return [];
        }
    }
    /**
     * Clear the logs for a server
     * @param serverId Server ID
     */
    clearLogs(serverId) {
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
    logToOutputChannel(entry) {
        const { timestamp, level, serverId, message, data } = entry;
        let logMessage = `[${timestamp}] [${level}] [${serverId}] ${message}`;
        if (data !== undefined) {
            try {
                const dataStr = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                logMessage += `\n${dataStr}`;
            }
            catch (error) {
                logMessage += `\n[Error serializing data: ${error}]`;
            }
        }
        this.outputChannel.appendLine(logMessage);
    }
    /**
     * Log to a file
     * @param entry Log entry
     */
    logToFile(entry) {
        const { serverId } = entry;
        const logFilePath = this.getLogFilePath(serverId);
        try {
            // Check if log rotation is needed
            this.rotateLogFileIfNeeded(logFilePath);
            // Append the log entry to the file
            const logLine = JSON.stringify(entry) + '\n';
            fs.appendFileSync(logFilePath, logLine, 'utf8');
        }
        catch (error) {
            console.error(`Error writing to log file: ${error}`);
            this.outputChannel.appendLine(`[ERROR] Failed to write to log file: ${error}`);
        }
    }
    /**
     * Rotate the log file if needed
     * @param logFilePath Log file path
     */
    rotateLogFileIfNeeded(logFilePath) {
        if (!fs.existsSync(logFilePath)) {
            return;
        }
        try {
            const stats = fs.statSync(logFilePath);
            if (stats.size >= this.maxLogSize) {
                this.rotateLogFile(logFilePath);
            }
        }
        catch (error) {
            console.error(`Error checking log file size: ${error}`);
        }
    }
    /**
     * Rotate the log file
     * @param logFilePath Log file path
     */
    rotateLogFile(logFilePath) {
        try {
            // Delete the oldest log file if we have reached the maximum number of log files
            const baseLogPath = logFilePath;
            const rotatedLogPath = (index) => `${baseLogPath}.${index}`;
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
        }
        catch (error) {
            console.error(`Error rotating log file: ${error}`);
        }
    }
}
exports.McpLogger = McpLogger;
//# sourceMappingURL=mcpLogger.js.map