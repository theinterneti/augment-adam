"use strict";
/**
 * Agent Selector
 *
 * Chooses the most appropriate agent for each subtask based on expertise, complexity, and available resources.
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
exports.AgentSelector = void 0;
const vscode = __importStar(require("vscode"));
const types_1 = require("./types");
const configuration_1 = require("../configuration");
/**
 * Agent Selector class
 */
class AgentSelector {
    /**
     * Constructor
     */
    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Agent Selector');
        // Initialize agent configurations
        this.agentConfigs = {
            [types_1.AgentType.Coordinator]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.MoESmall, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.MoESmall, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.XXLarge, thinkingMode: types_1.ThinkingMode.Enabled }
            },
            [types_1.AgentType.Development]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.MoESmall, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.XXLarge, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.XLarge, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.Testing]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.XLarge, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.CICD]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Disabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Small, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.GitHub]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Disabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Small, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.Documentation]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Small, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.Architecture]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.MoESmall, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.XXLarge, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.XLarge, thinkingMode: types_1.ThinkingMode.Enabled }
            },
            [types_1.AgentType.Security]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.XLarge, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Disabled }
            },
            [types_1.AgentType.Performance]: {
                [types_1.TaskComplexity.High]: { modelSize: types_1.ModelSize.XLarge, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Medium]: { modelSize: types_1.ModelSize.Large, thinkingMode: types_1.ThinkingMode.Enabled },
                [types_1.TaskComplexity.Low]: { modelSize: types_1.ModelSize.Medium, thinkingMode: types_1.ThinkingMode.Disabled }
            }
        };
        this.outputChannel.appendLine('Agent Selector initialized');
    }
    /**
     * Select appropriate agents for each subtask
     * @param subtasks The subtasks to assign agents to
     * @param availableResources Available system resources
     * @returns Agent assignments for each subtask
     */
    async selectAgents(subtasks, availableResources) {
        try {
            this.outputChannel.appendLine(`Selecting agents for ${Object.keys(subtasks).length} subtasks`);
            // Get user configuration
            const config = (0, configuration_1.getConfiguration)();
            const preferredModel = config.get('preferredModel', 'auto');
            const preferThinking = config.get('preferThinkingMode', true);
            // Initialize agent assignments
            const agentAssignments = {};
            // Sort subtasks by dependencies (fewer dependencies first)
            const sortedSubtasks = Object.values(subtasks).sort((a, b) => a.dependencies.length - b.dependencies.length);
            // Assign agents to each subtask
            for (const subtask of sortedSubtasks) {
                const expertise = subtask.expertise;
                const complexity = subtask.complexity;
                // Get the appropriate agent configuration
                let agentConfig = this.agentConfigs[expertise][complexity];
                // Apply user preferences
                if (preferredModel !== 'auto') {
                    // Override model size based on user preference
                    const userModelSize = this._getUserModelSize(preferredModel);
                    if (userModelSize) {
                        agentConfig = { ...agentConfig, modelSize: userModelSize };
                    }
                }
                if (preferThinking) {
                    // Prefer thinking mode if user has enabled it
                    agentConfig = { ...agentConfig, thinkingMode: types_1.ThinkingMode.Enabled };
                }
                // Check if we have enough resources for this agent
                if (this._checkResources(agentConfig, availableResources)) {
                    agentAssignments[subtask.id] = {
                        type: expertise,
                        modelSize: agentConfig.modelSize,
                        thinkingMode: agentConfig.thinkingMode
                    };
                }
                else {
                    // Fallback to a smaller model if resources are constrained
                    const fallbackAgent = this._getFallbackAgent(expertise, availableResources);
                    agentAssignments[subtask.id] = fallbackAgent;
                }
                this.outputChannel.appendLine(`Assigned ${agentAssignments[subtask.id].type} agent with ${agentAssignments[subtask.id].modelSize} model to subtask ${subtask.id}`);
            }
            return agentAssignments;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error selecting agents: ${error.message}`);
            throw error;
        }
    }
    /**
     * Check if we have enough resources for this agent
     * @param agentConfig The agent configuration
     * @param availableResources Available system resources
     * @returns Whether we have enough resources
     */
    _checkResources(agentConfig, availableResources) {
        // Calculate resource requirements based on model size and thinking mode
        let memoryRequirement = 0;
        let cpuRequirement = 0;
        // Memory requirements
        switch (agentConfig.modelSize) {
            case types_1.ModelSize.MoELarge:
                memoryRequirement = 0.8;
                break;
            case types_1.ModelSize.MoESmall:
                memoryRequirement = 0.5;
                break;
            case types_1.ModelSize.XXLarge:
                memoryRequirement = 0.4;
                break;
            case types_1.ModelSize.XLarge:
                memoryRequirement = 0.3;
                break;
            case types_1.ModelSize.Large:
                memoryRequirement = 0.2;
                break;
            case types_1.ModelSize.Medium:
                memoryRequirement = 0.1;
                break;
            case types_1.ModelSize.Small:
                memoryRequirement = 0.05;
                break;
            case types_1.ModelSize.Tiny:
                memoryRequirement = 0.02;
                break;
        }
        // CPU requirements
        switch (agentConfig.modelSize) {
            case types_1.ModelSize.MoELarge:
                cpuRequirement = 0.8;
                break;
            case types_1.ModelSize.MoESmall:
                cpuRequirement = 0.5;
                break;
            case types_1.ModelSize.XXLarge:
                cpuRequirement = 0.4;
                break;
            case types_1.ModelSize.XLarge:
                cpuRequirement = 0.3;
                break;
            case types_1.ModelSize.Large:
                cpuRequirement = 0.2;
                break;
            case types_1.ModelSize.Medium:
                cpuRequirement = 0.1;
                break;
            case types_1.ModelSize.Small:
                cpuRequirement = 0.05;
                break;
            case types_1.ModelSize.Tiny:
                cpuRequirement = 0.02;
                break;
        }
        // Adjust for thinking mode
        if (agentConfig.thinkingMode === types_1.ThinkingMode.Enabled) {
            memoryRequirement *= 1.5;
            cpuRequirement *= 1.5;
        }
        // Check if we have enough resources
        return (availableResources.memory >= memoryRequirement &&
            availableResources.cpu >= cpuRequirement);
    }
    /**
     * Get a fallback agent with lower resource requirements
     * @param expertise The required expertise
     * @param availableResources Available system resources
     * @returns A fallback agent configuration
     */
    _getFallbackAgent(expertise, availableResources) {
        this.outputChannel.appendLine(`Finding fallback agent for ${expertise} due to resource constraints`);
        // Try progressively smaller models
        const modelSizes = [
            types_1.ModelSize.Medium,
            types_1.ModelSize.Small,
            types_1.ModelSize.Tiny
        ];
        // Try without thinking mode first
        for (const modelSize of modelSizes) {
            const config = { modelSize, thinkingMode: types_1.ThinkingMode.Disabled };
            if (this._checkResources(config, availableResources)) {
                return { type: expertise, ...config };
            }
        }
        // If all else fails, use the smallest possible configuration
        return {
            type: expertise,
            modelSize: types_1.ModelSize.Tiny,
            thinkingMode: types_1.ThinkingMode.Disabled
        };
    }
    /**
     * Convert user model preference to ModelSize
     * @param preferredModel The user's preferred model
     * @returns The corresponding ModelSize or undefined
     */
    _getUserModelSize(preferredModel) {
        switch (preferredModel.toLowerCase()) {
            case 'tiny':
                return types_1.ModelSize.Tiny;
            case 'small':
                return types_1.ModelSize.Small;
            case 'medium':
                return types_1.ModelSize.Medium;
            case 'large':
                return types_1.ModelSize.Large;
            case 'xlarge':
                return types_1.ModelSize.XLarge;
            case 'xxlarge':
                return types_1.ModelSize.XXLarge;
            case 'moesmall':
            case 'moe-small':
                return types_1.ModelSize.MoESmall;
            case 'moelarge':
            case 'moe-large':
                return types_1.ModelSize.MoELarge;
            default:
                return undefined;
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.AgentSelector = AgentSelector;
//# sourceMappingURL=agentSelector.js.map