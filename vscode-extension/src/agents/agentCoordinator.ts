/**
 * Agent Coordinator
 *
 * The central component that orchestrates the hierarchical agent system.
 * Responsible for task decomposition, agent selection, and result aggregation.
 */

import * as vscode from 'vscode';
import { QwenApiClient } from '../qwenApi';
import { AgentSelector } from './agentSelector';
import { ResourceManager } from './resourceManager';
import { ResultAggregator } from './resultAggregator';
import { TaskDecomposer } from './taskDecomposer';
import {
    AgentResult,
    AgentType
} from './types';

/**
 * Agent Coordinator class
 */
export class AgentCoordinator {
  private taskDecomposer: TaskDecomposer;
  private agentSelector: AgentSelector;
  private resourceManager: ResourceManager;
  private resultAggregator: ResultAggregator;
  private qwenApi: QwenApiClient;
  private outputChannel: vscode.OutputChannel;
  private config: any;

  /**
   * Constructor
   */
  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Agent Coordinator');
    this.qwenApi = new QwenApiClient();
    this.taskDecomposer = new TaskDecomposer(this.qwenApi);
    this.agentSelector = new AgentSelector();
    this.resourceManager = new ResourceManager();
    this.resultAggregator = new ResultAggregator(this.qwenApi);

    this.outputChannel.appendLine('Agent Coordinator initialized');
  }

  /**
   * Update the configuration
   * @param config New configuration
   */
  public updateConfig(config: any): void {
    this.config = config;
    this.outputChannel.appendLine('Configuration updated');
  }

  /**
   * Process a user request
   * @param userRequest The user's request
   * @returns The final response
   */
  public async processRequest(userRequest: string): Promise<string> {
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
      const results: Record<string, AgentResult> = {};
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
        } catch (error) {
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
    } catch (error) {
      this.outputChannel.appendLine(`Error processing request: ${error.message}`);
      throw error;
    }
  }

  /**
   * Instantiate an agent based on agent info
   * @param agentInfo The agent information
   * @returns The instantiated agent
   */
  private async instantiateAgent(agentInfo: any): Promise<any> {
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
        case AgentType.Development:
          const { DevelopmentAgent } = await import('./developmentAgent');
          return new DevelopmentAgent(agentId, this.qwenApi, modelSize, thinkingMode);

        case AgentType.Testing:
          const { TestingAgent } = await import('./testingAgent');
          return new TestingAgent(agentId, this.qwenApi, modelSize, thinkingMode);

        case AgentType.CICD:
          const { CICDAgent } = await import('./cicdAgent');
          return new CICDAgent(agentId, this.qwenApi, modelSize, thinkingMode);

        case AgentType.GitHub:
          const { GitHubAgent } = await import('./githubAgent');
          return new GitHubAgent(agentId, this.qwenApi, modelSize, thinkingMode);

        default:
          throw new Error(`Unsupported agent type: ${agentType}`);
      }
    } catch (error) {
      this.outputChannel.appendLine(`Error instantiating agent: ${error.message}`);
      await this.resourceManager.unregisterAgent(agentId);
      throw error;
    }
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
