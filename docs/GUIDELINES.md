# Context Engine Guidelines

This document provides guidelines for using and extending the high-performance context engine.

## Memory System Guidelines

### Vector Storage

- **Primary Storage**: Use Redis for real-time vector similarity search
- **Secondary Storage**: Use Neo4j for graph-aware vector search
- **Embedding Model**: Use `all-MiniLM-L6-v2` for code embeddings
- **Vector Dimensions**: 384 dimensions
- **Similarity Metric**: Cosine similarity
- **Index Algorithm**: HNSW (Hierarchical Navigable Small World)
- **Index Parameters**:
  - M: 16 (maximum number of connections per node)
  - EF Construction: 200 (size of the dynamic list for the nearest neighbors)
  - EF Runtime: 10 (size of the dynamic list for the nearest neighbors at query time)

### Tiered Memory

- **Hot Tier**:
  - Storage: Redis
  - TTL: None (no expiration)
  - Priority: High
  - Use for: Real-time queries, frequently accessed vectors
  
- **Warm Tier**:
  - Storage: Redis
  - TTL: 24 hours
  - Priority: Medium
  - Use for: Background tasks, less frequently accessed vectors
  
- **Cold Tier**:
  - Storage: Neo4j
  - TTL: None (no expiration)
  - Priority: Low
  - Use for: Complex queries, rarely accessed vectors, relationship data

### Asynchronous Processing

- **Worker Concurrency**: 4 workers
- **Task Queue**: `context_engine:tasks`
- **Task Types**:
  - `index_code`: Index code in the vector database
  - `update_knowledge_graph`: Update the knowledge graph with new relationships
  - `sync_vectors`: Synchronize vectors between Redis and Neo4j
  - `prune_vectors`: Prune old or unused vectors
- **Task Priorities**: high, medium, low

## Code Indexing Guidelines

### Languages

Support the following languages:
- Python
- JavaScript
- TypeScript
- Java
- Go
- Rust
- C
- C++

### Parsing Strategy

Use AST (Abstract Syntax Tree) parsing for accurate code understanding.

### Indexing Levels

Index code at multiple levels:
- File level
- Function level
- Class level
- Code block level

### Metadata

Extract the following metadata:
- File path
- Language
- Imports
- Dependencies
- Function name
- Class name
- Docstring
- Parameters
- Return type

## Query Processing Guidelines

### Query Routing

Use a hybrid routing strategy:
- Route simple vector similarity queries to Redis
- Route complex graph-based queries to Neo4j
- Use a query classifier to automatically determine the best route

### Query Caching

- Enable caching for improved performance
- Set TTL to 1 hour
- Use semantic caching for similar queries

### Result Merging

Use a weighted merging strategy:
- Vector similarity: 70% weight
- Graph relevance: 30% weight

### Result Ranking

Use a combined ranking strategy based on:
- Similarity score
- Recency
- Popularity
- Relevance

## Integration Guidelines

### API

- Base URL: `http://localhost:8080`
- Endpoints:
  - `/search`: Search for similar vectors
  - `/graph-search`: Search for similar vectors with graph context
  - `/store`: Store a vector in the database

### Client Libraries

Provide client libraries for:
- Python
- JavaScript

### Authentication

- Method: API key
- Header: `X-API-Key`

## Performance Guidelines

### Redis Configuration

- Max memory: 6GB
- Max memory policy: allkeys-lru
- IO threads: 2
- Threads: 6

### Neo4j Configuration

- Heap initial size: 1GB
- Heap max size: 4GB
- Pagecache size: 2GB
- Transaction concurrent maximum: 32

### API Configuration

- Workers: 4
- Timeout: 30 seconds

### Worker Configuration

- Concurrency: 4
- Batch size: 100

## Development Guidelines

### Docker

- Use existing Docker containers when available
- Build custom containers only when necessary

### Testing

- Write unit tests for all components
- Write integration tests for API endpoints
- Write performance tests for critical paths

### Documentation

- Document all API endpoints
- Document the architecture
- Provide examples for common use cases
