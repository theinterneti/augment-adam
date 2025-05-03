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
exports.FileIndexer = void 0;
const vscode = __importStar(require("vscode"));
const symbolExtractor_1 = require("./symbolExtractor");
class FileIndexer {
    constructor(symbolExtractor, embeddingService, vectorStore) {
        this.symbolExtractor = symbolExtractor;
        this.embeddingService = embeddingService;
        this.vectorStore = vectorStore;
        // Create status bar item
        this.indexingStatus = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        // Set up file watcher
        this.fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.*');
        this.fileWatcher.onDidChange(this.handleFileChange.bind(this));
        this.fileWatcher.onDidCreate(this.handleFileCreate.bind(this));
        this.fileWatcher.onDidDelete(this.handleFileDelete.bind(this));
    }
    /**
     * Index the entire workspace
     */
    async indexWorkspace() {
        this.indexingStatus.text = '$(sync~spin) Indexing workspace...';
        this.indexingStatus.show();
        try {
            // Expanded file pattern to include more languages
            const files = await vscode.workspace.findFiles('**/*.{js,ts,jsx,tsx,py,java,c,cpp,h,hpp,cs,go,rb,php,rs,swift,kt,html,css,scss,sass,json,yaml,yml,xml,md}', '{**/node_modules/**,**/dist/**,**/build/**,**/.git/**,**/venv/**,**/__pycache__/**}');
            let processedFiles = 0;
            const totalFiles = files.length;
            // Process files in batches to avoid blocking the UI
            const batchSize = 20;
            for (let i = 0; i < totalFiles; i += batchSize) {
                const batch = files.slice(i, i + batchSize);
                // Process batch in parallel
                await Promise.all(batch.map(file => this.indexFile(file)));
                processedFiles += batch.length;
                this.indexingStatus.text = `$(sync~spin) Indexing workspace... ${processedFiles}/${totalFiles}`;
                // Yield to the event loop to keep the UI responsive
                await new Promise(resolve => setTimeout(resolve, 0));
            }
            this.indexingStatus.text = `$(check) Workspace indexed (${totalFiles} files)`;
            setTimeout(() => {
                this.indexingStatus.hide();
            }, 3000);
        }
        catch (error) {
            this.indexingStatus.text = '$(error) Indexing failed';
            console.error('Error indexing workspace:', error);
        }
    }
    /**
     * Index a single file
     * @param uri File URI
     */
    async indexFile(uri) {
        try {
            // Get file path
            const filePath = uri.fsPath;
            // Try to detect language from file extension
            let language = symbolExtractor_1.SymbolExtractor.detectLanguageFromPath(filePath);
            // If we can't detect the language from the path, try to open the document
            if (!language) {
                try {
                    const document = await vscode.workspace.openTextDocument(uri);
                    language = document.languageId;
                }
                catch (e) {
                    // If we can't open the document, use a generic language
                    language = 'text';
                }
            }
            // Read file content
            let content;
            try {
                const document = await vscode.workspace.openTextDocument(uri);
                content = document.getText();
            }
            catch (e) {
                // If we can't open the document, skip this file
                console.warn(`Skipping file ${filePath}: Unable to read content`);
                return;
            }
            // Skip empty files or files that are too large
            if (content.length === 0) {
                console.log(`Skipping empty file: ${filePath}`);
                return;
            }
            if (content.length > 1000000) {
                console.log(`Skipping large file (${content.length} bytes): ${filePath}`);
                return;
            }
            // Skip binary files
            if (this.isBinaryContent(content)) {
                console.log(`Skipping binary file: ${filePath}`);
                return;
            }
            // Split file into chunks
            const chunks = this.chunkFile(content, filePath, language);
            // Process each chunk
            for (const chunk of chunks) {
                try {
                    // Extract symbols
                    const { symbols, imports, dependencies } = await this.symbolExtractor.extractSymbols(chunk.content, language);
                    chunk.symbols = symbols;
                    chunk.imports = imports;
                    // Generate embedding
                    chunk.embedding = await this.embeddingService.generateEmbedding(chunk.content);
                    // Add to vector store
                    await this.vectorStore.addChunk(chunk);
                }
                catch (chunkError) {
                    console.error(`Error processing chunk ${chunk.id}:`, chunkError);
                }
            }
        }
        catch (error) {
            console.error(`Error indexing file ${uri.fsPath}:`, error);
        }
    }
    /**
     * Check if content appears to be binary
     * @param content File content
     * @returns True if the content appears to be binary
     */
    isBinaryContent(content) {
        // Check for null bytes or a high percentage of non-printable characters
        if (content.includes('\0')) {
            return true;
        }
        // Check the first 1000 characters
        const sampleSize = Math.min(1000, content.length);
        const sample = content.substring(0, sampleSize);
        // Count non-printable characters
        let nonPrintableCount = 0;
        for (let i = 0; i < sample.length; i++) {
            const charCode = sample.charCodeAt(i);
            if ((charCode < 32 && charCode !== 9 && charCode !== 10 && charCode !== 13) || charCode > 126) {
                nonPrintableCount++;
            }
        }
        // If more than 10% of characters are non-printable, consider it binary
        return nonPrintableCount > sampleSize * 0.1;
    }
    /**
     * Split a file into chunks based on its content and language
     * @param content File content
     * @param filePath File path
     * @param language Language ID
     * @returns Array of code chunks
     */
    chunkFile(content, filePath, language) {
        const chunks = [];
        const lines = content.split('\n');
        // For very small files, use a single chunk
        if (lines.length <= 50) {
            chunks.push({
                id: `${filePath}:0-${lines.length}`,
                filePath,
                content,
                startLine: 0,
                endLine: lines.length,
                symbols: [],
                imports: [],
                language
            });
            return chunks;
        }
        // For medium-sized files, use a single chunk if it's not code
        if (lines.length <= 200 && this.isDataOrDocFile(language)) {
            chunks.push({
                id: `${filePath}:0-${lines.length}`,
                filePath,
                content,
                startLine: 0,
                endLine: lines.length,
                symbols: [],
                imports: [],
                language
            });
            return chunks;
        }
        // For larger files, use language-specific chunking
        switch (language) {
            case 'javascript':
            case 'typescript':
            case 'javascriptreact':
            case 'typescriptreact':
                return this.chunkJavaScriptFile(content, filePath, language, lines);
            case 'python':
                return this.chunkPythonFile(content, filePath, language, lines);
            case 'java':
            case 'csharp':
            case 'cpp':
            case 'c':
                return this.chunkCStyleFile(content, filePath, language, lines);
            default:
                return this.chunkGenericFile(content, filePath, language, lines);
        }
    }
    /**
     * Check if the file is a data or documentation file
     * @param language Language ID
     * @returns True if the file is a data or documentation file
     */
    isDataOrDocFile(language) {
        return ['json', 'yaml', 'xml', 'markdown', 'html', 'css', 'scss', 'sass'].includes(language);
    }
    /**
     * Chunk a JavaScript/TypeScript file
     */
    chunkJavaScriptFile(content, filePath, language, lines) {
        const chunks = [];
        let chunkStart = 0;
        let braceBalance = 0;
        let inFunction = false;
        let inClass = false;
        // Always include imports in the first chunk
        let importsEndLine = 0;
        for (let i = 0; i < Math.min(50, lines.length); i++) {
            if (lines[i].includes('import ') || lines[i].includes('require(')) {
                importsEndLine = i + 1;
            }
        }
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            // Track brace balance
            braceBalance += (line.match(/{/g) || []).length;
            braceBalance -= (line.match(/}/g) || []).length;
            // Detect function or class start
            if (!inFunction && !inClass) {
                if (line.includes('function ') || line.includes('=>') || line.includes('class ')) {
                    inFunction = line.includes('function ') || line.includes('=>');
                    inClass = line.includes('class ');
                }
            }
            // Check if we should end the current chunk
            const isBlockEnd = (braceBalance === 0 && (inFunction || inClass)) ||
                i === lines.length - 1;
            if (isBlockEnd || (i - chunkStart > 200)) {
                // Create a chunk
                const chunkEndLine = i + 1;
                const chunkContent = lines.slice(chunkStart, chunkEndLine).join('\n');
                // For the first chunk, include imports
                if (chunkStart === 0 && importsEndLine > 0 && chunkStart !== importsEndLine) {
                    const importsContent = lines.slice(0, importsEndLine).join('\n');
                    chunks.push({
                        id: `${filePath}:0-${importsEndLine}`,
                        filePath,
                        content: importsContent,
                        startLine: 0,
                        endLine: importsEndLine,
                        symbols: [],
                        imports: [],
                        language
                    });
                    // If the first chunk is just imports, continue to the next chunk
                    if (chunkEndLine <= importsEndLine) {
                        chunkStart = chunkEndLine;
                        inFunction = false;
                        inClass = false;
                        continue;
                    }
                }
                chunks.push({
                    id: `${filePath}:${chunkStart}-${chunkEndLine}`,
                    filePath,
                    content: chunkContent,
                    startLine: chunkStart,
                    endLine: chunkEndLine,
                    symbols: [],
                    imports: [],
                    language
                });
                chunkStart = chunkEndLine;
                inFunction = false;
                inClass = false;
            }
        }
        return chunks;
    }
    /**
     * Chunk a Python file
     */
    chunkPythonFile(content, filePath, language, lines) {
        const chunks = [];
        let chunkStart = 0;
        let indentLevel = 0;
        let inFunction = false;
        let inClass = false;
        // Always include imports in the first chunk
        let importsEndLine = 0;
        for (let i = 0; i < Math.min(50, lines.length); i++) {
            if (lines[i].includes('import ') || lines[i].includes('from ')) {
                importsEndLine = i + 1;
            }
        }
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmedLine = line.trim();
            // Skip empty lines and comments
            if (trimmedLine === '' || trimmedLine.startsWith('#')) {
                continue;
            }
            // Calculate indent level
            const currentIndent = line.length - line.trimStart().length;
            // Detect function or class start
            if (currentIndent === 0 && !inFunction && !inClass) {
                if (trimmedLine.startsWith('def ') || trimmedLine.startsWith('class ')) {
                    inFunction = trimmedLine.startsWith('def ');
                    inClass = trimmedLine.startsWith('class ');
                    indentLevel = currentIndent;
                }
            }
            // Check if we should end the current chunk
            const isBlockEnd = (currentIndent <= indentLevel && (inFunction || inClass) && i > chunkStart) ||
                i === lines.length - 1;
            if (isBlockEnd || (i - chunkStart > 200)) {
                // Create a chunk
                const chunkEndLine = i;
                const chunkContent = lines.slice(chunkStart, chunkEndLine).join('\n');
                // For the first chunk, include imports
                if (chunkStart === 0 && importsEndLine > 0 && chunkStart !== importsEndLine) {
                    const importsContent = lines.slice(0, importsEndLine).join('\n');
                    chunks.push({
                        id: `${filePath}:0-${importsEndLine}`,
                        filePath,
                        content: importsContent,
                        startLine: 0,
                        endLine: importsEndLine,
                        symbols: [],
                        imports: [],
                        language
                    });
                    // If the first chunk is just imports, continue to the next chunk
                    if (chunkEndLine <= importsEndLine) {
                        chunkStart = chunkEndLine;
                        inFunction = false;
                        inClass = false;
                        indentLevel = 0;
                        continue;
                    }
                }
                chunks.push({
                    id: `${filePath}:${chunkStart}-${chunkEndLine}`,
                    filePath,
                    content: chunkContent,
                    startLine: chunkStart,
                    endLine: chunkEndLine,
                    symbols: [],
                    imports: [],
                    language
                });
                chunkStart = chunkEndLine;
                inFunction = false;
                inClass = false;
                indentLevel = 0;
            }
        }
        // Handle the case where the file ends without a block end
        if (chunkStart < lines.length) {
            const chunkContent = lines.slice(chunkStart).join('\n');
            chunks.push({
                id: `${filePath}:${chunkStart}-${lines.length}`,
                filePath,
                content: chunkContent,
                startLine: chunkStart,
                endLine: lines.length,
                symbols: [],
                imports: [],
                language
            });
        }
        return chunks;
    }
    /**
     * Chunk a C-style file (Java, C#, C, C++)
     */
    chunkCStyleFile(content, filePath, language, lines) {
        const chunks = [];
        let chunkStart = 0;
        let braceBalance = 0;
        let inFunction = false;
        let inClass = false;
        // Always include imports/includes in the first chunk
        let importsEndLine = 0;
        for (let i = 0; i < Math.min(50, lines.length); i++) {
            if (lines[i].includes('import ') || lines[i].includes('#include ') ||
                lines[i].includes('using ') || lines[i].includes('package ')) {
                importsEndLine = i + 1;
            }
        }
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            // Track brace balance
            braceBalance += (line.match(/{/g) || []).length;
            braceBalance -= (line.match(/}/g) || []).length;
            // Detect function or class start
            if (!inFunction && !inClass && braceBalance === 0) {
                if ((line.includes('(') && line.includes(')') && !line.includes(';')) ||
                    line.includes('class ') || line.includes('interface ') ||
                    line.includes('struct ') || line.includes('enum ')) {
                    inFunction = line.includes('(') && line.includes(')') && !line.includes(';');
                    inClass = line.includes('class ') || line.includes('interface ') ||
                        line.includes('struct ') || line.includes('enum ');
                }
            }
            // Check if we should end the current chunk
            const isBlockEnd = (braceBalance === 0 && (inFunction || inClass) && i > chunkStart) ||
                i === lines.length - 1;
            if (isBlockEnd || (i - chunkStart > 200)) {
                // Create a chunk
                const chunkEndLine = i + 1;
                const chunkContent = lines.slice(chunkStart, chunkEndLine).join('\n');
                // For the first chunk, include imports
                if (chunkStart === 0 && importsEndLine > 0 && chunkStart !== importsEndLine) {
                    const importsContent = lines.slice(0, importsEndLine).join('\n');
                    chunks.push({
                        id: `${filePath}:0-${importsEndLine}`,
                        filePath,
                        content: importsContent,
                        startLine: 0,
                        endLine: importsEndLine,
                        symbols: [],
                        imports: [],
                        language
                    });
                    // If the first chunk is just imports, continue to the next chunk
                    if (chunkEndLine <= importsEndLine) {
                        chunkStart = chunkEndLine;
                        inFunction = false;
                        inClass = false;
                        braceBalance = 0;
                        continue;
                    }
                }
                chunks.push({
                    id: `${filePath}:${chunkStart}-${chunkEndLine}`,
                    filePath,
                    content: chunkContent,
                    startLine: chunkStart,
                    endLine: chunkEndLine,
                    symbols: [],
                    imports: [],
                    language
                });
                chunkStart = chunkEndLine;
                inFunction = false;
                inClass = false;
                braceBalance = 0;
            }
        }
        return chunks;
    }
    /**
     * Chunk a generic file (fallback for unsupported languages)
     */
    chunkGenericFile(content, filePath, language, lines) {
        const chunks = [];
        const maxChunkSize = 100; // lines
        // For data files, use larger chunks
        const chunkSize = this.isDataOrDocFile(language) ? 200 : maxChunkSize;
        for (let i = 0; i < lines.length; i += chunkSize) {
            const chunkEndLine = Math.min(i + chunkSize, lines.length);
            const chunkContent = lines.slice(i, chunkEndLine).join('\n');
            chunks.push({
                id: `${filePath}:${i}-${chunkEndLine}`,
                filePath,
                content: chunkContent,
                startLine: i,
                endLine: chunkEndLine,
                symbols: [],
                imports: [],
                language
            });
        }
        return chunks;
    }
    async handleFileChange(uri) {
        // Delete existing chunks for this file
        await this.deleteFileChunks(uri.fsPath);
        // Re-index the file
        await this.indexFile(uri);
    }
    async handleFileCreate(uri) {
        await this.indexFile(uri);
    }
    async handleFileDelete(uri) {
        await this.deleteFileChunks(uri.fsPath);
    }
    /**
     * Delete all chunks for a file
     * @param filePath File path
     */
    async deleteFileChunks(filePath) {
        try {
            // Get all chunks from the vector store
            const allChunks = await this.vectorStore.findSimilarChunks('', 10000);
            // Filter chunks for this file
            const fileChunks = allChunks.filter(chunk => chunk.filePath === filePath);
            // Delete each chunk
            for (const chunk of fileChunks) {
                await this.vectorStore.deleteChunk(chunk.id);
            }
            console.log(`Deleted ${fileChunks.length} chunks for file: ${filePath}`);
        }
        catch (error) {
            console.error(`Error deleting chunks for file ${filePath}:`, error);
        }
    }
    dispose() {
        this.fileWatcher.dispose();
        this.indexingStatus.dispose();
    }
}
exports.FileIndexer = FileIndexer;
//# sourceMappingURL=fileIndexer.js.map