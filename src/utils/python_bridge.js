/**
 * Python Bridge for Augment Linux Assistant
 * 
 * This module provides a bridge between the VS Code extension (JavaScript)
 * and the Python backend for model inference.
 */

const { spawn } = require('child_process');
const path = require('path');
const vscode = require('vscode');

/**
 * Class to handle communication with Python scripts
 */
class PythonBridge {
    constructor(extensionContext) {
        this.extensionContext = extensionContext;
        this.pythonPath = this._getPythonPath();
    }

    /**
     * Get the Python executable path
     * @returns {string} Path to Python executable
     */
    _getPythonPath() {
        // Try to get from settings
        const pythonConfig = vscode.workspace.getConfiguration('python');
        let pythonPath = pythonConfig.get('defaultInterpreterPath');
        
        if (!pythonPath) {
            // Fallback to system Python
            pythonPath = process.platform === 'win32' ? 'python' : 'python3';
        }
        
        return pythonPath;
    }

    /**
     * Execute a Python script and return the result
     * @param {string} scriptPath - Path to the Python script
     * @param {Array} args - Arguments to pass to the script
     * @returns {Promise<string>} - Output from the script
     */
    async runScript(scriptPath, args = []) {
        return new Promise((resolve, reject) => {
            const fullPath = path.join(this.extensionContext.extensionPath, scriptPath);
            const process = spawn(this.pythonPath, [fullPath, ...args]);
            
            let stdout = '';
            let stderr = '';
            
            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            process.on('close', (code) => {
                if (code === 0) {
                    resolve(stdout.trim());
                } else {
                    reject(new Error(`Python script error (${code}): ${stderr}`));
                }
            });
            
            process.on('error', (err) => {
                reject(new Error(`Failed to start Python process: ${err.message}`));
            });
        });
    }

    /**
     * Generate a response using the model
     * @param {string} prompt - User prompt
     * @param {string} systemPrompt - System prompt
     * @returns {Promise<string>} - Model response
     */
    async generateResponse(prompt, systemPrompt = null) {
        try {
            const scriptPath = 'src/models/generate_response.py';
            const args = [
                '--prompt', prompt
            ];
            
            if (systemPrompt) {
                args.push('--system', systemPrompt);
            }
            
            // Get model settings from configuration
            const config = vscode.workspace.getConfiguration('augmentLinuxAssistant');
            const modelType = config.get('modelType');
            const useLocal = modelType === 'local';
            
            args.push('--local', useLocal ? 'true' : 'false');
            
            return await this.runScript(scriptPath, args);
        } catch (error) {
            console.error('Error generating response:', error);
            return `Error: ${error.message}`;
        }
    }
}

module.exports = PythonBridge;
