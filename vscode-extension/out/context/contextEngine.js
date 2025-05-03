"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContextEngine = void 0;
const vscode = __importStar(require("vscode"));
const contextComposer_1 = require("./contextComposer");
const dependencyGraph_1 = require("./dependencyGraph");
const embeddingService_1 = require("./embeddingService");
const fileIndexer_1 = require("./fileIndexer");
const semanticSearch_1 = require("./semanticSearch");
const symbolExtractor_1 = require("./symbolExtractor");
const vectorStore_1 = require("./vectorStore");
class ContextEngine {
    constructor() {
        this.isInitialized = false;
        this.embeddingService = new embeddingService_1.EmbeddingService();
        this.symbolExtractor = new symbolExtractor_1.SymbolExtractor();
        // Get configuration for context engine
        const config = getConfiguration().contextEngine;
        // Use persistent vector store if enabled in configuration
        if (config.persistEmbeddings) {
            console.log('Using persistent vector store for embeddings');
            this.vectorStore = new PersistentVectorStore(this.embeddingService, config.databasePath || undefined, config.autoSaveIntervalMs);
        }
        else {
            console.log('Using in-memory vector store for embeddings');
            this.vectorStore = new vectorStore_1.VectorStore(this.embeddingService);
        }
        this.contextComposer = new contextComposer_1.ContextComposer();
        this.dependencyGraph = new dependencyGraph_1.DependencyGraph();
        this.semanticSearch = new semanticSearch_1.SemanticSearch(this.vectorStore, this.embeddingService);
        this.fileIndexer = new fileIndexer_1.FileIndexer(this.symbolExtractor, this.embeddingService, this.vectorStore);
    }
    async initialize() {
        if (this.isInitialized) {
            return;
        }
        // Initialize the persistent vector store if needed
        if (this.vectorStore instanceof PersistentVectorStore) {
            console.log('Initializing persistent vector store');
            await this.vectorStore.initialize();
        }
        // Only index the workspace if the vector store is empty
        const existingChunks = await this.vectorStore.findSimilarChunks('', 10);
        if (existingChunks.length === 0) {
            console.log('Vector store is empty, indexing workspace');
            await this.fileIndexer.indexWorkspace();
        }
        else {
            console.log(`Found ${existingChunks.length} existing chunks in vector store, skipping indexing`);
        }
        // Build dependency graph
        const allChunks = await this.vectorStore.findSimilarChunks('', 10000);
        for (const chunk of allChunks) {
            this.dependencyGraph.addChunk(chunk);
        }
        this.dependencyGraph.buildGraph();
        this.isInitialized = true;
    }
    async getContext(query, tokenLimit = 4000) {
        if (!this.isInitialized) {
            await this.initialize();
        }
        // Find relevant chunks using semantic search
        const relevantChunks = await this.semanticSearch.search(query, 10);
        // Extract symbols from the query
        const symbols = this.extractSymbolsFromQuery(query);
        // If we found symbols, add chunks related to those symbols
        if (symbols.length > 0) {
            for (const symbol of symbols) {
                const symbolChunks = await this.semanticSearch.searchBySymbol(symbol, 5);
                // Add symbol chunks to relevant chunks, avoiding duplicates
                const existingIds = new Set(relevantChunks.map(chunk => chunk.id));
                for (const chunk of symbolChunks) {
                    if (!existingIds.has(chunk.id)) {
                        relevantChunks.push(chunk);
                        existingIds.add(chunk.id);
                    }
                }
            }
        }
        // Get the active editor file path
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor) {
            const filePath = activeEditor.document.uri.fsPath;
            // Get related files from dependency graph
            const relatedFiles = this.dependencyGraph.getRelatedFiles(filePath, 1);
            // Add chunks from related files
            for (const relatedFile of relatedFiles) {
                const fileChunks = await this.getChunksForFile(relatedFile);
                // Add file chunks to relevant chunks, avoiding duplicates
                const existingIds = new Set(relevantChunks.map(chunk => chunk.id));
                for (const chunk of fileChunks) {
                    if (!existingIds.has(chunk.id)) {
                        relevantChunks.push(chunk);
                        existingIds.add(chunk.id);
                    }
                }
            }
        }
        // Compose context
        return this.contextComposer.composeContext(query, relevantChunks, tokenLimit);
    }
    async getContextForFile(filePath, tokenLimit = 4000) {
        if (!this.isInitialized) {
            await this.initialize();
        }
        // Get chunks for this file
        const fileChunks = await this.getChunksForFile(filePath);
        // Get related files from dependency graph
        const relatedFiles = this.dependencyGraph.getRelatedFiles(filePath, 1);
        // Add chunks from related files
        const allChunks = [...fileChunks];
        const existingIds = new Set(allChunks.map(chunk => chunk.id));
        for (const relatedFile of relatedFiles) {
            const relatedChunks = await this.getChunksForFile(relatedFile);
            for (const chunk of relatedChunks) {
                if (!existingIds.has(chunk.id)) {
                    allChunks.push(chunk);
                    existingIds.add(chunk.id);
                }
            }
        }
        // Compose context
        return this.contextComposer.composeContext(`File: ${filePath}`, allChunks, tokenLimit);
    }
    async getContextForSymbol(symbol, tokenLimit = 4000) {
        if (!this.isInitialized) {
            await this.initialize();
        }
        // Find chunks related to this symbol
        const symbolChunks = await this.semanticSearch.searchBySymbol(symbol, 10);
        // Compose context
        return this.contextComposer.composeContext(`Symbol: ${symbol}`, symbolChunks, tokenLimit);
    }
    async getChunksForFile(filePath) {
        // Find chunks for this file
        const allChunks = await this.vectorStore.findSimilarChunks('', 10000);
        return allChunks.filter(chunk => chunk.filePath === filePath);
    }
    extractSymbolsFromQuery(query) {
        // Extract potential symbols from the query
        // This is a simplified implementation
        const words = query.split(/\s+/);
        const symbols = [];
        for (const word of words) {
            // Clean up the word
            const cleanWord = word.replace(/[^\w]/g, '');
            // Check if it looks like a symbol (camelCase, PascalCase, snake_case)
            if (cleanWord.length > 0 &&
                (cleanWord.match(/[a-z][A-Z]/) || // camelCase
                    cleanWord.match(/^[A-Z][a-z]/) || // PascalCase
                    cleanWord.includes('_'))) { // snake_case
                symbols.push(cleanWord);
            }
        }
        return symbols;
    }
    async dispose() {
        // Dispose the file indexer
        this.fileIndexer.dispose();
        // Dispose the persistent vector store if needed
        if (this.vectorStore instanceof PersistentVectorStore) {
            console.log('Disposing persistent vector store');
            await this.vectorStore.dispose();
        }
    }
}
exports.ContextEngine = ContextEngine;
//# sourceMappingURL=contextEngine.js.map