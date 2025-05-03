import * as assert from 'assert';
import * as sinon from 'sinon';
import { VectorStore } from '../../context/vectorStore';
import { CodeChunk } from '../../context/types';

suite('Vector Store Test Suite', () => {
  let vectorStore: VectorStore;
  
  setup(() => {
    vectorStore = new VectorStore();
  });
  
  teardown(() => {
    sinon.restore();
  });
  
  test('Should add chunks to vector store', async () => {
    // Setup
    const chunks: CodeChunk[] = [
      {
        content: 'function test() { return true; }',
        embedding: [0.1, 0.2, 0.3],
        filePath: 'src/test.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      },
      {
        content: 'class Example { constructor() {} }',
        embedding: [0.4, 0.5, 0.6],
        filePath: 'src/example.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      }
    ];
    
    // Execute
    await vectorStore.addChunks(chunks);
    
    // Verify - we can't directly access private members, so we'll test via search
    const results = await vectorStore.search([0.1, 0.2, 0.3], 5);
    assert.strictEqual(results.length, 2, 'Should return added chunks');
    assert.strictEqual(results[0].content, 'function test() { return true; }', 'Should return correct content');
  });
  
  test('Should search for similar chunks', async () => {
    // Setup
    const chunks: CodeChunk[] = [
      {
        content: 'function calculateDistance(a, b) { return Math.sqrt(a*a + b*b); }',
        embedding: [0.1, 0.2, 0.3],
        filePath: 'src/math.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      },
      {
        content: 'class User { constructor(name) { this.name = name; } }',
        embedding: [0.7, 0.8, 0.9],
        filePath: 'src/user.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      }
    ];
    
    await vectorStore.addChunks(chunks);
    
    // Execute - search with embedding closer to the first chunk
    const results = await vectorStore.search([0.15, 0.25, 0.35], 1);
    
    // Verify
    assert.strictEqual(results.length, 1, 'Should return requested number of results');
    assert.strictEqual(results[0].content.includes('calculateDistance'), true, 'Should return most similar chunk');
  });
  
  test('Should clear vector store', async () => {
    // Setup
    const chunks: CodeChunk[] = [
      {
        content: 'function test() { return true; }',
        embedding: [0.1, 0.2, 0.3],
        filePath: 'src/test.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      }
    ];
    
    await vectorStore.addChunks(chunks);
    
    // Execute
    await vectorStore.clear();
    
    // Verify
    const results = await vectorStore.search([0.1, 0.2, 0.3], 5);
    assert.strictEqual(results.length, 0, 'Should return no results after clearing');
  });
  
  test('Should filter search results by file path', async () => {
    // Setup
    const chunks: CodeChunk[] = [
      {
        content: 'function test1() { return true; }',
        embedding: [0.1, 0.2, 0.3],
        filePath: 'src/test1.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      },
      {
        content: 'function test2() { return false; }',
        embedding: [0.15, 0.25, 0.35],
        filePath: 'src/test2.ts',
        startLine: 1,
        endLine: 3,
        language: 'typescript'
      }
    ];
    
    await vectorStore.addChunks(chunks);
    
    // Execute
    const results = await vectorStore.search([0.1, 0.2, 0.3], 5, 'src/test1.ts');
    
    // Verify
    assert.strictEqual(results.length, 1, 'Should return only results matching file path');
    assert.strictEqual(results[0].filePath, 'src/test1.ts', 'Should return correct file');
  });
});
