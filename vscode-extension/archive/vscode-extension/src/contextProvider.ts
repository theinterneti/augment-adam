import * as path from 'path';
import * as vscode from 'vscode';
import { ContextEngine } from './context/contextEngine';

// Create a singleton instance of the context engine
const contextEngine = new ContextEngine();

export interface CodeContext {
  selectedCode: string;
  fullDocumentText: string;
  fileName: string;
  fileExtension: string;
  language: string;
  selection: vscode.Selection | null;
  visibleRangeText: string;
  projectContext?: string;
}

export async function getEditorContext(): Promise<CodeContext | null> {
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

export async function getProjectContext(query: string = '', maxTokens: number = 4000): Promise<string> {
  try {
    // Initialize the context engine if it hasn't been initialized yet
    if (!contextEngine) {
      return "Context engine not available";
    }

    // Get context from the context engine
    return await contextEngine.getContext(query, maxTokens);
  } catch (error) {
    console.error('Error getting project context:', error);
    return `Error getting project context: ${error instanceof Error ? error.message : String(error)}`;
  }
}

export async function getContextForFile(filePath: string, maxTokens: number = 4000): Promise<string> {
  try {
    // Initialize the context engine if it hasn't been initialized yet
    if (!contextEngine) {
      return "Context engine not available";
    }

    // Get context for the file
    return await contextEngine.getContextForFile(filePath, maxTokens);
  } catch (error) {
    console.error('Error getting file context:', error);
    return `Error getting file context: ${error instanceof Error ? error.message : String(error)}`;
  }
}

export async function getContextForSymbol(symbol: string, maxTokens: number = 4000): Promise<string> {
  try {
    // Initialize the context engine if it hasn't been initialized yet
    if (!contextEngine) {
      return "Context engine not available";
    }

    // Get context for the symbol
    return await contextEngine.getContextForSymbol(symbol, maxTokens);
  } catch (error) {
    console.error('Error getting symbol context:', error);
    return `Error getting symbol context: ${error instanceof Error ? error.message : String(error)}`;
  }
}

export async function initializeContextEngine(): Promise<void> {
  try {
    await contextEngine.initialize();
  } catch (error) {
    console.error('Error initializing context engine:', error);
  }
}

export async function disposeContextEngine(): Promise<void> {
  try {
    await contextEngine.dispose();
  } catch (error) {
    console.error('Error disposing context engine:', error);
  }
}
