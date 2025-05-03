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
exports.QwenResponsePanel = void 0;
const vscode = __importStar(require("vscode"));
const responseFormatter_1 = require("../responseFormatter");
class QwenResponsePanel {
    static createOrShow(extensionUri, title = 'Qwen Coder Response') {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        // If we already have a panel, show it
        if (QwenResponsePanel.currentPanel) {
            QwenResponsePanel.currentPanel._panel.reveal(column);
            QwenResponsePanel.currentPanel._panel.title = title;
            return QwenResponsePanel.currentPanel;
        }
        // Otherwise, create a new panel
        const panel = vscode.window.createWebviewPanel('qwenResponse', title, column || vscode.ViewColumn.Beside, {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(extensionUri, 'media')
            ],
            retainContextWhenHidden: true
        });
        QwenResponsePanel.currentPanel = new QwenResponsePanel(panel, extensionUri);
        return QwenResponsePanel.currentPanel;
    }
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        // Set the webview's initial html content
        this._update('');
        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'copy':
                    vscode.env.clipboard.writeText(message.text);
                    vscode.window.showInformationMessage('Code copied to clipboard');
                    break;
                case 'insert':
                    (0, responseFormatter_1.insertCodeIntoEditor)(message.text);
                    vscode.window.showInformationMessage('Code inserted into editor');
                    break;
            }
        }, null, this._disposables);
    }
    dispose() {
        QwenResponsePanel.currentPanel = undefined;
        // Clean up our resources
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
    setContent(content) {
        this._update(content);
    }
    /**
     * Append content to the existing content (for streaming)
     * @param chunk The content chunk to append
     * @param isComplete Whether this is the final chunk
     */
    appendContent(chunk, isComplete) {
        // Send a message to the webview to append content
        this._panel.webview.postMessage({
            command: 'append',
            text: chunk,
            isComplete
        });
    }
    _update(content) {
        const webview = this._panel.webview;
        // Get paths to resources
        const cssUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css'));
        const highlightJsUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'highlight.js'));
        // Create HTML content
        this._panel.webview.html = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="${cssUri}">
        <title>Qwen Coder Response</title>
      </head>
      <body>
        <div id="response-container" class="response-container">
          ${this._formatMarkdown(content)}
        </div>
        <script src="${highlightJsUri}"></script>
        <script>
          const vscode = acquireVsCodeApi();
          let currentMarkdown = '';
          let isProcessingStream = false;
          const responseContainer = document.getElementById('response-container');

          // Listen for messages from the extension
          window.addEventListener('message', event => {
            const message = event.data;

            switch (message.command) {
              case 'append':
                // Handle streaming content
                currentMarkdown += message.text;
                responseContainer.innerHTML = formatMarkdown(currentMarkdown);

                // Apply syntax highlighting and add buttons to code blocks
                applyCodeFormatting();

                // If this is the final chunk, do any final processing
                if (message.isComplete) {
                  isProcessingStream = false;
                  // Final formatting pass
                  responseContainer.innerHTML = formatMarkdown(currentMarkdown);
                  applyCodeFormatting();
                }

                // Scroll to bottom to show new content
                window.scrollTo(0, document.body.scrollHeight);
                break;
            }
          });

          // Function to format markdown text to HTML
          function formatMarkdown(text) {
            if (!text) {
              return '<p>No response yet...</p>';
            }

            // Replace code blocks
            let html = text.replace(/\`\`\`(\w+)?\n([\s\S]*?)\`\`\`/g, (_, lang, code) => {
              return \`<pre><code class="language-\${lang || 'text'}">\${escapeHtml(code)}</code></pre>\`;
            });

            // Replace inline code
            html = html.replace(/\`([^\`]+)\`/g, '<code>$1</code>');

            // Replace headers
            html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');

            // Replace lists
            html = html.replace(/^\* (.*$)/gm, '<ul><li>$1</li></ul>');
            html = html.replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>');
            html = html.replace(/^(\d+)\. (.*$)/gm, '<ol><li>$2</li></ol>');

            // Replace paragraphs
            html = html.replace(/^(?!<[hou]).+$/gm, '<p>$&</p>');

            // Fix nested lists
            html = html.replace(/<\/ul>\s*<ul>/g, '');
            html = html.replace(/<\/ol>\s*<ol>/g, '');

            return html;
          }

          // Function to escape HTML special characters
          function escapeHtml(text) {
            return text
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
          }

          // Function to apply syntax highlighting and add buttons to code blocks
          function applyCodeFormatting() {
            // Apply syntax highlighting to code blocks
            document.querySelectorAll('pre code').forEach((codeBlock) => {
              const language = codeBlock.className.replace('language-', '');
              if (language && language !== 'text') {
                const originalCode = codeBlock.textContent;
                try {
                  codeBlock.innerHTML = window.HighlightJS.highlight(originalCode, language);
                } catch (e) {
                  console.error('Error highlighting code:', e);
                }
              }
            });

            // Add copy and insert buttons to code blocks that don't already have them
            document.querySelectorAll('pre:not(.processed)').forEach((pre) => {
              pre.classList.add('processed');

              const container = document.createElement('div');
              container.className = 'code-block-container';
              pre.parentNode.insertBefore(container, pre);
              container.appendChild(pre);

              const copyButton = document.createElement('button');
              copyButton.className = 'copy-button';
              copyButton.textContent = 'Copy';
              copyButton.addEventListener('click', () => {
                const code = pre.textContent;
                vscode.postMessage({
                  command: 'copy',
                  text: code
                });
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                  copyButton.textContent = 'Copy';
                }, 2000);
              });

              const insertButton = document.createElement('button');
              insertButton.className = 'insert-button';
              insertButton.textContent = 'Insert';
              insertButton.addEventListener('click', () => {
                const code = pre.textContent;
                vscode.postMessage({
                  command: 'insert',
                  text: code
                });
              });

              container.appendChild(copyButton);
              container.appendChild(insertButton);
            });
          }

          // Initial formatting for any content that's already there
          applyCodeFormatting();
        </script>
      </body>
      </html>
    `;
    }
    _formatMarkdown(text) {
        if (!text) {
            return '<p>No response yet...</p>';
        }
        // Replace code blocks
        let html = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
            return `<pre><code class="language-${lang || 'text'}">${this._escapeHtml(code)}</code></pre>`;
        });
        // Replace inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Replace headers
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        // Replace lists
        html = html.replace(/^\* (.*$)/gm, '<ul><li>$1</li></ul>');
        html = html.replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>');
        html = html.replace(/^(\d+)\. (.*$)/gm, '<ol><li>$2</li></ol>');
        // Replace paragraphs
        html = html.replace(/^(?!<[hou]).+$/gm, '<p>$&</p>');
        // Fix nested lists
        html = html.replace(/<\/ul>\s*<ul>/g, '');
        html = html.replace(/<\/ol>\s*<ol>/g, '');
        return html;
    }
    _escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
exports.QwenResponsePanel = QwenResponsePanel;
//# sourceMappingURL=panel.js.map