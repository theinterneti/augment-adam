import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
  vscode.window.showInformationMessage('Start all tests.');

  test('Extension should be present', () => {
    assert.ok(vscode.extensions.getExtension('qwen-coder-assistant'));
  });

  test('Extension should activate', async () => {
    const extension = vscode.extensions.getExtension('qwen-coder-assistant');
    if (!extension) {
      assert.fail('Extension not found');
      return;
    }
    
    await extension.activate();
    assert.ok(extension.isActive);
  });

  test('Commands should be registered', async () => {
    const commands = await vscode.commands.getCommands();
    assert.ok(commands.includes('qwen-coder-assistant.askQwen'));
    assert.ok(commands.includes('qwen-coder-assistant.explainCode'));
    assert.ok(commands.includes('qwen-coder-assistant.generateCode'));
  });
});
