/**
 * Development Agent
 * 
 * Specialized agent for code generation, refactoring, and documentation.
 */

import * as vscode from 'vscode';
import { AgentType, ModelSize, ThinkingMode, Subtask, AgentResult } from './types';
import { QwenApiClient } from '../qwenApi';
import { getContextForCurrentFile } from '../contextProvider';

/**
 * Development Agent class
 */
export class DevelopmentAgent {
  private id: string;
  private qwenApi: QwenApiClient;
  private modelSize: ModelSize;
  private thinkingMode: ThinkingMode;
  private outputChannel: vscode.OutputChannel;

  /**
   * Constructor
   * @param id The agent ID
   * @param qwenApi The Qwen API client
   * @param modelSize The model size to use
   * @param thinkingMode The thinking mode to use
   */
  constructor(
    id: string,
    qwenApi: QwenApiClient,
    modelSize: ModelSize,
    thinkingMode: ThinkingMode
  ) {
    this.id = id;
    this.qwenApi = qwenApi;
    this.modelSize = modelSize;
    this.thinkingMode = thinkingMode;
    this.outputChannel = vscode.window.createOutputChannel(`Development Agent ${id}`);
    
    this.outputChannel.appendLine(`Development Agent initialized with model ${modelSize} and thinking mode ${thinkingMode}`);
  }

  /**
   * Execute a subtask
   * @param subtask The subtask to execute
   * @returns The result of the execution
   */
  public async execute(subtask: Subtask): Promise<AgentResult> {
    try {
      this.outputChannel.appendLine(`Executing subtask: ${subtask.description}`);
      
      // Get context from the current file
      const context = await getContextForCurrentFile();
      
      // Prepare the system message
      const systemMessage = `
        You are a Development Agent specializing in writing high-quality code, refactoring, and documentation.
        Your task is to help with development-related activities in a DevOps workflow.
        
        You excel at:
        1. Writing clean, efficient, and well-documented code
        2. Refactoring existing code to improve quality and maintainability
        3. Implementing best practices and design patterns
        4. Creating comprehensive documentation
        5. Solving complex programming problems
        
        When writing code:
        - Follow language-specific conventions and best practices
        - Include appropriate error handling
        - Add clear comments explaining complex logic
        - Consider edge cases and potential issues
        - Optimize for readability and maintainability
        
        When providing explanations:
        - Be clear and concise
        - Use examples to illustrate concepts
        - Explain your reasoning and decision-making process
        - Highlight trade-offs and alternatives considered
      `;
      
      // Prepare the user message
      const userMessage = `
        I need help with the following development task: ${subtask.description}
        
        ${context ? `Here is the current context:\n\n${context}` : ''}
      `;
      
      // Prepare the messages for the API call
      const messages = [
        { role: 'system', content: systemMessage },
        { role: 'user', content: userMessage }
      ];
      
      // Call the Qwen API with the appropriate thinking mode
      const enableThinking = this.thinkingMode === ThinkingMode.Enabled;
      const response = await this.qwenApi.chat(messages, {
        enableThinking,
        temperature: 0.3,
        maxTokens: 4096,
        modelName: this.modelSize
      });
      
      this.outputChannel.appendLine('Subtask executed successfully');
      
      return {
        subtaskId: subtask.id,
        thinking: enableThinking ? this._extractThinking(response) : undefined,
        content: this._extractContent(response, enableThinking),
        status: 'success'
      };
    } catch (error) {
      this.outputChannel.appendLine(`Error executing subtask: ${error.message}`);
      
      return {
        subtaskId: subtask.id,
        content: '',
        status: 'error',
        error: error.message
      };
    }
  }

  /**
   * Extract thinking from response
   * @param response The API response
   * @returns The extracted thinking
   */
  private _extractThinking(response: string): string {
    const thinkingMatch = response.match(/<think>([\s\S]*?)<\/think>/);
    return thinkingMatch ? thinkingMatch[1].trim() : '';
  }

  /**
   * Extract content from response
   * @param response The API response
   * @param enableThinking Whether thinking mode was enabled
   * @returns The extracted content
   */
  private _extractContent(response: string, enableThinking: boolean): string {
    if (enableThinking) {
      // Remove thinking tags and content
      return response.replace(/<think>[\s\S]*?<\/think>/, '').trim();
    }
    
    return response.trim();
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
