/**
 * Types for MCP client and server management
 */

/**
 * MCP function schema
 */
export interface MCPFunctionSchema {
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
export interface MCPToolSchema {
  name: string;
  description: string;
  functions: MCPFunctionSchema[];
}

/**
 * MCP function call result
 */
export interface MCPFunctionCallResult {
  status: 'success' | 'error';
  result?: any;
  error?: string;
}

/**
 * MCP tool parameter
 */
export interface MCPToolParameter {
  name: string;
  description: string;
  type: string;
  required: boolean;
  default?: any;
}

/**
 * MCP tool return
 */
export interface MCPToolReturn {
  description: string;
  type: string;
}
