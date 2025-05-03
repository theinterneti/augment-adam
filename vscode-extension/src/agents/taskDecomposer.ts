/**
 * Task Decomposer
 * 
 * Breaks down complex user requests into smaller, manageable subtasks.
 * Uses Qwen's thinking mode to perform detailed analysis.
 */

import * as vscode from 'vscode';
import { v4 as uuidv4 } from 'uuid';
import { AgentType, TaskComplexity, Subtask, ResourceUsage } from './types';
import { QwenApiClient } from '../qwenApi';

/**
 * Task Decomposer class
 */
export class TaskDecomposer {
  private qwenApi: QwenApiClient;
  private outputChannel: vscode.OutputChannel;

  /**
   * Constructor
   * @param qwenApi The Qwen API client
   */
  constructor(qwenApi: QwenApiClient) {
    this.qwenApi = qwenApi;
    this.outputChannel = vscode.window.createOutputChannel('Task Decomposer');
  }

  /**
   * Decompose a user request into subtasks
   * @param userRequest The user's request
   * @param availableResources Available system resources
   * @returns A record of subtasks
   */
  public async decompose(userRequest: string, availableResources: ResourceUsage): Promise<Record<string, Subtask>> {
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
    } catch (error) {
      this.outputChannel.appendLine(`Error decomposing task: ${error.message}`);
      throw error;
    }
  }

  /**
   * Parse the LLM response to extract subtasks
   * @param response The LLM response
   * @returns A record of subtasks
   */
  private _parseSubtasks(response: string): Record<string, Subtask> {
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
      const subtasks: Record<string, Subtask> = {};
      for (const subtask of parsed.subtasks) {
        // Ensure the subtask has a valid ID
        const id = subtask.id || uuidv4();
        
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
    } catch (error) {
      this.outputChannel.appendLine(`Error parsing subtasks: ${error.message}`);
      
      // Fallback: create a single subtask
      const id = uuidv4();
      return {
        [id]: {
          id,
          description: 'Execute the requested task',
          expertise: AgentType.Development,
          complexity: TaskComplexity.Medium,
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
  private _validateExpertise(expertise: string): AgentType {
    if (!expertise || typeof expertise !== 'string') {
      return AgentType.Development;
    }
    
    const normalized = expertise.toLowerCase();
    
    switch (normalized) {
      case 'development':
        return AgentType.Development;
      case 'testing':
        return AgentType.Testing;
      case 'ci_cd':
      case 'cicd':
        return AgentType.CICD;
      case 'github':
        return AgentType.GitHub;
      case 'documentation':
        return AgentType.Documentation;
      case 'architecture':
        return AgentType.Architecture;
      case 'security':
        return AgentType.Security;
      case 'performance':
        return AgentType.Performance;
      default:
        return AgentType.Development;
    }
  }

  /**
   * Validate the complexity field
   * @param complexity The complexity string
   * @returns A valid TaskComplexity
   */
  private _validateComplexity(complexity: string): TaskComplexity {
    if (!complexity || typeof complexity !== 'string') {
      return TaskComplexity.Medium;
    }
    
    const normalized = complexity.toLowerCase();
    
    switch (normalized) {
      case 'low':
        return TaskComplexity.Low;
      case 'medium':
        return TaskComplexity.Medium;
      case 'high':
        return TaskComplexity.High;
      default:
        return TaskComplexity.Medium;
    }
  }

  /**
   * Validate subtasks and ensure they're within resource constraints
   * @param subtasks The subtasks to validate
   * @param availableResources Available system resources
   * @returns Validated subtasks
   */
  private _validateSubtasks(subtasks: Record<string, Subtask>, availableResources: ResourceUsage): Record<string, Subtask> {
    // Check if we have enough resources for all subtasks
    const totalSubtasks = Object.keys(subtasks).length;
    
    if (totalSubtasks > 10 && availableResources.memory < 0.5) {
      // If resources are limited, reduce the number of subtasks
      this.outputChannel.appendLine('Limited resources detected, reducing number of subtasks');
      
      // Sort subtasks by dependencies (fewer dependencies first)
      const sortedSubtasks = Object.values(subtasks).sort((a, b) => 
        a.dependencies.length - b.dependencies.length
      );
      
      // Keep only the first 5-10 subtasks
      const maxSubtasks = Math.max(5, Math.min(10, Math.floor(availableResources.memory * 20)));
      const reducedSubtasks: Record<string, Subtask> = {};
      
      for (let i = 0; i < Math.min(maxSubtasks, sortedSubtasks.length); i++) {
        const subtask = sortedSubtasks[i];
        reducedSubtasks[subtask.id] = subtask;
      }
      
      return reducedSubtasks;
    }
    
    // Check for circular dependencies
    const visited = new Set<string>();
    const visiting = new Set<string>();
    
    const hasCycle = (id: string): boolean => {
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
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
