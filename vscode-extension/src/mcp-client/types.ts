/**
 * Types for MCP client and server management
 */

/**
 * Status of an MCP server
 */
export enum McpServerStatus {
  Running = 'running',
  Stopped = 'stopped',
  Starting = 'starting',
  Stopping = 'stopping',
  Error = 'error',
  Unknown = 'unknown'
}

/**
 * Type of MCP server
 */
export enum McpServerType {
  Docker = 'docker',
  Process = 'process'
}

/**
 * Authentication type for MCP servers
 */
export type McpServerAuthType = 'token' | 'basic' | 'api_key' | 'oauth2' | 'none';

/**
 * Base authentication configuration for MCP servers
 */
export interface McpServerAuthConfigBase {
  type: McpServerAuthType;
}

/**
 * Token authentication configuration
 */
export interface McpServerTokenAuthConfig extends McpServerAuthConfigBase {
  type: 'token';
  token: string;
}

/**
 * Basic authentication configuration
 */
export interface McpServerBasicAuthConfig extends McpServerAuthConfigBase {
  type: 'basic';
  username: string;
  password: string;
}

/**
 * API key authentication configuration
 */
export interface McpServerApiKeyAuthConfig extends McpServerAuthConfigBase {
  type: 'api_key';
  apiKey: string;
  headerName?: string;
}

/**
 * OAuth2 authentication configuration
 */
export interface McpServerOAuth2AuthConfig extends McpServerAuthConfigBase {
  type: 'oauth2';
  clientId: string;
  clientSecret: string;
  authUrl: string;
  tokenUrl: string;
  scopes: string[];
  accessToken: string;
  refreshToken: string;
  expiresAt?: string;
}

/**
 * No authentication configuration
 */
export interface McpServerNoAuthConfig extends McpServerAuthConfigBase {
  type: 'none';
}

/**
 * Authentication configuration for MCP servers
 */
export type McpServerAuthConfig =
  | McpServerTokenAuthConfig
  | McpServerBasicAuthConfig
  | McpServerApiKeyAuthConfig
  | McpServerOAuth2AuthConfig
  | McpServerNoAuthConfig;

/**
 * MCP server information
 */
export interface McpServer {
  id: string;
  name: string;
  description: string;
  repoUrl: string;
  version: string;
  status: McpServerStatus;
  type: McpServerType;
  endpoint?: string;
  containerId?: string;
  processId?: number;
  error?: string;
  lastStarted?: Date;
  lastStopped?: Date;
  autoStart: boolean;
  schema?: McpServerSchema;
  logs: string[];
  localPath?: string;
  dockerfilePath?: string;
  healthStatus?: 'healthy' | 'unhealthy' | 'unknown';
  lastHealthCheck?: Date;
}

/**
 * MCP server schema
 */
export interface McpServerSchema {
  name: string;
  description: string;
  version: string;
  apiVersion?: 'v1' | 'v2';
  tools: McpTool[];
  resources?: any[];
  authentication?: {
    type: McpServerAuthType;
    required: boolean;
    scopes?: string[];
    authUrl?: string;
    tokenUrl?: string;
  };
}

/**
 * MCP tool
 */
export interface McpTool {
  name: string;
  description: string;
  parameters: McpToolParameter[];
  returns: McpToolReturn;
}

/**
 * MCP tool parameter
 */
export interface McpToolParameter {
  name: string;
  description: string;
  type: string;
  required: boolean;
  default?: any;
}

/**
 * MCP tool return
 */
export interface McpToolReturn {
  description: string;
  type: string;
}

/**
 * MCP tool invocation
 */
export interface McpToolInvocation {
  tool: string;
  parameters: Record<string, any>;
}

/**
 * MCP tool response
 */
export interface McpToolResponse {
  status: 'success' | 'error';
  result?: any;
  error?: string;
}
