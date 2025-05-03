import * as path from 'path';
import * as fs from 'fs';
import * as vscode from 'vscode';
import * as sqlite3 from 'sqlite3';
import { Database, open } from 'sqlite';
import { CodeChunk } from './types';
import { EmbeddingService } from './embeddingService';
import { VectorStore } from './vectorStore';

/**
 * A vector store that persists embeddings to disk using SQLite
 */
export class PersistentVectorStore extends VectorStore {
  private dbPath: string;
  private db: Database | null = null;
  private autoSaveInterval: NodeJS.Timeout | null = null;
  private isDirty: boolean = false;
  private isInitialized: boolean = false;
  
  /**
   * Create a new persistent vector store
   * @param embeddingService The embedding service to use
   * @param dbPath Path to the SQLite database file (optional, defaults to extension storage path)
   * @param autoSaveIntervalMs Interval in milliseconds to auto-save changes (optional, defaults to 60000)
   */
  constructor(
    embeddingService: EmbeddingService, 
    dbPath?: string,
    autoSaveIntervalMs: number = 60000
  ) {
    super(embeddingService);
    
    // If no dbPath is provided, use the extension's storage path
    if (!dbPath) {
      const storagePath = this.getStoragePath();
      if (!storagePath) {
        throw new Error('Could not determine storage path for persistent vector store');
      }
      
      // Ensure the directory exists
      if (!fs.existsSync(storagePath)) {
        fs.mkdirSync(storagePath, { recursive: true });
      }
      
      this.dbPath = path.join(storagePath, 'vector-store.db');
    } else {
      this.dbPath = dbPath;
    }
    
    // Set up auto-save if interval is positive
    if (autoSaveIntervalMs > 0) {
      this.autoSaveInterval = setInterval(() => {
        if (this.isDirty) {
          this.saveToDatabase().catch(error => {
            console.error('Error auto-saving vector store:', error);
          });
        }
      }, autoSaveIntervalMs);
    }
  }
  
  /**
   * Initialize the database
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }
    
    try {
      // Open the database
      this.db = await open({
        filename: this.dbPath,
        driver: sqlite3.Database
      });
      
      // Create tables if they don't exist
      await this.db.exec(`
        CREATE TABLE IF NOT EXISTS chunks (
          id TEXT PRIMARY KEY,
          filePath TEXT NOT NULL,
          content TEXT NOT NULL,
          startLine INTEGER NOT NULL,
          endLine INTEGER NOT NULL,
          language TEXT NOT NULL,
          symbols TEXT,
          imports TEXT
        );
        
        CREATE TABLE IF NOT EXISTS embeddings (
          chunk_id TEXT PRIMARY KEY,
          embedding BLOB NOT NULL,
          FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_chunks_filePath ON chunks (filePath);
      `);
      
      // Load existing chunks from the database
      await this.loadFromDatabase();
      
      this.isInitialized = true;
    } catch (error) {
      console.error('Error initializing persistent vector store:', error);
      throw error;
    }
  }
  
  /**
   * Add a chunk to the vector store
   * @param chunk The chunk to add
   */
  public async addChunk(chunk: CodeChunk): Promise<void> {
    // Call the parent method to add the chunk to memory
    await super.addChunk(chunk);
    
    // Mark as dirty to trigger auto-save
    this.isDirty = true;
  }
  
  /**
   * Delete a chunk from the vector store
   * @param id The ID of the chunk to delete
   */
  public async deleteChunk(id: string): Promise<void> {
    // Call the parent method to delete the chunk from memory
    await super.deleteChunk(id);
    
    // Delete from database if initialized
    if (this.db) {
      try {
        await this.db.run('DELETE FROM chunks WHERE id = ?', id);
        await this.db.run('DELETE FROM embeddings WHERE chunk_id = ?', id);
      } catch (error) {
        console.error(`Error deleting chunk ${id} from database:`, error);
      }
    }
    
    // Mark as dirty to trigger auto-save
    this.isDirty = true;
  }
  
  /**
   * Clear the vector store
   */
  public async clear(): Promise<void> {
    // Call the parent method to clear the in-memory store
    await super.clear();
    
    // Clear the database if initialized
    if (this.db) {
      try {
        await this.db.exec('DELETE FROM embeddings');
        await this.db.exec('DELETE FROM chunks');
      } catch (error) {
        console.error('Error clearing database:', error);
      }
    }
    
    // Mark as dirty to trigger auto-save
    this.isDirty = true;
  }
  
  /**
   * Save all chunks to the database
   */
  public async saveToDatabase(): Promise<void> {
    if (!this.db) {
      await this.initialize();
    }
    
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    
    try {
      // Start a transaction
      await this.db.exec('BEGIN TRANSACTION');
      
      // Get all chunks
      const chunks = await this.getAllChunks();
      
      // Insert or update each chunk
      for (const chunk of chunks) {
        // Insert or replace the chunk
        await this.db.run(
          `INSERT OR REPLACE INTO chunks (id, filePath, content, startLine, endLine, language, symbols, imports)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
          chunk.id,
          chunk.filePath,
          chunk.content,
          chunk.startLine,
          chunk.endLine,
          chunk.language,
          JSON.stringify(chunk.symbols),
          JSON.stringify(chunk.imports)
        );
        
        // Insert or replace the embedding if it exists
        if (chunk.embedding) {
          await this.db.run(
            `INSERT OR REPLACE INTO embeddings (chunk_id, embedding)
             VALUES (?, ?)`,
            chunk.id,
            Buffer.from(new Float32Array(chunk.embedding).buffer)
          );
        }
      }
      
      // Commit the transaction
      await this.db.exec('COMMIT');
      
      // Reset dirty flag
      this.isDirty = false;
      
      console.log(`Saved ${chunks.length} chunks to database`);
    } catch (error) {
      // Rollback the transaction on error
      if (this.db) {
        await this.db.exec('ROLLBACK');
      }
      
      console.error('Error saving to database:', error);
      throw error;
    }
  }
  
  /**
   * Load chunks from the database
   */
  private async loadFromDatabase(): Promise<void> {
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    
    try {
      // Get all chunks from the database
      const rows = await this.db.all(`
        SELECT c.id, c.filePath, c.content, c.startLine, c.endLine, c.language, c.symbols, c.imports, e.embedding
        FROM chunks c
        LEFT JOIN embeddings e ON c.id = e.chunk_id
      `);
      
      // Clear existing chunks
      await super.clear();
      
      // Add each chunk to the in-memory store
      for (const row of rows) {
        const chunk: CodeChunk = {
          id: row.id,
          filePath: row.filePath,
          content: row.content,
          startLine: row.startLine,
          endLine: row.endLine,
          language: row.language,
          symbols: row.symbols ? JSON.parse(row.symbols) : [],
          imports: row.imports ? JSON.parse(row.imports) : []
        };
        
        // Add embedding if it exists
        if (row.embedding) {
          const buffer = Buffer.from(row.embedding);
          const float32Array = new Float32Array(buffer.buffer, buffer.byteOffset, buffer.byteLength / 4);
          chunk.embedding = Array.from(float32Array);
        }
        
        // Add to in-memory store without saving to database
        await super.addChunk(chunk);
      }
      
      console.log(`Loaded ${rows.length} chunks from database`);
    } catch (error) {
      console.error('Error loading from database:', error);
      throw error;
    }
  }
  
  /**
   * Get the storage path for the extension
   */
  private getStoragePath(): string | undefined {
    // Get the extension context
    const extension = vscode.extensions.getExtension('qwen-coder-assistant');
    if (extension) {
      return extension.extensionPath;
    }
    
    // Fallback to the workspace storage path
    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
      return path.join(vscode.workspace.workspaceFolders[0].uri.fsPath, '.vscode');
    }
    
    return undefined;
  }
  
  /**
   * Dispose of resources
   */
  public async dispose(): Promise<void> {
    // Clear auto-save interval
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }
    
    // Save any pending changes
    if (this.isDirty && this.db) {
      try {
        await this.saveToDatabase();
      } catch (error) {
        console.error('Error saving vector store during disposal:', error);
      }
    }
    
    // Close the database
    if (this.db) {
      await this.db.close();
      this.db = null;
    }
  }
}
