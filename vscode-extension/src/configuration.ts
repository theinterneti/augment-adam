import * as vscode from 'vscode';

export interface DockerOptions {
  socketPath: string;
  memory: number;
  cpus: number;
}

export interface GitHubOptions {
  token: string;
  timeout: number;
}

export interface McpServersConfig {
  storagePath: string;
  autoStart: boolean;
  autoStartList: string[];
  dockerOptions: DockerOptions;
  githubOptions: GitHubOptions;
}

export interface QwenCoderConfig {
  apiEndpoint: string;
  apiKey: string;
  maxTokens: number;
  temperature: number;
  cacheEnabled?: boolean;
  cacheTTLMinutes?: number;
  cacheMaxEntries?: number;
  mcpServers: McpServersConfig;
}

/**
 * Get the extension configuration
 * @returns The extension configuration
 */
export function getConfiguration(): QwenCoderConfig {
  const config = vscode.workspace.getConfiguration('qwen-coder-assistant');

  return {
    apiEndpoint: config.get<string>('apiEndpoint') || 'http://localhost:8000/v1',
    apiKey: config.get<string>('apiKey') || '',
    maxTokens: config.get<number>('maxTokens') || 2048,
    temperature: config.get<number>('temperature') || 0.7,
    cacheEnabled: config.get<boolean>('cacheEnabled') !== false, // Default to true
    cacheTTLMinutes: config.get<number>('cacheTTLMinutes') || 30,
    cacheMaxEntries: config.get<number>('cacheMaxEntries') || 100,
    mcpServers: {
      storagePath: config.get<string>('mcpServers.storagePath') || '',
      autoStart: config.get<boolean>('mcpServers.autoStart') !== false, // Default to true
      autoStartList: config.get<string[]>('mcpServers.autoStartList') || [],
      dockerOptions: config.get<DockerOptions>('mcpServers.dockerOptions') || {
        socketPath: '/var/run/docker.sock',
        memory: 2048,
        cpus: 2
      },
      githubOptions: config.get<GitHubOptions>('mcpServers.githubOptions') || {
        token: '',
        timeout: 30000
      }
    }
  };
}

/**
 * Verify that the configuration is valid
 * @param config The configuration to verify
 * @returns An object with validation results
 */
export function verifyConfiguration(config: QwenCoderConfig): {
  isValid: boolean;
  issues: string[];
  apiConfigured: boolean;
  mcpConfigured: boolean;
} {
  const issues: string[] = [];

  // Check API configuration
  const apiConfigured = Boolean(config.apiEndpoint && config.apiEndpoint.trim() !== '');
  if (!apiConfigured) {
    issues.push('API endpoint is not configured');
  }

  // Check MCP server configuration
  const mcpConfigured = Boolean(config.mcpServers.storagePath && config.mcpServers.storagePath.trim() !== '');
  if (!mcpConfigured) {
    issues.push('MCP server storage path is not configured');
  }

  // Check Docker configuration
  if (!config.mcpServers.dockerOptions.socketPath) {
    issues.push('Docker socket path is not configured');
  }

  return {
    isValid: issues.length === 0,
    issues,
    apiConfigured,
    mcpConfigured
  };
}

// Listen for configuration changes
export function registerConfigurationListener(callback: (config: QwenCoderConfig) => void): vscode.Disposable {
  return vscode.workspace.onDidChangeConfiguration(event => {
    if (event.affectsConfiguration('qwen-coder-assistant')) {
      callback(getConfiguration());
    }
  });
}
