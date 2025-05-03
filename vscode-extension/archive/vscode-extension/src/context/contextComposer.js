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
exports.ContextComposer = void 0;
const path = __importStar(require("path"));
class ContextComposer {
    constructor() {
        this.MAX_TOKENS_PER_CHUNK = 1000;
    }
    async composeContext(query, relevantChunks, tokenLimit = 4000) {
        // Sort chunks by relevance (assuming they're already sorted)
        // Group chunks by file
        const chunksByFile = {};
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
        const allSymbols = new Set();
        const allImports = new Set();
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
    estimateTokens(text) {
        // A very rough estimate: 1 token ≈ 4 characters
        return Math.ceil(text.length / 4);
    }
}
exports.ContextComposer = ContextComposer;
//# sourceMappingURL=contextComposer.js.map