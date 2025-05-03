import * as vscode from 'vscode';
import { ContextComposer } from './contextComposer';
import { DependencyGraph } from './dependencyGraph';
import { EmbeddingService } from './embeddingService';
import { FileIndexer } from './fileIndexer';
import { SemanticSearch } from './semanticSearch';
import { SymbolExtractor } from './symbolExtractor';
import { CodeChunk } from './types';
import { VectorStore } from './vectorStore';

export class ContextEngine {
  private fileIndexer: FileIndexer;
  private embeddingService: EmbeddingService;
  private vectorStore: VectorStore;
  private symbolExtractor: SymbolExtractor;
  private contextComposer: ContextComposer;
  private dependencyGraph: DependencyGraph;
  private semanticSearch: SemanticSearch;
  private isInitialized: boolean = false;

  constructor() {
    this.embeddingService = new EmbeddingService();
    this.symbolExtractor = new SymbolExtractor();

    // Get configuration for context engine
    const config = getConfiguration().contextEngine;

    // Use persistent vector store if enabled in configuration
    if (config.persistEmbeddings) {
      console.log('Using persistent vector store for embeddings');
      this.vectorStore = new PersistentVectorStore(
        this.embeddingService,
        config.databasePath || undefined,
        config.autoSaveIntervalMs
      );
    } else {
      console.log('Using in-memory vector store for embeddings');
      this.vectorStore = new VectorStore(this.embeddingService);
    }

    this.contextComposer = new ContextComposer();
    this.dependencyGraph = new DependencyGraph();
    this.semanticSearch = new SemanticSearch(this.vectorStore, this.embeddingService);
    this.fileIndexer = new FileIndexer(
      this.symbolExtractor,
      this.embeddingService,
      this.vectorStore
    );
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    // Initialize the persistent vector store if needed
    if (this.vectorStore instanceof PersistentVectorStore) {
      console.log('Initializing persistent vector store');
      await (this.vectorStore as PersistentVectorStore).initialize();
    }

    // Only index the workspace if the vector store is empty
    const existingChunks = await this.vectorStore.findSimilarChunks('', 10);
    if (existingChunks.length === 0) {
      console.log('Vector store is empty, indexing workspace');
      await this.fileIndexer.indexWorkspace();
    } else {
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

  public async getContext(query: string, tokenLimit: number = 4000): Promise<string> {
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

  public async getContextForFile(filePath: string, tokenLimit: number = 4000): Promise<string> {
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

  public async getContextForSymbol(symbol: string, tokenLimit: number = 4000): Promise<string> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // Find chunks related to this symbol
    const symbolChunks = await this.semanticSearch.searchBySymbol(symbol, 10);

    // Compose context
    return this.contextComposer.composeContext(`Symbol: ${symbol}`, symbolChunks, tokenLimit);
  }

  private async getChunksForFile(filePath: string): Promise<CodeChunk[]> {
    // Find chunks for this file
    const allChunks = await this.vectorStore.findSimilarChunks('', 10000);
    return allChunks.filter(chunk => chunk.filePath === filePath);
  }

  private extractSymbolsFromQuery(query: string): string[] {
    // Extract potential symbols from the query
    // This is a simplified implementation
    const words = query.split(/\s+/);
    const symbols: string[] = [];

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

  public async dispose(): Promise<void> {
    // Dispose the file indexer
    this.fileIndexer.dispose();

    // Dispose the persistent vector store if needed
    if (this.vectorStore instanceof PersistentVectorStore) {
      console.log('Disposing persistent vector store');
      await (this.vectorStore as PersistentVectorStore).dispose();
    }
  }
}
