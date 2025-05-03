import * as assert from 'assert';
import * as sinon from 'sinon';
import * as vscode from 'vscode';
import { ContextProvider } from '../../contextProvider';
import { ContextEngine } from '../../context/contextEngine';

suite('Context Provider Test Suite', () => {
  let contextProvider: ContextProvider;
  let mockContextEngine: sinon.SinonStubbedInstance<ContextEngine>;
  let mockEditor: vscode.TextEditor;
  
  setup(() => {
    // Create mock context engine
    mockContextEngine = sinon.createStubInstance(ContextEngine);
    
    // Create mock text editor
    mockEditor = {
      document: {
        fileName: '/workspace/src/test.ts',
        languageId: 'typescript',
        getText: sinon.stub().returns('function test() {\n  return true;\n}'),
        lineAt: sinon.stub().callsFake((line: number) => {
          const lines = ['function test() {', '  return true;', '}'];
          return { text: lines[line] };
        }),
        uri: vscode.Uri.file('/workspace/src/test.ts')
      },
      selection: new vscode.Selection(0, 0, 2, 1)
    } as unknown as vscode.TextEditor;
    
    // Stub active editor
    sinon.stub(vscode.window, 'activeTextEditor').value(mockEditor);
    
    // Initialize context provider with mock
    contextProvider = new ContextProvider(mockContextEngine as unknown as ContextEngine);
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should get context for query', async () => {
    // Setup
    const query = 'How does the test function work?';
    mockContextEngine.getContextForQuery.resolves('Context for test function');
    
    // Execute
    const context = await contextProvider.getContextForQuery(query);
    
    // Verify
    assert.strictEqual(mockContextEngine.getContextForQuery.calledOnce, true, 'Should call context engine');
    assert.strictEqual(context, 'Context for test function', 'Should return context from engine');
  });
  
  test('Should get context for current file', async () => {
    // Setup
    mockContextEngine.getContextForFile.resolves('Context for current file');
    
    // Execute
    const context = await contextProvider.getContextForCurrentFile();
    
    // Verify
    assert.strictEqual(mockContextEngine.getContextForFile.calledOnce, true, 'Should call context engine');
    assert.strictEqual(context, 'Context for current file', 'Should return context from engine');
    
    // Verify file path was passed correctly
    const filePathArg = mockContextEngine.getContextForFile.firstCall.args[0];
    assert.strictEqual(filePathArg, '/workspace/src/test.ts', 'Should pass correct file path');
  });
  
  test('Should get context for selected code', async () => {
    // Setup
    mockContextEngine.getContextForCode.resolves('Context for selected code');
    
    // Execute
    const context = await contextProvider.getContextForSelectedCode();
    
    // Verify
    assert.strictEqual(mockContextEngine.getContextForCode.calledOnce, true, 'Should call context engine');
    assert.strictEqual(context, 'Context for selected code', 'Should return context from engine');
    
    // Verify selected code was passed correctly
    const codeArg = mockContextEngine.getContextForCode.firstCall.args[0];
    assert.strictEqual(codeArg, 'function test() {\n  return true;\n}', 'Should pass selected code');
  });
  
  test('Should handle no active editor', async () => {
    // Setup - simulate no active editor
    sinon.stub(vscode.window, 'activeTextEditor').value(undefined);
    
    // Execute and verify
    const context = await contextProvider.getContextForCurrentFile();
    assert.strictEqual(context, '', 'Should return empty string when no active editor');
    assert.strictEqual(mockContextEngine.getContextForFile.called, false, 'Should not call context engine');
  });
  
  test('Should handle no selection', async () => {
    // Setup - simulate empty selection
    const editorWithEmptySelection = {
      ...mockEditor,
      selection: new vscode.Selection(0, 0, 0, 0)
    };
    sinon.stub(vscode.window, 'activeTextEditor').value(editorWithEmptySelection);
    
    // Execute
    const context = await contextProvider.getContextForSelectedCode();
    
    // Verify
    assert.strictEqual(context, '', 'Should return empty string for empty selection');
    assert.strictEqual(mockContextEngine.getContextForCode.called, false, 'Should not call context engine');
  });
  
  test('Should get context with depth parameter', async () => {
    // Setup
    mockContextEngine.getContextForQuery.resolves('Deep context for query');
    
    // Execute
    const context = await contextProvider.getContextForQuery('Complex query', 'deep');
    
    // Verify
    assert.strictEqual(mockContextEngine.getContextForQuery.calledOnce, true, 'Should call context engine');
    
    // Verify depth parameter was passed correctly
    const depthArg = mockContextEngine.getContextForQuery.firstCall.args[1];
    assert.strictEqual(depthArg, 'deep', 'Should pass depth parameter');
  });
  
  test('Should get context for symbol under cursor', async () => {
    // Setup
    mockContextEngine.getContextForSymbol.resolves('Context for symbol');
    
    // Execute
    const context = await contextProvider.getContextForSymbolUnderCursor();
    
    // Verify
    assert.strictEqual(mockContextEngine.getContextForSymbol.calledOnce, true, 'Should call context engine');
    assert.strictEqual(context, 'Context for symbol', 'Should return context from engine');
  });
});
