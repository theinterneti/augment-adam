
/**
 * Language-specific symbol extractor for code files.
 * Extracts symbols, imports, and dependencies from code content.
 */
export class SymbolExtractor {
  // Map of file extensions to language IDs
  private static readonly extensionToLanguage: Record<string, string> = {
    // JavaScript/TypeScript
    '.js': 'javascript',
    '.jsx': 'javascriptreact',
    '.ts': 'typescript',
    '.tsx': 'typescriptreact',
    // Python
    '.py': 'python',
    '.pyw': 'python',
    '.ipynb': 'python',
    // Java
    '.java': 'java',
    // C/C++
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    // C#
    '.cs': 'csharp',
    // Go
    '.go': 'go',
    // Ruby
    '.rb': 'ruby',
    // PHP
    '.php': 'php',
    // Rust
    '.rs': 'rust',
    // Swift
    '.swift': 'swift',
    // Kotlin
    '.kt': 'kotlin',
    // HTML/CSS
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    // Other
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown'
  };

  /**
   * Detect language from file extension
   * @param filePath Path to the file
   * @returns Language ID or undefined if not detected
   */
  public static detectLanguageFromPath(filePath: string): string | undefined {
    const extension = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
    return SymbolExtractor.extensionToLanguage[extension];
  }

  /**
   * Extract symbols, imports, and dependencies from code content
   * @param content Code content
   * @param language Language ID
   * @returns Object containing symbols, imports, and dependencies
   */
  public async extractSymbols(content: string, language: string): Promise<{
    symbols: string[];
    imports: string[];
    dependencies: string[];
  }> {
    const symbols: string[] = [];
    const imports: string[] = [];
    const dependencies: string[] = [];

    // Extract based on language
    switch (language) {
      // JavaScript family
      case 'javascript':
      case 'typescript':
      case 'javascriptreact':
      case 'typescriptreact':
        this.extractJavaScriptSymbols(content, symbols, imports, dependencies);
        break;

      // Python
      case 'python':
        this.extractPythonSymbols(content, symbols, imports, dependencies);
        break;

      // Java
      case 'java':
        this.extractJavaSymbols(content, symbols, imports, dependencies);
        break;

      // C/C++
      case 'c':
      case 'cpp':
        this.extractCppSymbols(content, symbols, imports, dependencies);
        break;

      // C#
      case 'csharp':
        this.extractCSharpSymbols(content, symbols, imports, dependencies);
        break;

      // Go
      case 'go':
        this.extractGoSymbols(content, symbols, imports, dependencies);
        break;

      // Ruby
      case 'ruby':
        this.extractRubySymbols(content, symbols, imports, dependencies);
        break;

      // PHP
      case 'php':
        this.extractPhpSymbols(content, symbols, imports, dependencies);
        break;

      // Rust
      case 'rust':
        this.extractRustSymbols(content, symbols, imports, dependencies);
        break;

      // Swift
      case 'swift':
        this.extractSwiftSymbols(content, symbols, imports, dependencies);
        break;

      // Kotlin
      case 'kotlin':
        this.extractKotlinSymbols(content, symbols, imports, dependencies);
        break;

      // HTML/CSS
      case 'html':
      case 'css':
      case 'scss':
      case 'sass':
        this.extractWebSymbols(content, symbols, imports, dependencies, language);
        break;

      // Data formats
      case 'json':
      case 'yaml':
      case 'xml':
        this.extractDataFormatSymbols(content, symbols, imports, dependencies, language);
        break;

      // Default fallback
      default:
        // Use regex-based fallback for unknown languages
        this.extractGenericSymbols(content, symbols, imports, dependencies);
    }

    // Remove duplicates
    return {
      symbols: [...new Set(symbols)],
      imports: [...new Set(imports)],
      dependencies: [...new Set(dependencies)]
    };
  }

  /**
   * Extract symbols from JavaScript/TypeScript code
   */
  private extractJavaScriptSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract function declarations (both regular and arrow functions)
    const functionRegex = /(?:function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)/g;
    let match;
    while ((match = functionRegex.exec(content)) !== null) {
      if (match[1]) {
        symbols.push(match[1]);
      } else if (match[2]) {
        symbols.push(match[2]);
      }
    }

    // Extract class declarations
    const classRegex = /class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/g;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract method declarations
    const methodRegex = /(?:async\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*{/g;
    while ((match = methodRegex.exec(content)) !== null) {
      // Filter out common keywords that might be matched
      const keywords = ['if', 'for', 'while', 'switch', 'catch'];
      if (!keywords.includes(match[1])) {
        symbols.push(match[1]);
      }
    }

    // Extract variable declarations
    const varRegex = /(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:[=;]|$)/g;
    while ((match = varRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract interface and type declarations (TypeScript)
    const typeRegex = /(?:interface|type)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/g;
    while ((match = typeRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract imports (ES modules)
    const importRegex = /import\s+(?:{([^}]*)}\s+from\s+['"]([^'"]+)['"]|.*?from\s+['"]([^'"]+)['"])/g;
    while ((match = importRegex.exec(content)) !== null) {
      // Extract the module path
      const modulePath = match[2] || match[3];
      if (modulePath) {
        imports.push(modulePath);
        dependencies.push(modulePath);
      }

      // Extract named imports if available
      if (match[1]) {
        const namedImports = match[1].split(',').map(s => s.trim());
        for (const namedImport of namedImports) {
          // Handle "as" aliases
          const importName = namedImport.split(' as ')[0].trim();
          if (importName) {
            symbols.push(importName);
          }
        }
      }
    }

    // Extract CommonJS requires
    const requireRegex = /(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*require\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
    while ((match = requireRegex.exec(content)) !== null) {
      symbols.push(match[1]); // The variable name
      imports.push(match[2]); // The module path
      dependencies.push(match[2]);
    }
  }

  /**
   * Extract symbols from Python code
   */
  private extractPythonSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract function declarations
    const functionRegex = /def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    let match;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract class declarations
    const classRegex = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(|:)/g;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract variable assignments (global level)
    const varRegex = /^([A-Z_][A-Z0-9_]*)\s*=/gm;
    while ((match = varRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract imports - from X import Y
    const fromImportRegex = /from\s+([a-zA-Z0-9_.]+)\s+import\s+([^#\n]+)/g;
    while ((match = fromImportRegex.exec(content)) !== null) {
      const module = match[1];
      imports.push(module);
      dependencies.push(module);

      // Extract imported symbols
      const importedSymbols = match[2].split(',').map(s => s.trim());
      for (const importedSymbol of importedSymbols) {
        // Handle "as" aliases
        const symbolName = importedSymbol.split(' as ')[0].trim();
        if (symbolName && symbolName !== '*') {
          symbols.push(symbolName);
        }
      }
    }

    // Extract imports - import X
    const importRegex = /import\s+([^#\n]+)/g;
    while ((match = importRegex.exec(content)) !== null) {
      const importedModules = match[1].split(',').map(s => s.trim());
      for (const importedModule of importedModules) {
        // Handle "as" aliases
        const moduleName = importedModule.split(' as ')[0].trim();
        if (moduleName) {
          imports.push(moduleName);
          dependencies.push(moduleName);

          // Also add the module name as a symbol (since it can be used directly)
          const alias = importedModule.includes(' as ')
            ? importedModule.split(' as ')[1].trim()
            : moduleName.split('.').pop() || '';
          if (alias) {
            symbols.push(alias);
          }
        }
      }
    }

    // Extract decorated functions and classes
    const decoratorRegex = /@[^\n]+\s+(?:def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = decoratorRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from Java code
   */
  private extractJavaSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class and interface declarations
    const classRegex = /(?:public|private|protected)?\s*(?:abstract|final)?\s*(?:class|interface|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract method declarations
    const methodRegex = /(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:<[^>]+>\s*)?(?:[a-zA-Z_][a-zA-Z0-9_.<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    while ((match = methodRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract field declarations
    const fieldRegex = /(?:public|private|protected)?\s*(?:static|final)?\s*(?:[a-zA-Z_][a-zA-Z0-9_.<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;)/g;
    while ((match = fieldRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract imports
    const importRegex = /import\s+([a-zA-Z0-9_.]+(?:\.[a-zA-Z0-9_*]+)*);/g;
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract package declaration
    const packageRegex = /package\s+([a-zA-Z0-9_.]+);/g;
    while ((match = packageRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from C/C++ code
   */
  private extractCppSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract function declarations
    const functionRegex = /(?:(?:static|inline|extern|const)\s+)*(?:[a-zA-Z_][a-zA-Z0-9_:]*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    let match;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract class/struct/enum declarations
    const classRegex = /(?:class|struct|enum|union)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract namespace declarations
    const namespaceRegex = /namespace\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = namespaceRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract #include directives
    const includeRegex = /#include\s+[<"]([^>"]+)[>"]/g;
    while ((match = includeRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract typedefs
    const typedefRegex = /typedef\s+(?:[a-zA-Z_][a-zA-Z0-9_:]*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = typedefRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract #define macros
    const defineRegex = /#define\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = defineRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from C# code
   */
  private extractCSharpSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class, interface, struct, enum declarations
    const classRegex = /(?:public|private|protected|internal)?\s*(?:abstract|sealed|static)?\s*(?:class|interface|struct|enum|record)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract method declarations
    const methodRegex = /(?:public|private|protected|internal)?\s*(?:static|virtual|abstract|override|sealed)?\s*(?:[a-zA-Z_][a-zA-Z0-9_.<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    while ((match = methodRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract property declarations
    const propertyRegex = /(?:public|private|protected|internal)?\s*(?:static|virtual|abstract|override|sealed)?\s*(?:[a-zA-Z_][a-zA-Z0-9_.<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{/g;
    while ((match = propertyRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract using directives
    const usingRegex = /using\s+([a-zA-Z0-9_.]+);/g;
    while ((match = usingRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract namespace declarations
    const namespaceRegex = /namespace\s+([a-zA-Z0-9_.]+)/g;
    while ((match = namespaceRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from Go code
   */
  private extractGoSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract function declarations
    const functionRegex = /func\s+(?:\([^)]*\)\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    let match;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract type declarations
    const typeRegex = /type\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:struct|interface|[a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = typeRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract const declarations
    const constRegex = /const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+/g;
    while ((match = constRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract var declarations
    const varRegex = /var\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+/g;
    while ((match = varRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract imports
    const importRegex = /import\s+(?:\(\s*((?:[^)]+))\s*\)|["']([^"']+)["'])/g;
    while ((match = importRegex.exec(content)) !== null) {
      if (match[1]) {
        // Multi-line import
        const importLines = match[1].split('\n');
        for (const line of importLines) {
          const importMatch = line.match(/["']([^"']+)["']/);
          if (importMatch) {
            imports.push(importMatch[1]);
            dependencies.push(importMatch[1]);
          }
        }
      } else if (match[2]) {
        // Single import
        imports.push(match[2]);
        dependencies.push(match[2]);
      }
    }

    // Extract package declaration
    const packageRegex = /package\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = packageRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from Ruby code
   */
  private extractRubySymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class declarations
    const classRegex = /class\s+([A-Z][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract module declarations
    const moduleRegex = /module\s+([A-Z][a-zA-Z0-9_]*)/g;
    while ((match = moduleRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract method declarations
    const methodRegex = /def\s+(?:self\.)?([a-zA-Z_][a-zA-Z0-9_?!]*)/g;
    while ((match = methodRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract constant declarations
    const constRegex = /([A-Z][A-Z0-9_]*)\s*=/g;
    while ((match = constRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract requires
    const requireRegex = /require\s+['"]([^'"]+)['"]/g;
    while ((match = requireRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract includes
    const includeRegex = /include\s+([A-Z][a-zA-Z0-9_]*)/g;
    while ((match = includeRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from PHP code
   */
  private extractPhpSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class declarations
    const classRegex = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract interface declarations
    const interfaceRegex = /interface\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = interfaceRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract function declarations
    const functionRegex = /function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract method declarations
    const methodRegex = /(?:public|private|protected)?\s*(?:static)?\s*function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    while ((match = methodRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract namespace declarations
    const namespaceRegex = /namespace\s+([a-zA-Z_][a-zA-Z0-9_\\]*)/g;
    while ((match = namespaceRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract use statements (imports)
    const useRegex = /use\s+([a-zA-Z_][a-zA-Z0-9_\\]*)/g;
    while ((match = useRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract require/include statements
    const requireRegex = /(?:require|include)(?:_once)?\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
    while ((match = requireRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }
  }

  /**
   * Extract symbols from Rust code
   */
  private extractRustSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract function declarations
    const functionRegex = /fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:<[^>]*>)?\s*\(/g;
    let match;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract struct declarations
    const structRegex = /struct\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = structRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract enum declarations
    const enumRegex = /enum\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = enumRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract trait declarations
    const traitRegex = /trait\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = traitRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract impl blocks
    const implRegex = /impl(?:<[^>]*>)?\s+(?:[^{]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = implRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract const declarations
    const constRegex = /const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g;
    while ((match = constRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract static declarations
    const staticRegex = /static\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g;
    while ((match = staticRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract use statements (imports)
    const useRegex = /use\s+([a-zA-Z0-9_:{}]+);/g;
    while ((match = useRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract mod declarations
    const modRegex = /mod\s+([a-zA-Z_][a-zA-Z0-9_]*);/g;
    while ((match = modRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from Swift code
   */
  private extractSwiftSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class declarations
    const classRegex = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract struct declarations
    const structRegex = /struct\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = structRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract enum declarations
    const enumRegex = /enum\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = enumRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract protocol declarations
    const protocolRegex = /protocol\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = protocolRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract function declarations
    const functionRegex = /func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:<[^>]*>)?\s*\(/g;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract variable declarations
    const varRegex = /(?:var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g;
    while ((match = varRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract import statements
    const importRegex = /import\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract extension declarations
    const extensionRegex = /extension\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = extensionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from Kotlin code
   */
  private extractKotlinSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Extract class declarations
    const classRegex = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    let match;
    while ((match = classRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract interface declarations
    const interfaceRegex = /interface\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = interfaceRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract function declarations
    const functionRegex = /fun\s+(?:<[^>]*>\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
    while ((match = functionRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract property declarations
    const propertyRegex = /(?:val|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::|=)/g;
    while ((match = propertyRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract object declarations
    const objectRegex = /object\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    while ((match = objectRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }

    // Extract import statements
    const importRegex = /import\s+([a-zA-Z0-9_.]*(?:\.[a-zA-Z0-9_*]+)*)/g;
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }

    // Extract package declaration
    const packageRegex = /package\s+([a-zA-Z0-9_.]+)/g;
    while ((match = packageRegex.exec(content)) !== null) {
      symbols.push(match[1]);
    }
  }

  /**
   * Extract symbols from HTML/CSS/SCSS/SASS code
   */
  private extractWebSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[],
    language: string
  ): void {
    if (language === 'html') {
      // Extract IDs
      const idRegex = /id=["']([^"']+)["']/g;
      let match;
      while ((match = idRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }

      // Extract classes
      const classRegex = /class=["']([^"']+)["']/g;
      while ((match = classRegex.exec(content)) !== null) {
        const classes = match[1].split(/\s+/);
        for (const cls of classes) {
          if (cls) {
            symbols.push(cls);
          }
        }
      }

      // Extract custom elements
      const customElementRegex = /<([a-z]+-[a-z-]+)/g;
      while ((match = customElementRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }

      // Extract script src and link href
      const linkRegex = /(?:src|href)=["']([^"']+)["']/g;
      while ((match = linkRegex.exec(content)) !== null) {
        imports.push(match[1]);
        dependencies.push(match[1]);
      }
    } else {
      // CSS/SCSS/SASS

      // Extract selectors
      const selectorRegex = /([.#][a-zA-Z_-][a-zA-Z0-9_-]*)/g;
      let match;
      while ((match = selectorRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }

      // Extract custom properties
      const customPropRegex = /(--[a-zA-Z0-9_-]+)\s*:/g;
      while ((match = customPropRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }

      // Extract @import statements
      const importRegex = /@import\s+["']([^"']+)["']/g;
      while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1]);
        dependencies.push(match[1]);
      }

      // Extract SCSS/SASS variables
      if (language === 'scss' || language === 'sass') {
        const varRegex = /\$([a-zA-Z_-][a-zA-Z0-9_-]*)\s*:/g;
        while ((match = varRegex.exec(content)) !== null) {
          symbols.push('$' + match[1]);
        }

        // Extract mixins
        const mixinRegex = /@mixin\s+([a-zA-Z_-][a-zA-Z0-9_-]*)/g;
        while ((match = mixinRegex.exec(content)) !== null) {
          symbols.push(match[1]);
        }
      }
    }
  }

  /**
   * Extract symbols from data formats (JSON, YAML, XML)
   */
  private extractDataFormatSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[],
    language: string
  ): void {
    if (language === 'json') {
      // Extract property names from JSON
      const propRegex = /"([a-zA-Z_][a-zA-Z0-9_]*)"\s*:/g;
      let match;
      while ((match = propRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }
    } else if (language === 'yaml') {
      // Extract keys from YAML
      const keyRegex = /^([a-zA-Z_][a-zA-Z0-9_]*)\s*:/gm;
      let match;
      while ((match = keyRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }
    } else if (language === 'xml') {
      // Extract tag names from XML
      const tagRegex = /<([a-zA-Z_][a-zA-Z0-9_:-]*)(?:\s|>|\/)/g;
      let match;
      while ((match = tagRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }

      // Extract attribute names
      const attrRegex = /\s([a-zA-Z_][a-zA-Z0-9_:-]*)=/g;
      while ((match = attrRegex.exec(content)) !== null) {
        symbols.push(match[1]);
      }
    }
  }

  /**
   * Generic symbol extraction for unsupported languages
   */
  private extractGenericSymbols(
    content: string,
    symbols: string[],
    imports: string[],
    dependencies: string[]
  ): void {
    // Generic symbol extraction using regex
    // This is a fallback for languages we don't have specific parsers for

    // Extract words that look like symbols (camelCase, PascalCase, snake_case)
    const symbolRegex = /\b([a-zA-Z_][a-zA-Z0-9_]*)\b/g;
    let match;
    while ((match = symbolRegex.exec(content)) !== null) {
      // Filter out common keywords across languages
      const keywords = [
        // Common programming keywords
        'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
        'return', 'function', 'class', 'struct', 'enum', 'interface', 'namespace',
        'public', 'private', 'protected', 'static', 'final', 'const', 'var', 'let',
        'void', 'int', 'float', 'double', 'string', 'bool', 'true', 'false', 'null',
        'this', 'super', 'new', 'delete', 'try', 'catch', 'finally', 'throw'
      ];

      if (!keywords.includes(match[1])) {
        // Prioritize symbols that look like identifiers
        // - PascalCase (class/type names)
        // - camelCase (method/variable names)
        // - snake_case (variable names in some languages)
        // - UPPER_CASE (constants)
        if (
          /^[A-Z][a-z0-9]+[A-Z]/.test(match[1]) || // PascalCase
          /^[a-z]+[A-Z]/.test(match[1]) || // camelCase
          match[1].includes('_') || // snake_case or UPPER_CASE
          /^[A-Z][A-Z0-9_]+$/.test(match[1]) // UPPER_CASE constants
        ) {
          symbols.push(match[1]);
        }
      }
    }

    // Try to extract imports based on common patterns across languages
    const importRegex = /(?:import|include|require|using|from|#include)\s+['"]?([a-zA-Z0-9_./\\<>]+)['"]?/g;
    while ((match = importRegex.exec(content)) !== null) {
      imports.push(match[1]);
      dependencies.push(match[1]);
    }
  }
}
