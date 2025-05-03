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
exports.getEditorContext = getEditorContext;
exports.getProjectContext = getProjectContext;
exports.getContextForFile = getContextForFile;
exports.getContextForSymbol = getContextForSymbol;
exports.initializeContextEngine = initializeContextEngine;
exports.disposeContextEngine = disposeContextEngine;
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const contextEngine_1 = require("./context/contextEngine");
// Create a singleton instance of the context engine
const contextEngine = new contextEngine_1.ContextEngine();
async function getEditorContext() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return null;
    }
    const document = editor.document;
    const selection = editor.selection;
    const selectedText = document.getText(selection);
    const fullText = document.getText();
    const fileName = path.basename(document.fileName);
    const fileExtension = path.extname(document.fileName).substring(1);
    const language = document.languageId;
    // Get visible range text
    const visibleRanges = editor.visibleRanges;
    let visibleText = '';
    for (const range of visibleRanges) {
        visibleText += document.getText(range) + '\n';
    }
    return {
        selectedCode: selectedText,
        fullDocumentText: fullText,
        fileName,
        fileExtension,
        language,
        selection: selection.isEmpty ? null : selection,
        visibleRangeText: visibleText
    };
}
async function getProjectContext(query = '', maxTokens = 4000) {
    try {
        // Initialize the context engine if it hasn't been initialized yet
        if (!contextEngine) {
            return "Context engine not available";
        }
        // Get context from the context engine
        return await contextEngine.getContext(query, maxTokens);
    }
    catch (error) {
        console.error('Error getting project context:', error);
        return `Error getting project context: ${error instanceof Error ? error.message : String(error)}`;
    }
}
async function getContextForFile(filePath, maxTokens = 4000) {
    try {
        // Initialize the context engine if it hasn't been initialized yet
        if (!contextEngine) {
            return "Context engine not available";
        }
        // Get context for the file
        return await contextEngine.getContextForFile(filePath, maxTokens);
    }
    catch (error) {
        console.error('Error getting file context:', error);
        return `Error getting file context: ${error instanceof Error ? error.message : String(error)}`;
    }
}
async function getContextForSymbol(symbol, maxTokens = 4000) {
    try {
        // Initialize the context engine if it hasn't been initialized yet
        if (!contextEngine) {
            return "Context engine not available";
        }
        // Get context for the symbol
        return await contextEngine.getContextForSymbol(symbol, maxTokens);
    }
    catch (error) {
        console.error('Error getting symbol context:', error);
        return `Error getting symbol context: ${error instanceof Error ? error.message : String(error)}`;
    }
}
async function initializeContextEngine() {
    try {
        await contextEngine.initialize();
    }
    catch (error) {
        console.error('Error initializing context engine:', error);
    }
}
async function disposeContextEngine() {
    try {
        await contextEngine.dispose();
    }
    catch (error) {
        console.error('Error disposing context engine:', error);
    }
}
//# sourceMappingURL=contextProvider.js.map