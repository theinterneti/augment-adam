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
exports.PersistentVectorStore = void 0;
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const vscode = __importStar(require("vscode"));
const sqlite3 = __importStar(require("sqlite3"));
const sqlite_1 = require("sqlite");
const vectorStore_1 = require("./vectorStore");
/**
 * A vector store that persists embeddings to disk using SQLite
 */
class PersistentVectorStore extends vectorStore_1.VectorStore {
    /**
     * Create a new persistent vector store
     * @param embeddingService The embedding service to use
     * @param dbPath Path to the SQLite database file (optional, defaults to extension storage path)
     * @param autoSaveIntervalMs Interval in milliseconds to auto-save changes (optional, defaults to 60000)
     */
    constructor(embeddingService, dbPath, autoSaveIntervalMs = 60000) {
        super(embeddingService);
        this.db = null;
        this.autoSaveInterval = null;
        this.isDirty = false;
        this.isInitialized = false;
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
        }
        else {
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
    async initialize() {
        if (this.isInitialized) {
            return;
        }
        try {
            // Open the database
            this.db = await (0, sqlite_1.open)({
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
        }
        catch (error) {
            console.error('Error initializing persistent vector store:', error);
            throw error;
        }
    }
    /**
     * Add a chunk to the vector store
     * @param chunk The chunk to add
     */
    async addChunk(chunk) {
        // Call the parent method to add the chunk to memory
        await super.addChunk(chunk);
        // Mark as dirty to trigger auto-save
        this.isDirty = true;
    }
    /**
     * Delete a chunk from the vector store
     * @param id The ID of the chunk to delete
     */
    async deleteChunk(id) {
        // Call the parent method to delete the chunk from memory
        await super.deleteChunk(id);
        // Delete from database if initialized
        if (this.db) {
            try {
                await this.db.run('DELETE FROM chunks WHERE id = ?', id);
                await this.db.run('DELETE FROM embeddings WHERE chunk_id = ?', id);
            }
            catch (error) {
                console.error(`Error deleting chunk ${id} from database:`, error);
            }
        }
        // Mark as dirty to trigger auto-save
        this.isDirty = true;
    }
    /**
     * Clear the vector store
     */
    async clear() {
        // Call the parent method to clear the in-memory store
        await super.clear();
        // Clear the database if initialized
        if (this.db) {
            try {
                await this.db.exec('DELETE FROM embeddings');
                await this.db.exec('DELETE FROM chunks');
            }
            catch (error) {
                console.error('Error clearing database:', error);
            }
        }
        // Mark as dirty to trigger auto-save
        this.isDirty = true;
    }
    /**
     * Save all chunks to the database
     */
    async saveToDatabase() {
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
                await this.db.run(`INSERT OR REPLACE INTO chunks (id, filePath, content, startLine, endLine, language, symbols, imports)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, chunk.id, chunk.filePath, chunk.content, chunk.startLine, chunk.endLine, chunk.language, JSON.stringify(chunk.symbols), JSON.stringify(chunk.imports));
                // Insert or replace the embedding if it exists
                if (chunk.embedding) {
                    await this.db.run(`INSERT OR REPLACE INTO embeddings (chunk_id, embedding)
             VALUES (?, ?)`, chunk.id, Buffer.from(new Float32Array(chunk.embedding).buffer));
                }
            }
            // Commit the transaction
            await this.db.exec('COMMIT');
            // Reset dirty flag
            this.isDirty = false;
            console.log(`Saved ${chunks.length} chunks to database`);
        }
        catch (error) {
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
    async loadFromDatabase() {
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
                const chunk = {
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
        }
        catch (error) {
            console.error('Error loading from database:', error);
            throw error;
        }
    }
    /**
     * Get the storage path for the extension
     */
    getStoragePath() {
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
    async dispose() {
        // Clear auto-save interval
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
        // Save any pending changes
        if (this.isDirty && this.db) {
            try {
                await this.saveToDatabase();
            }
            catch (error) {
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
exports.PersistentVectorStore = PersistentVectorStore;
//# sourceMappingURL=persistentVectorStore.js.map