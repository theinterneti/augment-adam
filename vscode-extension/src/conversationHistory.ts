import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

/**
 * Represents a conversation entry in the history
 */
export interface ConversationEntry {
  id: string;
  title: string;
  timestamp: number;
  prompt: string;
  response: string;
  systemPrompt?: string;
}

/**
 * Manages conversation history for the extension
 */
export class ConversationHistoryManager {
  private static instance: ConversationHistoryManager;
  private conversations: ConversationEntry[] = [];
  private storageUri?: vscode.Uri;
  private readonly MAX_HISTORY_ITEMS = 50;

  private constructor(context: vscode.ExtensionContext) {
    this.storageUri = context.globalStorageUri;
    this.loadConversations();
  }

  /**
   * Get the singleton instance of the conversation history manager
   */
  public static getInstance(context: vscode.ExtensionContext): ConversationHistoryManager {
    if (!ConversationHistoryManager.instance) {
      ConversationHistoryManager.instance = new ConversationHistoryManager(context);
    }
    return ConversationHistoryManager.instance;
  }

  /**
   * Add a new conversation to the history
   */
  public addConversation(prompt: string, response: string, systemPrompt?: string): ConversationEntry {
    // Generate a title from the prompt (first line or first few words)
    const title = this.generateTitle(prompt);

    // Create a new conversation entry
    const entry: ConversationEntry = {
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
  public getConversations(): ConversationEntry[] {
    return [...this.conversations];
  }

  /**
   * Get a conversation by ID
   */
  public getConversation(id: string): ConversationEntry | undefined {
    return this.conversations.find(c => c.id === id);
  }

  /**
   * Delete a conversation by ID
   */
  public deleteConversation(id: string): boolean {
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
  public clearConversations(): void {
    this.conversations = [];
    this.saveConversations();
  }

  /**
   * Generate a title from the prompt
   */
  private generateTitle(prompt: string): string {
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
  private loadConversations(): void {
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
    } catch (error) {
      console.error('Error loading conversations:', error);
      this.conversations = [];
    }
  }

  /**
   * Save conversations to storage
   */
  private saveConversations(): void {
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
    } catch (error) {
      console.error('Error saving conversations:', error);
    }
  }
}

/**
 * Tree data provider for conversation history
 */
export class ConversationHistoryProvider implements vscode.TreeDataProvider<ConversationTreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<ConversationTreeItem | undefined | null | void> = new vscode.EventEmitter<ConversationTreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<ConversationTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

  constructor(private historyManager: ConversationHistoryManager) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ConversationTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: ConversationTreeItem): Thenable<ConversationTreeItem[]> {
    if (element) {
      return Promise.resolve([]);
    } else {
      const conversations = this.historyManager.getConversations();
      return Promise.resolve(
        conversations.map(conversation => new ConversationTreeItem(conversation))
      );
    }
  }
}

/**
 * Tree item for a conversation
 */
export class ConversationTreeItem extends vscode.TreeItem {
  constructor(public readonly conversation: ConversationEntry) {
    super(conversation.title, vscode.TreeItemCollapsibleState.None);

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

/**
 * Register the conversation history view
 */
export function registerConversationHistoryView(context: vscode.ExtensionContext): void {
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
  const refreshCommand = vscode.commands.registerCommand(
    'qwen-coder-assistant.refreshConversationHistory',
    () => {
      treeDataProvider.refresh();
    }
  );

  // Register the open conversation command
  const openConversationCommand = vscode.commands.registerCommand(
    'qwen-coder-assistant.openConversation',
    (conversation: ConversationEntry) => {
      // Import the QwenResponsePanel class to use its functionality
      const { QwenResponsePanel } = require('./webview/panel');

      // Create or show the panel
      const panel = QwenResponsePanel.createOrShow(
        context.extensionUri,
        `Conversation: ${conversation.title}`
      );

      // Format the conversation for display
      const content = `# ${conversation.title}\n\n## Prompt\n\n${conversation.prompt}\n\n## Response\n\n${conversation.response}`;

      // Set the content
      panel.setContent(content);
    }
  );

  // Register the delete conversation command
  const deleteConversationCommand = vscode.commands.registerCommand(
    'qwen-coder-assistant.deleteConversation',
    async (item: ConversationTreeItem) => {
      const result = await vscode.window.showWarningMessage(
        `Are you sure you want to delete the conversation "${item.conversation.title}"?`,
        { modal: true },
        'Delete'
      );

      if (result === 'Delete') {
        historyManager.deleteConversation(item.conversation.id);
        treeDataProvider.refresh();
      }
    }
  );

  // Register the clear all conversations command
  const clearConversationsCommand = vscode.commands.registerCommand(
    'qwen-coder-assistant.clearConversations',
    async () => {
      const result = await vscode.window.showWarningMessage(
        'Are you sure you want to clear all conversations? This cannot be undone.',
        { modal: true },
        'Clear All'
      );

      if (result === 'Clear All') {
        historyManager.clearConversations();
        treeDataProvider.refresh();
      }
    }
  );

  // Add to subscriptions
  context.subscriptions.push(
    treeView,
    refreshCommand,
    openConversationCommand,
    deleteConversationCommand,
    clearConversationsCommand
  );
}

/**
 * Save a conversation to history
 */
export function saveToHistory(
  context: vscode.ExtensionContext,
  prompt: string,
  response: string,
  systemPrompt?: string
): void {
  const historyManager = ConversationHistoryManager.getInstance(context);
  historyManager.addConversation(prompt, response, systemPrompt);

  // Refresh the tree view
  vscode.commands.executeCommand('qwen-coder-assistant.refreshConversationHistory');
}
