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
exports.McpQwenBridge = void 0;
const vscode = __importStar(require("vscode"));
const contextGatherer_1 = require("./contextGatherer");
/**
 * Bridge between MCP and Qwen
 * Handles converting MCP tools to Qwen tools and processing tool calls
 */
class McpQwenBridge {
    constructor(qwenClient, mcpClient) {
        this.qwenClient = qwenClient;
        this.mcpClient = mcpClient;
        this.outputChannel = vscode.window.createOutputChannel('MCP-Qwen Bridge');
        this.contextGatherer = new contextGatherer_1.ContextGatherer(mcpClient);
    }
    /**
     * Process a user message with MCP tools
     * @param message User message
     * @param options Options for processing
     * @returns Response from Qwen with tool results if applicable
     */
    async processMessage(message, options = {}) {
        try {
            this.outputChannel.appendLine(`Processing message: ${message.substring(0, 100)}...`);
            // Get available tools from MCP servers
            const mcpTools = await this.mcpClient.getAllTools();
            this.outputChannel.appendLine(`Found ${mcpTools.length} MCP tools`);
            // Convert MCP tools to Qwen tools
            const qwenTools = mcpTools.map(tool => this.convertToolToQwenFormat(tool));
            // Create messages array
            const messages = [];
            // Add system message if provided
            if (options.systemPrompt) {
                messages.push({
                    role: 'system',
                    content: options.systemPrompt
                });
            }
            // Add context messages if provided
            if (options.contextMessages && options.contextMessages.length > 0) {
                messages.push(...options.contextMessages);
            }
            // Gather context if enabled
            if (options.gatherContext !== false) {
                try {
                    const contextMessages = await this.contextGatherer.gatherContext(message);
                    if (contextMessages.length > 0) {
                        this.outputChannel.appendLine(`Adding ${contextMessages.length} context messages`);
                        messages.push(...contextMessages);
                    }
                }
                catch (error) {
                    this.outputChannel.appendLine(`Error gathering context: ${error}`);
                }
            }
            // Add user message
            messages.push({
                role: 'user',
                content: message
            });
            // Call Qwen API with tools
            const response = await this.qwenClient.chatWithTools(messages, {
                thinkingMode: options.thinkingMode || 'auto',
                thinkingBudget: options.thinkingBudget,
                temperature: options.temperature,
                maxTokens: options.maxTokens,
                modelName: options.modelName,
                tools: qwenTools
            });
            // Process tool calls if present
            if (response.tool_calls && response.tool_calls.length > 0) {
                return await this.processToolCallsAndGetFinalResponse(response, messages);
            }
            return response.text;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error processing message: ${error}`);
            return `Error: ${error}`;
        }
    }
    /**
     * Process a user message with MCP tools using streaming
     * @param message User message
     * @param options Options for processing
     * @param onChunk Callback function to handle streaming chunks
     */
    async processMessageStream(message, options = {}, onChunk) {
        try {
            this.outputChannel.appendLine(`Processing message with streaming: ${message.substring(0, 100)}...`);
            // Get available tools from MCP servers
            const mcpTools = await this.mcpClient.getAllTools();
            this.outputChannel.appendLine(`Found ${mcpTools.length} MCP tools`);
            // Convert MCP tools to Qwen tools
            const qwenTools = mcpTools.map(tool => this.convertToolToQwenFormat(tool));
            // Create messages array
            const messages = [];
            // Add system message if provided
            if (options.systemPrompt) {
                messages.push({
                    role: 'system',
                    content: options.systemPrompt
                });
            }
            // Add context messages if provided
            if (options.contextMessages && options.contextMessages.length > 0) {
                messages.push(...options.contextMessages);
            }
            // Gather context if enabled
            if (options.gatherContext !== false) {
                try {
                    const contextMessages = await this.contextGatherer.gatherContext(message);
                    if (contextMessages.length > 0) {
                        this.outputChannel.appendLine(`Adding ${contextMessages.length} context messages`);
                        messages.push(...contextMessages);
                    }
                }
                catch (error) {
                    this.outputChannel.appendLine(`Error gathering context: ${error}`);
                }
            }
            // Add user message
            messages.push({
                role: 'user',
                content: message
            });
            // Accumulate the full response and tool calls
            let fullResponse = '';
            let toolCalls = [];
            // Call Qwen API with tools and streaming
            await this.qwenClient.chatStreamWithTools(messages, {
                thinkingMode: options.thinkingMode || 'auto',
                thinkingBudget: options.thinkingBudget,
                temperature: options.temperature,
                maxTokens: options.maxTokens,
                modelName: options.modelName,
                tools: qwenTools
            }, async (chunk, done, chunkToolCalls) => {
                // Accumulate the response
                fullResponse += chunk;
                // Update tool calls if present
                if (chunkToolCalls && chunkToolCalls.length > 0) {
                    toolCalls = chunkToolCalls;
                }
                // Pass to the original handler
                onChunk(chunk, false, toolCalls);
                // When streaming is complete, process tool calls if present
                if (done && toolCalls.length > 0) {
                    // Add assistant message with tool calls
                    messages.push({
                        role: 'assistant',
                        content: fullResponse,
                        tool_calls: toolCalls
                    });
                    // Process tool calls
                    await this.processToolCallsAndStreamFinalResponse(toolCalls, messages, onChunk);
                }
                else if (done) {
                    // Signal completion if no tool calls
                    onChunk('', true);
                }
            });
        }
        catch (error) {
            this.outputChannel.appendLine(`Error processing message with streaming: ${error}`);
            onChunk(`Error: ${error}`, true);
        }
    }
    /**
     * Process tool calls and get a final response
     * @param initialResponse Initial response with tool calls
     * @param messages Conversation messages
     * @returns Final response after tool execution
     */
    async processToolCallsAndGetFinalResponse(initialResponse, messages) {
        if (!initialResponse.tool_calls || initialResponse.tool_calls.length === 0) {
            return initialResponse.text;
        }
        this.outputChannel.appendLine(`Processing ${initialResponse.tool_calls.length} tool calls`);
        // Add assistant message with tool calls
        messages.push({
            role: 'assistant',
            content: initialResponse.text,
            tool_calls: initialResponse.tool_calls
        });
        // Process each tool call
        const toolResults = await Promise.all(initialResponse.tool_calls.map(async (toolCall) => {
            try {
                const result = await this.executeToolCall(toolCall);
                return {
                    tool_call_id: toolCall.id,
                    role: 'tool',
                    name: toolCall.function.name,
                    content: typeof result === 'string' ? result : JSON.stringify(result)
                };
            }
            catch (error) {
                return {
                    tool_call_id: toolCall.id,
                    role: 'tool',
                    name: toolCall.function.name,
                    content: `Error: ${error}`
                };
            }
        }));
        // Add tool results to messages
        messages.push(...toolResults);
        // Get final response from Qwen
        const finalResponse = await this.qwenClient.chat(messages);
        return finalResponse;
    }
    /**
     * Process tool calls and stream the final response
     * @param toolCalls Tool calls to process
     * @param messages Conversation messages
     * @param onChunk Callback function to handle streaming chunks
     */
    async processToolCallsAndStreamFinalResponse(toolCalls, messages, onChunk) {
        try {
            this.outputChannel.appendLine(`Processing ${toolCalls.length} tool calls for streaming response`);
            // Process each tool call
            const toolResults = await Promise.all(toolCalls.map(async (toolCall) => {
                try {
                    const result = await this.executeToolCall(toolCall);
                    return {
                        tool_call_id: toolCall.id,
                        role: 'tool',
                        name: toolCall.function.name,
                        content: typeof result === 'string' ? result : JSON.stringify(result)
                    };
                }
                catch (error) {
                    return {
                        tool_call_id: toolCall.id,
                        role: 'tool',
                        name: toolCall.function.name,
                        content: `Error: ${error}`
                    };
                }
            }));
            // Add tool results to messages
            messages.push(...toolResults);
            // Stream final response from Qwen
            await this.qwenClient.chatStream(messages, {}, (chunk, done) => {
                onChunk(chunk, done);
            });
        }
        catch (error) {
            this.outputChannel.appendLine(`Error processing tool calls for streaming: ${error}`);
            onChunk(`Error: ${error}`, true);
        }
    }
    /**
     * Execute a tool call
     * @param toolCall Tool call to execute
     * @returns Result of the tool call
     */
    async executeToolCall(toolCall) {
        try {
            this.outputChannel.appendLine(`Executing tool call: ${toolCall.function.name}`);
            // Parse the function name (format: serverId.toolName.functionName)
            const [serverId, toolName, functionName] = toolCall.function.name.split('.');
            if (!serverId || !toolName || !functionName) {
                throw new Error(`Invalid function name format: ${toolCall.function.name}`);
            }
            // Parse arguments
            let args;
            try {
                args = JSON.parse(toolCall.function.arguments);
            }
            catch (error) {
                throw new Error(`Invalid arguments: ${error}`);
            }
            // Call the function
            const result = await this.mcpClient.callFunction(serverId, toolName, functionName, args);
            // Check for errors
            if (result.status === 'error') {
                throw new Error(result.error || 'Unknown error');
            }
            this.outputChannel.appendLine(`Tool call executed successfully`);
            return result.result;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error executing tool call: ${error}`);
            throw error;
        }
    }
    /**
     * Convert MCP tool to Qwen tool format
     * @param mcpTool MCP tool
     * @returns Qwen tool
     */
    convertToolToQwenFormat(mcpTool) {
        try {
            const { serverId, tool } = mcpTool;
            // Create a tool for each function in the MCP tool
            return {
                type: 'function',
                function: {
                    name: `${serverId}.${tool.name}`,
                    description: tool.description || `Tool provided by ${serverId}`,
                    parameters: {
                        type: 'object',
                        properties: this.convertParametersToQwenFormat(tool.parameters || []),
                        required: tool.parameters
                            ?.filter(param => param.required)
                            .map(param => param.name) || []
                    }
                }
            };
        }
        catch (error) {
            this.outputChannel.appendLine(`Error converting MCP tool to Qwen format: ${error}`);
            throw error;
        }
    }
    /**
     * Convert MCP parameters to Qwen format
     * @param parameters MCP parameters
     * @returns Qwen parameters
     */
    convertParametersToQwenFormat(parameters) {
        const result = {};
        for (const param of parameters) {
            result[param.name] = {
                type: this.mapMcpTypeToQwenType(param.type),
                description: param.description || `Parameter ${param.name}`
            };
            // Add enum if available
            if (param.enum && param.enum.length > 0) {
                result[param.name].enum = param.enum;
            }
        }
        return result;
    }
    /**
     * Map MCP type to Qwen type
     * @param mcpType MCP type
     * @returns Qwen type
     */
    mapMcpTypeToQwenType(mcpType) {
        // Convert MCP types to Qwen types
        switch (mcpType.toLowerCase()) {
            case 'string':
            case 'text':
            case 'char':
                return 'string';
            case 'integer':
            case 'int':
            case 'long':
            case 'short':
            case 'byte':
            case 'float':
            case 'double':
            case 'decimal':
            case 'number':
                return 'number';
            case 'boolean':
            case 'bool':
                return 'boolean';
            case 'array':
            case 'list':
            case 'collection':
                return 'array';
            case 'object':
            case 'map':
            case 'dict':
            case 'dictionary':
                return 'object';
            case 'null':
                return 'null';
            default:
                // Default to string for unknown types
                this.outputChannel.appendLine(`Unknown MCP type: ${mcpType}, defaulting to string`);
                return 'string';
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
        this.contextGatherer.dispose();
    }
}
exports.McpQwenBridge = McpQwenBridge;
//# sourceMappingURL=mcpQwenBridge.js.map