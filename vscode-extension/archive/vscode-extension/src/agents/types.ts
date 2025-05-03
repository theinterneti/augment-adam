/**
 * Type definitions for the hierarchical agent system
 */

/**
 * Agent types supported by the system
 */
export enum AgentType {
  Coordinator = 'coordinator',
  Development = 'development',
  Testing = 'testing',
  CICD = 'ci_cd',
  GitHub = 'github',
  Documentation = 'documentation',
  Architecture = 'architecture',
  Security = 'security',
  Performance = 'performance'
}

/**
 * Model sizes available for agents
 */
export enum ModelSize {
  Tiny = 'Qwen3-0.6B',
  Small = 'Qwen3-1.7B',
  Medium = 'Qwen3-4B',
  Large = 'Qwen3-8B',
  XLarge = 'Qwen3-14B',
  XXLarge = 'Qwen3-32B',
  MoESmall = 'Qwen3-30B-A3B',
  MoELarge = 'Qwen3-235B-A22B'
}

/**
 * Task complexity levels
 */
export enum TaskComplexity {
  Low = 'low',
  Medium = 'medium',
  High = 'high'
}

/**
 * Thinking mode options
 */
export enum ThinkingMode {
  Enabled = 'enabled',
  Disabled = 'disabled',
  Auto = 'auto'
}

/**
 * Agent configuration
 */
export interface AgentConfig {
  type: AgentType;
  modelSize: ModelSize;
  thinkingMode: ThinkingMode;
  systemMessage: string;
  maxTokens: number;
}

/**
 * Subtask definition
 */
export interface Subtask {
  id: string;
  description: string;
  expertise: AgentType;
  complexity: TaskComplexity;
  dependencies: string[];
}

/**
 * Agent result
 */
export interface AgentResult {
  subtaskId: string;
  thinking?: string;
  content: string;
  status: 'success' | 'error';
  error?: string;
}

/**
 * Resource usage information
 */
export interface ResourceUsage {
  memory: number;
  cpu: number;
  activeAgents: number;
}

/**
 * Agent status
 */
export interface AgentStatus {
  id: string;
  type: AgentType;
  modelSize: ModelSize;
  thinkingMode: ThinkingMode;
  status: 'idle' | 'running' | 'completed' | 'failed';
  startTime: number;
  endTime?: number;
  error?: string;
}
