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
  Performance = 'performance',
  Simple = 'simple',
  DevOps = 'devops',
  ML = 'machine_learning',
  WebDev = 'web_development'
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
  High = 'high',
  // New complexity levels for dynamic agent selection
  Simple = 'simple',
  Moderate = 'moderate',
  Complex = 'complex',
  VeryComplex = 'very_complex'
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

/**
 * Agent capabilities
 */
export type AgentCapability = 'context' | 'tools' | 'reasoning' | 'code' | 'testing' | 'documentation' | 'architecture';

/**
 * Agent definition for dynamic selection
 */
export interface Agent {
  name: string;
  type: AgentType;
  capabilities: AgentCapability[];
  modelSize: ModelSize;
  maxComplexity: TaskComplexity;
  specializations?: string[];
  systemPrompt: string;
  available: boolean;
}

/**
 * Task domain types
 */
export type TaskDomain = 'general' | 'web-development' | 'machine-learning' | 'devops' | 'database' | 'mobile-development';

/**
 * Context scope types
 */
export type ContextScope = 'none' | 'file' | 'directory' | 'project' | 'deep';

/**
 * Task definition for agent selection
 */
export interface Task {
  description: string;
  complexity?: TaskComplexity;
  requiresContext: boolean;
  requiresTools: boolean;
  contextScope?: ContextScope;
  requiredTools?: string[];
  domain?: TaskDomain;
}
