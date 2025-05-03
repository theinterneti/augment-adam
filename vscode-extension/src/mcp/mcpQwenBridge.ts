import * as vscode from 'vscode';
import { QwenApiClient, QwenMessage, QwenResponse, QwenTool, QwenToolCall } from '../qwenApi';
import { ContextGatherer } from './contextGatherer';
import { McpClient } from './mcpClient';
import { MCPToolSchema } from './mcpTypes';

/**
 * Type for streaming response handler
 */
export type StreamingResponseHandler = (chunk: string, done: boolean, toolCalls?: QwenToolCall[]) => void;

/**
 * Bridge between MCP and Qwen
 * Handles converting MCP tools to Qwen tools and processing tool calls
 */
export class McpQwenBridge {
  private outputChannel: vscode.OutputChannel;
  private contextGatherer: ContextGatherer;

  constructor(
    private qwenClient: QwenApiClient,
    private mcpClient: McpClient
  ) {
    this.outputChannel = vscode.window.createOutputChannel('MCP-Qwen Bridge');
    this.contextGatherer = new ContextGatherer(mcpClient);
  }

  /**
   * Process a user message with MCP tools
   * @param message User message
   * @param options Options for processing
   * @returns Response from Qwen with tool results if applicable
   */
  public async processMessage(
    message: string,
    options: {
      systemPrompt?: string;
      thinkingMode?: 'auto' | 'always' | 'never';
      thinkingBudget?: number;
      temperature?: number;
      maxTokens?: number;
      modelName?: string;
      contextMessages?: QwenMessage[];
      gatherContext?: boolean;
    } = {}
  ): Promise<string> {
    try {
      this.outputChannel.appendLine(`Processing message: ${message.substring(0, 100)}...`);

      // Get available tools from MCP servers
      const mcpTools = await this.mcpClient.getAllTools();
      this.outputChannel.appendLine(`Found ${mcpTools.length} MCP tools`);

      // Convert MCP tools to Qwen tools
      const qwenTools = mcpTools.map(tool => this.convertToolToQwenFormat(tool));

      // Create messages array
      const messages: QwenMessage[] = [];

      // Add system message if provided
      if (options.systemPrompt) {
        messages.push({
          role: 'system',
          content: options.systemPrompt
        });
      }

      // Add context messages if provided
      if (options.contextMessages && options.contextMessages.length > 0) {
        messages.push(...options.contextMessages);
      }

      // Gather context if enabled
      if (options.gatherContext !== false) {
        try {
          const contextMessages = await this.contextGatherer.gatherContext(message);
          if (contextMessages.length > 0) {
            this.outputChannel.appendLine(`Adding ${contextMessages.length} context messages`);
            messages.push(...contextMessages);
          }
        } catch (error) {
          this.outputChannel.appendLine(`Error gathering context: ${error}`);
        }
      }

      // Add user message
      messages.push({
        role: 'user',
        content: message
      });

      // Call Qwen API with tools
      const response = await this.qwenClient.chatWithTools(messages, {
        thinkingMode: options.thinkingMode || 'auto',
        thinkingBudget: options.thinkingBudget,
        temperature: options.temperature,
        maxTokens: options.maxTokens,
        modelName: options.modelName,
        tools: qwenTools
      });

      // Process tool calls if present
      if (response.tool_calls && response.tool_calls.length > 0) {
        return await this.processToolCallsAndGetFinalResponse(response, messages);
      }

      return response.text;
    } catch (error) {
      this.outputChannel.appendLine(`Error processing message: ${error}`);
      return `Error: ${error}`;
    }
  }

  /**
   * Process a user message with MCP tools using streaming
   * @param message User message
   * @param options Options for processing
   * @param onChunk Callback function to handle streaming chunks
   */
  public async processMessageStream(
    message: string,
    options: {
      systemPrompt?: string;
      thinkingMode?: 'auto' | 'always' | 'never';
      thinkingBudget?: number;
      temperature?: number;
      maxTokens?: number;
      modelName?: string;
      contextMessages?: QwenMessage[];
      gatherContext?: boolean;
    } = {},
    onChunk: StreamingResponseHandler
  ): Promise<void> {
    try {
      this.outputChannel.appendLine(`Processing message with streaming: ${message.substring(0, 100)}...`);

      // Get available tools from MCP servers
      const mcpTools = await this.mcpClient.getAllTools();
      this.outputChannel.appendLine(`Found ${mcpTools.length} MCP tools`);

      // Convert MCP tools to Qwen tools
      const qwenTools = mcpTools.map(tool => this.convertToolToQwenFormat(tool));

      // Create messages array
      const messages: QwenMessage[] = [];

      // Add system message if provided
      if (options.systemPrompt) {
        messages.push({
          role: 'system',
          content: options.systemPrompt
        });
      }

      // Add context messages if provided
      if (options.contextMessages && options.contextMessages.length > 0) {
        messages.push(...options.contextMessages);
      }

      // Gather context if enabled
      if (options.gatherContext !== false) {
        try {
          const contextMessages = await this.contextGatherer.gatherContext(message);
          if (contextMessages.length > 0) {
            this.outputChannel.appendLine(`Adding ${contextMessages.length} context messages`);
            messages.push(...contextMessages);
          }
        } catch (error) {
          this.outputChannel.appendLine(`Error gathering context: ${error}`);
        }
      }

      // Add user message
      messages.push({
        role: 'user',
        content: message
      });

      // Accumulate the full response and tool calls
      let fullResponse = '';
      let toolCalls: QwenToolCall[] = [];

      // Call Qwen API with tools and streaming
      await this.qwenClient.chatStreamWithTools(
        messages,
        {
          thinkingMode: options.thinkingMode || 'auto',
          thinkingBudget: options.thinkingBudget,
          temperature: options.temperature,
          maxTokens: options.maxTokens,
          modelName: options.modelName,
          tools: qwenTools
        },
        async (chunk, done, chunkToolCalls) => {
          // Accumulate the response
          fullResponse += chunk;

          // Update tool calls if present
          if (chunkToolCalls && chunkToolCalls.length > 0) {
            toolCalls = chunkToolCalls;
          }

          // Pass to the original handler
          onChunk(chunk, false, toolCalls);

          // When streaming is complete, process tool calls if present
          if (done && toolCalls.length > 0) {
            // Add assistant message with tool calls
            messages.push({
              role: 'assistant',
              content: fullResponse,
              tool_calls: toolCalls
            });

            // Process tool calls
            await this.processToolCallsAndStreamFinalResponse(toolCalls, messages, onChunk);
          } else if (done) {
            // Signal completion if no tool calls
            onChunk('', true);
          }
        }
      );
    } catch (error) {
      this.outputChannel.appendLine(`Error processing message with streaming: ${error}`);
      onChunk(`Error: ${error}`, true);
    }
  }

  /**
   * Process tool calls and get a final response
   * @param initialResponse Initial response with tool calls
   * @param messages Conversation messages
   * @returns Final response after tool execution
   */
  private async processToolCallsAndGetFinalResponse(
    initialResponse: QwenResponse,
    messages: QwenMessage[]
  ): Promise<string> {
    if (!initialResponse.tool_calls || initialResponse.tool_calls.length === 0) {
      return initialResponse.text;
    }

    this.outputChannel.appendLine(`Processing ${initialResponse.tool_calls.length} tool calls`);

    // Add assistant message with tool calls
    messages.push({
      role: 'assistant',
      content: initialResponse.text,
      tool_calls: initialResponse.tool_calls
    });

    // Process each tool call
    const toolResults = await Promise.all(
      initialResponse.tool_calls.map(async (toolCall) => {
        try {
          const result = await this.executeToolCall(toolCall);
          return {
            tool_call_id: toolCall.id,
            role: 'tool' as const,
            name: toolCall.function.name,
            content: typeof result === 'string' ? result : JSON.stringify(result)
          };
        } catch (error) {
          return {
            tool_call_id: toolCall.id,
            role: 'tool' as const,
            name: toolCall.function.name,
            content: `Error: ${error}`
          };
        }
      })
    );

    // Add tool results to messages
    messages.push(...toolResults);

    // Get final response from Qwen
    const finalResponse = await this.qwenClient.chat(messages);
    return finalResponse;
  }

  /**
   * Process tool calls and stream the final response
   * @param toolCalls Tool calls to process
   * @param messages Conversation messages
   * @param onChunk Callback function to handle streaming chunks
   */
  private async processToolCallsAndStreamFinalResponse(
    toolCalls: QwenToolCall[],
    messages: QwenMessage[],
    onChunk: StreamingResponseHandler
  ): Promise<void> {
    try {
      this.outputChannel.appendLine(`Processing ${toolCalls.length} tool calls for streaming response`);

      // Process each tool call
      const toolResults = await Promise.all(
        toolCalls.map(async (toolCall) => {
          try {
            const result = await this.executeToolCall(toolCall);
            return {
              tool_call_id: toolCall.id,
              role: 'tool' as const,
              name: toolCall.function.name,
              content: typeof result === 'string' ? result : JSON.stringify(result)
            };
          } catch (error) {
            return {
              tool_call_id: toolCall.id,
              role: 'tool' as const,
              name: toolCall.function.name,
              content: `Error: ${error}`
            };
          }
        })
      );

      // Add tool results to messages
      messages.push(...toolResults);

      // Stream final response from Qwen
      await this.qwenClient.chatStream(
        messages,
        {},
        (chunk, done) => {
          onChunk(chunk, done);
        }
      );
    } catch (error) {
      this.outputChannel.appendLine(`Error processing tool calls for streaming: ${error}`);
      onChunk(`Error: ${error}`, true);
    }
  }

  /**
   * Execute a tool call
   * @param toolCall Tool call to execute
   * @returns Result of the tool call
   */
  private async executeToolCall(toolCall: QwenToolCall): Promise<any> {
    try {
      this.outputChannel.appendLine(`Executing tool call: ${toolCall.function.name}`);

      // Parse the function name (format: serverId.toolName.functionName)
      const [serverId, toolName, functionName] = toolCall.function.name.split('.');

      if (!serverId || !toolName || !functionName) {
        throw new Error(`Invalid function name format: ${toolCall.function.name}`);
      }

      // Parse arguments
      let args: Record<string, any>;
      try {
        args = JSON.parse(toolCall.function.arguments);
      } catch (error) {
        throw new Error(`Invalid arguments: ${error}`);
      }

      // Call the function
      const result = await this.mcpClient.callFunction(serverId, toolName, functionName, args);

      // Check for errors
      if (result.status === 'error') {
        throw new Error(result.error || 'Unknown error');
      }

      this.outputChannel.appendLine(`Tool call executed successfully`);
      return result.result;
    } catch (error) {
      this.outputChannel.appendLine(`Error executing tool call: ${error}`);
      throw error;
    }
  }

  /**
   * Convert MCP tool to Qwen tool format
   * @param mcpTool MCP tool
   * @returns Qwen tool
   */
  private convertToolToQwenFormat(mcpTool: { serverId: string; tool: MCPToolSchema }): QwenTool {
    try {
      const { serverId, tool } = mcpTool;

      // Create a tool for each function in the MCP tool
      return {
        type: 'function',
        function: {
          name: `${serverId}.${tool.name}`,
          description: tool.description || `Tool provided by ${serverId}`,
          parameters: {
            type: 'object',
            properties: this.convertParametersToQwenFormat(tool.parameters || []),
            required: tool.parameters
              ?.filter(param => param.required)
              .map(param => param.name) || []
          }
        }
      };
    } catch (error) {
      this.outputChannel.appendLine(`Error converting MCP tool to Qwen format: ${error}`);
      throw error;
    }
  }

  /**
   * Convert MCP parameters to Qwen format
   * @param parameters MCP parameters
   * @returns Qwen parameters
   */
  private convertParametersToQwenFormat(
    parameters: Array<{
      name: string;
      type: string;
      description?: string;
      required?: boolean;
      enum?: string[];
    }>
  ): Record<string, any> {
    const result: Record<string, any> = {};

    for (const param of parameters) {
      result[param.name] = {
        type: this.mapMcpTypeToQwenType(param.type),
        description: param.description || `Parameter ${param.name}`
      };

      // Add enum if available
      if (param.enum && param.enum.length > 0) {
        result[param.name].enum = param.enum;
      }
    }

    return result;
  }

  /**
   * Map MCP type to Qwen type
   * @param mcpType MCP type
   * @returns Qwen type
   */
  private mapMcpTypeToQwenType(mcpType: string): string {
    // Convert MCP types to Qwen types
    switch (mcpType.toLowerCase()) {
      case 'string':
      case 'text':
      case 'char':
        return 'string';
      case 'integer':
      case 'int':
      case 'long':
      case 'short':
      case 'byte':
      case 'float':
      case 'double':
      case 'decimal':
      case 'number':
        return 'number';
      case 'boolean':
      case 'bool':
        return 'boolean';
      case 'array':
      case 'list':
      case 'collection':
        return 'array';
      case 'object':
      case 'map':
      case 'dict':
      case 'dictionary':
        return 'object';
      case 'null':
        return 'null';
      default:
        // Default to string for unknown types
        this.outputChannel.appendLine(`Unknown MCP type: ${mcpType}, defaulting to string`);
        return 'string';
    }
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this.outputChannel.dispose();
    this.contextGatherer.dispose();
  }
}
