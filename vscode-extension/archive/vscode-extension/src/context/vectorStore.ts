import { CodeChunk } from './types';
import { EmbeddingService } from './embeddingService';

export class VectorStore {
  private chunks: CodeChunk[] = [];
  private embeddingService: EmbeddingService;
  
  constructor(embeddingService: EmbeddingService) {
    this.embeddingService = embeddingService;
  }
  
  public async addChunk(chunk: CodeChunk): Promise<void> {
    // If the chunk doesn't have an embedding, generate one
    if (!chunk.embedding) {
      chunk.embedding = await this.embeddingService.generateEmbedding(chunk.content);
    }
    
    // Check if chunk already exists (by ID)
    const existingIndex = this.chunks.findIndex(c => c.id === chunk.id);
    if (existingIndex >= 0) {
      // Replace existing chunk
      this.chunks[existingIndex] = chunk;
    } else {
      // Add new chunk
      this.chunks.push(chunk);
    }
  }
  
  public async findSimilarChunks(query: string, limit: number = 5): Promise<CodeChunk[]> {
    // Generate embedding for the query
    const queryEmbedding = await this.embeddingService.generateEmbedding(query);
    
    // Find similar chunks
    return this.findSimilarChunksByEmbedding(queryEmbedding, limit);
  }
  
  public async findSimilarChunksByEmbedding(embedding: number[], limit: number = 5): Promise<CodeChunk[]> {
    // Calculate cosine similarity for each chunk
    const chunksWithSimilarity = this.chunks.map(chunk => {
      const similarity = this.cosineSimilarity(embedding, chunk.embedding!);
      return { chunk, similarity };
    });
    
    // Sort by similarity (descending)
    chunksWithSimilarity.sort((a, b) => b.similarity - a.similarity);
    
    // Return top N chunks
    return chunksWithSimilarity.slice(0, limit).map(item => item.chunk);
  }
  
  public async deleteChunk(id: string): Promise<void> {
    this.chunks = this.chunks.filter(chunk => chunk.id !== id);
  }
  
  public async clear(): Promise<void> {
    this.chunks = [];
  }
  
  private cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have the same length');
    }
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}
