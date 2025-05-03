# Context Engine for VS Code Extension

This directory contains the implementation of the advanced context engine for the Qwen Coder Assistant VS Code extension. The context engine is designed to provide relevant code context to the Qwen 3 model, enabling it to generate more accurate and contextually aware responses.

## Architecture

The context engine consists of several components that work together to provide a comprehensive understanding of the codebase:

### 1. File Indexer and Chunker (`fileIndexer.ts`)

- Scans the workspace for code files
- Splits files into manageable chunks
- Handles file changes, additions, and deletions
- Updates the index incrementally

### 2. Embedding Service (`embeddingService.ts`)

- Generates vector embeddings for code chunks
- Uses the Qwen 3 embedding model
- Supports batch embedding generation
- Handles API communication for embeddings

### 3. Vector Store (`vectorStore.ts`)

- Stores code chunks and their embeddings
- Provides semantic search capabilities
- Calculates similarity between queries and code
- Manages the lifecycle of stored chunks

### 4. Symbol Extractor (`symbolExtractor.ts`)

- Extracts symbols (functions, classes, variables) from code
- Identifies imports and dependencies
- Supports multiple programming languages
- Provides language-specific extraction strategies

### 5. Dependency Graph (`dependencyGraph.ts`)

- Builds a graph of code dependencies
- Tracks relationships between files
- Identifies related files for a given file
- Supports traversal of the dependency graph

### 6. Semantic Search (`semanticSearch.ts`)

- Provides advanced search capabilities
- Combines exact and semantic matching
- Searches for symbols across the codebase
- Ranks results by relevance

### 7. Context Composer (`contextComposer.ts`)

- Composes relevant context from code chunks
- Manages token limits for context
- Organizes context by file and relevance
- Provides summaries of symbols and imports

### 8. Context Engine (`contextEngine.ts`)

- Coordinates all components
- Provides a unified API for context retrieval
- Handles initialization and cleanup
- Manages the lifecycle of the context system

## Usage

The context engine is used by the VS Code extension to provide relevant code context to the Qwen 3 model. It is initialized when the extension is activated and is used by the various commands to retrieve context for the current task.

### Basic Usage

```typescript
import { getProjectContext } from './contextProvider';

// Get context for a query
const context = await getProjectContext('How do I implement a binary search?');

// Use the context in a prompt
const prompt = `${userQuery}\n\nRelevant code context:\n${context}`;
```

### Advanced Usage

```typescript
import { getContextForFile, getContextForSymbol } from './contextProvider';

// Get context for a specific file
const fileContext = await getContextForFile('/path/to/file.ts');

// Get context for a specific symbol
const symbolContext = await getContextForSymbol('BinarySearch');
```

## Performance Considerations

The context engine is designed to be efficient and scalable, but there are some performance considerations to keep in mind:

- **Indexing**: The initial indexing of a large codebase can take some time. Progress is shown in the status bar.
- **Memory Usage**: The vector store keeps embeddings in memory, which can use significant RAM for large codebases.
- **API Calls**: The embedding service makes API calls to generate embeddings, which can incur costs and latency.

## Current Status and Future Improvements

### Implemented Features

- ✅ **Multi-Language Support**: Enhanced symbol extractor with support for 15+ programming languages
- ✅ **Incremental Indexing**: Optimized indexing process with batching and background processing
- ✅ **Language-Specific Chunking**: Intelligent chunking strategies based on language semantics
- ✅ **Binary File Detection**: Automatic detection and skipping of binary files

### Planned Improvements

- **Custom Context Filters**: Allow users to specify which files or directories to include/exclude
- **Context Visualization**: Add a way for users to see what context is being used
- **Persistent Storage**: Store embeddings on disk to avoid re-indexing on restart
- **Parallel Processing**: Use worker threads for indexing and embedding generation
- **Improved Dependency Analysis**: Better detection of relationships between files

## Contributing

Contributions to the context engine are welcome! Please follow these guidelines:

1. Write tests for new functionality
2. Document your code with JSDoc comments
3. Follow the existing code style
4. Consider performance implications for large codebases
