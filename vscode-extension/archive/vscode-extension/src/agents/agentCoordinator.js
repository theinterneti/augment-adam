"use strict";
/**
 * Agent Coordinator
 *
 * The central component that orchestrates the hierarchical agent system.
 * Responsible for task decomposition, agent selection, and result aggregation.
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
exports.AgentCoordinator = void 0;
const vscode = __importStar(require("vscode"));
const types_1 = require("./types");
const taskDecomposer_1 = require("./taskDecomposer");
const agentSelector_1 = require("./agentSelector");
const resourceManager_1 = require("./resourceManager");
const resultAggregator_1 = require("./resultAggregator");
const qwenApi_1 = require("../qwenApi");
/**
 * Agent Coordinator class
 */
class AgentCoordinator {
    /**
     * Constructor
     */
    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Agent Coordinator');
        this.qwenApi = new qwenApi_1.QwenApiClient();
        this.taskDecomposer = new taskDecomposer_1.TaskDecomposer(this.qwenApi);
        this.agentSelector = new agentSelector_1.AgentSelector();
        this.resourceManager = new resourceManager_1.ResourceManager();
        this.resultAggregator = new resultAggregator_1.ResultAggregator(this.qwenApi);
        this.outputChannel.appendLine('Agent Coordinator initialized');
    }
    /**
     * Process a user request
     * @param userRequest The user's request
     * @returns The final response
     */
    async processRequest(userRequest) {
        try {
            this.outputChannel.appendLine(`Processing request: ${userRequest}`);
            // Get available resources
            const availableResources = await this.resourceManager.getAvailableResources();
            this.outputChannel.appendLine(`Available resources: ${JSON.stringify(availableResources)}`);
            // Decompose the task
            const subtasks = await this.taskDecomposer.decompose(userRequest, availableResources);
            this.outputChannel.appendLine(`Task decomposed into ${Object.keys(subtasks).length} subtasks`);
            // Select appropriate agents for each subtask
            const agentAssignments = await this.agentSelector.selectAgents(subtasks, availableResources);
            this.outputChannel.appendLine(`Agent assignments: ${JSON.stringify(agentAssignments)}`);
            // Execute subtasks with assigned agents
            const results = {};
            for (const subtaskId in agentAssignments) {
                const agentInfo = agentAssignments[subtaskId];
                const subtask = subtasks[subtaskId];
                this.outputChannel.appendLine(`Executing subtask ${subtaskId} with agent ${agentInfo.type}`);
                // Check if all dependencies are completed
                const dependenciesMet = subtask.dependencies.every(depId => results[depId] && results[depId].status === 'success');
                if (!dependenciesMet) {
                    this.outputChannel.appendLine(`Skipping subtask ${subtaskId} due to unmet dependencies`);
                    continue;
                }
                // Execute the subtask
                try {
                    const agent = await this.instantiateAgent(agentInfo);
                    results[subtaskId] = await agent.execute(subtask);
                    this.outputChannel.appendLine(`Subtask ${subtaskId} completed successfully`);
                }
                catch (error) {
                    this.outputChannel.appendLine(`Error executing subtask ${subtaskId}: ${error.message}`);
                    results[subtaskId] = {
                        subtaskId,
                        content: '',
                        status: 'error',
                        error: error.message
                    };
                }
            }
            // Aggregate results
            const finalResponse = await this.resultAggregator.aggregate(results, subtasks);
            this.outputChannel.appendLine('Request processing completed');
            return finalResponse;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error processing request: ${error.message}`);
            throw error;
        }
    }
    /**
     * Instantiate an agent based on agent info
     * @param agentInfo The agent information
     * @returns The instantiated agent
     */
    async instantiateAgent(agentInfo) {
        // This is a placeholder for agent instantiation
        // In a real implementation, we would dynamically import and instantiate the appropriate agent
        const agentType = agentInfo.type;
        const modelSize = agentInfo.modelSize;
        const thinkingMode = agentInfo.thinkingMode;
        this.outputChannel.appendLine(`Instantiating agent: ${agentType} with model ${modelSize} and thinking mode ${thinkingMode}`);
        // Register the agent with the resource manager
        const agentId = await this.resourceManager.registerAgent(agentType, {
            modelSize,
            thinkingMode
        });
        // Import the appropriate agent class
        try {
            switch (agentType) {
                case types_1.AgentType.Development:
                    const { DevelopmentAgent } = await Promise.resolve().then(() => __importStar(require('./developmentAgent')));
                    return new DevelopmentAgent(agentId, this.qwenApi, modelSize, thinkingMode);
                case types_1.AgentType.Testing:
                    const { TestingAgent } = await Promise.resolve().then(() => __importStar(require('./testingAgent')));
                    return new TestingAgent(agentId, this.qwenApi, modelSize, thinkingMode);
                case types_1.AgentType.CICD:
                    const { CICDAgent } = await Promise.resolve().then(() => __importStar(require('./cicdAgent')));
                    return new CICDAgent(agentId, this.qwenApi, modelSize, thinkingMode);
                case types_1.AgentType.GitHub:
                    const { GitHubAgent } = await Promise.resolve().then(() => __importStar(require('./githubAgent')));
                    return new GitHubAgent(agentId, this.qwenApi, modelSize, thinkingMode);
                default:
                    throw new Error(`Unsupported agent type: ${agentType}`);
            }
        }
        catch (error) {
            this.outputChannel.appendLine(`Error instantiating agent: ${error.message}`);
            await this.resourceManager.unregisterAgent(agentId);
            throw error;
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.AgentCoordinator = AgentCoordinator;
//# sourceMappingURL=agentCoordinator.js.map