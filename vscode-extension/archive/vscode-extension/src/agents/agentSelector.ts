/**
 * Agent Selector
 * 
 * Chooses the most appropriate agent for each subtask based on expertise, complexity, and available resources.
 */

import * as vscode from 'vscode';
import { 
  AgentType, 
  ModelSize, 
  ThinkingMode, 
  TaskComplexity, 
  Subtask, 
  ResourceUsage 
} from './types';
import { getConfiguration } from '../configuration';

/**
 * Agent Selector class
 */
export class AgentSelector {
  private outputChannel: vscode.OutputChannel;
  private agentConfigs: Record<AgentType, Record<TaskComplexity, { modelSize: ModelSize, thinkingMode: ThinkingMode }>>;

  /**
   * Constructor
   */
  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Agent Selector');
    
    // Initialize agent configurations
    this.agentConfigs = {
      [AgentType.Coordinator]: {
        [TaskComplexity.High]: { modelSize: ModelSize.MoESmall, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.MoESmall, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.XXLarge, thinkingMode: ThinkingMode.Enabled }
      },
      [AgentType.Development]: {
        [TaskComplexity.High]: { modelSize: ModelSize.MoESmall, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.XXLarge, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.XLarge, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.Testing]: {
        [TaskComplexity.High]: { modelSize: ModelSize.XLarge, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.CICD]: {
        [TaskComplexity.High]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Disabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Small, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.GitHub]: {
        [TaskComplexity.High]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Disabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Small, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.Documentation]: {
        [TaskComplexity.High]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Small, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.Architecture]: {
        [TaskComplexity.High]: { modelSize: ModelSize.MoESmall, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.XXLarge, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.XLarge, thinkingMode: ThinkingMode.Enabled }
      },
      [AgentType.Security]: {
        [TaskComplexity.High]: { modelSize: ModelSize.XLarge, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Disabled }
      },
      [AgentType.Performance]: {
        [TaskComplexity.High]: { modelSize: ModelSize.XLarge, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Medium]: { modelSize: ModelSize.Large, thinkingMode: ThinkingMode.Enabled },
        [TaskComplexity.Low]: { modelSize: ModelSize.Medium, thinkingMode: ThinkingMode.Disabled }
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
  public async selectAgents(
    subtasks: Record<string, Subtask>, 
    availableResources: ResourceUsage
  ): Promise<Record<string, { type: AgentType, modelSize: ModelSize, thinkingMode: ThinkingMode }>> {
    try {
      this.outputChannel.appendLine(`Selecting agents for ${Object.keys(subtasks).length} subtasks`);
      
      // Get user configuration
      const config = getConfiguration();
      const preferredModel = config.get<string>('preferredModel', 'auto');
      const preferThinking = config.get<boolean>('preferThinkingMode', true);
      
      // Initialize agent assignments
      const agentAssignments: Record<string, { type: AgentType, modelSize: ModelSize, thinkingMode: ThinkingMode }> = {};
      
      // Sort subtasks by dependencies (fewer dependencies first)
      const sortedSubtasks = Object.values(subtasks).sort((a, b) => 
        a.dependencies.length - b.dependencies.length
      );
      
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
          agentConfig = { ...agentConfig, thinkingMode: ThinkingMode.Enabled };
        }
        
        // Check if we have enough resources for this agent
        if (this._checkResources(agentConfig, availableResources)) {
          agentAssignments[subtask.id] = {
            type: expertise,
            modelSize: agentConfig.modelSize,
            thinkingMode: agentConfig.thinkingMode
          };
        } else {
          // Fallback to a smaller model if resources are constrained
          const fallbackAgent = this._getFallbackAgent(expertise, availableResources);
          agentAssignments[subtask.id] = fallbackAgent;
        }
        
        this.outputChannel.appendLine(`Assigned ${agentAssignments[subtask.id].type} agent with ${agentAssignments[subtask.id].modelSize} model to subtask ${subtask.id}`);
      }
      
      return agentAssignments;
    } catch (error) {
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
  private _checkResources(
    agentConfig: { modelSize: ModelSize, thinkingMode: ThinkingMode }, 
    availableResources: ResourceUsage
  ): boolean {
    // Calculate resource requirements based on model size and thinking mode
    let memoryRequirement = 0;
    let cpuRequirement = 0;
    
    // Memory requirements
    switch (agentConfig.modelSize) {
      case ModelSize.MoELarge:
        memoryRequirement = 0.8;
        break;
      case ModelSize.MoESmall:
        memoryRequirement = 0.5;
        break;
      case ModelSize.XXLarge:
        memoryRequirement = 0.4;
        break;
      case ModelSize.XLarge:
        memoryRequirement = 0.3;
        break;
      case ModelSize.Large:
        memoryRequirement = 0.2;
        break;
      case ModelSize.Medium:
        memoryRequirement = 0.1;
        break;
      case ModelSize.Small:
        memoryRequirement = 0.05;
        break;
      case ModelSize.Tiny:
        memoryRequirement = 0.02;
        break;
    }
    
    // CPU requirements
    switch (agentConfig.modelSize) {
      case ModelSize.MoELarge:
        cpuRequirement = 0.8;
        break;
      case ModelSize.MoESmall:
        cpuRequirement = 0.5;
        break;
      case ModelSize.XXLarge:
        cpuRequirement = 0.4;
        break;
      case ModelSize.XLarge:
        cpuRequirement = 0.3;
        break;
      case ModelSize.Large:
        cpuRequirement = 0.2;
        break;
      case ModelSize.Medium:
        cpuRequirement = 0.1;
        break;
      case ModelSize.Small:
        cpuRequirement = 0.05;
        break;
      case ModelSize.Tiny:
        cpuRequirement = 0.02;
        break;
    }
    
    // Adjust for thinking mode
    if (agentConfig.thinkingMode === ThinkingMode.Enabled) {
      memoryRequirement *= 1.5;
      cpuRequirement *= 1.5;
    }
    
    // Check if we have enough resources
    return (
      availableResources.memory >= memoryRequirement &&
      availableResources.cpu >= cpuRequirement
    );
  }

  /**
   * Get a fallback agent with lower resource requirements
   * @param expertise The required expertise
   * @param availableResources Available system resources
   * @returns A fallback agent configuration
   */
  private _getFallbackAgent(
    expertise: AgentType, 
    availableResources: ResourceUsage
  ): { type: AgentType, modelSize: ModelSize, thinkingMode: ThinkingMode } {
    this.outputChannel.appendLine(`Finding fallback agent for ${expertise} due to resource constraints`);
    
    // Try progressively smaller models
    const modelSizes = [
      ModelSize.Medium,
      ModelSize.Small,
      ModelSize.Tiny
    ];
    
    // Try without thinking mode first
    for (const modelSize of modelSizes) {
      const config = { modelSize, thinkingMode: ThinkingMode.Disabled };
      if (this._checkResources(config, availableResources)) {
        return { type: expertise, ...config };
      }
    }
    
    // If all else fails, use the smallest possible configuration
    return {
      type: expertise,
      modelSize: ModelSize.Tiny,
      thinkingMode: ThinkingMode.Disabled
    };
  }

  /**
   * Convert user model preference to ModelSize
   * @param preferredModel The user's preferred model
   * @returns The corresponding ModelSize or undefined
   */
  private _getUserModelSize(preferredModel: string): ModelSize | undefined {
    switch (preferredModel.toLowerCase()) {
      case 'tiny':
        return ModelSize.Tiny;
      case 'small':
        return ModelSize.Small;
      case 'medium':
        return ModelSize.Medium;
      case 'large':
        return ModelSize.Large;
      case 'xlarge':
        return ModelSize.XLarge;
      case 'xxlarge':
        return ModelSize.XXLarge;
      case 'moesmall':
      case 'moe-small':
        return ModelSize.MoESmall;
      case 'moelarge':
      case 'moe-large':
        return ModelSize.MoELarge;
      default:
        return undefined;
    }
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
