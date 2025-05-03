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
exports.getConfiguration = getConfiguration;
exports.verifyConfiguration = verifyConfiguration;
exports.registerConfigurationListener = registerConfigurationListener;
const vscode = __importStar(require("vscode"));
/**
 * Get the extension configuration
 * @returns The extension configuration
 */
function getConfiguration() {
    const config = vscode.workspace.getConfiguration('qwen-coder-assistant');
    return {
        apiEndpoint: config.get('apiEndpoint') || 'http://localhost:8000/v1',
        apiKey: config.get('apiKey') || '',
        maxTokens: config.get('maxTokens') || 2048,
        temperature: config.get('temperature') || 0.7,
        cacheEnabled: config.get('cacheEnabled') !== false, // Default to true
        cacheTTLMinutes: config.get('cacheTTLMinutes') || 30,
        cacheMaxEntries: config.get('cacheMaxEntries') || 100,
        mcpServers: {
            storagePath: config.get('mcpServers.storagePath') || '',
            autoStart: config.get('mcpServers.autoStart') !== false, // Default to true
            autoStartList: config.get('mcpServers.autoStartList') || [],
            dockerOptions: config.get('mcpServers.dockerOptions') || {
                socketPath: '/var/run/docker.sock',
                memory: 2048,
                cpus: 2
            },
            githubOptions: config.get('mcpServers.githubOptions') || {
                token: '',
                timeout: 30000
            }
        }
    };
}
/**
 * Verify that the configuration is valid
 * @param config The configuration to verify
 * @returns An object with validation results
 */
function verifyConfiguration(config) {
    const issues = [];
    // Check API configuration
    const apiConfigured = Boolean(config.apiEndpoint && config.apiEndpoint.trim() !== '');
    if (!apiConfigured) {
        issues.push('API endpoint is not configured');
    }
    // Check MCP server configuration
    const mcpConfigured = Boolean(config.mcpServers.storagePath && config.mcpServers.storagePath.trim() !== '');
    if (!mcpConfigured) {
        issues.push('MCP server storage path is not configured');
    }
    // Check Docker configuration
    if (!config.mcpServers.dockerOptions.socketPath) {
        issues.push('Docker socket path is not configured');
    }
    return {
        isValid: issues.length === 0,
        issues,
        apiConfigured,
        mcpConfigured
    };
}
// Listen for configuration changes
function registerConfigurationListener(callback) {
    return vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('qwen-coder-assistant')) {
            callback(getConfiguration());
        }
    });
}
//# sourceMappingURL=configuration.js.map