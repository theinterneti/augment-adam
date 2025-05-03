"use strict";
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
exports.DockerContainerManager = void 0;
const Docker = __importStar(require("dockerode"));
const path = __importStar(require("path"));
/**
 * Manager for Docker containers
 */
class DockerContainerManager {
    /**
     * Create a new Docker container manager
     * @param options Docker options
     */
    constructor(options) {
        this.options = options;
        this.docker = new Docker({
            socketPath: options.socketPath
        });
    }
    /**
     * Start a container from a Dockerfile
     * @param name Container name
     * @param dockerfilePath Path to the directory containing the Dockerfile
     * @param actualDockerfilePath Optional path to the actual Dockerfile if it's not in the root directory
     * @returns Promise that resolves to the container ID
     */
    async startContainer(name, dockerfilePath, actualDockerfilePath) {
        try {
            console.log(`Starting container for ${name} from ${dockerfilePath}`);
            // Determine the context and Dockerfile path
            let context = dockerfilePath;
            let dockerfile = 'Dockerfile';
            if (actualDockerfilePath) {
                // If the Dockerfile is not in the root directory, we need to adjust the paths
                const relativePath = path.relative(dockerfilePath, actualDockerfilePath);
                if (relativePath.includes('..')) {
                    // If the Dockerfile is outside the context, we need to use its directory as context
                    context = path.dirname(actualDockerfilePath);
                    dockerfile = path.basename(actualDockerfilePath);
                }
                else {
                    // If the Dockerfile is inside the context, we just need to specify its relative path
                    dockerfile = relativePath;
                }
            }
            console.log(`Building image with context: ${context}, dockerfile: ${dockerfile}`);
            // Build the image
            const stream = await this.docker.buildImage({
                context,
                src: [dockerfile]
            }, {
                t: `mcp-server-${name}`,
                dockerfile
            });
            // Wait for the build to complete
            await new Promise((resolve, reject) => {
                this.docker.modem.followProgress(stream, (err, res) => {
                    if (err) {
                        console.error('Error building image:', err);
                        reject(err);
                    }
                    else {
                        console.log('Image built successfully');
                        resolve(res);
                    }
                });
            });
            // Check if a container with the same name already exists
            const containers = await this.docker.listContainers({ all: true });
            const existingContainer = containers.find(c => c.Names.includes(`/mcp-server-${name}`));
            if (existingContainer) {
                console.log(`Container with name mcp-server-${name} already exists, removing it`);
                const container = this.docker.getContainer(existingContainer.Id);
                if (existingContainer.State === 'running') {
                    await container.stop();
                }
                await container.remove();
            }
            // Create the container
            console.log(`Creating container for ${name}`);
            const container = await this.docker.createContainer({
                Image: `mcp-server-${name}`,
                name: `mcp-server-${name}`,
                ExposedPorts: {
                    '8000/tcp': {}
                },
                HostConfig: {
                    PortBindings: {
                        '8000/tcp': [
                            {
                                HostPort: '0' // Let Docker assign a random port
                            }
                        ]
                    },
                    Memory: this.options.memory * 1024 * 1024, // Convert MB to bytes
                    NanoCpus: this.options.cpus * 1000000000, // Convert CPUs to nanoCPUs
                    RestartPolicy: {
                        Name: 'on-failure',
                        MaximumRetryCount: 3
                    }
                }
            });
            // Start the container
            console.log(`Starting container for ${name}`);
            await container.start();
            // Wait a moment to ensure the container is running
            await new Promise(resolve => setTimeout(resolve, 2000));
            // Check if the container is running
            const info = await container.inspect();
            if (!info.State.Running) {
                throw new Error(`Container failed to start: ${info.State.Error || 'Unknown error'}`);
            }
            console.log(`Container for ${name} started successfully with ID ${container.id}`);
            return container.id;
        }
        catch (error) {
            console.error('Error starting container:', error);
            throw error;
        }
    }
    /**
     * Stop a container
     * @param containerId Container ID
     * @returns Promise that resolves when the container is stopped
     */
    async stopContainer(containerId) {
        try {
            const container = this.docker.getContainer(containerId);
            await container.stop();
            await container.remove();
        }
        catch (error) {
            console.error('Error stopping container:', error);
            throw error;
        }
    }
    /**
     * Get the endpoint for a container
     * @param containerId Container ID
     * @returns Promise that resolves to the container endpoint
     */
    async getContainerEndpoint(containerId) {
        try {
            const container = this.docker.getContainer(containerId);
            const info = await container.inspect();
            // Get the host port
            const hostPort = info.NetworkSettings.Ports['8000/tcp'][0].HostPort;
            return `http://localhost:${hostPort}`;
        }
        catch (error) {
            console.error('Error getting container endpoint:', error);
            throw error;
        }
    }
    /**
     * Get the logs for a container
     * @param containerId Container ID
     * @returns Promise that resolves to the container logs
     */
    async getContainerLogs(containerId) {
        try {
            const container = this.docker.getContainer(containerId);
            const logs = await container.logs({
                stdout: true,
                stderr: true,
                tail: 100
            });
            return logs.toString();
        }
        catch (error) {
            console.error('Error getting container logs:', error);
            throw error;
        }
    }
    /**
     * Check if a container is running
     * @param containerId Container ID
     * @returns Promise that resolves to true if the container is running
     */
    async isContainerRunning(containerId) {
        try {
            const container = this.docker.getContainer(containerId);
            const info = await container.inspect();
            return info.State.Running;
        }
        catch (error) {
            console.error('Error checking if container is running:', error);
            return false;
        }
    }
}
exports.DockerContainerManager = DockerContainerManager;
//# sourceMappingURL=dockerContainerManager.js.map