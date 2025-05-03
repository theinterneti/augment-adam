import * as assert from 'assert';
import * as sinon from 'sinon';
import * as vscode from 'vscode';
import { ResponseFormatter } from '../../responseFormatter';

suite('Response Formatter Test Suite', () => {
  let responseFormatter: ResponseFormatter;
  let mockWebviewPanel: vscode.WebviewPanel;
  
  setup(() => {
    // Create mock webview panel
    mockWebviewPanel = {
      webview: {
        html: '',
        onDidReceiveMessage: sinon.stub(),
        postMessage: sinon.stub().resolves()
      },
      onDidDispose: sinon.stub(),
      reveal: sinon.stub(),
      dispose: sinon.stub()
    } as unknown as vscode.WebviewPanel;
    
    // Create stub for webview panel creation
    sinon.stub(vscode.window, 'createWebviewPanel').returns(mockWebviewPanel);
    
    // Initialize response formatter
    responseFormatter = new ResponseFormatter();
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should format markdown response', () => {
    // Setup
    const markdown = '# Heading\n\nThis is a paragraph with **bold** and *italic* text.\n\n```javascript\nconst x = 1;\n```';
    
    // Execute
    const formatted = responseFormatter.formatMarkdown(markdown);
    
    // Verify
    assert.strictEqual(formatted.includes('<h1>Heading</h1>'), true, 'Should convert heading');
    assert.strictEqual(formatted.includes('<strong>bold</strong>'), true, 'Should convert bold text');
    assert.strictEqual(formatted.includes('<em>italic</em>'), true, 'Should convert italic text');
    assert.strictEqual(formatted.includes('<pre><code class="language-javascript">'), true, 'Should format code blocks');
  });
  
  test('Should format code response', () => {
    // Setup
    const code = 'function test() {\n  return true;\n}';
    const language = 'javascript';
    
    // Execute
    const formatted = responseFormatter.formatCode(code, language);
    
    // Verify
    assert.strictEqual(formatted.includes('<pre><code class="language-javascript">'), true, 'Should include language class');
    assert.strictEqual(formatted.includes('function test()'), true, 'Should include code content');
  });
  
  test('Should display response in webview panel', async () => {
    // Setup
    const response = 'This is a test response';
    
    // Execute
    await responseFormatter.displayResponse(response, 'Test Response');
    
    // Verify
    assert.strictEqual(vscode.window.createWebviewPanel.calledOnce, true, 'Should create webview panel');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(response), true, 'Should set HTML content');
    assert.strictEqual(mockWebviewPanel.reveal.calledOnce, true, 'Should reveal panel');
  });
  
  test('Should handle code explanation display', async () => {
    // Setup
    const code = 'function test() {\n  return true;\n}';
    const explanation = 'This function always returns true';
    
    // Execute
    await responseFormatter.displayCodeExplanation(code, 'javascript', explanation);
    
    // Verify
    assert.strictEqual(vscode.window.createWebviewPanel.calledOnce, true, 'Should create webview panel');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(code), true, 'Should include code');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(explanation), true, 'Should include explanation');
  });
  
  test('Should handle generated code display', async () => {
    // Setup
    const request = 'Generate a function that returns true';
    const generatedCode = 'function alwaysTrue() {\n  return true;\n}';
    
    // Execute
    await responseFormatter.displayGeneratedCode(request, 'javascript', generatedCode);
    
    // Verify
    assert.strictEqual(vscode.window.createWebviewPanel.calledOnce, true, 'Should create webview panel');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(request), true, 'Should include request');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(generatedCode), true, 'Should include generated code');
    assert.strictEqual(mockWebviewPanel.webview.html.includes('Insert Code'), true, 'Should include insert button');
  });
  
  test('Should handle error display', async () => {
    // Setup
    const error = 'API Error: Rate limit exceeded';
    
    // Execute
    await responseFormatter.displayError(error);
    
    // Verify
    assert.strictEqual(vscode.window.createWebviewPanel.calledOnce, true, 'Should create webview panel');
    assert.strictEqual(mockWebviewPanel.webview.html.includes(error), true, 'Should include error message');
    assert.strictEqual(mockWebviewPanel.webview.html.includes('Error'), true, 'Should indicate error status');
  });
  
  test('Should handle streaming response updates', async () => {
    // Setup
    const initialResponse = 'This is ';
    const updatedResponse = 'This is a complete response';
    
    // Create panel first
    await responseFormatter.displayResponse(initialResponse, 'Streaming Response');
    
    // Reset the HTML to simulate starting fresh
    mockWebviewPanel.webview.html = '';
    
    // Execute - update with streaming content
    await responseFormatter.updateStreamingResponse(updatedResponse);
    
    // Verify
    assert.strictEqual(mockWebviewPanel.webview.postMessage.called, true, 'Should post message to webview');
    
    // The actual HTML update would be handled by the webview's JavaScript,
    // so we're verifying the message was sent with the updated content
    const messageArg = mockWebviewPanel.webview.postMessage.firstCall.args[0];
    assert.strictEqual(messageArg.type, 'update', 'Should send update message type');
    assert.strictEqual(messageArg.content, updatedResponse, 'Should send updated content');
  });
});
