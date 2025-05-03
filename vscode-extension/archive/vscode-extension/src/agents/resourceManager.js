"use strict";
/**
 * Resource Manager
 *
 * Monitors system resources and controls agent instantiation.
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
exports.ResourceManager = void 0;
const vscode = __importStar(require("vscode"));
const os = __importStar(require("os"));
const uuid_1 = require("uuid");
/**
 * Resource Manager class
 */
class ResourceManager {
    /**
     * Constructor
     * @param maxMemoryUsage Maximum memory usage (0-1)
     * @param maxCpuUsage Maximum CPU usage (0-1)
     */
    constructor(maxMemoryUsage = 0.8, maxCpuUsage = 0.8) {
        this.outputChannel = vscode.window.createOutputChannel('Resource Manager');
        this.activeAgents = {};
        this.maxMemoryUsage = maxMemoryUsage;
        this.maxCpuUsage = maxCpuUsage;
        this.resourceCheckInterval = null;
        // Start resource monitoring
        this._startResourceMonitoring();
        this.outputChannel.appendLine('Resource Manager initialized');
    }
    /**
     * Get available system resources
     * @returns Available resources
     */
    async getAvailableResources() {
        try {
            // Get current system resource usage
            const currentMemoryUsage = this._getMemoryUsage();
            const currentCpuUsage = await this._getCpuUsage();
            // Calculate available resources
            const availableMemory = Math.max(0, this.maxMemoryUsage - currentMemoryUsage);
            const availableCpu = Math.max(0, this.maxCpuUsage - currentCpuUsage);
            const resources = {
                memory: availableMemory,
                cpu: availableCpu,
                activeAgents: Object.keys(this.activeAgents).length
            };
            this.outputChannel.appendLine(`Available resources: memory=${availableMemory.toFixed(2)}, cpu=${availableCpu.toFixed(2)}, activeAgents=${resources.activeAgents}`);
            return resources;
        }
        catch (error) {
            this.outputChannel.appendLine(`Error getting available resources: ${error.message}`);
            // Return conservative estimates in case of error
            return {
                memory: 0.2,
                cpu: 0.2,
                activeAgents: Object.keys(this.activeAgents).length
            };
        }
    }
    /**
     * Register a new agent with its resource requirements
     * @param type Agent type
     * @param requirements Resource requirements
     * @returns Agent ID
     */
    async registerAgent(type, requirements) {
        const agentId = (0, uuid_1.v4)();
        this.activeAgents[agentId] = {
            type,
            modelSize: requirements.modelSize,
            thinkingMode: requirements.thinkingMode,
            startTime: Date.now()
        };
        this.outputChannel.appendLine(`Registered agent ${agentId} of type ${type} with model ${requirements.modelSize}`);
        return agentId;
    }
    /**
     * Unregister an agent when it's no longer needed
     * @param agentId Agent ID
     */
    async unregisterAgent(agentId) {
        if (agentId in this.activeAgents) {
            const agent = this.activeAgents[agentId];
            const duration = (Date.now() - agent.startTime) / 1000;
            this.outputChannel.appendLine(`Unregistered agent ${agentId} of type ${agent.type} after ${duration.toFixed(2)}s`);
            delete this.activeAgents[agentId];
        }
    }
    /**
     * Get current memory usage
     * @returns Memory usage (0-1)
     */
    _getMemoryUsage() {
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        return usedMem / totalMem;
    }
    /**
     * Get current CPU usage
     * @returns CPU usage (0-1)
     */
    async _getCpuUsage() {
        return new Promise((resolve) => {
            const startMeasure = os.cpus().map(cpu => cpu.times);
            // Measure CPU usage over a short interval
            setTimeout(() => {
                const endMeasure = os.cpus().map(cpu => cpu.times);
                const cpuUsage = endMeasure.map((end, i) => {
                    const start = startMeasure[i];
                    const idle = end.idle - start.idle;
                    const total = (end.user - start.user) +
                        (end.nice - start.nice) +
                        (end.sys - start.sys) +
                        (end.irq - start.irq) +
                        idle;
                    return 1 - (idle / total);
                });
                // Average CPU usage across all cores
                const avgCpuUsage = cpuUsage.reduce((sum, usage) => sum + usage, 0) / cpuUsage.length;
                resolve(avgCpuUsage);
            }, 100);
        });
    }
    /**
     * Start resource monitoring
     */
    _startResourceMonitoring() {
        if (this.resourceCheckInterval) {
            clearInterval(this.resourceCheckInterval);
        }
        this.resourceCheckInterval = setInterval(async () => {
            try {
                const resources = await this.getAvailableResources();
                // Log resource usage periodically
                if (Object.keys(this.activeAgents).length > 0) {
                    this.outputChannel.appendLine(`Resource check: memory=${(1 - resources.memory).toFixed(2)}, cpu=${(1 - resources.cpu).toFixed(2)}, activeAgents=${resources.activeAgents}`);
                }
                // Check for resource constraints
                if (resources.memory < 0.1 || resources.cpu < 0.1) {
                    this.outputChannel.appendLine('WARNING: System resources are critically low');
                    // Notify the user
                    vscode.window.showWarningMessage('System resources are running low. Some agent operations may be delayed.');
                }
            }
            catch (error) {
                this.outputChannel.appendLine(`Error monitoring resources: ${error.message}`);
            }
        }, 30000); // Check every 30 seconds
    }
    /**
     * Dispose of resources
     */
    dispose() {
        if (this.resourceCheckInterval) {
            clearInterval(this.resourceCheckInterval);
            this.resourceCheckInterval = null;
        }
        this.outputChannel.dispose();
    }
}
exports.ResourceManager = ResourceManager;
//# sourceMappingURL=resourceManager.js.map