import * as assert from 'assert';
import * as sinon from 'sinon';
import axios from 'axios';
import { QwenApiClient } from '../../qwenApi';
import { QwenMessage, QwenResponse } from '../../qwenApi';

suite('Qwen API Client Test Suite', () => {
  let qwenApiClient: QwenApiClient;
  let axiosStub: sinon.SinonStub;
  
  setup(() => {
    // Create API client with test configuration
    qwenApiClient = new QwenApiClient({
      apiKey: 'test-api-key',
      apiEndpoint: 'https://test-api-endpoint.com',
      model: 'qwen-test-model'
    });
    
    // Stub axios to prevent actual API calls
    axiosStub = sinon.stub(axios, 'post');
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should send chat completion request', async () => {
    // Setup mock response
    const mockResponse = {
      data: {
        id: 'test-response-id',
        object: 'chat.completion',
        created: Date.now(),
        model: 'qwen-test-model',
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: 'This is a test response'
            },
            finish_reason: 'stop'
          }
        ]
      }
    };
    
    axiosStub.resolves(mockResponse);
    
    // Create test messages
    const messages: QwenMessage[] = [
      { role: 'system', content: 'You are a helpful assistant' },
      { role: 'user', content: 'Hello, how are you?' }
    ];
    
    // Execute
    const response = await qwenApiClient.getChatCompletion(messages);
    
    // Verify
    assert.strictEqual(axiosStub.calledOnce, true, 'Should make API call');
    assert.strictEqual(response.choices[0].message.content, 'This is a test response', 'Should return correct response');
    
    // Verify request format
    const requestArg = axiosStub.firstCall.args[1];
    assert.strictEqual(requestArg.messages.length, 2, 'Should send correct number of messages');
    assert.strictEqual(requestArg.model, 'qwen-test-model', 'Should use configured model');
  });
  
  test('Should handle streaming responses', async () => {
    // Setup
    const mockStreamingResponse = {
      data: {
        id: 'test-stream-id',
        object: 'chat.completion.chunk',
        created: Date.now(),
        model: 'qwen-test-model',
        choices: [
          {
            index: 0,
            delta: {
              content: 'This is '
            },
            finish_reason: null
          }
        ]
      }
    };
    
    // Create a mock for the streaming response
    const mockStream = {
      [Symbol.asyncIterator]: () => {
        let count = 0;
        const chunks = [
          { data: JSON.stringify(mockStreamingResponse.data) },
          { 
            data: JSON.stringify({
              ...mockStreamingResponse.data,
              choices: [
                {
                  index: 0,
                  delta: {
                    content: 'a test'
                  },
                  finish_reason: null
                }
              ]
            })
          },
          { 
            data: JSON.stringify({
              ...mockStreamingResponse.data,
              choices: [
                {
                  index: 0,
                  delta: {
                    content: ' response'
                  },
                  finish_reason: 'stop'
                }
              ]
            })
          }
        ];
        
        return {
          next: () => {
            if (count < chunks.length) {
              return Promise.resolve({ value: chunks[count++], done: false });
            }
            return Promise.resolve({ done: true });
          }
        };
      }
    };
    
    // Stub axios to return the mock stream
    axiosStub.returns(Promise.resolve({ data: mockStream }));
    
    // Create test messages
    const messages: QwenMessage[] = [
      { role: 'system', content: 'You are a helpful assistant' },
      { role: 'user', content: 'Hello, how are you?' }
    ];
    
    // Create a callback to collect streaming responses
    const streamingResponses: string[] = [];
    const onChunk = (chunk: string) => {
      streamingResponses.push(chunk);
    };
    
    // Execute
    await qwenApiClient.getStreamingChatCompletion(messages, onChunk);
    
    // Verify
    assert.strictEqual(axiosStub.calledOnce, true, 'Should make API call');
    assert.strictEqual(streamingResponses.length, 3, 'Should receive all chunks');
    assert.strictEqual(streamingResponses.join(''), 'This is a test response', 'Should concatenate to full response');
    
    // Verify request format
    const requestArg = axiosStub.firstCall.args[1];
    assert.strictEqual(requestArg.stream, true, 'Should set stream parameter');
  });
  
  test('Should handle API errors', async () => {
    // Setup - simulate API error
    axiosStub.rejects({
      response: {
        status: 401,
        data: {
          error: 'Invalid API key'
        }
      }
    });
    
    // Create test messages
    const messages: QwenMessage[] = [
      { role: 'user', content: 'Hello' }
    ];
    
    // Execute and verify
    try {
      await qwenApiClient.getChatCompletion(messages);
      assert.fail('Should throw an error');
    } catch (error) {
      assert.strictEqual(error.message.includes('Invalid API key'), true, 'Should include error message from API');
    }
  });
  
  test('Should handle tool calls in responses', async () => {
    // Setup mock response with tool calls
    const mockResponse = {
      data: {
        id: 'test-response-id',
        object: 'chat.completion',
        created: Date.now(),
        model: 'qwen-test-model',
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: null,
              tool_calls: [
                {
                  id: 'tool-call-1',
                  type: 'function',
                  function: {
                    name: 'get_weather',
                    arguments: '{"location":"New York","unit":"celsius"}'
                  }
                }
              ]
            },
            finish_reason: 'tool_calls'
          }
        ]
      }
    };
    
    axiosStub.resolves(mockResponse);
    
    // Create test messages
    const messages: QwenMessage[] = [
      { role: 'user', content: 'What\'s the weather in New York?' }
    ];
    
    // Execute
    const response = await qwenApiClient.getChatCompletion(messages);
    
    // Verify
    assert.strictEqual(response.choices[0].message.tool_calls?.length, 1, 'Should include tool calls');
    assert.strictEqual(response.choices[0].message.tool_calls?.[0].function.name, 'get_weather', 'Should have correct tool name');
    assert.strictEqual(response.choices[0].finish_reason, 'tool_calls', 'Should have correct finish reason');
  });
});
