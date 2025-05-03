"use strict";
/**
 * Standalone test for the dynamic agent selector
 *
 * This file contains a simplified version of the agent selector that can be tested
 * without the VS Code extension API.
 */
// Agent types
var AgentType;
(function (AgentType) {
    AgentType["Simple"] = "simple";
    AgentType["Development"] = "development";
    AgentType["Architecture"] = "architecture";
    AgentType["DevOps"] = "devops";
    AgentType["ML"] = "machine_learning";
    AgentType["WebDev"] = "web_development";
})(AgentType || (AgentType = {}));
// Model sizes
var ModelSize;
(function (ModelSize) {
    ModelSize["Small"] = "small";
    ModelSize["Medium"] = "medium";
    ModelSize["Large"] = "large";
    ModelSize["XLarge"] = "xlarge";
})(ModelSize || (ModelSize = {}));
// Task complexity levels
var TaskComplexity;
(function (TaskComplexity) {
    TaskComplexity["Simple"] = "simple";
    TaskComplexity["Moderate"] = "moderate";
    TaskComplexity["Complex"] = "complex";
    TaskComplexity["VeryComplex"] = "very_complex";
})(TaskComplexity || (TaskComplexity = {}));
/**
 * Agent Selector class for dynamic agent selection
 */
class AgentSelector {
    /**
     * Constructor
     */
    constructor() {
        this.agentAvailability = new Map();
        // Initialize available agents
        this.agents = [
            {
                name: 'SimpleAgent',
                type: AgentType.Simple,
                capabilities: ['code'],
                modelSize: ModelSize.Small,
                maxComplexity: TaskComplexity.Simple,
                systemPrompt: 'You are a simple coding assistant that helps with basic tasks.',
                available: true
            },
            {
                name: 'DevelopmentAgent',
                type: AgentType.Development,
                capabilities: ['code', 'context', 'reasoning'],
                modelSize: ModelSize.Large,
                maxComplexity: TaskComplexity.Complex,
                systemPrompt: 'You are a development assistant that helps with coding tasks.',
                available: true
            },
            {
                name: 'ArchitectAgent',
                type: AgentType.Architecture,
                capabilities: ['code', 'context', 'reasoning', 'architecture'],
                modelSize: ModelSize.XLarge,
                maxComplexity: TaskComplexity.VeryComplex,
                systemPrompt: 'You are an architecture assistant that helps with system design and architecture.',
                available: true
            },
            {
                name: 'DevOpsAgent',
                type: AgentType.DevOps,
                capabilities: ['code', 'tools', 'context'],
                modelSize: ModelSize.Large,
                maxComplexity: TaskComplexity.Complex,
                specializations: ['github', 'docker', 'ci-cd'],
                systemPrompt: 'You are a DevOps assistant that helps with CI/CD, deployment, and infrastructure.',
                available: true
            },
            {
                name: 'MLAgent',
                type: AgentType.ML,
                capabilities: ['code', 'context', 'reasoning'],
                modelSize: ModelSize.XLarge,
                maxComplexity: TaskComplexity.VeryComplex,
                specializations: ['machine-learning', 'data-science', 'neural-networks'],
                systemPrompt: 'You are a machine learning assistant that helps with ML models and algorithms.',
                available: true
            },
            {
                name: 'WebDevAgent',
                type: AgentType.WebDev,
                capabilities: ['code', 'context'],
                modelSize: ModelSize.Medium,
                maxComplexity: TaskComplexity.Complex,
                specializations: ['web-development', 'frontend', 'backend'],
                systemPrompt: 'You are a web development assistant that helps with frontend and backend tasks.',
                available: true
            }
        ];
        console.log('Dynamic Agent Selector initialized with ' + this.agents.length + ' agents');
    }
    /**
     * Select the most appropriate agent for a task
     * @param task The task to select an agent for
     * @returns The selected agent
     */
    async selectAgent(task) {
        try {
            console.log(`Selecting agent for task: ${task.description}`);
            // Determine task complexity if not specified
            if (!task.complexity) {
                task.complexity = this.analyzeTaskComplexity(task.description);
                console.log(`Inferred task complexity: ${task.complexity}`);
            }
            // Filter agents by availability
            const availableAgents = this.agents.filter(agent => this.isAgentAvailable(agent.name));
            if (availableAgents.length === 0) {
                throw new Error('No agents available');
            }
            // Filter agents by complexity
            const complexityMap = {
                [TaskComplexity.Simple]: 1,
                [TaskComplexity.Moderate]: 2,
                [TaskComplexity.Complex]: 3,
                [TaskComplexity.VeryComplex]: 4
            };
            const taskComplexityValue = complexityMap[task.complexity];
            const capableAgents = availableAgents.filter(agent => {
                const agentComplexityValue = complexityMap[agent.maxComplexity];
                return agentComplexityValue >= taskComplexityValue;
            });
            if (capableAgents.length === 0) {
                // Fallback to the agent with the highest complexity capability
                const fallbackAgent = availableAgents.sort((a, b) => complexityMap[b.maxComplexity] - complexityMap[a.maxComplexity])[0];
                console.log(`No agent capable of handling complexity ${task.complexity}, falling back to ${fallbackAgent.name}`);
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
                console.log(`No agent with required capabilities, falling back to most capable agent`);
                return capableAgents[0];
            }
            // Filter by domain specialization if specified
            if (task.domain && task.domain !== 'general') {
                const domainAgents = filteredAgents.filter(agent => agent.specializations?.some(spec => spec.toLowerCase().includes(task.domain.toLowerCase())));
                if (domainAgents.length > 0) {
                    filteredAgents = domainAgents;
                    console.log(`Found ${domainAgents.length} agents specialized in ${task.domain}`);
                }
            }
            // Filter by required tools if specified
            if (task.requiredTools && task.requiredTools.length > 0) {
                // For this example, we'll just check if the agent has tools capability
                // In a real implementation, we would check if the agent supports the specific tools
                const toolAgents = filteredAgents.filter(agent => agent.capabilities.includes('tools'));
                if (toolAgents.length > 0) {
                    filteredAgents = toolAgents;
                    console.log(`Found ${toolAgents.length} agents with required tool support`);
                }
            }
            // Select the best agent from the filtered list
            // For now, we'll just take the first one
            // In a real implementation, we might use a more sophisticated selection algorithm
            const selectedAgent = filteredAgents[0];
            console.log(`Selected agent: ${selectedAgent.name}`);
            return selectedAgent;
        }
        catch (error) {
            console.error(`Error selecting agent: ${error instanceof Error ? error.message : String(error)}`);
            // Return a default agent as fallback
            const defaultAgent = this.agents.find(a => a.name === 'DevelopmentAgent') || this.agents[0];
            console.log(`Falling back to default agent: ${defaultAgent.name}`);
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
            return TaskComplexity.Complex;
        }
        // Check for keywords indicating complex tasks
        const complexKeywords = [
            'implement', 'create', 'develop', 'build', 'design',
            'algorithm', 'feature', 'functionality', 'integration'
        ];
        if (complexKeywords.some(keyword => description_lower.includes(keyword))) {
            return TaskComplexity.Moderate;
        }
        // Check for keywords indicating simple tasks
        const simpleKeywords = [
            'fix', 'update', 'change', 'modify', 'add', 'remove',
            'format', 'rename', 'explain', 'help'
        ];
        if (simpleKeywords.some(keyword => description_lower.includes(keyword))) {
            return TaskComplexity.Simple;
        }
        // Default to moderate complexity
        return TaskComplexity.Moderate;
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
        console.log(`Set ${agentName} availability to ${available}`);
    }
}
// Run tests
async function runTests() {
    const agentSelector = new AgentSelector();
    // Test 1: Simple task
    const simpleTask = {
        description: 'Format this code snippet',
        complexity: TaskComplexity.Simple,
        requiresContext: false,
        requiresTools: false
    };
    const simpleAgent = await agentSelector.selectAgent(simpleTask);
    console.assert(simpleAgent.name === 'SimpleAgent', 'Should select SimpleAgent for simple tasks');
    // Test 2: Moderate task
    const moderateTask = {
        description: 'Explain how this algorithm works',
        complexity: TaskComplexity.Moderate,
        requiresContext: true,
        requiresTools: false
    };
    const moderateAgent = await agentSelector.selectAgent(moderateTask);
    console.assert(moderateAgent.name === 'DevelopmentAgent', 'Should select DevelopmentAgent for moderate tasks');
    // Test 3: Complex task
    const complexTask = {
        description: 'Refactor this code to use the factory pattern',
        complexity: TaskComplexity.Complex,
        requiresContext: true,
        requiresTools: false
    };
    const complexAgent = await agentSelector.selectAgent(complexTask);
    console.assert(complexAgent.name === 'ArchitectAgent', 'Should select ArchitectAgent for complex tasks');
    // Test 4: Task requiring tools
    const taskRequiringTools = {
        description: 'Create a pull request for these changes',
        complexity: TaskComplexity.Moderate,
        requiresContext: true,
        requiresTools: true,
        requiredTools: ['github.createPullRequest']
    };
    const toolAgent = await agentSelector.selectAgent(taskRequiringTools);
    console.assert(toolAgent.capabilities.includes('tools'), 'Selected agent should have tools capability');
    console.assert(toolAgent.name === 'DevOpsAgent', 'Should select DevOpsAgent for tasks requiring GitHub tools');
    // Test 5: Task requiring context
    const taskRequiringContext = {
        description: 'Explain the relationship between these classes',
        complexity: TaskComplexity.Moderate,
        requiresContext: true,
        requiresTools: false,
        contextScope: 'deep'
    };
    const contextAgent = await agentSelector.selectAgent(taskRequiringContext);
    console.assert(contextAgent.capabilities.includes('context'), 'Selected agent should have context capability');
    console.assert(contextAgent.name === 'DevelopmentAgent', 'Should select DevelopmentAgent for tasks requiring deep context');
    // Test 6: Domain-specific tasks
    const mlTask = {
        description: 'Optimize this machine learning model',
        complexity: TaskComplexity.Complex,
        requiresContext: true,
        requiresTools: false,
        domain: 'machine-learning'
    };
    const mlAgent = await agentSelector.selectAgent(mlTask);
    console.assert(mlAgent.name === 'MLAgent', 'Should select MLAgent for machine learning tasks');
    const webTask = {
        description: 'Create a responsive layout for this component',
        complexity: TaskComplexity.Moderate,
        requiresContext: true,
        requiresTools: false,
        domain: 'web-development'
    };
    const webAgent = await agentSelector.selectAgent(webTask);
    console.assert(webAgent.name === 'WebDevAgent', 'Should select WebDevAgent for web development tasks');
    // Test 7: Infer complexity from description
    const implicitComplexTask = {
        description: 'Refactor this monolithic application into a microservices architecture',
        requiresContext: true,
        requiresTools: false
    };
    const inferredComplexityAgent = await agentSelector.selectAgent(implicitComplexTask);
    console.assert(inferredComplexityAgent.name === 'ArchitectAgent', 'Should infer complexity from description and select appropriate agent');
    // Test 8: Handle agent unavailability
    agentSelector.setAgentAvailability('ArchitectAgent', false);
    const unavailableAgentTask = {
        description: 'Design a scalable system architecture',
        complexity: TaskComplexity.Complex,
        requiresContext: true,
        requiresTools: false
    };
    const fallbackAgent = await agentSelector.selectAgent(unavailableAgentTask);
    console.assert(fallbackAgent.name !== 'ArchitectAgent', 'Should not select unavailable agent');
    console.assert(fallbackAgent.name === 'DevelopmentAgent', 'Should select fallback agent when preferred agent is unavailable');
    console.log('All tests completed successfully!');
}
// Run the tests
runTests().catch(error => {
    console.error('Test failed:', error);
});
//# sourceMappingURL=agentSelectorTest.js.map