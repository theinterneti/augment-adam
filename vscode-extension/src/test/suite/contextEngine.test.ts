import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';
import { ContextEngine } from '../../context/contextEngine';
import { VectorStore } from '../../context/vectorStore';
import { FileIndexer } from '../../context/fileIndexer';
import { EmbeddingService } from '../../context/embeddingService';

suite('Context Engine Test Suite', () => {
  let contextEngine: ContextEngine;
  let mockVectorStore: sinon.SinonStubbedInstance<VectorStore>;
  let mockFileIndexer: sinon.SinonStubbedInstance<FileIndexer>;
  let mockEmbeddingService: sinon.SinonStubbedInstance<EmbeddingService>;
  
  setup(() => {
    // Create mock instances
    mockVectorStore = sinon.createStubInstance(VectorStore);
    mockFileIndexer = sinon.createStubInstance(FileIndexer);
    mockEmbeddingService = sinon.createStubInstance(EmbeddingService);
    
    // Initialize context engine with mocks
    contextEngine = new ContextEngine(
      mockVectorStore as unknown as VectorStore,
      mockFileIndexer as unknown as FileIndexer,
      mockEmbeddingService as unknown as EmbeddingService
    );
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should initialize context engine', async () => {
    // Setup
    mockVectorStore.initialize.resolves();
    
    // Execute
    await contextEngine.initialize();
    
    // Verify
    assert.strictEqual(mockVectorStore.initialize.calledOnce, true, 'Vector store should be initialized');
  });
  
  test('Should get context for query', async () => {
    // Setup
    const query = 'How does the context engine work?';
    const mockEmbedding = [0.1, 0.2, 0.3];
    const mockResults = [
      { content: 'Context engine processes queries', score: 0.9, filePath: 'src/context/contextEngine.ts' },
      { content: 'Vector store manages embeddings', score: 0.8, filePath: 'src/context/vectorStore.ts' }
    ];
    
    mockEmbeddingService.getEmbedding.resolves(mockEmbedding);
    mockVectorStore.search.resolves(mockResults);
    
    // Execute
    const context = await contextEngine.getContextForQuery(query);
    
    // Verify
    assert.strictEqual(mockEmbeddingService.getEmbedding.calledOnce, true, 'Should get embedding for query');
    assert.strictEqual(mockVectorStore.search.calledOnce, true, 'Should search vector store');
    assert.ok(context.includes('Context engine processes queries'), 'Context should include relevant content');
    assert.ok(context.includes('Vector store manages embeddings'), 'Context should include relevant content');
  });
  
  test('Should index workspace files', async () => {
    // Setup
    const mockFiles = [
      vscode.Uri.file('/workspace/src/file1.ts'),
      vscode.Uri.file('/workspace/src/file2.ts')
    ];
    const mockChunks = [
      { content: 'File content 1', embedding: [0.1, 0.2], filePath: '/workspace/src/file1.ts', startLine: 1, endLine: 10 },
      { content: 'File content 2', embedding: [0.3, 0.4], filePath: '/workspace/src/file2.ts', startLine: 1, endLine: 10 }
    ];
    
    // Mock workspace.findFiles
    sinon.stub(vscode.workspace, 'findFiles').resolves(mockFiles);
    
    // Mock file indexer
    mockFileIndexer.indexFile.resolves(mockChunks);
    
    // Mock vector store
    mockVectorStore.addChunks.resolves();
    
    // Execute
    await contextEngine.indexWorkspace();
    
    // Verify
    assert.strictEqual(mockFileIndexer.indexFile.callCount, 2, 'Should index each file');
    assert.strictEqual(mockVectorStore.addChunks.callCount, 2, 'Should add chunks to vector store');
  });
  
  test('Should dispose resources', async () => {
    // Setup
    mockVectorStore.dispose.resolves();
    
    // Execute
    await contextEngine.dispose();
    
    // Verify
    assert.strictEqual(mockVectorStore.dispose.calledOnce, true, 'Vector store should be disposed');
  });
});
