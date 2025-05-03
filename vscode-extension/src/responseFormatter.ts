import * as vscode from 'vscode';

export interface FormattedResponse {
  markdown: string;
  codeBlocks: { language: string; code: string }[];
}

export function formatResponse(response: string): FormattedResponse {
  // Extract code blocks from the response
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const codeBlocks: { language: string; code: string }[] = [];

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

export function insertCodeIntoEditor(code: string, editor?: vscode.TextEditor): void {
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
    } else {
      editBuilder.replace(selection, code);
    }
  });
}

export function showResponseInPanel(response: string, context: vscode.ExtensionContext): void {
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
export function showStreamingResponseInPanel(
  context: vscode.ExtensionContext,
  onPanelReady: (streamHandler: (chunk: string, isComplete: boolean) => void) => void
): void {
  // Import the QwenResponsePanel class to use its functionality
  const { QwenResponsePanel } = require('./webview/panel');

  // Create or show the panel
  const panel = QwenResponsePanel.createOrShow(context.extensionUri, 'Qwen Coder Response (Streaming)');

  // Set initial empty content
  panel.setContent('');

  // Create a streaming handler function
  const streamHandler = (chunk: string, isComplete: boolean) => {
    panel.appendContent(chunk, isComplete);
  };

  // Call the callback with the streaming handler
  onPanelReady(streamHandler);
}


