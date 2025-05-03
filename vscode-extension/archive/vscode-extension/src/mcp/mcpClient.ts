/**
 * MCP Client
 * 
 * Client for interacting with Model-Control-Protocol (MCP) tools.
 */

import * as vscode from 'vscode';
import axios from 'axios';
import { ContainerManager } from '../containers/containerManager';

/**
 * MCP function schema
 */
interface MCPFunctionSchema {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, {
      type: string;
      description: string;
      enum?: string[];
    }>;
    required: string[];
  };
}

/**
 * MCP tool schema
 */
interface MCPToolSchema {
  name: string;
  description: string;
  functions: MCPFunctionSchema[];
}

/**
 * MCP function call result
 */
interface MCPFunctionCallResult {
  status: 'success' | 'error';
  result?: any;
  error?: string;
}

/**
 * MCP Client class
 */
export class MCPClient {
  private containerManager: ContainerManager;
  private outputChannel: vscode.OutputChannel;
  private toolSchemas: Record<string, MCPToolSchema>;

  /**
   * Constructor
   * @param containerManager The container manager
   */
  constructor(containerManager: ContainerManager) {
    this.containerManager = containerManager;
    this.outputChannel = vscode.window.createOutputChannel('MCP Client');
    this.toolSchemas = {};
    
    this.outputChannel.appendLine('MCP Client initialized');
  }

  /**
   * Initialize the MCP client
   */
  public async initialize(): Promise<void> {
    try {
      this.outputChannel.appendLine('Initializing MCP client');
      
      // Get active containers
      const containerStatus = this.containerManager.getContainerStatus();
      
      // Fetch schemas for running containers
      for (const containerName in containerStatus) {
        const container = containerStatus[containerName];
        
        if (container.status === 'running') {
          try {
            await this.fetchToolSchema(containerName);
          } catch (error) {
            this.outputChannel.appendLine(`Error fetching schema for ${containerName}: ${error.message}`);
          }
        }
      }
      
      this.outputChannel.appendLine('MCP client initialized');
    } catch (error) {
      this.outputChannel.appendLine(`Error initializing MCP client: ${error.message}`);
      throw error;
    }
  }

  /**
   * Fetch the schema for a tool
   * @param toolName The name of the tool
   * @returns The tool schema
   */
  public async fetchToolSchema(toolName: string): Promise<MCPToolSchema> {
    try {
      this.outputChannel.appendLine(`Fetching schema for tool: ${toolName}`);
      
      // Get container URL
      const url = this.containerManager.getContainerUrl(toolName);
      
      // Fetch schema
      const response = await axios.get(`${url}/schema`);
      const schema = response.data;
      
      // Validate schema
      if (!schema.name || !schema.functions || !Array.isArray(schema.functions)) {
        throw new Error(`Invalid schema for tool ${toolName}`);
      }
      
      // Store schema
      this.toolSchemas[toolName] = schema;
      
      this.outputChannel.appendLine(`Schema fetched for tool ${toolName}: ${schema.functions.length} functions available`);
      
      return schema;
    } catch (error) {
      this.outputChannel.appendLine(`Error fetching schema for tool ${toolName}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get the schema for a tool
   * @param toolName The name of the tool
   * @returns The tool schema
   */
  public getToolSchema(toolName: string): MCPToolSchema | undefined {
    return this.toolSchemas[toolName];
  }

  /**
   * Get all available tools
   * @returns The available tools
   */
  public getAvailableTools(): string[] {
    return Object.keys(this.toolSchemas);
  }

  /**
   * Call a function on a tool
   * @param toolName The name of the tool
   * @param functionName The name of the function
   * @param parameters The function parameters
   * @returns The function call result
   */
  public async callFunction(
    toolName: string,
    functionName: string,
    parameters: Record<string, any>
  ): Promise<MCPFunctionCallResult> {
    try {
      this.outputChannel.appendLine(`Calling function ${functionName} on tool ${toolName}`);
      
      // Check if tool is available
      if (!this.toolSchemas[toolName]) {
        // Try to fetch schema
        try {
          await this.fetchToolSchema(toolName);
        } catch (error) {
          throw new Error(`Tool ${toolName} is not available: ${error.message}`);
        }
      }
      
      // Check if function exists
      const functionSchema = this.toolSchemas[toolName].functions.find(f => f.name === functionName);
      if (!functionSchema) {
        throw new Error(`Function ${functionName} not found in tool ${toolName}`);
      }
      
      // Validate parameters
      this._validateParameters(parameters, functionSchema);
      
      // Get container URL
      const url = this.containerManager.getContainerUrl(toolName);
      
      // Call function
      const response = await axios.post(`${url}/invoke`, {
        function: functionName,
        parameters
      });
      
      const result = response.data;
      
      this.outputChannel.appendLine(`Function ${functionName} called successfully on tool ${toolName}`);
      
      return result;
    } catch (error) {
      this.outputChannel.appendLine(`Error calling function ${functionName} on tool ${toolName}: ${error.message}`);
      
      return {
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * Validate function parameters
   * @param parameters The parameters to validate
   * @param functionSchema The function schema
   */
  private _validateParameters(parameters: Record<string, any>, functionSchema: MCPFunctionSchema): void {
    // Check required parameters
    for (const requiredParam of functionSchema.parameters.required) {
      if (parameters[requiredParam] === undefined) {
        throw new Error(`Missing required parameter: ${requiredParam}`);
      }
    }
    
    // Check parameter types
    for (const paramName in parameters) {
      const paramSchema = functionSchema.parameters.properties[paramName];
      
      if (!paramSchema) {
        throw new Error(`Unknown parameter: ${paramName}`);
      }
      
      // Basic type checking
      const paramValue = parameters[paramName];
      const paramType = paramSchema.type;
      
      if (paramType === 'string' && typeof paramValue !== 'string') {
        throw new Error(`Parameter ${paramName} should be a string`);
      } else if (paramType === 'number' && typeof paramValue !== 'number') {
        throw new Error(`Parameter ${paramName} should be a number`);
      } else if (paramType === 'boolean' && typeof paramValue !== 'boolean') {
        throw new Error(`Parameter ${paramName} should be a boolean`);
      } else if (paramType === 'array' && !Array.isArray(paramValue)) {
        throw new Error(`Parameter ${paramName} should be an array`);
      } else if (paramType === 'object' && (typeof paramValue !== 'object' || paramValue === null || Array.isArray(paramValue))) {
        throw new Error(`Parameter ${paramName} should be an object`);
      }
      
      // Check enum values
      if (paramSchema.enum && !paramSchema.enum.includes(paramValue)) {
        throw new Error(`Parameter ${paramName} should be one of: ${paramSchema.enum.join(', ')}`);
      }
    }
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
