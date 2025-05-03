"use strict";
/**
 * Context Gatherer for MCP Servers
 *
 * Gathers context from MCP servers to provide to Qwen
 */
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
exports.ContextGatherer = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Context Gatherer class
 */
class ContextGatherer {
    /**
     * Constructor
     * @param mcpClient MCP client
     */
    constructor(mcpClient) {
        this.mcpClient = mcpClient;
        this.outputChannel = vscode.window.createOutputChannel('MCP Context Gatherer');
    }
    /**
     * Gather context from MCP servers
     * @param userMessage User message
     * @returns Context messages
     */
    async gatherContext(userMessage) {
        try {
            this.outputChannel.appendLine(`Gathering context for message: ${userMessage.substring(0, 100)}...`);
            const contextMessages = [];
            // Get available tools
            const tools = await this.mcpClient.getAllTools();
            // Get workspace context if available
            const workspaceContext = await this.getWorkspaceContext();
            if (workspaceContext) {
                contextMessages.push({
                    role: 'system',
                    content: `Workspace context:\n${workspaceContext}`
                });
            }
            // Get git context if available
            const gitContext = await this.getGitContext();
            if (gitContext) {
                contextMessages.push({
                    role: 'system',
                    content: `Git context:\n${gitContext}`
                });
            }
            // Get file context if available
            const fileContext = await this.getFileContext(userMessage);
            if (fileContext) {
                contextMessages.push({
                    role: 'system',
                    content: `File context:\n${fileContext}`
                });
            }
            this.outputChannel.appendLine(`Gathered ${contextMessages.length} context messages`);
            return contextMessages;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error gathering context: ${error}`);
            return [];
        }
    }
    /**
     * Get workspace context
     * @returns Workspace context
     */
    async getWorkspaceContext() {
        try {
            // Check if we have a filesystem tool
            const filesystemTool = await this.mcpClient.findTool('filesystem');
            if (!filesystemTool) {
                return null;
            }
            // Get workspace folders
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                return null;
            }
            // Get workspace root
            const workspaceRoot = workspaceFolders[0].uri.fsPath;
            // Get workspace structure
            const result = await this.mcpClient.callFunction(filesystemTool.serverId, 'filesystem', 'listDirectory', { path: workspaceRoot, recursive: false, maxDepth: 2 });
            if (result.status === 'error' || !result.result) {
                return null;
            }
            // Format workspace structure
            const files = result.result.files || [];
            const directories = result.result.directories || [];
            let context = `Workspace root: ${workspaceRoot}\n\n`;
            context += 'Directories:\n';
            context += directories.map((dir) => `- ${dir}`).join('\n');
            context += '\n\nFiles:\n';
            context += files.map((file) => `- ${file}`).join('\n');
            return context;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error getting workspace context: ${error}`);
            return null;
        }
    }
    /**
     * Get git context
     * @returns Git context
     */
    async getGitContext() {
        try {
            // Check if we have a git tool
            const gitTool = await this.mcpClient.findTool('git');
            if (!gitTool) {
                return null;
            }
            // Get current branch
            const branchResult = await this.mcpClient.callFunction(gitTool.serverId, 'git', 'getCurrentBranch', {});
            if (branchResult.status === 'error' || !branchResult.result) {
                return null;
            }
            // Get status
            const statusResult = await this.mcpClient.callFunction(gitTool.serverId, 'git', 'getStatus', {});
            if (statusResult.status === 'error' || !statusResult.result) {
                return null;
            }
            // Format git context
            let context = `Current branch: ${branchResult.result}\n\n`;
            context += 'Git status:\n';
            const status = statusResult.result;
            if (status.modified && status.modified.length > 0) {
                context += 'Modified files:\n';
                context += status.modified.map((file) => `- ${file}`).join('\n');
                context += '\n\n';
            }
            if (status.added && status.added.length > 0) {
                context += 'Added files:\n';
                context += status.added.map((file) => `- ${file}`).join('\n');
                context += '\n\n';
            }
            if (status.deleted && status.deleted.length > 0) {
                context += 'Deleted files:\n';
                context += status.deleted.map((file) => `- ${file}`).join('\n');
                context += '\n\n';
            }
            return context;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error getting git context: ${error}`);
            return null;
        }
    }
    /**
     * Get file context
     * @param userMessage User message
     * @returns File context
     */
    async getFileContext(userMessage) {
        try {
            // Check if we have a filesystem tool
            const filesystemTool = await this.mcpClient.findTool('filesystem');
            if (!filesystemTool) {
                return null;
            }
            // Get active editor
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return null;
            }
            // Get file path
            const filePath = editor.document.uri.fsPath;
            // Get file content
            const result = await this.mcpClient.callFunction(filesystemTool.serverId, 'filesystem', 'readFile', { path: filePath });
            if (result.status === 'error' || !result.result) {
                return null;
            }
            // Get file content
            const content = result.result.content || '';
            // Get selection if any
            let selection = '';
            if (!editor.selection.isEmpty) {
                selection = editor.document.getText(editor.selection);
            }
            // Format file context
            let context = `Active file: ${filePath}\n\n`;
            if (selection) {
                context += 'Selected text:\n```\n';
                context += selection;
                context += '\n```\n\n';
            }
            // Only include file content if it's not too large
            if (content.length < 10000) {
                context += 'File content:\n```\n';
                context += content;
                context += '\n```';
            }
            else {
                context += 'File content is too large to include in context.';
            }
            return context;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error getting file context: ${error}`);
            return null;
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this.outputChannel.dispose();
    }
}
exports.ContextGatherer = ContextGatherer;
//# sourceMappingURL=contextGatherer.js.map