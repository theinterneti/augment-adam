"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.QwenApiClient = void 0;
const axios_1 = __importDefault(require("axios"));
const cache_1 = require("./cache");
const errorHandler_1 = require("./errorHandler");
class QwenApiClient {
    constructor(config) {
        this.config = config;
        this.client = axios_1.default.create({
            baseURL: config.apiEndpoint,
            headers: config.apiKey ? {
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Type': 'application/json'
            } : {
                'Content-Type': 'application/json'
            }
        });
        this.cache = cache_1.ResponseCache.getInstance();
    }
    updateConfig(config) {
        this.config = config;
        this.client = axios_1.default.create({
            baseURL: config.apiEndpoint,
            headers: config.apiKey ? {
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Type': 'application/json'
            } : {
                'Content-Type': 'application/json'
            }
        });
        // Update cache configuration if provided
        if (config.cacheTTLMinutes && config.cacheMaxEntries) {
            this.cache.configure(config.cacheMaxEntries, config.cacheTTLMinutes);
        }
    }
    async generateCompletion(options) {
        // Check cache first (unless skipCache is true)
        if (!options.skipCache) {
            const cacheKey = (0, cache_1.generateCacheKey)(options.prompt, {
                systemPrompt: options.systemPrompt,
                maxTokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            });
            const cachedResponse = this.cache.get(cacheKey);
            if (cachedResponse) {
                console.log('Using cached response for prompt:', options.prompt.substring(0, 50) + '...');
                return {
                    ...cachedResponse,
                    cached: true
                };
            }
        }
        try {
            // Set timeout for the request
            const timeoutMs = 30000; // 30 seconds timeout
            const response = await this.client.post('/chat/completions', {
                model: 'qwen3-coder',
                messages: [
                    ...(options.systemPrompt ? [{ role: 'system', content: options.systemPrompt }] : []),
                    { role: 'user', content: options.prompt }
                ],
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            }, { timeout: timeoutMs });
            const result = {
                text: response.data.choices[0].message.content,
                usage: response.data.usage
            };
            // Cache the response (unless skipCache is true)
            if (!options.skipCache) {
                const cacheKey = (0, cache_1.generateCacheKey)(options.prompt, {
                    systemPrompt: options.systemPrompt,
                    maxTokens: options.maxTokens || this.config.maxTokens,
                    temperature: options.temperature || this.config.temperature
                });
                this.cache.set(cacheKey, result);
            }
            return result;
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error calling Qwen API: ${errorDetails.type}`, error);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Generate a streaming completion
     * @param options Request options
     * @param onChunk Callback function to handle streaming chunks
     */
    async generateStreamingCompletion(options, onChunk) {
        // Streaming responses can't be cached, so we don't check the cache
        try {
            // Set timeout for the request
            const timeoutMs = 60000; // 60 seconds timeout for streaming
            const response = await this.client.post('/chat/completions', {
                model: 'qwen3-coder',
                messages: [
                    ...(options.systemPrompt ? [{ role: 'system', content: options.systemPrompt }] : []),
                    { role: 'user', content: options.prompt }
                ],
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature,
                stream: true
            }, {
                timeout: timeoutMs,
                responseType: 'stream'
            });
            // Process the streaming response
            const stream = response.data;
            stream.on('data', (chunk) => {
                try {
                    const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
                    for (const line of lines) {
                        // Skip empty lines and "data: [DONE]" messages
                        if (!line || line === 'data: [DONE]') {
                            continue;
                        }
                        // Remove the "data: " prefix
                        const jsonStr = line.replace(/^data: /, '');
                        try {
                            const json = JSON.parse(jsonStr);
                            if (json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content) {
                                const content = json.choices[0].delta.content;
                                onChunk(content, false);
                            }
                        }
                        catch (parseError) {
                            console.error('Error parsing streaming response JSON:', parseError);
                        }
                    }
                }
                catch (error) {
                    console.error('Error processing stream chunk:', error);
                }
            });
            stream.on('end', () => {
                onChunk('', true); // Signal that streaming is complete
            });
            stream.on('error', (error) => {
                const errorDetails = errorHandler_1.ErrorHandler.processError(error);
                console.error(`Error in stream: ${errorDetails.type}`, error);
                throw new Error(errorDetails.message);
            });
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error setting up streaming: ${errorDetails.type}`, error);
            // Signal error to the handler
            onChunk(`Error: ${errorDetails.message}`, true);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Chat with Qwen using messages
     * @param messages Array of messages
     * @param options Chat options
     * @returns Promise that resolves to the response text
     */
    async chat(messages, options = {}) {
        // Check cache first (unless skipCache is true)
        if (!options.skipCache) {
            const cacheKey = (0, cache_1.generateCacheKey)(JSON.stringify(messages), {
                enableThinking: options.enableThinking,
                temperature: options.temperature || this.config.temperature,
                maxTokens: options.maxTokens || this.config.maxTokens,
                modelName: options.modelName || 'qwen3-coder'
            });
            const cachedResponse = this.cache.get(cacheKey);
            if (cachedResponse) {
                console.log('Using cached response for chat');
                return cachedResponse.text;
            }
        }
        try {
            // Set timeout for the request
            const timeoutMs = 60000; // 60 seconds timeout for chat
            // Add thinking mode if enabled
            let systemMessage = messages.find(m => m.role === 'system');
            if (options.enableThinking && systemMessage) {
                systemMessage.content = `${systemMessage.content}\n\nWhen solving complex problems, use <think></think> tags to show your reasoning process.`;
            }
            const response = await this.client.post('/chat/completions', {
                model: options.modelName || 'qwen3-coder',
                messages,
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            }, { timeout: timeoutMs });
            const result = {
                text: response.data.choices[0].message.content,
                usage: response.data.usage
            };
            // Cache the response (unless skipCache is true)
            if (!options.skipCache) {
                const cacheKey = (0, cache_1.generateCacheKey)(JSON.stringify(messages), {
                    enableThinking: options.enableThinking,
                    temperature: options.temperature || this.config.temperature,
                    maxTokens: options.maxTokens || this.config.maxTokens,
                    modelName: options.modelName || 'qwen3-coder'
                });
                this.cache.set(cacheKey, result);
            }
            return result.text;
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error calling Qwen API chat: ${errorDetails.type}`, error);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Chat with Qwen using messages with streaming response
     * @param messages Array of messages
     * @param options Chat options
     * @param onChunk Callback function to handle streaming chunks
     */
    async chatStream(messages, options = {}, onChunk) {
        try {
            // Set timeout for the request
            const timeoutMs = 60000; // 60 seconds timeout for streaming
            // Add thinking mode if enabled
            let systemMessage = messages.find(m => m.role === 'system');
            if (options.enableThinking && systemMessage) {
                systemMessage.content = `${systemMessage.content}\n\nWhen solving complex problems, use <think></think> tags to show your reasoning process.`;
            }
            const response = await this.client.post('/chat/completions', {
                model: options.modelName || 'qwen3-coder',
                messages,
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature,
                stream: true
            }, {
                timeout: timeoutMs,
                responseType: 'stream'
            });
            // Process the streaming response
            const stream = response.data;
            stream.on('data', (chunk) => {
                try {
                    const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
                    for (const line of lines) {
                        // Skip empty lines and "data: [DONE]" messages
                        if (!line || line === 'data: [DONE]') {
                            continue;
                        }
                        // Remove the "data: " prefix
                        const jsonStr = line.replace(/^data: /, '');
                        try {
                            const json = JSON.parse(jsonStr);
                            if (json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content) {
                                const content = json.choices[0].delta.content;
                                onChunk(content, false);
                            }
                        }
                        catch (parseError) {
                            console.error('Error parsing streaming response JSON:', parseError);
                        }
                    }
                }
                catch (error) {
                    console.error('Error processing stream chunk:', error);
                }
            });
            stream.on('end', () => {
                onChunk('', true); // Signal that streaming is complete
            });
            stream.on('error', (error) => {
                const errorDetails = errorHandler_1.ErrorHandler.processError(error);
                console.error(`Error in stream: ${errorDetails.type}`, error);
                throw new Error(errorDetails.message);
            });
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error setting up streaming chat: ${errorDetails.type}`, error);
            // Signal error to the handler
            onChunk(`Error: ${errorDetails.message}`, true);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Chat with Qwen using messages and tools
     * @param messages Array of messages
     * @param options Chat options including tools
     * @returns Promise that resolves to the response with possible tool calls
     */
    async chatWithTools(messages, options = {}) {
        // Check cache first (unless skipCache is true)
        if (!options.skipCache) {
            const cacheKey = (0, cache_1.generateCacheKey)(JSON.stringify(messages), {
                enableThinking: options.enableThinking,
                thinkingMode: options.thinkingMode,
                thinkingBudget: options.thinkingBudget,
                temperature: options.temperature || this.config.temperature,
                maxTokens: options.maxTokens || this.config.maxTokens,
                modelName: options.modelName || 'qwen3-coder',
                tools: options.tools ? JSON.stringify(options.tools) : undefined
            });
            const cachedResponse = this.cache.get(cacheKey);
            if (cachedResponse) {
                console.log('Using cached response for chat with tools');
                return cachedResponse;
            }
        }
        try {
            // Set timeout for the request
            const timeoutMs = 60000; // 60 seconds timeout for chat with tools
            // Apply thinking mode
            let systemMessage = messages.find(m => m.role === 'system');
            this._applyThinkingMode(systemMessage, options);
            // Prepare the request payload
            const payload = {
                model: options.modelName || 'qwen3-coder',
                messages,
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            };
            // Add tools if provided
            if (options.tools && options.tools.length > 0) {
                payload.tools = options.tools;
            }
            const response = await this.client.post('/chat/completions', payload, { timeout: timeoutMs });
            // Extract tool calls if present
            const toolCalls = response.data.choices[0].message.tool_calls || [];
            const result = {
                text: response.data.choices[0].message.content,
                tool_calls: toolCalls.length > 0 ? toolCalls : undefined,
                usage: response.data.usage
            };
            // Cache the response (unless skipCache is true)
            if (!options.skipCache) {
                const cacheKey = (0, cache_1.generateCacheKey)(JSON.stringify(messages), {
                    enableThinking: options.enableThinking,
                    thinkingMode: options.thinkingMode,
                    thinkingBudget: options.thinkingBudget,
                    temperature: options.temperature || this.config.temperature,
                    maxTokens: options.maxTokens || this.config.maxTokens,
                    modelName: options.modelName || 'qwen3-coder',
                    tools: options.tools ? JSON.stringify(options.tools) : undefined
                });
                this.cache.set(cacheKey, result);
            }
            return result;
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error calling Qwen API chat with tools: ${errorDetails.type}`, error);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Chat with Qwen using messages and tools with streaming response
     * @param messages Array of messages
     * @param options Chat options including tools
     * @param onChunk Callback function to handle streaming chunks
     */
    async chatStreamWithTools(messages, options = {}, onChunk) {
        try {
            // Set timeout for the request
            const timeoutMs = 60000; // 60 seconds timeout for streaming
            // Apply thinking mode
            let systemMessage = messages.find(m => m.role === 'system');
            this._applyThinkingMode(systemMessage, options);
            // Prepare the request payload
            const payload = {
                model: options.modelName || 'qwen3-coder',
                messages,
                max_tokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature,
                stream: true
            };
            // Add tools if provided
            if (options.tools && options.tools.length > 0) {
                payload.tools = options.tools;
            }
            const response = await this.client.post('/chat/completions', payload, {
                timeout: timeoutMs,
                responseType: 'stream'
            });
            // Process the streaming response
            const stream = response.data;
            let toolCalls = [];
            stream.on('data', (chunk) => {
                try {
                    const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
                    for (const line of lines) {
                        // Skip empty lines and "data: [DONE]" messages
                        if (!line || line === 'data: [DONE]') {
                            continue;
                        }
                        // Remove the "data: " prefix
                        const jsonStr = line.replace(/^data: /, '');
                        try {
                            const json = JSON.parse(jsonStr);
                            // Handle content
                            if (json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content) {
                                const content = json.choices[0].delta.content;
                                onChunk(content, false);
                            }
                            // Handle tool calls
                            if (json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.tool_calls) {
                                // Process tool calls
                                for (const toolCallDelta of json.choices[0].delta.tool_calls) {
                                    // Find existing tool call or create a new one
                                    let toolCall = toolCalls.find(tc => tc.id === toolCallDelta.id);
                                    if (!toolCall) {
                                        // Create a new tool call
                                        toolCall = {
                                            id: toolCallDelta.id,
                                            type: 'function',
                                            function: {
                                                name: toolCallDelta.function?.name || '',
                                                arguments: toolCallDelta.function?.arguments || ''
                                            }
                                        };
                                        toolCalls.push(toolCall);
                                    }
                                    else {
                                        // Update existing tool call
                                        if (toolCallDelta.function?.name) {
                                            toolCall.function.name = toolCallDelta.function.name;
                                        }
                                        if (toolCallDelta.function?.arguments) {
                                            toolCall.function.arguments += toolCallDelta.function.arguments;
                                        }
                                    }
                                    // Notify about the tool call
                                    onChunk('', false, toolCall);
                                }
                            }
                        }
                        catch (parseError) {
                            console.error('Error parsing streaming response JSON:', parseError);
                        }
                    }
                }
                catch (error) {
                    console.error('Error processing stream chunk:', error);
                }
            });
            stream.on('end', () => {
                onChunk('', true); // Signal that streaming is complete
            });
            stream.on('error', (error) => {
                const errorDetails = errorHandler_1.ErrorHandler.processError(error);
                console.error(`Error in stream: ${errorDetails.type}`, error);
                throw new Error(errorDetails.message);
            });
        }
        catch (error) {
            // Use the error handler to process the error
            const errorDetails = errorHandler_1.ErrorHandler.processError(error);
            console.error(`Error setting up streaming chat with tools: ${errorDetails.type}`, error);
            // Signal error to the handler
            onChunk(`Error: ${errorDetails.message}`, true);
            // Throw a more informative error
            throw new Error(errorDetails.message);
        }
    }
    /**
     * Apply thinking mode to the system message based on options
     * @param systemMessage The system message to modify
     * @param options Chat options
     */
    _applyThinkingMode(systemMessage, options) {
        if (!systemMessage) {
            return;
        }
        // Handle legacy enableThinking option
        if (options.enableThinking !== undefined) {
            if (options.enableThinking) {
                systemMessage.content = `${systemMessage.content}\n\nWhen solving complex problems, use <think></think> tags to show your reasoning process.`;
            }
            return;
        }
        // Handle new thinkingMode option
        if (options.thinkingMode) {
            switch (options.thinkingMode) {
                case 'always':
                    systemMessage.content = `${systemMessage.content}\n\nAlways use <think></think> tags to show your reasoning process for all problems.`;
                    break;
                case 'auto':
                    systemMessage.content = `${systemMessage.content}\n\nWhen solving complex problems, use <think></think> tags to show your reasoning process. For simple tasks, respond directly.`;
                    if (options.thinkingBudget) {
                        systemMessage.content += `\n\nLimit your thinking to approximately ${options.thinkingBudget} tokens.`;
                    }
                    break;
                case 'never':
                    // No thinking tags
                    break;
            }
        }
    }
    /**
     * Clear the response cache
     */
    clearCache() {
        this.cache.clear();
    }
}
exports.QwenApiClient = QwenApiClient;
//# sourceMappingURL=qwenApi.js.map