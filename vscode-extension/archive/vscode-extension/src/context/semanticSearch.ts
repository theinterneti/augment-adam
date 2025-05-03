import { VectorStore } from './vectorStore';
import { EmbeddingService } from './embeddingService';
import { CodeChunk } from './types';

export class SemanticSearch {
  private vectorStore: VectorStore;
  private embeddingService: EmbeddingService;
  
  constructor(vectorStore: VectorStore, embeddingService: EmbeddingService) {
    this.vectorStore = vectorStore;
    this.embeddingService = embeddingService;
  }
  
  public async search(query: string, limit: number = 10): Promise<CodeChunk[]> {
    // Generate embedding for the query
    const queryEmbedding = await this.embeddingService.generateEmbedding(query);
    
    // Find similar chunks
    return this.vectorStore.findSimilarChunksByEmbedding(queryEmbedding, limit);
  }
  
  public async searchBySymbol(symbol: string, limit: number = 10): Promise<CodeChunk[]> {
    // First, try to find exact symbol matches
    const allChunks = await this.vectorStore.findSimilarChunks('', 1000);
    const exactMatches = allChunks.filter(chunk => 
      chunk.symbols.includes(symbol) || 
      chunk.content.includes(`function ${symbol}`) ||
      chunk.content.includes(`class ${symbol}`) ||
      chunk.content.includes(`def ${symbol}`)
    );
    
    if (exactMatches.length >= limit) {
      return exactMatches.slice(0, limit);
    }
    
    // If we don't have enough exact matches, supplement with semantic search
    const semanticMatches = await this.search(symbol, limit - exactMatches.length);
    
    // Combine results, removing duplicates
    const combinedResults: CodeChunk[] = [...exactMatches];
    const existingIds = new Set(combinedResults.map(chunk => chunk.id));
    
    for (const match of semanticMatches) {
      if (!existingIds.has(match.id)) {
        combinedResults.push(match);
        existingIds.add(match.id);
      }
    }
    
    return combinedResults;
  }
}
