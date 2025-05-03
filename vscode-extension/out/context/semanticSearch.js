"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SemanticSearch = void 0;
class SemanticSearch {
    constructor(vectorStore, embeddingService) {
        this.vectorStore = vectorStore;
        this.embeddingService = embeddingService;
    }
    async search(query, limit = 10) {
        // Generate embedding for the query
        const queryEmbedding = await this.embeddingService.generateEmbedding(query);
        // Find similar chunks
        return this.vectorStore.findSimilarChunksByEmbedding(queryEmbedding, limit);
    }
    async searchBySymbol(symbol, limit = 10) {
        // First, try to find exact symbol matches
        const allChunks = await this.vectorStore.findSimilarChunks('', 1000);
        const exactMatches = allChunks.filter(chunk => chunk.symbols.includes(symbol) ||
            chunk.content.includes(`function ${symbol}`) ||
            chunk.content.includes(`class ${symbol}`) ||
            chunk.content.includes(`def ${symbol}`));
        if (exactMatches.length >= limit) {
            return exactMatches.slice(0, limit);
        }
        // If we don't have enough exact matches, supplement with semantic search
        const semanticMatches = await this.search(symbol, limit - exactMatches.length);
        // Combine results, removing duplicates
        const combinedResults = [...exactMatches];
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
exports.SemanticSearch = SemanticSearch;
//# sourceMappingURL=semanticSearch.js.map