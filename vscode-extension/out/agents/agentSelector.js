"use strict";
/**
 * Agent Selector
 *
 * Chooses the most appropriate agent for each subtask based on expertise, complexity, and available resources.
 * Also provides dynamic agent selection based on task requirements.
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
const configuration_1 = require("../configuration");
const types_1 = require("./types");
/**
 * Agent Selector class
 */
class AgentSelector {
    /**
     * Constructor
     */
    constructor() {
        this.agents = [];
        this.agentAvailability = new Map();
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
     * Register an agent with the selector
     * @param agent The agent to register
     */
    registerAgent(agent) {
        this.agents.push(agent);
        this.outputChannel.appendLine(`Registered agent: ${agent.name}`);
    }
    /**
     * Select the most appropriate agent for a task
     * @param task The task to select an agent for
     * @returns The selected agent
     */
    async selectAgent(task) {
        try {
            this.outputChannel.appendLine(`Selecting agent for task: ${task.description}`);
            // Determine task complexity if not specified
            if (!task.complexity) {
                task.complexity = this.analyzeTaskComplexity(task.description);
                this.outputChannel.appendLine(`Inferred task complexity: ${task.complexity}`);
            }
            // Filter agents by availability
            const availableAgents = this.agents.filter(agent => this.isAgentAvailable(agent.name));
            if (availableAgents.length === 0) {
                throw new Error('No agents available');
            }
            // Filter agents by complexity
            const complexityMap = {
                [types_1.TaskComplexity.Simple]: 1,
                [types_1.TaskComplexity.Moderate]: 2,
                [types_1.TaskComplexity.Complex]: 3,
                [types_1.TaskComplexity.VeryComplex]: 4
            };
            const taskComplexityValue = complexityMap[task.complexity];
            const capableAgents = availableAgents.filter(agent => {
                const agentComplexityValue = complexityMap[agent.maxComplexity];
                return agentComplexityValue >= taskComplexityValue;
            });
            if (capableAgents.length === 0) {
                // Fallback to the agent with the highest complexity capability
                const fallbackAgent = availableAgents.sort((a, b) => complexityMap[b.maxComplexity] - complexityMap[a.maxComplexity])[0];
                this.outputChannel.appendLine(`No agent capable of handling complexity ${task.complexity}, falling back to ${fallbackAgent.name}`);
                return fallbackAgent;
            }
            // Filter by required capabilities
            let filteredAgents = capableAgents;
            if (task.requiresContext) {
                filteredAgents = filteredAgents.filter(agent => agent.capabilities.includes('context'));
            }
            if (task.requiresTools) {
                filteredAgents = filteredAgents.filter(agent => agent.capabilities.includes('tools'));
            }
            if (filteredAgents.length === 0) {
                this.outputChannel.appendLine(`No agent with required capabilities, falling back to most capable agent`);
                return capableAgents[0];
            }
            // Filter by domain specialization if specified
            if (task.domain && task.domain !== 'general') {
                const domainAgents = filteredAgents.filter(agent => agent.specializations?.some(spec => spec.toLowerCase().includes(task.domain.toLowerCase())));
                if (domainAgents.length > 0) {
                    filteredAgents = domainAgents;
                    this.outputChannel.appendLine(`Found ${domainAgents.length} agents specialized in ${task.domain}`);
                }
            }
            // Filter by required tools if specified
            if (task.requiredTools && task.requiredTools.length > 0) {
                // For this example, we'll just check if the agent has tools capability
                // In a real implementation, we would check if the agent supports the specific tools
                const toolAgents = filteredAgents.filter(agent => agent.capabilities.includes('tools'));
                if (toolAgents.length > 0) {
                    filteredAgents = toolAgents;
                    this.outputChannel.appendLine(`Found ${toolAgents.length} agents with required tool support`);
                }
            }
            // Select the best agent from the filtered list
            // For now, we'll just take the first one
            // In a real implementation, we might use a more sophisticated selection algorithm
            const selectedAgent = filteredAgents[0];
            this.outputChannel.appendLine(`Selected agent: ${selectedAgent.name}`);
            return selectedAgent;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error selecting agent: ${error instanceof Error ? error.message : String(error)}`);
            // Return a default agent as fallback
            const defaultAgent = this.agents.find(a => a.name === 'DevelopmentAgent') || this.agents[0];
            this.outputChannel.appendLine(`Falling back to default agent: ${defaultAgent.name}`);
            return defaultAgent;
        }
    }
    /**
     * Analyze task description to determine complexity
     * @param description Task description
     * @returns Inferred task complexity
     */
    analyzeTaskComplexity(description) {
        const description_lower = description.toLowerCase();
        // Check for keywords indicating very complex tasks
        const veryComplexKeywords = [
            'architecture', 'redesign', 'system design', 'microservice',
            'distributed', 'scale', 'optimize', 'performance', 'security',
            'refactor', 'monolithic'
        ];
        if (veryComplexKeywords.some(keyword => description_lower.includes(keyword))) {
            return types_1.TaskComplexity.Complex;
        }
        // Check for keywords indicating complex tasks
        const complexKeywords = [
            'implement', 'create', 'develop', 'build', 'design',
            'algorithm', 'feature', 'functionality', 'integration'
        ];
        if (complexKeywords.some(keyword => description_lower.includes(keyword))) {
            return types_1.TaskComplexity.Moderate;
        }
        // Check for keywords indicating simple tasks
        const simpleKeywords = [
            'fix', 'update', 'change', 'modify', 'add', 'remove',
            'format', 'rename', 'explain', 'help'
        ];
        if (simpleKeywords.some(keyword => description_lower.includes(keyword))) {
            return types_1.TaskComplexity.Simple;
        }
        // Default to moderate complexity
        return types_1.TaskComplexity.Moderate;
    }
    /**
     * Check if an agent is available
     * @param agentName Agent name
     * @returns Whether the agent is available
     */
    isAgentAvailable(agentName) {
        // If we have an explicit availability setting, use that
        if (this.agentAvailability.has(agentName)) {
            return this.agentAvailability.get(agentName);
        }
        // Otherwise, check the agent's default availability
        const agent = this.agents.find(a => a.name === agentName);
        return agent ? agent.available : false;
    }
    /**
     * Set agent availability
     * @param agentName Agent name
     * @param available Whether the agent is available
     */
    setAgentAvailability(agentName, available) {
        this.agentAvailability.set(agentName, available);
        this.outputChannel.appendLine(`Set ${agentName} availability to ${available}`);
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