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
exports.ConversationTreeItem = exports.ConversationHistoryProvider = exports.ConversationHistoryManager = void 0;
exports.registerConversationHistoryView = registerConversationHistoryView;
exports.saveToHistory = saveToHistory;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
/**
 * Manages conversation history for the extension
 */
class ConversationHistoryManager {
    constructor(context) {
        this.conversations = [];
        this.MAX_HISTORY_ITEMS = 50;
        this.storageUri = context.globalStorageUri;
        this.loadConversations();
    }
    /**
     * Get the singleton instance of the conversation history manager
     */
    static getInstance(context) {
        if (!ConversationHistoryManager.instance) {
            ConversationHistoryManager.instance = new ConversationHistoryManager(context);
        }
        return ConversationHistoryManager.instance;
    }
    /**
     * Add a new conversation to the history
     */
    addConversation(prompt, response, systemPrompt) {
        // Generate a title from the prompt (first line or first few words)
        const title = this.generateTitle(prompt);
        // Create a new conversation entry
        const entry = {
            id: Date.now().toString(),
            title,
            timestamp: Date.now(),
            prompt,
            response,
            systemPrompt
        };
        // Add to the beginning of the array
        this.conversations.unshift(entry);
        // Limit the number of conversations
        if (this.conversations.length > this.MAX_HISTORY_ITEMS) {
            this.conversations = this.conversations.slice(0, this.MAX_HISTORY_ITEMS);
        }
        // Save the updated conversations
        this.saveConversations();
        return entry;
    }
    /**
     * Get all conversations
     */
    getConversations() {
        return [...this.conversations];
    }
    /**
     * Get a conversation by ID
     */
    getConversation(id) {
        return this.conversations.find(c => c.id === id);
    }
    /**
     * Delete a conversation by ID
     */
    deleteConversation(id) {
        const initialLength = this.conversations.length;
        this.conversations = this.conversations.filter(c => c.id !== id);
        if (this.conversations.length !== initialLength) {
            this.saveConversations();
            return true;
        }
        return false;
    }
    /**
     * Clear all conversations
     */
    clearConversations() {
        this.conversations = [];
        this.saveConversations();
    }
    /**
     * Generate a title from the prompt
     */
    generateTitle(prompt) {
        // Use the first line if it's short enough
        const firstLine = prompt.split('\n')[0].trim();
        if (firstLine.length <= 50) {
            return firstLine;
        }
        // Otherwise use the first few words
        return firstLine.substring(0, 47) + '...';
    }
    /**
     * Load conversations from storage
     */
    loadConversations() {
        try {
            if (!this.storageUri) {
                return;
            }
            // Create the storage directory if it doesn't exist
            const dirPath = this.storageUri.fsPath;
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
            }
            const filePath = path.join(dirPath, 'conversations.json');
            if (fs.existsSync(filePath)) {
                const data = fs.readFileSync(filePath, 'utf8');
                this.conversations = JSON.parse(data);
            }
        }
        catch (error) {
            console.error('Error loading conversations:', error);
            this.conversations = [];
        }
    }
    /**
     * Save conversations to storage
     */
    saveConversations() {
        try {
            if (!this.storageUri) {
                return;
            }
            // Create the storage directory if it doesn't exist
            const dirPath = this.storageUri.fsPath;
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
            }
            const filePath = path.join(dirPath, 'conversations.json');
            fs.writeFileSync(filePath, JSON.stringify(this.conversations, null, 2), 'utf8');
        }
        catch (error) {
            console.error('Error saving conversations:', error);
        }
    }
}
exports.ConversationHistoryManager = ConversationHistoryManager;
/**
 * Tree data provider for conversation history
 */
class ConversationHistoryProvider {
    constructor(historyManager) {
        this.historyManager = historyManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            return Promise.resolve([]);
        }
        else {
            const conversations = this.historyManager.getConversations();
            return Promise.resolve(conversations.map(conversation => new ConversationTreeItem(conversation)));
        }
    }
}
exports.ConversationHistoryProvider = ConversationHistoryProvider;
/**
 * Tree item for a conversation
 */
class ConversationTreeItem extends vscode.TreeItem {
    constructor(conversation) {
        super(conversation.title, vscode.TreeItemCollapsibleState.None);
        this.conversation = conversation;
        // Format the date
        const date = new Date(conversation.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        this.tooltip = `${conversation.title}\n${formattedDate}`;
        this.description = formattedDate;
        this.contextValue = 'conversation';
        // Set the command to open the conversation
        this.command = {
            command: 'qwen-coder-assistant.openConversation',
            title: 'Open Conversation',
            arguments: [conversation]
        };
    }
}
exports.ConversationTreeItem = ConversationTreeItem;
/**
 * Register the conversation history view
 */
function registerConversationHistoryView(context) {
    // Create the history manager
    const historyManager = ConversationHistoryManager.getInstance(context);
    // Create the tree data provider
    const treeDataProvider = new ConversationHistoryProvider(historyManager);
    // Register the tree view
    const treeView = vscode.window.createTreeView('qwenConversationHistory', {
        treeDataProvider,
        showCollapseAll: false
    });
    // Register the refresh command
    const refreshCommand = vscode.commands.registerCommand('qwen-coder-assistant.refreshConversationHistory', () => {
        treeDataProvider.refresh();
    });
    // Register the open conversation command
    const openConversationCommand = vscode.commands.registerCommand('qwen-coder-assistant.openConversation', (conversation) => {
        // Import the QwenResponsePanel class to use its functionality
        const { QwenResponsePanel } = require('./webview/panel');
        // Create or show the panel
        const panel = QwenResponsePanel.createOrShow(context.extensionUri, `Conversation: ${conversation.title}`);
        // Format the conversation for display
        const content = `# ${conversation.title}\n\n## Prompt\n\n${conversation.prompt}\n\n## Response\n\n${conversation.response}`;
        // Set the content
        panel.setContent(content);
    });
    // Register the delete conversation command
    const deleteConversationCommand = vscode.commands.registerCommand('qwen-coder-assistant.deleteConversation', async (item) => {
        const result = await vscode.window.showWarningMessage(`Are you sure you want to delete the conversation "${item.conversation.title}"?`, { modal: true }, 'Delete');
        if (result === 'Delete') {
            historyManager.deleteConversation(item.conversation.id);
            treeDataProvider.refresh();
        }
    });
    // Register the clear all conversations command
    const clearConversationsCommand = vscode.commands.registerCommand('qwen-coder-assistant.clearConversations', async () => {
        const result = await vscode.window.showWarningMessage('Are you sure you want to clear all conversations? This cannot be undone.', { modal: true }, 'Clear All');
        if (result === 'Clear All') {
            historyManager.clearConversations();
            treeDataProvider.refresh();
        }
    });
    // Add to subscriptions
    context.subscriptions.push(treeView, refreshCommand, openConversationCommand, deleteConversationCommand, clearConversationsCommand);
}
/**
 * Save a conversation to history
 */
function saveToHistory(context, prompt, response, systemPrompt) {
    const historyManager = ConversationHistoryManager.getInstance(context);
    historyManager.addConversation(prompt, response, systemPrompt);
    // Refresh the tree view
    vscode.commands.executeCommand('qwen-coder-assistant.refreshConversationHistory');
}
//# sourceMappingURL=conversationHistory.js.map