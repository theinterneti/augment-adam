import { CodeChunk } from './types';
import * as path from 'path';

export class ContextComposer {
  private readonly MAX_TOKENS_PER_CHUNK = 1000;
  
  public async composeContext(query: string, relevantChunks: CodeChunk[], tokenLimit: number = 4000): Promise<string> {
    // Sort chunks by relevance (assuming they're already sorted)
    // Group chunks by file
    const chunksByFile: { [filePath: string]: CodeChunk[] } = {};
    for (const chunk of relevantChunks) {
      if (!chunksByFile[chunk.filePath]) {
        chunksByFile[chunk.filePath] = [];
      }
      chunksByFile[chunk.filePath].push(chunk);
    }
    
    // Sort chunks within each file by line number
    for (const filePath in chunksByFile) {
      chunksByFile[filePath].sort((a, b) => a.startLine - b.startLine);
    }
    
    // Compose context
    let context = `Query: ${query}\n\n`;
    let tokenCount = this.estimateTokens(context);
    
    // Add file contexts until we reach the token limit
    for (const filePath in chunksByFile) {
      const fileName = path.basename(filePath);
      const fileContext = `File: ${fileName} (${filePath})\n`;
      tokenCount += this.estimateTokens(fileContext);
      
      if (tokenCount > tokenLimit) {
        break;
      }
      
      context += fileContext;
      
      // Add chunks from this file
      for (const chunk of chunksByFile[filePath]) {
        const chunkHeader = `Lines ${chunk.startLine}-${chunk.endLine}:\n`;
        const chunkContent = chunk.content;
        const chunkTokens = this.estimateTokens(chunkHeader + chunkContent);
        
        if (tokenCount + chunkTokens > tokenLimit) {
          // If adding this chunk would exceed the token limit, skip it
          continue;
        }
        
        context += chunkHeader + chunkContent + '\n\n';
        tokenCount += chunkTokens;
      }
      
      context += '\n';
    }
    
    // Add a summary of symbols found in the context
    const allSymbols = new Set<string>();
    const allImports = new Set<string>();
    
    for (const chunk of relevantChunks) {
      chunk.symbols.forEach(symbol => allSymbols.add(symbol));
      chunk.imports.forEach(imp => allImports.add(imp));
    }
    
    const symbolSummary = `Symbols: ${Array.from(allSymbols).join(', ')}\n`;
    const importSummary = `Imports: ${Array.from(allImports).join(', ')}\n`;
    
    if (tokenCount + this.estimateTokens(symbolSummary + importSummary) <= tokenLimit) {
      context += '\nSummary:\n' + symbolSummary + importSummary;
    }
    
    return context;
  }
  
  private estimateTokens(text: string): number {
    // A very rough estimate: 1 token ≈ 4 characters
    return Math.ceil(text.length / 4);
  }
}
