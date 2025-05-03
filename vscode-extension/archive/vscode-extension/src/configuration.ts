import * as vscode from 'vscode';

export interface ContextEngineConfig {
  persistEmbeddings: boolean;
  databasePath: string;
  autoSaveIntervalMs: number;
}

export interface QwenCoderConfig {
  apiEndpoint: string;
  apiKey: string;
  maxTokens: number;
  temperature: number;
  cacheEnabled: boolean;
  cacheTTLMinutes: number;
  cacheMaxEntries: number;
  streamingEnabled: boolean;
  contextEngine: ContextEngineConfig;
}

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
    streamingEnabled: config.get<boolean>('streamingEnabled') !== false, // Default to true
    contextEngine: {
      persistEmbeddings: config.get<boolean>('contextEngine.persistEmbeddings') !== false, // Default to true
      databasePath: config.get<string>('contextEngine.databasePath') || '',
      autoSaveIntervalMs: config.get<number>('contextEngine.autoSaveIntervalMs') || 60000
    }
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
