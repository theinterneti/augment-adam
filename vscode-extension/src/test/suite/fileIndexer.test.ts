import * as assert from 'assert';
import * as sinon from 'sinon';
import * as vscode from 'vscode';
import { FileIndexer } from '../../context/fileIndexer';
import { EmbeddingService } from '../../context/embeddingService';
import { SymbolExtractor } from '../../context/symbolExtractor';

suite('File Indexer Test Suite', () => {
  let fileIndexer: FileIndexer;
  let mockEmbeddingService: sinon.SinonStubbedInstance<EmbeddingService>;
  let mockSymbolExtractor: sinon.SinonStubbedInstance<SymbolExtractor>;
  let mockTextDocument: vscode.TextDocument;
  
  setup(() => {
    // Create mock instances
    mockEmbeddingService = sinon.createStubInstance(EmbeddingService);
    mockSymbolExtractor = sinon.createStubInstance(SymbolExtractor);
    
    // Mock text document
    mockTextDocument = {
      fileName: '/workspace/src/test.ts',
      languageId: 'typescript',
      lineCount: 10,
      getText: sinon.stub().returns('function test() {\n  return true;\n}'),
      lineAt: sinon.stub().callsFake((line: number) => {
        const lines = ['function test() {', '  return true;', '}'];
        return { text: lines[line] };
      }),
      uri: vscode.Uri.file('/workspace/src/test.ts')
    } as unknown as vscode.TextDocument;
    
    // Initialize file indexer with mocks
    fileIndexer = new FileIndexer(
      mockEmbeddingService as unknown as EmbeddingService,
      mockSymbolExtractor as unknown as SymbolExtractor
    );
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should index TypeScript file', async () => {
    // Setup
    const mockEmbedding = [0.1, 0.2, 0.3];
    mockEmbeddingService.getEmbedding.resolves(mockEmbedding);
    
    // Mock document loading
    sinon.stub(vscode.workspace, 'openTextDocument').resolves(mockTextDocument);
    
    // Execute
    const chunks = await fileIndexer.indexFile(vscode.Uri.file('/workspace/src/test.ts'));
    
    // Verify
    assert.strictEqual(chunks.length > 0, true, 'Should return chunks');
    assert.strictEqual(chunks[0].filePath, '/workspace/src/test.ts', 'Should set correct file path');
    assert.strictEqual(chunks[0].language, 'typescript', 'Should set correct language');
    assert.strictEqual(chunks[0].embedding, mockEmbedding, 'Should set embedding');
    assert.strictEqual(mockEmbeddingService.getEmbedding.called, true, 'Should get embedding for chunk');
  });
  
  test('Should extract symbols from file', async () => {
    // Setup
    const mockSymbols = [
      { name: 'test', kind: vscode.SymbolKind.Function, range: new vscode.Range(0, 0, 2, 1) }
    ];
    
    mockSymbolExtractor.extractSymbols.resolves(mockSymbols);
    mockEmbeddingService.getEmbedding.resolves([0.1, 0.2, 0.3]);
    
    // Mock document loading
    sinon.stub(vscode.workspace, 'openTextDocument').resolves(mockTextDocument);
    
    // Execute
    const chunks = await fileIndexer.indexFile(vscode.Uri.file('/workspace/src/test.ts'));
    
    // Verify
    assert.strictEqual(mockSymbolExtractor.extractSymbols.called, true, 'Should extract symbols');
    assert.strictEqual(chunks.some(chunk => chunk.symbol), true, 'Should include symbol information in chunks');
  });
  
  test('Should handle unsupported file types', async () => {
    // Setup - create a binary file mock
    const binaryDocument = {
      fileName: '/workspace/src/image.png',
      languageId: 'binary',
      lineCount: 0,
      getText: sinon.stub().returns(''),
      uri: vscode.Uri.file('/workspace/src/image.png')
    } as unknown as vscode.TextDocument;
    
    // Mock document loading
    sinon.stub(vscode.workspace, 'openTextDocument').resolves(binaryDocument);
    
    // Execute
    const chunks = await fileIndexer.indexFile(vscode.Uri.file('/workspace/src/image.png'));
    
    // Verify
    assert.strictEqual(chunks.length, 0, 'Should return empty array for unsupported file types');
  });
  
  test('Should handle large files by chunking', async () => {
    // Setup - create a large file mock
    const largeFileContent = Array(1000).fill('console.log("test");').join('\n');
    const largeDocument = {
      fileName: '/workspace/src/large.ts',
      languageId: 'typescript',
      lineCount: 1000,
      getText: sinon.stub().returns(largeFileContent),
      lineAt: sinon.stub().callsFake((line: number) => {
        return { text: 'console.log("test");' };
      }),
      uri: vscode.Uri.file('/workspace/src/large.ts')
    } as unknown as vscode.TextDocument;
    
    // Mock document loading
    sinon.stub(vscode.workspace, 'openTextDocument').resolves(largeDocument);
    mockEmbeddingService.getEmbedding.resolves([0.1, 0.2, 0.3]);
    
    // Execute
    const chunks = await fileIndexer.indexFile(vscode.Uri.file('/workspace/src/large.ts'));
    
    // Verify
    assert.strictEqual(chunks.length > 1, true, 'Should split large file into multiple chunks');
  });
});
