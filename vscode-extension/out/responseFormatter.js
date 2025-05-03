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
exports.formatResponse = formatResponse;
exports.insertCodeIntoEditor = insertCodeIntoEditor;
exports.showResponseInPanel = showResponseInPanel;
exports.showStreamingResponseInPanel = showStreamingResponseInPanel;
const vscode = __importStar(require("vscode"));
function formatResponse(response) {
    // Extract code blocks from the response
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const codeBlocks = [];
    let match;
    while ((match = codeBlockRegex.exec(response)) !== null) {
        const language = match[1] || 'text';
        const code = match[2];
        codeBlocks.push({ language, code });
    }
    return {
        markdown: response,
        codeBlocks
    };
}
function insertCodeIntoEditor(code, editor) {
    if (!editor) {
        editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }
    }
    const selection = editor.selection;
    editor.edit(editBuilder => {
        if (selection.isEmpty) {
            editBuilder.insert(selection.start, code);
        }
        else {
            editBuilder.replace(selection, code);
        }
    });
}
function showResponseInPanel(response, context) {
    // Import the QwenResponsePanel class to use its functionality
    const { QwenResponsePanel } = require('./webview/panel');
    // Create or show the panel
    const panel = QwenResponsePanel.createOrShow(context.extensionUri, 'Qwen Coder Response');
    // Set the content
    panel.setContent(response);
}
/**
 * Show a streaming response in a webview panel
 * @param context The extension context
 * @param onPanelReady Callback that receives the streaming handler function
 */
function showStreamingResponseInPanel(context, onPanelReady) {
    // Import the QwenResponsePanel class to use its functionality
    const { QwenResponsePanel } = require('./webview/panel');
    // Create or show the panel
    const panel = QwenResponsePanel.createOrShow(context.extensionUri, 'Qwen Coder Response (Streaming)');
    // Set initial empty content
    panel.setContent('');
    // Create a streaming handler function
    const streamHandler = (chunk, isComplete) => {
        panel.appendContent(chunk, isComplete);
    };
    // Call the callback with the streaming handler
    onPanelReady(streamHandler);
}
//# sourceMappingURL=responseFormatter.js.map