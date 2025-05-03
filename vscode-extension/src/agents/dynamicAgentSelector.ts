/**
 * Dynamic Agent Selector
 * 
 * Selects the most appropriate agent for a task based on its requirements,
 * complexity, and domain.
 */

import * as vscode from 'vscode';
import {
  Agent,
  AgentCapability,
  AgentType,
  ModelSize,
  Task,
  TaskComplexity,
  TaskDomain,
  ThinkingMode
} from './types';

/**
 * Agent Selector class for dynamic agent selection
 */
export class AgentSelector {
  private outputChannel: vscode.OutputChannel;
  private agents: Agent[];
  private agentAvailability: Map<string, boolean>;

  /**
   * Constructor
   */
  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Dynamic Agent Selector');
    this.agentAvailability = new Map<string, boolean>();
    
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
    
    this.outputChannel.appendLine('Dynamic Agent Selector initialized with ' + this.agents.length + ' agents');
  }

  /**
   * Select the most appropriate agent for a task
   * @param task The task to select an agent for
   * @returns The selected agent
   */
  public async selectAgent(task: Task): Promise<Agent> {
    try {
      this.outputChannel.appendLine(`Selecting agent for task: ${task.description}`);
      
      // Determine task complexity if not specified
      if (!task.complexity) {
        task.complexity = this.analyzeTaskComplexity(task.description);
        this.outputChannel.appendLine(`Inferred task complexity: ${task.complexity}`);
      }
      
      // Filter agents by availability
      const availableAgents = this.agents.filter(agent => 
        this.isAgentAvailable(agent.name)
      );
      
      if (availableAgents.length === 0) {
        throw new Error('No agents available');
      }
      
      // Filter agents by complexity
      const complexityMap: Record<TaskComplexity, number> = {
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
        const fallbackAgent = availableAgents.sort((a, b) => 
          complexityMap[b.maxComplexity] - complexityMap[a.maxComplexity]
        )[0];
        
        this.outputChannel.appendLine(`No agent capable of handling complexity ${task.complexity}, falling back to ${fallbackAgent.name}`);
        return fallbackAgent;
      }
      
      // Filter by required capabilities
      let filteredAgents = capableAgents;
      
      if (task.requiresContext) {
        filteredAgents = filteredAgents.filter(agent => 
          agent.capabilities.includes('context')
        );
      }
      
      if (task.requiresTools) {
        filteredAgents = filteredAgents.filter(agent => 
          agent.capabilities.includes('tools')
        );
      }
      
      if (filteredAgents.length === 0) {
        this.outputChannel.appendLine(`No agent with required capabilities, falling back to most capable agent`);
        return capableAgents[0];
      }
      
      // Filter by domain specialization if specified
      if (task.domain && task.domain !== 'general') {
        const domainAgents = filteredAgents.filter(agent => 
          agent.specializations?.some(spec => 
            spec.toLowerCase().includes(task.domain!.toLowerCase())
          )
        );
        
        if (domainAgents.length > 0) {
          filteredAgents = domainAgents;
          this.outputChannel.appendLine(`Found ${domainAgents.length} agents specialized in ${task.domain}`);
        }
      }
      
      // Filter by required tools if specified
      if (task.requiredTools && task.requiredTools.length > 0) {
        // For this example, we'll just check if the agent has tools capability
        // In a real implementation, we would check if the agent supports the specific tools
        const toolAgents = filteredAgents.filter(agent => 
          agent.capabilities.includes('tools')
        );
        
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
    } catch (error) {
      this.outputChannel.appendLine(`Error selecting agent: ${error.message}`);
      
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
  private analyzeTaskComplexity(description: string): TaskComplexity {
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
  public isAgentAvailable(agentName: string): boolean {
    // If we have an explicit availability setting, use that
    if (this.agentAvailability.has(agentName)) {
      return this.agentAvailability.get(agentName)!;
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
  public setAgentAvailability(agentName: string, available: boolean): void {
    this.agentAvailability.set(agentName, available);
    this.outputChannel.appendLine(`Set ${agentName} availability to ${available}`);
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
