"use strict";
/**
 * Result Aggregator
 *
 * Combines outputs from multiple agents into a coherent response.
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.ResultAggregator = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Result Aggregator class
 */
class ResultAggregator {
    /**
     * Constructor
     * @param qwenApi The Qwen API client
     */
    constructor(qwenApi) {
        this.qwenApi = qwenApi;
        this.outputChannel = vscode.window.createOutputChannel('Result Aggregator');
    }
    /**
     * Aggregate results from multiple agents
     * @param results The results from each agent
     * @param subtasks The original subtasks
     * @returns The aggregated response
     */
    async aggregate(results, subtasks) {
        try {
            this.outputChannel.appendLine(`Aggregating results from ${Object.keys(results).length} agents`);
            // Check if we have any results
            if (Object.keys(results).length === 0) {
                return 'No results were generated. Please try again with a more specific request.';
            }
            // Check if we have only one result
            if (Object.keys(results).length === 1) {
                const result = Object.values(results)[0];
                return result.content;
            }
            // Prepare the system message
            const systemMessage = `
        You are a Result Aggregator. Your job is to combine outputs from multiple specialized agents into a coherent, unified response.
        Ensure that the final response is well-structured, consistent, and addresses all aspects of the original request.
        
        Follow these guidelines:
        1. Organize information logically, grouping related content together
        2. Eliminate redundancies while preserving important details
        3. Ensure a consistent tone and style throughout
        4. Highlight key insights and recommendations
        5. Format code snippets, commands, and technical information appropriately
        6. Provide a clear summary at the beginning if the response is lengthy
      `;
            // Prepare the context with all results
            let context = "Here are the results from different specialized agents:\n\n";
            // Sort subtasks by dependencies to maintain logical order
            const sortedSubtaskIds = this._sortSubtasksByDependencies(subtasks);
            // Add results in dependency order
            for (const subtaskId of sortedSubtaskIds) {
                if (results[subtaskId]) {
                    const subtask = subtasks[subtaskId];
                    const result = results[subtaskId];
                    context += `## Subtask: ${subtask.description}\n`;
                    context += `Expertise: ${subtask.expertise}\n`;
                    context += `Status: ${result.status}\n`;
                    if (result.status === 'error') {
                        context += `Error: ${result.error}\n\n`;
                    }
                    else {
                        context += `Result:\n${result.content}\n\n`;
                    }
                }
            }
            // Prepare the user message
            const userMessage = `Please combine these results into a coherent response:\n\n${context}`;
            // Prepare the messages for the API call
            const messages = [
                { role: 'system', content: systemMessage },
                { role: 'user', content: userMessage }
            ];
            // Call the Qwen API with thinking mode enabled
            const response = await this.qwenApi.chat(messages, {
                enableThinking: true,
                temperature: 0.3,
                maxTokens: 4096
            });
            this.outputChannel.appendLine('Results aggregated successfully');
            return response;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error aggregating results: ${error.message}`);
            // Fallback: concatenate results
            let fallbackResponse = '# Combined Agent Results\n\n';
            for (const subtaskId in results) {
                const result = results[subtaskId];
                const subtask = subtasks[subtaskId];
                fallbackResponse += `## ${subtask.description}\n\n`;
                if (result.status === 'error') {
                    fallbackResponse += `**Error:** ${result.error}\n\n`;
                }
                else {
                    fallbackResponse += `${result.content}\n\n`;
                }
            }
            return fallbackResponse;
        }
    }
    /**
     * Sort subtasks by dependencies
     * @param subtasks The subtasks to sort
     * @returns Sorted subtask IDs
     */
    _sortSubtasksByDependencies(subtasks) {
        const visited = new Set();
        const result = [];
        const visit = (id) => {
            if (visited.has(id)) {
                return;
            }
            visited.add(id);
            // Visit dependencies first
            for (const depId of subtasks[id].dependencies) {
                if (subtasks[depId]) {
                    visit(depId);
                }
            }
            result.push(id);
        };
        // Visit all subtasks
        for (const id in subtasks) {
            visit(id);
        }
        return result;
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.ResultAggregator = ResultAggregator;
//# sourceMappingURL=resultAggregator.js.map