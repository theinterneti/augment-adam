/**
 * A lightweight syntax highlighting library for code blocks in the webview
 */
class HighlightJS {
  constructor() {
    this.languages = {
      javascript: {
        keywords: [
          'const', 'let', 'var', 'function', 'class', 'extends', 'return', 'if', 'else', 'for', 'while', 'do',
          'switch', 'case', 'break', 'continue', 'new', 'try', 'catch', 'throw', 'finally', 'typeof', 'instanceof',
          'import', 'export', 'default', 'from', 'as', 'async', 'await', 'yield', 'this', 'super', 'null', 'undefined',
          'true', 'false'
        ],
        operators: ['=>', '===', '!==', '==', '!=', '>=', '<=', '>', '<', '+', '-', '*', '/', '%', '&&', '||', '!', '='],
        symbols: ['{', '}', '(', ')', '[', ']', ';', ',', '.', ':'],
        comments: {
          line: '//',
          block: { start: '/*', end: '*/' }
        },
        strings: ['"', "'", '`']
      },
      typescript: {
        keywords: [
          'const', 'let', 'var', 'function', 'class', 'extends', 'return', 'if', 'else', 'for', 'while', 'do',
          'switch', 'case', 'break', 'continue', 'new', 'try', 'catch', 'throw', 'finally', 'typeof', 'instanceof',
          'import', 'export', 'default', 'from', 'as', 'async', 'await', 'yield', 'this', 'super', 'null', 'undefined',
          'true', 'false', 'interface', 'type', 'namespace', 'enum', 'any', 'string', 'number', 'boolean', 'void',
          'readonly', 'private', 'protected', 'public', 'static', 'implements', 'abstract'
        ],
        operators: ['=>', '===', '!==', '==', '!=', '>=', '<=', '>', '<', '+', '-', '*', '/', '%', '&&', '||', '!', '='],
        symbols: ['{', '}', '(', ')', '[', ']', ';', ',', '.', ':', '<', '>'],
        comments: {
          line: '//',
          block: { start: '/*', end: '*/' }
        },
        strings: ['"', "'", '`']
      },
      python: {
        keywords: [
          'def', 'class', 'from', 'import', 'as', 'return', 'if', 'elif', 'else', 'for', 'while', 'break',
          'continue', 'try', 'except', 'finally', 'raise', 'assert', 'with', 'lambda', 'yield', 'pass',
          'None', 'True', 'False', 'and', 'or', 'not', 'is', 'in', 'global', 'nonlocal', 'del', 'async', 'await'
        ],
        operators: ['==', '!=', '>=', '<=', '>', '<', '+', '-', '*', '/', '%', '**', '//', '=', '+=', '-=', '*=', '/=', '%='],
        symbols: ['{', '}', '(', ')', '[', ']', ':', ',', '.'],
        comments: {
          line: '#',
          block: null
        },
        strings: ['"', "'", '"""', "'''"]
      }
    };
  }

  /**
   * Highlight code based on language
   * @param {string} code - The code to highlight
   * @param {string} language - The programming language
   * @returns {string} - HTML with syntax highlighting
   */
  highlight(code, language) {
    if (!code) return '';
    
    // Default to text if language not supported
    const lang = this.languages[language] || null;
    if (!lang) {
      return this.escapeHtml(code);
    }

    let result = '';
    let inComment = false;
    let inString = false;
    let stringChar = '';
    let currentToken = '';
    let i = 0;

    while (i < code.length) {
      const char = code[i];
      const nextChar = code[i + 1] || '';
      
      // Check for comments
      if (!inString && !inComment && lang.comments) {
        // Line comments
        if (lang.comments.line && char === lang.comments.line[0] && nextChar === lang.comments.line[1]) {
          const lineEnd = code.indexOf('\n', i);
          const commentText = lineEnd !== -1 ? code.substring(i, lineEnd) : code.substring(i);
          result += `<span class="hljs-comment">${this.escapeHtml(commentText)}</span>`;
          i += commentText.length;
          continue;
        }
        
        // Block comments
        if (lang.comments.block && 
            char === lang.comments.block.start[0] && 
            nextChar === lang.comments.block.start[1]) {
          const commentEnd = code.indexOf(lang.comments.block.end, i + 2);
          if (commentEnd !== -1) {
            const commentText = code.substring(i, commentEnd + lang.comments.block.end.length);
            result += `<span class="hljs-comment">${this.escapeHtml(commentText)}</span>`;
            i += commentText.length;
            continue;
          }
        }
      }

      // Check for strings
      if (!inComment && lang.strings) {
        if (inString) {
          currentToken += char;
          if (char === stringChar && code[i - 1] !== '\\') {
            result += `<span class="hljs-string">${this.escapeHtml(currentToken)}</span>`;
            inString = false;
            currentToken = '';
          }
          i++;
          continue;
        } else {
          for (const strChar of lang.strings) {
            if (char === strChar[0]) {
              if (strChar.length === 1 || 
                 (strChar.length > 1 && code.substring(i, i + strChar.length) === strChar)) {
                inString = true;
                stringChar = strChar;
                currentToken = char;
                if (strChar.length > 1) {
                  currentToken = strChar;
                  i += strChar.length;
                } else {
                  i++;
                }
                continue;
              }
            }
          }
        }
      }

      // If we're in a comment or string, continue to next character
      if (inComment || inString) {
        i++;
        continue;
      }

      // Check for whitespace
      if (/\s/.test(char)) {
        result += char;
        i++;
        continue;
      }

      // Build token
      currentToken = '';
      while (i < code.length && !/\s/.test(code[i]) && 
             !lang.symbols.includes(code[i]) && 
             !lang.operators.some(op => code.substring(i).startsWith(op))) {
        currentToken += code[i];
        i++;
      }

      // Check if token is a keyword
      if (currentToken && lang.keywords.includes(currentToken)) {
        result += `<span class="hljs-keyword">${currentToken}</span>`;
        continue;
      }

      // If token is not a keyword, add it as is
      if (currentToken) {
        result += this.escapeHtml(currentToken);
        continue;
      }

      // Check for operators
      let foundOperator = false;
      for (const op of lang.operators) {
        if (code.substring(i).startsWith(op)) {
          result += `<span class="hljs-operator">${this.escapeHtml(op)}</span>`;
          i += op.length;
          foundOperator = true;
          break;
        }
      }
      if (foundOperator) continue;

      // Check for symbols
      if (lang.symbols.includes(char)) {
        result += `<span class="hljs-symbol">${char}</span>`;
        i++;
        continue;
      }

      // Default case: just add the character
      result += this.escapeHtml(char);
      i++;
    }

    return result;
  }

  /**
   * Escape HTML special characters
   * @param {string} text - Text to escape
   * @returns {string} - Escaped text
   */
  escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Make available to the webview
window.HighlightJS = new HighlightJS();
