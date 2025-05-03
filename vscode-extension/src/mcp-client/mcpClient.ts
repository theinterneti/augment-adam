import * as vscode from 'vscode';
import { AuthManager } from './authentication/authManager';
import { McpServerManager } from './mcpServerManager';
import { McpTool, McpToolInvocation, McpToolResponse } from './types';

/**
 * Client for MCP servers
 */
export class McpClient implements vscode.Disposable {
  private serverManager: McpServerManager;
  private authManager?: AuthManager;

  /**
   * Create a new MCP client
   * @param serverManager MCP server manager
   * @param authManager Authentication manager (optional)
   */
  constructor(serverManager: McpServerManager, authManager?: AuthManager) {
    this.serverManager = serverManager;
    this.authManager = authManager;
  }

  /**
   * Get all available tools from all running servers
   * @returns Promise that resolves to an array of tools
   */
  public async getAllTools(): Promise<{ serverId: string; tool: McpTool }[]> {
    const servers = this.serverManager.getServers();
    const tools: { serverId: string; tool: McpTool }[] = [];

    for (const server of servers) {
      if (server.status === 'running' && server.schema?.tools) {
        for (const tool of server.schema.tools) {
          tools.push({
            serverId: server.id,
            tool
          });
        }
      }
    }

    return tools;
  }

  /**
   * Invoke a tool
   * @param serverId Server ID
   * @param toolName Tool name
   * @param parameters Tool parameters
   * @returns Promise that resolves to the tool response
   */
  public async invokeTool(serverId: string, toolName: string, parameters: Record<string, any>): Promise<McpToolResponse> {
    try {
      // Get the server
      const server = this.serverManager.getServer(serverId);
      if (!server) {
        return {
          status: 'error',
          error: `Server ${serverId} not found`
        };
      }

      // Check if the server is running
      if (server.status !== 'running') {
        return {
          status: 'error',
          error: `Server ${serverId} is not running`
        };
      }

      // Check if the server has a schema
      if (!server.schema) {
        return {
          status: 'error',
          error: `Server ${serverId} has no schema`
        };
      }

      // Find the tool in the schema
      const tool = server.schema.tools.find(t => t.name === toolName);
      if (!tool) {
        return {
          status: 'error',
          error: `Tool ${toolName} not found in server ${serverId}`
        };
      }

      // Validate parameters
      const validationResult = this.validateParameters(tool, parameters);
      if (validationResult.status === 'error') {
        return validationResult;
      }

      // Handle authentication if needed
      if (this.authManager && server.schema.authentication?.required) {
        try {
          // Check if we have authentication configured
          const hasAuth = await this.authManager.hasAuthConfig(serverId);
          if (!hasAuth) {
            // Prompt for authentication
            await this.authManager.promptForAuthentication(server);
          }

          // Check if token needs refresh
          const needsRefresh = await this.authManager.needsTokenRefresh(serverId);
          if (needsRefresh) {
            await this.authManager.refreshOAuthToken(serverId);
          }
        } catch (authError) {
          console.error(`Authentication error for server ${serverId}:`, authError);
          return {
            status: 'error',
            error: `Authentication error: ${authError}`
          };
        }
      }

      // Create the invocation
      const invocation: McpToolInvocation = {
        tool: toolName,
        parameters
      };

      // Get authentication headers if available
      let authHeaders: Record<string, string> | undefined;
      if (this.authManager) {
        authHeaders = await this.authManager.getAuthHeaders(serverId);
      }

      // Invoke the tool with authentication headers
      return this.serverManager.invokeTool(serverId, invocation, authHeaders);
    } catch (error) {
      console.error(`Error invoking tool ${toolName} on server ${serverId}:`, error);
      return {
        status: 'error',
        error: `Error invoking tool: ${error}`
      };
    }
  }

  /**
   * Validate parameters against a tool's schema
   * @param tool Tool schema
   * @param parameters Parameters to validate
   * @returns Validation result
   */
  private validateParameters(tool: McpTool, parameters: Record<string, any>): McpToolResponse {
    try {
      // Check for required parameters
      for (const param of tool.parameters) {
        if (param.required && parameters[param.name] === undefined) {
          return {
            status: 'error',
            error: `Missing required parameter: ${param.name}`
          };
        }
      }

      // Check parameter types (basic validation)
      for (const paramName in parameters) {
        const param = tool.parameters.find(p => p.name === paramName);
        if (!param) {
          return {
            status: 'error',
            error: `Unknown parameter: ${paramName}`
          };
        }

        // Basic type checking
        const value = parameters[paramName];

        if (param.type === 'string' && typeof value !== 'string') {
          return {
            status: 'error',
            error: `Parameter ${paramName} should be a string`
          };
        } else if (param.type === 'number' && typeof value !== 'number') {
          return {
            status: 'error',
            error: `Parameter ${paramName} should be a number`
          };
        } else if (param.type === 'boolean' && typeof value !== 'boolean') {
          return {
            status: 'error',
            error: `Parameter ${paramName} should be a boolean`
          };
        } else if (param.type === 'array' && !Array.isArray(value)) {
          return {
            status: 'error',
            error: `Parameter ${paramName} should be an array`
          };
        } else if (param.type === 'object' && (typeof value !== 'object' || value === null || Array.isArray(value))) {
          return {
            status: 'error',
            error: `Parameter ${paramName} should be an object`
          };
        }
      }

      return { status: 'success' };
    } catch (error) {
      console.error('Error validating parameters:', error);
      return {
        status: 'error',
        error: `Error validating parameters: ${error}`
      };
    }
  }

  /**
   * Find a tool by name
   * @param toolName Tool name
   * @returns Promise that resolves to the tool and server ID, or undefined if not found
   */
  public async findTool(toolName: string): Promise<{ serverId: string; tool: McpTool } | undefined> {
    const tools = await this.getAllTools();
    return tools.find(t => t.tool.name === toolName);
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    // Nothing to dispose
  }
}
