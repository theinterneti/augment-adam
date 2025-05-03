#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ensure the scripts directory exists
const scriptsDir = path.join(__dirname);
if (!fs.existsSync(scriptsDir)) {
  fs.mkdirSync(scriptsDir, { recursive: true });
}

// Function to execute shell commands
function executeCommand(command) {
  console.log(`Executing: ${command}`);
  try {
    execSync(command, { stdio: 'inherit' });
  } catch (error) {
    console.error(`Error executing command: ${command}`);
    console.error(error);
    process.exit(1);
  }
}

// Main function
function packageExtension() {
  console.log('Packaging VS Code Extension...');
  
  // Check if vsce is installed
  try {
    execSync('which vsce', { stdio: 'ignore' });
  } catch (error) {
    console.log('vsce not found, installing...');
    executeCommand('npm install -g @vscode/vsce');
  }
  
  // Clean the out directory
  console.log('Cleaning output directory...');
  if (fs.existsSync('out')) {
    fs.rmSync('out', { recursive: true, force: true });
  }
  
  // Compile the TypeScript code
  console.log('Compiling TypeScript...');
  executeCommand('npm run compile');
  
  // Run linting
  console.log('Running linting...');
  executeCommand('npm run lint');
  
  // Package the extension
  console.log('Creating VSIX package...');
  executeCommand('vsce package');
  
  console.log('Extension packaging complete!');
}

// Run the main function
packageExtension();
