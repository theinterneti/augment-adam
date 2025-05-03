"use strict";
/**
 * MCP Client
 *
 * Client for interacting with Model-Control-Protocol (MCP) tools.
 */
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MCPClient = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
/**
 * MCP Client class
 */
class MCPClient {
    /**
     * Constructor
     * @param containerManager The container manager
     */
    constructor(containerManager) {
        this.containerManager = containerManager;
        this.outputChannel = vscode.window.createOutputChannel('MCP Client');
        this.toolSchemas = {};
        this.outputChannel.appendLine('MCP Client initialized');
    }
    /**
     * Initialize the MCP client
     */
    async initialize() {
        try {
            this.outputChannel.appendLine('Initializing MCP client');
            // Get active containers
            const containerStatus = this.containerManager.getContainerStatus();
            // Fetch schemas for running containers
            for (const containerName in containerStatus) {
                const container = containerStatus[containerName];
                if (container.status === 'running') {
                    try {
                        await this.fetchToolSchema(containerName);
                    }
                    catch (error) {
                        this.outputChannel.appendLine(`Error fetching schema for ${containerName}: ${error.message}`);
                    }
                }
            }
            this.outputChannel.appendLine('MCP client initialized');
        }
        catch (error) {
            this.outputChannel.appendLine(`Error initializing MCP client: ${error.message}`);
            throw error;
        }
    }
    /**
     * Fetch the schema for a tool
     * @param toolName The name of the tool
     * @returns The tool schema
     */
    async fetchToolSchema(toolName) {
        try {
            this.outputChannel.appendLine(`Fetching schema for tool: ${toolName}`);
            // Get container URL
            const url = this.containerManager.getContainerUrl(toolName);
            // Fetch schema
            const response = await axios_1.default.get(`${url}/schema`);
            const schema = response.data;
            // Validate schema
            if (!schema.name || !schema.functions || !Array.isArray(schema.functions)) {
                throw new Error(`Invalid schema for tool ${toolName}`);
            }
            // Store schema
            this.toolSchemas[toolName] = schema;
            this.outputChannel.appendLine(`Schema fetched for tool ${toolName}: ${schema.functions.length} functions available`);
            return schema;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error fetching schema for tool ${toolName}: ${error.message}`);
            throw error;
        }
    }
    /**
     * Get the schema for a tool
     * @param toolName The name of the tool
     * @returns The tool schema
     */
    getToolSchema(toolName) {
        return this.toolSchemas[toolName];
    }
    /**
     * Get all available tools
     * @returns The available tools
     */
    getAvailableTools() {
        return Object.keys(this.toolSchemas);
    }
    /**
     * Call a function on a tool
     * @param toolName The name of the tool
     * @param functionName The name of the function
     * @param parameters The function parameters
     * @returns The function call result
     */
    async callFunction(toolName, functionName, parameters) {
        try {
            this.outputChannel.appendLine(`Calling function ${functionName} on tool ${toolName}`);
            // Check if tool is available
            if (!this.toolSchemas[toolName]) {
                // Try to fetch schema
                try {
                    await this.fetchToolSchema(toolName);
                }
                catch (error) {
                    throw new Error(`Tool ${toolName} is not available: ${error.message}`);
                }
            }
            // Check if function exists
            const functionSchema = this.toolSchemas[toolName].functions.find(f => f.name === functionName);
            if (!functionSchema) {
                throw new Error(`Function ${functionName} not found in tool ${toolName}`);
            }
            // Validate parameters
            this._validateParameters(parameters, functionSchema);
            // Get container URL
            const url = this.containerManager.getContainerUrl(toolName);
            // Call function
            const response = await axios_1.default.post(`${url}/invoke`, {
                function: functionName,
                parameters
            });
            const result = response.data;
            this.outputChannel.appendLine(`Function ${functionName} called successfully on tool ${toolName}`);
            return result;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error calling function ${functionName} on tool ${toolName}: ${error.message}`);
            return {
                status: 'error',
                error: error.message
            };
        }
    }
    /**
     * Validate function parameters
     * @param parameters The parameters to validate
     * @param functionSchema The function schema
     */
    _validateParameters(parameters, functionSchema) {
        // Check required parameters
        for (const requiredParam of functionSchema.parameters.required) {
            if (parameters[requiredParam] === undefined) {
                throw new Error(`Missing required parameter: ${requiredParam}`);
            }
        }
        // Check parameter types
        for (const paramName in parameters) {
            const paramSchema = functionSchema.parameters.properties[paramName];
            if (!paramSchema) {
                throw new Error(`Unknown parameter: ${paramName}`);
            }
            // Basic type checking
            const paramValue = parameters[paramName];
            const paramType = paramSchema.type;
            if (paramType === 'string' && typeof paramValue !== 'string') {
                throw new Error(`Parameter ${paramName} should be a string`);
            }
            else if (paramType === 'number' && typeof paramValue !== 'number') {
                throw new Error(`Parameter ${paramName} should be a number`);
            }
            else if (paramType === 'boolean' && typeof paramValue !== 'boolean') {
                throw new Error(`Parameter ${paramName} should be a boolean`);
            }
            else if (paramType === 'array' && !Array.isArray(paramValue)) {
                throw new Error(`Parameter ${paramName} should be an array`);
            }
            else if (paramType === 'object' && (typeof paramValue !== 'object' || paramValue === null || Array.isArray(paramValue))) {
                throw new Error(`Parameter ${paramName} should be an object`);
            }
            // Check enum values
            if (paramSchema.enum && !paramSchema.enum.includes(paramValue)) {
                throw new Error(`Parameter ${paramName} should be one of: ${paramSchema.enum.join(', ')}`);
            }
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.MCPClient = MCPClient;
//# sourceMappingURL=mcpClient.js.map