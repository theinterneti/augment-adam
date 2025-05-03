"use strict";
/**
 * Types for MCP client and server management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.McpServerType = exports.McpServerStatus = void 0;
/**
 * Status of an MCP server
 */
var McpServerStatus;
(function (McpServerStatus) {
    McpServerStatus["Running"] = "running";
    McpServerStatus["Stopped"] = "stopped";
    McpServerStatus["Starting"] = "starting";
    McpServerStatus["Stopping"] = "stopping";
    McpServerStatus["Error"] = "error";
    McpServerStatus["Unknown"] = "unknown";
})(McpServerStatus || (exports.McpServerStatus = McpServerStatus = {}));
/**
 * Type of MCP server
 */
var McpServerType;
(function (McpServerType) {
    McpServerType["Docker"] = "docker";
    McpServerType["Process"] = "process";
})(McpServerType || (exports.McpServerType = McpServerType = {}));
//# sourceMappingURL=types.js.map