"use strict";
/**
 * Container Manager
 *
 * Handles the lifecycle of containerized MCP tools.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContainerManager = void 0;
const vscode = __importStar(require("vscode"));
const configuration_1 = require("../configuration");
/**
 * Container Manager class
 */
class ContainerManager {
    /**
     * Constructor
     */
    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Container Manager');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
        this.statusBarItem.text = '$(docker) MCP Tools';
        this.statusBarItem.tooltip = 'MCP Tools Status';
        this.statusBarItem.command = 'qwenCoder.showContainerStatus';
        this.containerRegistry = {
            'github': {
                image: 'qwen-mcp-github:latest',
                command: 'uvx',
                args: ['mcp-server-github'],
                ports: [{ internal: 8080, external: 0 }]
            },
            'docker': {
                image: 'qwen-mcp-docker:latest',
                command: 'uvx',
                args: ['mcp-server-docker'],
                ports: [{ internal: 8080, external: 0 }]
            },
            'testing': {
                image: 'qwen-mcp-testing:latest',
                command: 'uvx',
                args: ['mcp-server-testing'],
                ports: [{ internal: 8080, external: 0 }]
            },
            'ci_cd': {
                image: 'qwen-mcp-cicd:latest',
                command: 'uvx',
                args: ['mcp-server-cicd'],
                ports: [{ internal: 8080, external: 0 }]
            }
        };
        this.activeContainers = {};
        this.healthCheckInterval = null;
        this.outputChannel.appendLine('Container Manager initialized');
    }
    /**
     * Initialize the container manager
     */
    async initialize() {
        try {
            this.statusBarItem.show();
            // Check if Docker is available
            const dockerAvailable = await this._checkDockerAvailability();
            if (!dockerAvailable) {
                this.outputChannel.appendLine('Docker is not available. Container features will be disabled.');
                this.statusBarItem.text = '$(alert) Docker Not Available';
                this.statusBarItem.tooltip = 'Docker is not available. Container features are disabled.';
                return;
            }
            // Start health check interval
            this._startHealthCheck();
            // Auto-start containers if configured
            const config = (0, configuration_1.getConfiguration)();
            const autoStartContainers = config.get('autoStartContainers', false);
            if (autoStartContainers) {
                this.outputChannel.appendLine('Auto-starting containers...');
                const containersToStart = config.get('autoStartContainerList', ['github', 'docker']);
                for (const containerName of containersToStart) {
                    try {
                        await this.startContainer(containerName);
                    }
                    catch (error) {
                        this.outputChannel.appendLine(`Error auto-starting container ${containerName}: ${error.message}`);
                    }
                }
            }
        }
        catch (error) {
            this.outputChannel.appendLine(`Error initializing Container Manager: ${error.message}`);
            this.statusBarItem.text = '$(error) MCP Tools Error';
            this.statusBarItem.tooltip = `Error: ${error.message}`;
        }
    }
    /**
     * Start a containerized MCP tool
     * @param containerName The name of the container to start
     * @returns The URL for accessing the container
     */
    async startContainer(containerName) {
        try {
            this.outputChannel.appendLine(`Starting container: ${containerName}`);
            // Check if container is already running
            if (this.activeContainers[containerName] && this.activeContainers[containerName].status === 'running') {
                this.outputChannel.appendLine(`Container ${containerName} is already running`);
                return this.activeContainers[containerName].url;
            }
            // Get container configuration
            const containerConfig = this.containerRegistry[containerName];
            if (!containerConfig) {
                throw new Error(`Unknown container: ${containerName}`);
            }
            // Check if Docker is available
            const dockerAvailable = await this._checkDockerAvailability();
            if (!dockerAvailable) {
                throw new Error('Docker is not available');
            }
            // Pull the image if needed
            await this._ensureImageAvailable(containerConfig.image);
            // Start the container
            const containerId = await this._startContainer(containerName, containerConfig);
            // Get container URL
            const url = await this._getContainerUrl(containerId, containerConfig);
            // Update active containers
            this.activeContainers[containerName] = {
                id: containerId,
                name: containerName,
                image: containerConfig.image,
                url,
                status: 'running',
                startTime: Date.now()
            };
            // Update status bar
            this._updateStatusBar();
            this.outputChannel.appendLine(`Container ${containerName} started successfully with URL: ${url}`);
            return url;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error starting container ${containerName}: ${error.message}`);
            // Update active containers with error status
            this.activeContainers[containerName] = {
                id: '',
                name: containerName,
                image: this.containerRegistry[containerName]?.image || '',
                url: '',
                status: 'error',
                startTime: Date.now(),
                error: error.message
            };
            // Update status bar
            this._updateStatusBar();
            throw error;
        }
    }
    /**
     * Stop a containerized MCP tool
     * @param containerName The name of the container to stop
     */
    async stopContainer(containerName) {
        try {
            this.outputChannel.appendLine(`Stopping container: ${containerName}`);
            // Check if container is running
            if (!this.activeContainers[containerName] || this.activeContainers[containerName].status !== 'running') {
                this.outputChannel.appendLine(`Container ${containerName} is not running`);
                return;
            }
            const containerId = this.activeContainers[containerName].id;
            // Stop and remove the container
            await this._stopContainer(containerId);
            // Update active containers
            this.activeContainers[containerName] = {
                ...this.activeContainers[containerName],
                status: 'stopped'
            };
            // Update status bar
            this._updateStatusBar();
            this.outputChannel.appendLine(`Container ${containerName} stopped successfully`);
        }
        catch (error) {
            this.outputChannel.appendLine(`Error stopping container ${containerName}: ${error.message}`);
            throw error;
        }
    }
    /**
     * Get the URL for a running container
     * @param containerName The name of the container
     * @returns The URL for accessing the container
     */
    getContainerUrl(containerName) {
        if (!this.activeContainers[containerName] || this.activeContainers[containerName].status !== 'running') {
            throw new Error(`Container ${containerName} is not running`);
        }
        return this.activeContainers[containerName].url;
    }
    /**
     * Get the status of all containers
     * @returns The status of all containers
     */
    getContainerStatus() {
        return { ...this.activeContainers };
    }
    /**
     * Check if Docker is available
     * @returns Whether Docker is available
     */
    async _checkDockerAvailability() {
        try {
            // This is a placeholder for Docker availability check
            // In a real implementation, we would use the Docker SDK to check if Docker is running
            // For now, we'll assume Docker is available
            return true;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error checking Docker availability: ${error.message}`);
            return false;
        }
    }
    /**
     * Ensure the Docker image is available
     * @param imageName The name of the image
     */
    async _ensureImageAvailable(imageName) {
        try {
            this.outputChannel.appendLine(`Ensuring image is available: ${imageName}`);
            // This is a placeholder for image availability check
            // In a real implementation, we would use the Docker SDK to check if the image exists locally
            // and pull it if it doesn't
            // For now, we'll assume the image is available
        }
        catch (error) {
            this.outputChannel.appendLine(`Error ensuring image availability: ${error.message}`);
            throw error;
        }
    }
    /**
     * Start a container
     * @param containerName The name of the container
     * @param config The container configuration
     * @returns The container ID
     */
    async _startContainer(containerName, config) {
        try {
            this.outputChannel.appendLine(`Starting container with image: ${config.image}`);
            // This is a placeholder for container start
            // In a real implementation, we would use the Docker SDK to start the container
            // For now, we'll return a fake container ID
            return `fake-container-id-${containerName}-${Date.now()}`;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error starting container: ${error.message}`);
            throw error;
        }
    }
    /**
     * Stop a container
     * @param containerId The ID of the container
     */
    async _stopContainer(containerId) {
        try {
            this.outputChannel.appendLine(`Stopping container: ${containerId}`);
            // This is a placeholder for container stop
            // In a real implementation, we would use the Docker SDK to stop and remove the container
        }
        catch (error) {
            this.outputChannel.appendLine(`Error stopping container: ${error.message}`);
            throw error;
        }
    }
    /**
     * Get the URL for a container
     * @param containerId The ID of the container
     * @param config The container configuration
     * @returns The URL for accessing the container
     */
    async _getContainerUrl(containerId, config) {
        try {
            // This is a placeholder for getting the container URL
            // In a real implementation, we would use the Docker SDK to get the port mapping
            // For now, we'll return a fake URL
            return `http://localhost:${8080 + Math.floor(Math.random() * 1000)}`;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error getting container URL: ${error.message}`);
            throw error;
        }
    }
    /**
     * Start health check interval
     */
    _startHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        this.healthCheckInterval = setInterval(async () => {
            try {
                for (const containerName in this.activeContainers) {
                    const container = this.activeContainers[containerName];
                    if (container.status === 'running') {
                        // Check container health
                        const isHealthy = await this._checkContainerHealth(container);
                        if (!isHealthy) {
                            this.outputChannel.appendLine(`Container ${containerName} is not healthy, attempting to restart`);
                            // Attempt to restart the container
                            try {
                                await this.stopContainer(containerName);
                                await this.startContainer(containerName);
                                this.outputChannel.appendLine(`Container ${containerName} restarted successfully`);
                            }
                            catch (error) {
                                this.outputChannel.appendLine(`Error restarting container ${containerName}: ${error.message}`);
                            }
                        }
                    }
                }
                // Update status bar
                this._updateStatusBar();
            }
            catch (error) {
                this.outputChannel.appendLine(`Error in health check: ${error.message}`);
            }
        }, 60000); // Check every minute
    }
    /**
     * Check container health
     * @param container The container to check
     * @returns Whether the container is healthy
     */
    async _checkContainerHealth(container) {
        try {
            // This is a placeholder for container health check
            // In a real implementation, we would use the Docker SDK to check the container health
            // For now, we'll assume the container is healthy
            return true;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error checking container health: ${error.message}`);
            return false;
        }
    }
    /**
     * Update status bar
     */
    _updateStatusBar() {
        const runningContainers = Object.values(this.activeContainers).filter(c => c.status === 'running').length;
        const totalContainers = Object.keys(this.activeContainers).length;
        if (runningContainers === 0) {
            this.statusBarItem.text = '$(docker) MCP Tools: None Running';
        }
        else {
            this.statusBarItem.text = `$(docker) MCP Tools: ${runningContainers}/${totalContainers} Running`;
        }
        // Update tooltip with container details
        let tooltip = 'MCP Tools Status:\n\n';
        for (const containerName in this.activeContainers) {
            const container = this.activeContainers[containerName];
            tooltip += `${containerName}: ${container.status}`;
            if (container.status === 'running') {
                tooltip += ` (${container.url})`;
            }
            else if (container.status === 'error') {
                tooltip += ` (${container.error})`;
            }
            tooltip += '\n';
        }
        this.statusBarItem.tooltip = tooltip;
    }
    /**
     * Stop all containers
     */
    async stopAllContainers() {
        try {
            this.outputChannel.appendLine('Stopping all containers');
            for (const containerName in this.activeContainers) {
                if (this.activeContainers[containerName].status === 'running') {
                    try {
                        await this.stopContainer(containerName);
                    }
                    catch (error) {
                        this.outputChannel.appendLine(`Error stopping container ${containerName}: ${error.message}`);
                    }
                }
            }
            this.outputChannel.appendLine('All containers stopped');
        }
        catch (error) {
            this.outputChannel.appendLine(`Error stopping all containers: ${error.message}`);
            throw error;
        }
    }
    /**
     * Dispose of resources
     */
    dispose() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
        this.stopAllContainers().catch(error => {
            this.outputChannel.appendLine(`Error stopping containers during disposal: ${error.message}`);
        });
        this.statusBarItem.dispose();
        this.outputChannel.dispose();
    }
}
exports.ContainerManager = ContainerManager;
//# sourceMappingURL=containerManager.js.map