/**
 * Resource Manager
 * 
 * Monitors system resources and controls agent instantiation.
 */

import * as vscode from 'vscode';
import * as os from 'os';
import { v4 as uuidv4 } from 'uuid';
import { AgentType, ModelSize, ThinkingMode, ResourceUsage } from './types';

/**
 * Resource Manager class
 */
export class ResourceManager {
  private outputChannel: vscode.OutputChannel;
  private activeAgents: Record<string, {
    type: AgentType;
    modelSize: ModelSize;
    thinkingMode: ThinkingMode;
    startTime: number;
  }>;
  private maxMemoryUsage: number;
  private maxCpuUsage: number;
  private resourceCheckInterval: NodeJS.Timeout | null;

  /**
   * Constructor
   * @param maxMemoryUsage Maximum memory usage (0-1)
   * @param maxCpuUsage Maximum CPU usage (0-1)
   */
  constructor(maxMemoryUsage = 0.8, maxCpuUsage = 0.8) {
    this.outputChannel = vscode.window.createOutputChannel('Resource Manager');
    this.activeAgents = {};
    this.maxMemoryUsage = maxMemoryUsage;
    this.maxCpuUsage = maxCpuUsage;
    this.resourceCheckInterval = null;
    
    // Start resource monitoring
    this._startResourceMonitoring();
    
    this.outputChannel.appendLine('Resource Manager initialized');
  }

  /**
   * Get available system resources
   * @returns Available resources
   */
  public async getAvailableResources(): Promise<ResourceUsage> {
    try {
      // Get current system resource usage
      const currentMemoryUsage = this._getMemoryUsage();
      const currentCpuUsage = await this._getCpuUsage();
      
      // Calculate available resources
      const availableMemory = Math.max(0, this.maxMemoryUsage - currentMemoryUsage);
      const availableCpu = Math.max(0, this.maxCpuUsage - currentCpuUsage);
      
      const resources = {
        memory: availableMemory,
        cpu: availableCpu,
        activeAgents: Object.keys(this.activeAgents).length
      };
      
      this.outputChannel.appendLine(`Available resources: memory=${availableMemory.toFixed(2)}, cpu=${availableCpu.toFixed(2)}, activeAgents=${resources.activeAgents}`);
      
      return resources;
    } catch (error) {
      this.outputChannel.appendLine(`Error getting available resources: ${error.message}`);
      
      // Return conservative estimates in case of error
      return {
        memory: 0.2,
        cpu: 0.2,
        activeAgents: Object.keys(this.activeAgents).length
      };
    }
  }

  /**
   * Register a new agent with its resource requirements
   * @param type Agent type
   * @param requirements Resource requirements
   * @returns Agent ID
   */
  public async registerAgent(
    type: AgentType, 
    requirements: { modelSize: ModelSize, thinkingMode: ThinkingMode }
  ): Promise<string> {
    const agentId = uuidv4();
    
    this.activeAgents[agentId] = {
      type,
      modelSize: requirements.modelSize,
      thinkingMode: requirements.thinkingMode,
      startTime: Date.now()
    };
    
    this.outputChannel.appendLine(`Registered agent ${agentId} of type ${type} with model ${requirements.modelSize}`);
    
    return agentId;
  }

  /**
   * Unregister an agent when it's no longer needed
   * @param agentId Agent ID
   */
  public async unregisterAgent(agentId: string): Promise<void> {
    if (agentId in this.activeAgents) {
      const agent = this.activeAgents[agentId];
      const duration = (Date.now() - agent.startTime) / 1000;
      
      this.outputChannel.appendLine(`Unregistered agent ${agentId} of type ${agent.type} after ${duration.toFixed(2)}s`);
      
      delete this.activeAgents[agentId];
    }
  }

  /**
   * Get current memory usage
   * @returns Memory usage (0-1)
   */
  private _getMemoryUsage(): number {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    
    return usedMem / totalMem;
  }

  /**
   * Get current CPU usage
   * @returns CPU usage (0-1)
   */
  private async _getCpuUsage(): Promise<number> {
    return new Promise<number>((resolve) => {
      const startMeasure = os.cpus().map(cpu => cpu.times);
      
      // Measure CPU usage over a short interval
      setTimeout(() => {
        const endMeasure = os.cpus().map(cpu => cpu.times);
        const cpuUsage = endMeasure.map((end, i) => {
          const start = startMeasure[i];
          const idle = end.idle - start.idle;
          const total = (end.user - start.user) + 
                        (end.nice - start.nice) + 
                        (end.sys - start.sys) + 
                        (end.irq - start.irq) + 
                        idle;
          
          return 1 - (idle / total);
        });
        
        // Average CPU usage across all cores
        const avgCpuUsage = cpuUsage.reduce((sum, usage) => sum + usage, 0) / cpuUsage.length;
        
        resolve(avgCpuUsage);
      }, 100);
    });
  }

  /**
   * Start resource monitoring
   */
  private _startResourceMonitoring(): void {
    if (this.resourceCheckInterval) {
      clearInterval(this.resourceCheckInterval);
    }
    
    this.resourceCheckInterval = setInterval(async () => {
      try {
        const resources = await this.getAvailableResources();
        
        // Log resource usage periodically
        if (Object.keys(this.activeAgents).length > 0) {
          this.outputChannel.appendLine(`Resource check: memory=${(1 - resources.memory).toFixed(2)}, cpu=${(1 - resources.cpu).toFixed(2)}, activeAgents=${resources.activeAgents}`);
        }
        
        // Check for resource constraints
        if (resources.memory < 0.1 || resources.cpu < 0.1) {
          this.outputChannel.appendLine('WARNING: System resources are critically low');
          
          // Notify the user
          vscode.window.showWarningMessage('System resources are running low. Some agent operations may be delayed.');
        }
      } catch (error) {
        this.outputChannel.appendLine(`Error monitoring resources: ${error.message}`);
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    if (this.resourceCheckInterval) {
      clearInterval(this.resourceCheckInterval);
      this.resourceCheckInterval = null;
    }
    
    this.outputChannel.dispose();
  }
}
