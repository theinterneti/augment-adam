"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VectorStore = void 0;
class VectorStore {
    constructor(embeddingService) {
        this.chunks = [];
        this.embeddingService = embeddingService;
    }
    async addChunk(chunk) {
        // If the chunk doesn't have an embedding, generate one
        if (!chunk.embedding) {
            chunk.embedding = await this.embeddingService.generateEmbedding(chunk.content);
        }
        // Check if chunk already exists (by ID)
        const existingIndex = this.chunks.findIndex(c => c.id === chunk.id);
        if (existingIndex >= 0) {
            // Replace existing chunk
            this.chunks[existingIndex] = chunk;
        }
        else {
            // Add new chunk
            this.chunks.push(chunk);
        }
    }
    async findSimilarChunks(query, limit = 5) {
        // Generate embedding for the query
        const queryEmbedding = await this.embeddingService.generateEmbedding(query);
        // Find similar chunks
        return this.findSimilarChunksByEmbedding(queryEmbedding, limit);
    }
    async findSimilarChunksByEmbedding(embedding, limit = 5) {
        // Calculate cosine similarity for each chunk
        const chunksWithSimilarity = this.chunks.map(chunk => {
            const similarity = this.cosineSimilarity(embedding, chunk.embedding);
            return { chunk, similarity };
        });
        // Sort by similarity (descending)
        chunksWithSimilarity.sort((a, b) => b.similarity - a.similarity);
        // Return top N chunks
        return chunksWithSimilarity.slice(0, limit).map(item => item.chunk);
    }
    async deleteChunk(id) {
        this.chunks = this.chunks.filter(chunk => chunk.id !== id);
    }
    async clear() {
        this.chunks = [];
    }
    cosineSimilarity(a, b) {
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
exports.VectorStore = VectorStore;
//# sourceMappingURL=vectorStore.js.map