import * as assert from 'assert';
import { AgentSelector } from '../agents/dynamicAgentSelector';
import { TaskComplexity } from '../agents/types';

describe('Dynamic Agent Selection', () => {
  let agentSelector: AgentSelector;

  beforeEach(() => {
    agentSelector = new AgentSelector();
  });

  it('should select appropriate agent based on task complexity', async () => {
    // Test simple task
    const simpleTask = {
      description: 'Format this code snippet',
      complexity: TaskComplexity.Simple,
      requiresContext: false,
      requiresTools: false
    };

    const simpleAgent = await agentSelector.selectAgent(simpleTask);
    assert.strictEqual(simpleAgent.name, 'SimpleAgent', 'Should select SimpleAgent for simple tasks');

    // Test moderate task
    const moderateTask = {
      description: 'Explain how this algorithm works',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: false
    };

    const moderateAgent = await agentSelector.selectAgent(moderateTask);
    assert.strictEqual(moderateAgent.name, 'DevelopmentAgent', 'Should select DevelopmentAgent for moderate tasks');

    // Test complex task
    const complexTask = {
      description: 'Refactor this code to use the factory pattern',
      complexity: TaskComplexity.Complex,
      requiresContext: true,
      requiresTools: false
    };

    const complexAgent = await agentSelector.selectAgent(complexTask);
    assert.strictEqual(complexAgent.name, 'ArchitectAgent', 'Should select ArchitectAgent for complex tasks');
  });

  it('should select agent with tool capabilities when tools are required', async () => {
    const taskRequiringTools = {
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

  it('should select agent with context capabilities when context is required', async () => {
    const taskRequiringContext = {
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

  it('should select specialized agent for domain-specific tasks', async () => {
    const mlTask = {
      description: 'Optimize this machine learning model',
      complexity: TaskComplexity.Complex,
      requiresContext: true,
      requiresTools: false,
      domain: 'machine-learning' as TaskDomain
    };

    const agent = await agentSelector.selectAgent(mlTask);
    assert.strictEqual(agent.name, 'MLAgent', 'Should select MLAgent for machine learning tasks');

    const webTask = {
      description: 'Create a responsive layout for this component',
      complexity: TaskComplexity.Moderate,
      requiresContext: true,
      requiresTools: false,
      domain: 'web-development' as TaskDomain
    };

    const webAgent = await agentSelector.selectAgent(webTask);
    assert.strictEqual(webAgent.name, 'WebDevAgent', 'Should select WebDevAgent for web development tasks');
  });

  it('should analyze task description to determine complexity when not specified', async () => {
    const implicitComplexTask = {
      description: 'Refactor this monolithic application into a microservices architecture',
      requiresContext: true,
      requiresTools: false
    };

    const agent = await agentSelector.selectAgent(implicitComplexTask);
    assert.strictEqual(agent.name, 'ArchitectAgent', 'Should infer complexity from description and select appropriate agent');
  });

  it('should handle agent unavailability by selecting fallback agent', async () => {
    // Mock unavailable agent
    agentSelector.setAgentAvailability('ArchitectAgent', false);

    const complexTask = {
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
