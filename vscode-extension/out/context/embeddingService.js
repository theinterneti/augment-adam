"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmbeddingService = void 0;
const axios_1 = __importDefault(require("axios"));
const configuration_1 = require("../configuration");
class EmbeddingService {
    constructor() {
        const config = (0, configuration_1.getConfiguration)();
        this.apiEndpoint = config.apiEndpoint;
        this.apiKey = config.apiKey;
    }
    async generateEmbedding(text) {
        try {
            const response = await axios_1.default.post(`${this.apiEndpoint}/embeddings`, {
                input: text,
                model: 'qwen3-embedding'
            }, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data.data[0].embedding;
        }
        catch (error) {
            console.error('Error generating embedding:', error);
            throw new Error('Failed to generate embedding');
        }
    }
    async generateBatchEmbeddings(texts) {
        try {
            const response = await axios_1.default.post(`${this.apiEndpoint}/embeddings`, {
                input: texts,
                model: 'qwen3-embedding'
            }, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data.data.map((item) => item.embedding);
        }
        catch (error) {
            console.error('Error generating batch embeddings:', error);
            throw new Error('Failed to generate batch embeddings');
        }
    }
}
exports.EmbeddingService = EmbeddingService;
//# sourceMappingURL=embeddingService.js.map