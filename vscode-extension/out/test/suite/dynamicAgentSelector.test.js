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
const assert = __importStar(require("assert"));
const agentSelector_1 = require("../../agents/agentSelector");
const types_1 = require("../../agents/types");
suite('Dynamic Agent Selection Test Suite', () => {
    let agentSelector;
    setup(() => {
        agentSelector = new agentSelector_1.AgentSelector();
        // Add test agents to the selector
        agentSelector.registerAgent({
            name: 'SimpleAgent',
            type: types_1.AgentType.Simple,
            capabilities: ['code'],
            modelSize: types_1.ModelSize.Small,
            maxComplexity: types_1.TaskComplexity.Simple,
            systemPrompt: 'You are a simple coding assistant that helps with basic tasks.',
            available: true
        });
        agentSelector.registerAgent({
            name: 'DevelopmentAgent',
            type: types_1.AgentType.Development,
            capabilities: ['code', 'context', 'reasoning'],
            modelSize: types_1.ModelSize.Large,
            maxComplexity: types_1.TaskComplexity.Complex,
            systemPrompt: 'You are a development assistant that helps with coding tasks.',
            available: true
        });
        agentSelector.registerAgent({
            name: 'ArchitectAgent',
            type: types_1.AgentType.Architecture,
            capabilities: ['code', 'context', 'reasoning', 'architecture'],
            modelSize: types_1.ModelSize.XLarge,
            maxComplexity: types_1.TaskComplexity.VeryComplex,
            systemPrompt: 'You are an architecture assistant that helps with system design and architecture.',
            available: true
        });
        agentSelector.registerAgent({
            name: 'DevOpsAgent',
            type: types_1.AgentType.DevOps,
            capabilities: ['code', 'tools', 'context'],
            modelSize: types_1.ModelSize.Large,
            maxComplexity: types_1.TaskComplexity.Complex,
            specializations: ['github', 'docker', 'ci-cd'],
            systemPrompt: 'You are a DevOps assistant that helps with CI/CD, deployment, and infrastructure.',
            available: true
        });
        agentSelector.registerAgent({
            name: 'MLAgent',
            type: types_1.AgentType.ML,
            capabilities: ['code', 'context', 'reasoning'],
            modelSize: types_1.ModelSize.XLarge,
            maxComplexity: types_1.TaskComplexity.VeryComplex,
            specializations: ['machine-learning', 'data-science', 'neural-networks'],
            systemPrompt: 'You are a machine learning assistant that helps with ML models and algorithms.',
            available: true
        });
        agentSelector.registerAgent({
            name: 'WebDevAgent',
            type: types_1.AgentType.WebDev,
            capabilities: ['code', 'context'],
            modelSize: types_1.ModelSize.Medium,
            maxComplexity: types_1.TaskComplexity.Complex,
            specializations: ['web-development', 'frontend', 'backend'],
            systemPrompt: 'You are a web development assistant that helps with frontend and backend tasks.',
            available: true
        });
    });
    test('Should select appropriate agent based on task complexity', async () => {
        // Test simple task
        const simpleTask = {
            description: 'Format this code snippet',
            complexity: types_1.TaskComplexity.Simple,
            requiresContext: false,
            requiresTools: false
        };
        const simpleAgent = await agentSelector.selectAgent(simpleTask);
        assert.strictEqual(simpleAgent.name, 'SimpleAgent', 'Should select SimpleAgent for simple tasks');
        // Test moderate task
        const moderateTask = {
            description: 'Explain how this algorithm works',
            complexity: types_1.TaskComplexity.Moderate,
            requiresContext: true,
            requiresTools: false
        };
        const moderateAgent = await agentSelector.selectAgent(moderateTask);
        assert.strictEqual(moderateAgent.name, 'DevelopmentAgent', 'Should select DevelopmentAgent for moderate tasks');
        // Test complex task
        const complexTask = {
            description: 'Refactor this code to use the factory pattern',
            complexity: types_1.TaskComplexity.Complex,
            requiresContext: true,
            requiresTools: false
        };
        const complexAgent = await agentSelector.selectAgent(complexTask);
        assert.strictEqual(complexAgent.name, 'ArchitectAgent', 'Should select ArchitectAgent for complex tasks');
    });
    test('Should select agent with tool capabilities when tools are required', async () => {
        const taskRequiringTools = {
            description: 'Create a pull request for these changes',
            complexity: types_1.TaskComplexity.Moderate,
            requiresContext: true,
            requiresTools: true,
            requiredTools: ['github.createPullRequest']
        };
        const agent = await agentSelector.selectAgent(taskRequiringTools);
        assert.ok(agent.capabilities.includes('tools'), 'Selected agent should have tools capability');
        assert.strictEqual(agent.name, 'DevOpsAgent', 'Should select DevOpsAgent for tasks requiring GitHub tools');
    });
    test('Should select agent with context capabilities when context is required', async () => {
        const taskRequiringContext = {
            description: 'Explain the relationship between these classes',
            complexity: types_1.TaskComplexity.Moderate,
            requiresContext: true,
            requiresTools: false,
            contextScope: 'deep'
        };
        const agent = await agentSelector.selectAgent(taskRequiringContext);
        assert.ok(agent.capabilities.includes('context'), 'Selected agent should have context capability');
        assert.strictEqual(agent.name, 'DevelopmentAgent', 'Should select DevelopmentAgent for tasks requiring deep context');
    });
    test('Should select specialized agent for domain-specific tasks', async () => {
        const mlTask = {
            description: 'Optimize this machine learning model',
            complexity: types_1.TaskComplexity.Complex,
            requiresContext: true,
            requiresTools: false,
            domain: 'machine-learning'
        };
        const agent = await agentSelector.selectAgent(mlTask);
        assert.strictEqual(agent.name, 'MLAgent', 'Should select MLAgent for machine learning tasks');
        const webTask = {
            description: 'Create a responsive layout for this component',
            complexity: types_1.TaskComplexity.Moderate,
            requiresContext: true,
            requiresTools: false,
            domain: 'web-development'
        };
        const webAgent = await agentSelector.selectAgent(webTask);
        assert.strictEqual(webAgent.name, 'WebDevAgent', 'Should select WebDevAgent for web development tasks');
    });
    test('Should analyze task description to determine complexity when not specified', async () => {
        const implicitComplexTask = {
            description: 'Refactor this monolithic application into a microservices architecture',
            requiresContext: true,
            requiresTools: false
        };
        const agent = await agentSelector.selectAgent(implicitComplexTask);
        assert.strictEqual(agent.name, 'ArchitectAgent', 'Should infer complexity from description and select appropriate agent');
    });
    test('Should handle agent unavailability by selecting fallback agent', async () => {
        // Mock unavailable agent
        agentSelector.setAgentAvailability('ArchitectAgent', false);
        const complexTask = {
            description: 'Design a scalable system architecture',
            complexity: types_1.TaskComplexity.Complex,
            requiresContext: true,
            requiresTools: false
        };
        const agent = await agentSelector.selectAgent(complexTask);
        assert.notStrictEqual(agent.name, 'ArchitectAgent', 'Should not select unavailable agent');
        assert.strictEqual(agent.name, 'DevelopmentAgent', 'Should select fallback agent when preferred agent is unavailable');
    });
});
//# sourceMappingURL=dynamicAgentSelector.test.js.map