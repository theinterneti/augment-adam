/**
 * Container Manager
 * 
 * Handles the lifecycle of containerized MCP tools.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { getConfiguration } from '../configuration';

/**
 * Container information
 */
interface ContainerInfo {
  id: string;
  name: string;
  image: string;
  url: string;
  status: 'running' | 'stopped' | 'error';
  startTime: number;
  error?: string;
}

/**
 * Container configuration
 */
interface ContainerConfig {
  image: string;
  command: string;
  args: string[];
  env?: Record<string, string>;
  ports?: { internal: number, external: number }[];
}

/**
 * Container Manager class
 */
export class ContainerManager {
  private outputChannel: vscode.OutputChannel;
  private containerRegistry: Record<string, ContainerConfig>;
  private activeContainers: Record<string, ContainerInfo>;
  private statusBarItem: vscode.StatusBarItem;
  private healthCheckInterval: NodeJS.Timeout | null;

  /**
   * Constructor
   */
  constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Container Manager');
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
    this.statusBarItem.text = '$(docker) MCP Tools';
    this.statusBarItem.tooltip = 'MCP Tools Status';
    this.statusBarItem.command = 'qwenCoder.showContainerStatus';
    
    this.containerRegistry = {
      'github': {
        image: 'qwen-mcp-github:latest',
        command: 'uvx',
        args: ['mcp-server-github'],
        ports: [{ internal: 8080, external: 0 }]
      },
      'docker': {
        image: 'qwen-mcp-docker:latest',
        command: 'uvx',
        args: ['mcp-server-docker'],
        ports: [{ internal: 8080, external: 0 }]
      },
      'testing': {
        image: 'qwen-mcp-testing:latest',
        command: 'uvx',
        args: ['mcp-server-testing'],
        ports: [{ internal: 8080, external: 0 }]
      },
      'ci_cd': {
        image: 'qwen-mcp-cicd:latest',
        command: 'uvx',
        args: ['mcp-server-cicd'],
        ports: [{ internal: 8080, external: 0 }]
      }
    };
    
    this.activeContainers = {};
    this.healthCheckInterval = null;
    
    this.outputChannel.appendLine('Container Manager initialized');
  }

  /**
   * Initialize the container manager
   */
  public async initialize(): Promise<void> {
    try {
      this.statusBarItem.show();
      
      // Check if Docker is available
      const dockerAvailable = await this._checkDockerAvailability();
      
      if (!dockerAvailable) {
        this.outputChannel.appendLine('Docker is not available. Container features will be disabled.');
        this.statusBarItem.text = '$(alert) Docker Not Available';
        this.statusBarItem.tooltip = 'Docker is not available. Container features are disabled.';
        return;
      }
      
      // Start health check interval
      this._startHealthCheck();
      
      // Auto-start containers if configured
      const config = getConfiguration();
      const autoStartContainers = config.get<boolean>('autoStartContainers', false);
      
      if (autoStartContainers) {
        this.outputChannel.appendLine('Auto-starting containers...');
        
        const containersToStart = config.get<string[]>('autoStartContainerList', ['github', 'docker']);
        
        for (const containerName of containersToStart) {
          try {
            await this.startContainer(containerName);
          } catch (error) {
            this.outputChannel.appendLine(`Error auto-starting container ${containerName}: ${error.message}`);
          }
        }
      }
    } catch (error) {
      this.outputChannel.appendLine(`Error initializing Container Manager: ${error.message}`);
      this.statusBarItem.text = '$(error) MCP Tools Error';
      this.statusBarItem.tooltip = `Error: ${error.message}`;
    }
  }

  /**
   * Start a containerized MCP tool
   * @param containerName The name of the container to start
   * @returns The URL for accessing the container
   */
  public async startContainer(containerName: string): Promise<string> {
    try {
      this.outputChannel.appendLine(`Starting container: ${containerName}`);
      
      // Check if container is already running
      if (this.activeContainers[containerName] && this.activeContainers[containerName].status === 'running') {
        this.outputChannel.appendLine(`Container ${containerName} is already running`);
        return this.activeContainers[containerName].url;
      }
      
      // Get container configuration
      const containerConfig = this.containerRegistry[containerName];
      if (!containerConfig) {
        throw new Error(`Unknown container: ${containerName}`);
      }
      
      // Check if Docker is available
      const dockerAvailable = await this._checkDockerAvailability();
      if (!dockerAvailable) {
        throw new Error('Docker is not available');
      }
      
      // Pull the image if needed
      await this._ensureImageAvailable(containerConfig.image);
      
      // Start the container
      const containerId = await this._startContainer(containerName, containerConfig);
      
      // Get container URL
      const url = await this._getContainerUrl(containerId, containerConfig);
      
      // Update active containers
      this.activeContainers[containerName] = {
        id: containerId,
        name: containerName,
        image: containerConfig.image,
        url,
        status: 'running',
        startTime: Date.now()
      };
      
      // Update status bar
      this._updateStatusBar();
      
      this.outputChannel.appendLine(`Container ${containerName} started successfully with URL: ${url}`);
      
      return url;
    } catch (error) {
      this.outputChannel.appendLine(`Error starting container ${containerName}: ${error.message}`);
      
      // Update active containers with error status
      this.activeContainers[containerName] = {
        id: '',
        name: containerName,
        image: this.containerRegistry[containerName]?.image || '',
        url: '',
        status: 'error',
        startTime: Date.now(),
        error: error.message
      };
      
      // Update status bar
      this._updateStatusBar();
      
      throw error;
    }
  }

  /**
   * Stop a containerized MCP tool
   * @param containerName The name of the container to stop
   */
  public async stopContainer(containerName: string): Promise<void> {
    try {
      this.outputChannel.appendLine(`Stopping container: ${containerName}`);
      
      // Check if container is running
      if (!this.activeContainers[containerName] || this.activeContainers[containerName].status !== 'running') {
        this.outputChannel.appendLine(`Container ${containerName} is not running`);
        return;
      }
      
      const containerId = this.activeContainers[containerName].id;
      
      // Stop and remove the container
      await this._stopContainer(containerId);
      
      // Update active containers
      this.activeContainers[containerName] = {
        ...this.activeContainers[containerName],
        status: 'stopped'
      };
      
      // Update status bar
      this._updateStatusBar();
      
      this.outputChannel.appendLine(`Container ${containerName} stopped successfully`);
    } catch (error) {
      this.outputChannel.appendLine(`Error stopping container ${containerName}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get the URL for a running container
   * @param containerName The name of the container
   * @returns The URL for accessing the container
   */
  public getContainerUrl(containerName: string): string {
    if (!this.activeContainers[containerName] || this.activeContainers[containerName].status !== 'running') {
      throw new Error(`Container ${containerName} is not running`);
    }
    
    return this.activeContainers[containerName].url;
  }

  /**
   * Get the status of all containers
   * @returns The status of all containers
   */
  public getContainerStatus(): Record<string, ContainerInfo> {
    return { ...this.activeContainers };
  }

  /**
   * Check if Docker is available
   * @returns Whether Docker is available
   */
  private async _checkDockerAvailability(): Promise<boolean> {
    try {
      // This is a placeholder for Docker availability check
      // In a real implementation, we would use the Docker SDK to check if Docker is running
      
      // For now, we'll assume Docker is available
      return true;
    } catch (error) {
      this.outputChannel.appendLine(`Error checking Docker availability: ${error.message}`);
      return false;
    }
  }

  /**
   * Ensure the Docker image is available
   * @param imageName The name of the image
   */
  private async _ensureImageAvailable(imageName: string): Promise<void> {
    try {
      this.outputChannel.appendLine(`Ensuring image is available: ${imageName}`);
      
      // This is a placeholder for image availability check
      // In a real implementation, we would use the Docker SDK to check if the image exists locally
      // and pull it if it doesn't
      
      // For now, we'll assume the image is available
    } catch (error) {
      this.outputChannel.appendLine(`Error ensuring image availability: ${error.message}`);
      throw error;
    }
  }

  /**
   * Start a container
   * @param containerName The name of the container
   * @param config The container configuration
   * @returns The container ID
   */
  private async _startContainer(containerName: string, config: ContainerConfig): Promise<string> {
    try {
      this.outputChannel.appendLine(`Starting container with image: ${config.image}`);
      
      // This is a placeholder for container start
      // In a real implementation, we would use the Docker SDK to start the container
      
      // For now, we'll return a fake container ID
      return `fake-container-id-${containerName}-${Date.now()}`;
    } catch (error) {
      this.outputChannel.appendLine(`Error starting container: ${error.message}`);
      throw error;
    }
  }

  /**
   * Stop a container
   * @param containerId The ID of the container
   */
  private async _stopContainer(containerId: string): Promise<void> {
    try {
      this.outputChannel.appendLine(`Stopping container: ${containerId}`);
      
      // This is a placeholder for container stop
      // In a real implementation, we would use the Docker SDK to stop and remove the container
    } catch (error) {
      this.outputChannel.appendLine(`Error stopping container: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get the URL for a container
   * @param containerId The ID of the container
   * @param config The container configuration
   * @returns The URL for accessing the container
   */
  private async _getContainerUrl(containerId: string, config: ContainerConfig): Promise<string> {
    try {
      // This is a placeholder for getting the container URL
      // In a real implementation, we would use the Docker SDK to get the port mapping
      
      // For now, we'll return a fake URL
      return `http://localhost:${8080 + Math.floor(Math.random() * 1000)}`;
    } catch (error) {
      this.outputChannel.appendLine(`Error getting container URL: ${error.message}`);
      throw error;
    }
  }

  /**
   * Start health check interval
   */
  private _startHealthCheck(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    
    this.healthCheckInterval = setInterval(async () => {
      try {
        for (const containerName in this.activeContainers) {
          const container = this.activeContainers[containerName];
          
          if (container.status === 'running') {
            // Check container health
            const isHealthy = await this._checkContainerHealth(container);
            
            if (!isHealthy) {
              this.outputChannel.appendLine(`Container ${containerName} is not healthy, attempting to restart`);
              
              // Attempt to restart the container
              try {
                await this.stopContainer(containerName);
                await this.startContainer(containerName);
                
                this.outputChannel.appendLine(`Container ${containerName} restarted successfully`);
              } catch (error) {
                this.outputChannel.appendLine(`Error restarting container ${containerName}: ${error.message}`);
              }
            }
          }
        }
        
        // Update status bar
        this._updateStatusBar();
      } catch (error) {
        this.outputChannel.appendLine(`Error in health check: ${error.message}`);
      }
    }, 60000); // Check every minute
  }

  /**
   * Check container health
   * @param container The container to check
   * @returns Whether the container is healthy
   */
  private async _checkContainerHealth(container: ContainerInfo): Promise<boolean> {
    try {
      // This is a placeholder for container health check
      // In a real implementation, we would use the Docker SDK to check the container health
      
      // For now, we'll assume the container is healthy
      return true;
    } catch (error) {
      this.outputChannel.appendLine(`Error checking container health: ${error.message}`);
      return false;
    }
  }

  /**
   * Update status bar
   */
  private _updateStatusBar(): void {
    const runningContainers = Object.values(this.activeContainers).filter(c => c.status === 'running').length;
    const totalContainers = Object.keys(this.activeContainers).length;
    
    if (runningContainers === 0) {
      this.statusBarItem.text = '$(docker) MCP Tools: None Running';
    } else {
      this.statusBarItem.text = `$(docker) MCP Tools: ${runningContainers}/${totalContainers} Running`;
    }
    
    // Update tooltip with container details
    let tooltip = 'MCP Tools Status:\n\n';
    
    for (const containerName in this.activeContainers) {
      const container = this.activeContainers[containerName];
      tooltip += `${containerName}: ${container.status}`;
      
      if (container.status === 'running') {
        tooltip += ` (${container.url})`;
      } else if (container.status === 'error') {
        tooltip += ` (${container.error})`;
      }
      
      tooltip += '\n';
    }
    
    this.statusBarItem.tooltip = tooltip;
  }

  /**
   * Stop all containers
   */
  public async stopAllContainers(): Promise<void> {
    try {
      this.outputChannel.appendLine('Stopping all containers');
      
      for (const containerName in this.activeContainers) {
        if (this.activeContainers[containerName].status === 'running') {
          try {
            await this.stopContainer(containerName);
          } catch (error) {
            this.outputChannel.appendLine(`Error stopping container ${containerName}: ${error.message}`);
          }
        }
      }
      
      this.outputChannel.appendLine('All containers stopped');
    } catch (error) {
      this.outputChannel.appendLine(`Error stopping all containers: ${error.message}`);
      throw error;
    }
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
    
    this.stopAllContainers().catch(error => {
      this.outputChannel.appendLine(`Error stopping containers during disposal: ${error.message}`);
    });
    
    this.statusBarItem.dispose();
    this.outputChannel.dispose();
  }
}
