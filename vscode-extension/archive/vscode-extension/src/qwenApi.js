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
     * Clear the response cache
     */
    clearCache() {
        this.cache.clear();
    }
}
exports.QwenApiClient = QwenApiClient;
//# sourceMappingURL=qwenApi.js.map