import * as assert from 'assert';
import { AgentSelector } from '../../agents/agentSelector';
import {
    Agent,
    AgentCapability,
    AgentType,
    ContextScope,
    ModelSize,
    Task,
    TaskComplexity,
    TaskDomain,
    ThinkingMode
} from '../../agents/types';

suite('Dynamic Agent Selection Test Suite', () => {
  let agentSelector: AgentSelector;

  setup(() => {
    agentSelector = new AgentSelector();
    
    // Add test agents to the selector
    agentSelector.registerAgent({
      name: 'SimpleAgent',
      type: AgentType.Simple,
      capabilities: ['code'],
      modelSize: ModelSize.Small,
      maxComplexity: TaskComplexity.Simple,
      systemPrompt: 'You are a simple coding assistant that helps with basic tasks.',
      available: true
    });
    
    agentSelector.registerAgent({
      name: 'DevelopmentAgent',
      type: AgentType.Development,
      capabilities: ['code', 'context', 'reasoning'],
      modelSize: ModelSize.Large,
      maxComplexity: TaskComplexity.Complex,
      systemPrompt: 'You are a development assistant that helps with coding tasks.',
      available: true
    });
    
    agentSelector.registerAgent({
      name: 'ArchitectAgent',
      type: AgentType.Architecture,
      capabilities: ['code', 'context', 'reasoning', 'architecture'],
      modelSize: ModelSize.XLarge,
      maxComplexity: TaskComplexity.VeryComplex,
      systemPrompt: 'You are an architecture assistant that helps with system design and architecture.',
      available: true
    });
    
    agentSelector.registerAgent({
      name: 'DevOpsAgent',
      type: AgentType.DevOps,
      capabilities: ['code', 'tools', 'context'],
      modelSize: ModelSize.Large,
      maxComplexity: TaskComplexity.Complex,
      specializations: ['github', 'docker', 'ci-cd'],
      systemPrompt: 'You are a DevOps assistant that helps with CI/CD, deployment, and infrastructure.',
      available: true
    });
    
    agentSelector.registerAgent({
      name: 'MLAgent',
      type: AgentType.ML,
      capabilities: ['code', 'context', 'reasoning'],
      modelSize: ModelSize.XLarge,
      maxComplexity: TaskComplexity.VeryComplex,
      specializations: ['machine-learning', 'data-science', 'neural-networks'],
      systemPrompt: 'You are a machine learning assistant that helps with ML models and algorithms.',
      available: true
    });
    
    agentSelector.registerAgent({
      name: 'WebDevAgent',
      type: AgentType.WebDev,
      capabilities: ['code', 'context'],
      modelSize: ModelSize.Medium,
      maxComplexity: TaskComplexity.Complex,
      specializations: ['web-development', 'frontend', 'backend'],
      systemPrompt: 'You are a web development assistant that helps with frontend and backend tasks.',
      available: true
    });
  });

  test('Should select appropriate agent based on task complexity', async () => {
    // Test simple task
    const simpleTask: Task = {
      description: 'Format this code snippet',
      complexity: TaskComplexity.Simple,
      requiresContext: false,
      requiresTools: false
    };
    
    const simpleAgent = await agentSelector.selectAgent(simpleTask);
    assert.strictEqual(simpleAgent.name, 'SimpleAgent', 'Should select SimpleAgent for simple tasks');
    
    // Test moderate task
    const moderateTask: Task = {
      description: 'Explain how this algorithm works',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: false
    };
    
    const moderateAgent = await agentSelector.selectAgent(moderateTask);
    assert.strictEqual(moderateAgent.name, 'DevelopmentAgent', 'Should select DevelopmentAgent for moderate tasks');
    
    // Test complex task
    const complexTask: Task = {
      description: 'Refactor this code to use the factory pattern',
      complexity: TaskComplexity.Complex,
      requiresContext: true,
      requiresTools: false
    };
    
    const complexAgent = await agentSelector.selectAgent(complexTask);
    assert.strictEqual(complexAgent.name, 'ArchitectAgent', 'Should select ArchitectAgent for complex tasks');
  });

  test('Should select agent with tool capabilities when tools are required', async () => {
    const taskRequiringTools: Task = {
      description: 'Create a pull request for these changes',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: true,
      requiredTools: ['github.createPullRequest']
    };
    
    const agent = await agentSelector.selectAgent(taskRequiringTools);
    assert.ok(agent.capabilities.includes('tools'), 'Selected agent should have tools capability');
    assert.strictEqual(agent.name, 'DevOpsAgent', 'Should select DevOpsAgent for tasks requiring GitHub tools');
  });

  test('Should select agent with context capabilities when context is required', async () => {
    const taskRequiringContext: Task = {
      description: 'Explain the relationship between these classes',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: false,
      contextScope: 'deep' as ContextScope
    };
    
    const agent = await agentSelector.selectAgent(taskRequiringContext);
    assert.ok(agent.capabilities.includes('context'), 'Selected agent should have context capability');
    assert.strictEqual(agent.name, 'DevelopmentAgent', 'Should select DevelopmentAgent for tasks requiring deep context');
  });

  test('Should select specialized agent for domain-specific tasks', async () => {
    const mlTask: Task = {
      description: 'Optimize this machine learning model',
      complexity: TaskComplexity.Complex,
      requiresContext: true,
      requiresTools: false,
      domain: 'machine-learning' as TaskDomain
    };
    
    const agent = await agentSelector.selectAgent(mlTask);
    assert.strictEqual(agent.name, 'MLAgent', 'Should select MLAgent for machine learning tasks');
    
    const webTask: Task = {
      description: 'Create a responsive layout for this component',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: false,
      domain: 'web-development' as TaskDomain
    };
    
    const webAgent = await agentSelector.selectAgent(webTask);
    assert.strictEqual(webAgent.name, 'WebDevAgent', 'Should select WebDevAgent for web development tasks');
  });

  test('Should analyze task description to determine complexity when not specified', async () => {
    const implicitComplexTask: Task = {
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
    
    const complexTask: Task = {
      description: 'Design a scalable system architecture',
      complexity: TaskComplexity.Complex,
      requiresContext: true,
      requiresTools: false
    };
    
    const agent = await agentSelector.selectAgent(complexTask);
    assert.notStrictEqual(agent.name, 'ArchitectAgent', 'Should not select unavailable agent');
    assert.strictEqual(agent.name, 'DevelopmentAgent', 'Should select fallback agent when preferred agent is unavailable');
  });
});
