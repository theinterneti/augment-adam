"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MockQwenApiClient = void 0;
const cache_1 = require("./cache");
const qwenApi_1 = require("./qwenApi");
/**
 * A mock implementation of the QwenApiClient for testing and development
 * without requiring an actual API endpoint.
 */
class MockQwenApiClient extends qwenApi_1.QwenApiClient {
    constructor(config) {
        super(config);
    }
    /**
     * Override the updateConfig method to update the cache configuration
     */
    updateConfig(config) {
        super.updateConfig(config);
    }
    /**
     * Override the generateCompletion method to return mock responses
     */
    async generateCompletion(options) {
        // Check cache first (unless skipCache is true or cacheEnabled is false)
        if (!options.skipCache && this.config.cacheEnabled) {
            const cacheKey = (0, cache_1.generateCacheKey)(options.prompt, {
                systemPrompt: options.systemPrompt,
                maxTokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            });
            const cachedResponse = this.cache.get(cacheKey);
            if (cachedResponse) {
                console.log('Using cached mock response for prompt:', options.prompt.substring(0, 50) + '...');
                return {
                    ...cachedResponse,
                    cached: true
                };
            }
        }
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        // Generate a mock response based on the prompt
        const prompt = options.prompt.toLowerCase();
        let response = '';
        if (prompt.includes('explain')) {
            response = this.generateExplanationResponse(prompt);
        }
        else if (prompt.includes('generate') || prompt.includes('write')) {
            response = this.generateCodeResponse(prompt);
        }
        else {
            response = this.generateGeneralResponse(prompt);
        }
        const result = {
            text: response,
            usage: {
                promptTokens: options.prompt.length,
                completionTokens: response.length,
                totalTokens: options.prompt.length + response.length
            }
        };
        // Cache the response (unless skipCache is true or cacheEnabled is false)
        if (!options.skipCache && this.config.cacheEnabled) {
            const cacheKey = (0, cache_1.generateCacheKey)(options.prompt, {
                systemPrompt: options.systemPrompt,
                maxTokens: options.maxTokens || this.config.maxTokens,
                temperature: options.temperature || this.config.temperature
            });
            this.cache.set(cacheKey, result);
        }
        return result;
    }
    generateExplanationResponse(prompt) {
        return `# Code Explanation

This code appears to be ${prompt.includes('javascript') ? 'JavaScript' : prompt.includes('python') ? 'Python' : 'a programming language'} code that performs some operations.

## Key Components:

1. **Initialization**: The code sets up initial variables and configurations.
2. **Processing**: It processes data through several steps.
3. **Output**: Finally, it returns or displays the results.

## How It Works:

The code follows a typical pattern where it:
1. Takes input
2. Transforms the input through algorithms
3. Produces output based on the transformation

## Best Practices:

The code demonstrates several good practices:
- Clear variable naming
- Proper error handling
- Efficient algorithm implementation

Would you like me to explain any specific part in more detail?`;
    }
    generateCodeResponse(prompt) {
        const language = prompt.includes('javascript') || prompt.includes('js') ? 'javascript' :
            prompt.includes('typescript') || prompt.includes('ts') ? 'typescript' :
                prompt.includes('python') || prompt.includes('py') ? 'python' : 'javascript';
        if (language === 'javascript' || language === 'typescript') {
            return `# Generated Code

Here's a ${language} implementation for your request:

\`\`\`${language}
/**
 * A utility function that performs the requested operation
 * @param {Array} data - The input data to process
 * @param {Object} options - Configuration options
 * @returns {Array} - The processed results
 */
function processData(data, options = {}) {
  // Default options
  const config = {
    sortBy: 'name',
    filterEmpty: true,
    maxResults: 100,
    ...options
  };

  // Input validation
  if (!Array.isArray(data)) {
    throw new Error('Input must be an array');
  }

  // Filter out empty items if configured
  let results = config.filterEmpty
    ? data.filter(item => item && Object.keys(item).length > 0)
    : [...data];

  // Sort the results if needed
  if (config.sortBy) {
    results.sort((a, b) => {
      if (a[config.sortBy] < b[config.sortBy]) return -1;
      if (a[config.sortBy] > b[config.sortBy]) return 1;
      return 0;
    });
  }

  // Limit the number of results
  if (config.maxResults && results.length > config.maxResults) {
    results = results.slice(0, config.maxResults);
  }

  return results;
}

// Example usage
const sampleData = [
  { name: 'Item 3', value: 30 },
  { name: 'Item 1', value: 10 },
  { name: 'Item 2', value: 20 },
  {},  // Empty object
  { name: 'Item 4', value: 40 }
];

const result = processData(sampleData, {
  sortBy: 'value',
  maxResults: 3
});

console.log(result);
\`\`\`

This implementation includes:
- Flexible configuration options
- Input validation
- Sorting and filtering capabilities
- Example usage

You can customize the function parameters and behavior based on your specific requirements.`;
        }
        else if (language === 'python') {
            return `# Generated Code

Here's a Python implementation for your request:

\`\`\`python
from typing import List, Dict, Any, Optional
import copy

def process_data(data: List[Dict[str, Any]],
                 sort_by: Optional[str] = 'name',
                 filter_empty: bool = True,
                 max_results: Optional[int] = 100) -> List[Dict[str, Any]]:
    """
    Process a list of dictionaries based on the provided options.

    Args:
        data: List of dictionaries to process
        sort_by: Key to sort by (None for no sorting)
        filter_empty: Whether to filter out empty dictionaries
        max_results: Maximum number of results to return (None for all)

    Returns:
        Processed list of dictionaries
    """
    # Input validation
    if not isinstance(data, list):
        raise TypeError("Input must be a list")

    # Create a copy to avoid modifying the original
    results = copy.deepcopy(data)

    # Filter out empty items if configured
    if filter_empty:
        results = [item for item in results if item and len(item) > 0]

    # Sort the results if needed
    if sort_by is not None:
        results.sort(key=lambda x: x.get(sort_by, None))

    # Limit the number of results
    if max_results is not None and len(results) > max_results:
        results = results[:max_results]

    return results

# Example usage
if __name__ == "__main__":
    sample_data = [
        {"name": "Item 3", "value": 30},
        {"name": "Item 1", "value": 10},
        {"name": "Item 2", "value": 20},
        {},  # Empty dictionary
        {"name": "Item 4", "value": 40}
    ]

    result = process_data(
        data=sample_data,
        sort_by="value",
        max_results=3
    )

    print(result)
\`\`\`

This implementation includes:
- Type hints for better code quality
- Docstring with parameter descriptions
- Input validation
- Deep copying to prevent modifying the original data
- Sorting and filtering capabilities
- Example usage

You can adjust the function parameters and behavior based on your specific requirements.`;
        }
        else {
            return `# Generated Code

I'm not sure which programming language you prefer, so here's a pseudocode implementation:

\`\`\`
function ProcessData(data, options)
    // Set default options
    if options.sortBy is undefined then options.sortBy = "name"
    if options.filterEmpty is undefined then options.filterEmpty = true
    if options.maxResults is undefined then options.maxResults = 100

    // Validate input
    if data is not a list/array then
        throw Error("Input must be an array/list")
    end if

    // Create a copy of the data
    results = copy(data)

    // Filter empty items if needed
    if options.filterEmpty then
        results = filter(results, item => item is not empty)
    end if

    // Sort if needed
    if options.sortBy is not null then
        results = sort(results by options.sortBy)
    end if

    // Limit results
    if options.maxResults is not null and length(results) > options.maxResults then
        results = first options.maxResults items from results
    end if

    return results
end function
\`\`\`

Let me know which programming language you'd prefer, and I can provide a more specific implementation.`;
        }
    }
    generateGeneralResponse(_prompt) {
        return `# Response

Thank you for your question! Here's what I can tell you:

The concept you're asking about is fundamental in software development. Let me break it down:

## Key Points:

1. **Understanding the Basics**:
   It's important to grasp the fundamental concepts before diving into implementation details.

2. **Best Practices**:
   - Write clean, maintainable code
   - Document your work thoroughly
   - Test your code regularly
   - Follow established patterns and conventions

3. **Common Approaches**:
   There are several ways to tackle this problem, each with its own advantages:
   - Method A: Simple but may not scale well
   - Method B: More complex but highly efficient
   - Method C: Balanced approach for most use cases

## Example:

Here's a simplified example to illustrate:

\`\`\`javascript
function demonstrateConcept(input) {
  // Validate input
  if (!input) {
    return null;
  }

  // Process the input
  const result = input.map(item => {
    return {
      ...item,
      processed: true,
      timestamp: Date.now()
    };
  });

  return result;
}
\`\`\`

## Further Learning:

If you'd like to explore this topic further, I recommend:
- Reading the official documentation
- Practicing with small projects
- Joining community discussions

Is there a specific aspect you'd like me to elaborate on?`;
    }
    /**
     * Override the generateStreamingCompletion method to simulate streaming responses
     */
    async generateStreamingCompletion(options, onChunk) {
        try {
            // Generate a complete response first
            const prompt = options.prompt.toLowerCase();
            let fullResponse = '';
            if (prompt.includes('explain')) {
                fullResponse = this.generateExplanationResponse(prompt);
            }
            else if (prompt.includes('generate') || prompt.includes('write')) {
                fullResponse = this.generateCodeResponse(prompt);
            }
            else {
                fullResponse = this.generateGeneralResponse(prompt);
            }
            // Simulate streaming by sending chunks with delays
            const chunks = this.chunkResponse(fullResponse);
            for (let i = 0; i < chunks.length; i++) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 100));
                // Send the chunk
                const isLast = i === chunks.length - 1;
                onChunk(chunks[i], isLast);
                // If we're simulating an error, break early
                if (prompt.includes('error') && i > chunks.length / 2) {
                    onChunk('\n\nError: Simulated streaming error for testing purposes', true);
                    break;
                }
            }
        }
        catch (error) {
            console.error('Error in mock streaming:', error);
            onChunk(`Error: ${error instanceof Error ? error.message : String(error)}`, true);
        }
    }
    /**
     * Split a response into chunks for simulated streaming
     */
    chunkResponse(response) {
        // Split by sentences or line breaks for more natural chunking
        const chunks = [];
        const sentences = response.split(/(?<=\.|\?|\!|\n)\s+/);
        // Group sentences into reasonable chunks
        let currentChunk = '';
        for (const sentence of sentences) {
            currentChunk += sentence + ' ';
            // When chunk gets big enough, add it to chunks array
            if (currentChunk.length > 30) {
                chunks.push(currentChunk.trim());
                currentChunk = '';
            }
        }
        // Add any remaining content
        if (currentChunk.trim()) {
            chunks.push(currentChunk.trim());
        }
        return chunks;
    }
}
exports.MockQwenApiClient = MockQwenApiClient;
//# sourceMappingURL=mockQwenApi.js.map