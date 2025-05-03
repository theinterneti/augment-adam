"use strict";
/**
 * Task Decomposer
 *
 * Breaks down complex user requests into smaller, manageable subtasks.
 * Uses Qwen's thinking mode to perform detailed analysis.
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
exports.TaskDecomposer = void 0;
const vscode = __importStar(require("vscode"));
const uuid_1 = require("uuid");
const types_1 = require("./types");
/**
 * Task Decomposer class
 */
class TaskDecomposer {
    /**
     * Constructor
     * @param qwenApi The Qwen API client
     */
    constructor(qwenApi) {
        this.qwenApi = qwenApi;
        this.outputChannel = vscode.window.createOutputChannel('Task Decomposer');
    }
    /**
     * Decompose a user request into subtasks
     * @param userRequest The user's request
     * @param availableResources Available system resources
     * @returns A record of subtasks
     */
    async decompose(userRequest, availableResources) {
        try {
            this.outputChannel.appendLine(`Decomposing request: ${userRequest}`);
            // Prepare the system message for task decomposition
            const systemMessage = `
        You are a task decomposition expert. Your job is to break down complex DevOps tasks into smaller, manageable subtasks.
        For each subtask, provide:
        1. A unique ID
        2. A clear description
        3. Required expertise (development, testing, ci_cd, github, documentation, architecture, security, performance)
        4. Estimated complexity (low, medium, high)
        5. Dependencies on other subtasks (if any)
        
        Format your response as a JSON object with the following structure:
        {
          "subtasks": [
            {
              "id": "unique_id",
              "description": "Clear description of the subtask",
              "expertise": "One of: development, testing, ci_cd, github, documentation, architecture, security, performance",
              "complexity": "One of: low, medium, high",
              "dependencies": ["id_of_dependency_1", "id_of_dependency_2"]
            },
            ...
          ]
        }
        
        Consider the available system resources when decomposing the task:
        - Memory: ${availableResources.memory * 100}%
        - CPU: ${availableResources.cpu * 100}%
        - Active Agents: ${availableResources.activeAgents}
        
        If resources are limited, prioritize essential subtasks and reduce complexity.
      `;
            // Prepare the messages for the API call
            const messages = [
                { role: 'system', content: systemMessage },
                { role: 'user', content: `Please decompose the following DevOps task into subtasks: ${userRequest}` }
            ];
            // Call the Qwen API with thinking mode enabled
            const response = await this.qwenApi.chat(messages, {
                enableThinking: true,
                temperature: 0.2,
                maxTokens: 2048
            });
            // Parse the response to extract subtasks
            const subtasks = this._parseSubtasks(response);
            // Validate subtasks and ensure they're within resource constraints
            const validatedSubtasks = this._validateSubtasks(subtasks, availableResources);
            this.outputChannel.appendLine(`Decomposed into ${Object.keys(validatedSubtasks).length} subtasks`);
            return validatedSubtasks;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error decomposing task: ${error.message}`);
            throw error;
        }
    }
    /**
     * Parse the LLM response to extract subtasks
     * @param response The LLM response
     * @returns A record of subtasks
     */
    _parseSubtasks(response) {
        try {
            // Extract JSON from the response
            const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/) ||
                response.match(/{[\s\S]*?}/);
            if (!jsonMatch) {
                throw new Error('No valid JSON found in the response');
            }
            const jsonStr = jsonMatch[0].startsWith('```') ? jsonMatch[1] : jsonMatch[0];
            const parsed = JSON.parse(jsonStr);
            if (!parsed.subtasks || !Array.isArray(parsed.subtasks)) {
                throw new Error('Invalid subtasks format in the response');
            }
            // Convert array to record
            const subtasks = {};
            for (const subtask of parsed.subtasks) {
                // Ensure the subtask has a valid ID
                const id = subtask.id || (0, uuid_1.v4)();
                // Ensure the subtask has valid dependencies
                const dependencies = Array.isArray(subtask.dependencies) ? subtask.dependencies : [];
                // Create the subtask object
                subtasks[id] = {
                    id,
                    description: subtask.description || '',
                    expertise: this._validateExpertise(subtask.expertise),
                    complexity: this._validateComplexity(subtask.complexity),
                    dependencies
                };
            }
            return subtasks;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error parsing subtasks: ${error.message}`);
            // Fallback: create a single subtask
            const id = (0, uuid_1.v4)();
            return {
                [id]: {
                    id,
                    description: 'Execute the requested task',
                    expertise: types_1.AgentType.Development,
                    complexity: types_1.TaskComplexity.Medium,
                    dependencies: []
                }
            };
        }
    }
    /**
     * Validate the expertise field
     * @param expertise The expertise string
     * @returns A valid AgentType
     */
    _validateExpertise(expertise) {
        if (!expertise || typeof expertise !== 'string') {
            return types_1.AgentType.Development;
        }
        const normalized = expertise.toLowerCase();
        switch (normalized) {
            case 'development':
                return types_1.AgentType.Development;
            case 'testing':
                return types_1.AgentType.Testing;
            case 'ci_cd':
            case 'cicd':
                return types_1.AgentType.CICD;
            case 'github':
                return types_1.AgentType.GitHub;
            case 'documentation':
                return types_1.AgentType.Documentation;
            case 'architecture':
                return types_1.AgentType.Architecture;
            case 'security':
                return types_1.AgentType.Security;
            case 'performance':
                return types_1.AgentType.Performance;
            default:
                return types_1.AgentType.Development;
        }
    }
    /**
     * Validate the complexity field
     * @param complexity The complexity string
     * @returns A valid TaskComplexity
     */
    _validateComplexity(complexity) {
        if (!complexity || typeof complexity !== 'string') {
            return types_1.TaskComplexity.Medium;
        }
        const normalized = complexity.toLowerCase();
        switch (normalized) {
            case 'low':
                return types_1.TaskComplexity.Low;
            case 'medium':
                return types_1.TaskComplexity.Medium;
            case 'high':
                return types_1.TaskComplexity.High;
            default:
                return types_1.TaskComplexity.Medium;
        }
    }
    /**
     * Validate subtasks and ensure they're within resource constraints
     * @param subtasks The subtasks to validate
     * @param availableResources Available system resources
     * @returns Validated subtasks
     */
    _validateSubtasks(subtasks, availableResources) {
        // Check if we have enough resources for all subtasks
        const totalSubtasks = Object.keys(subtasks).length;
        if (totalSubtasks > 10 && availableResources.memory < 0.5) {
            // If resources are limited, reduce the number of subtasks
            this.outputChannel.appendLine('Limited resources detected, reducing number of subtasks');
            // Sort subtasks by dependencies (fewer dependencies first)
            const sortedSubtasks = Object.values(subtasks).sort((a, b) => a.dependencies.length - b.dependencies.length);
            // Keep only the first 5-10 subtasks
            const maxSubtasks = Math.max(5, Math.min(10, Math.floor(availableResources.memory * 20)));
            const reducedSubtasks = {};
            for (let i = 0; i < Math.min(maxSubtasks, sortedSubtasks.length); i++) {
                const subtask = sortedSubtasks[i];
                reducedSubtasks[subtask.id] = subtask;
            }
            return reducedSubtasks;
        }
        // Check for circular dependencies
        const visited = new Set();
        const visiting = new Set();
        const hasCycle = (id) => {
            if (visiting.has(id)) {
                return true;
            }
            if (visited.has(id)) {
                return false;
            }
            visiting.add(id);
            for (const depId of subtasks[id].dependencies) {
                if (!subtasks[depId]) {
                    // Remove invalid dependency
                    subtasks[id].dependencies = subtasks[id].dependencies.filter(d => d !== depId);
                    continue;
                }
                if (hasCycle(depId)) {
                    return true;
                }
            }
            visiting.delete(id);
            visited.add(id);
            return false;
        };
        // Check each subtask for cycles
        for (const id in subtasks) {
            if (hasCycle(id)) {
                // Remove circular dependencies
                this.outputChannel.appendLine(`Circular dependency detected in subtask ${id}, removing dependencies`);
                subtasks[id].dependencies = [];
            }
        }
        return subtasks;
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.TaskDecomposer = TaskDecomposer;
//# sourceMappingURL=taskDecomposer.js.map