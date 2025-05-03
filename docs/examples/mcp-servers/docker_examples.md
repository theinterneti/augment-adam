# Docker MCP Server Examples

This document provides examples of how to use the Docker MCP server with the VS Code extension.

## Setup

Before using the Docker MCP server, you need to add it to your MCP server list and configure it.

### Adding the Docker MCP Server

1. Open the MCP Servers view in VS Code
2. Click the "Add Official MCP Server" button
3. Select "Docker MCP Server" from the list
4. Wait for the server to be added

### Configuring the Docker MCP Server

1. Right-click the Docker server in the MCP Servers view
2. Select "Configure Server"
3. Configure the following settings:
   - `DOCKER_HOST`: Docker daemon socket (default: unix:///var/run/docker.sock)
   - `DOCKER_API_VERSION`: Docker API version (default: 1.41)
   - `MAX_CONTAINER_LOGS`: Maximum number of log lines to return (default: 100)
4. Click "Save"

## Examples

### Example 1: List Containers

This example shows how to list all Docker containers.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function listContainers(mcpClient: McpClient, showAll: boolean = true) {
  try {
    // Invoke the listContainers tool
    const response = await mcpClient.invokeTool('docker', 'listContainers', {
      all: showAll
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the results
    const containers = response.result;
    console.log(`Found ${containers.length} containers:`);
    
    for (const container of containers) {
      const status = container.State === 'running' ? 'Running' : container.State;
      const name = container.Names[0].replace(/^\//, '');
      console.log(`- ${name} (${container.Image}): ${status}`);
    }

    return containers;
  } catch (error) {
    console.error('Error listing containers:', error);
    vscode.window.showErrorMessage(`Error listing containers: ${error}`);
    return [];
  }
}
```

### Example 2: Pull an Image

This example shows how to pull a Docker image.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function pullImage(mcpClient: McpClient, image: string) {
  try {
    // Show a progress notification
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: `Pulling image ${image}...`,
      cancellable: false
    }, async () => {
      // Invoke the pullImage tool
      const response = await mcpClient.invokeTool('docker', 'pullImage', {
        image
      });

      if (response.status === 'error') {
        throw new Error(response.error);
      }

      // Process the result
      console.log(`Successfully pulled image: ${image}`);
      vscode.window.showInformationMessage(`Successfully pulled image: ${image}`);
    });
  } catch (error) {
    console.error('Error pulling image:', error);
    vscode.window.showErrorMessage(`Error pulling image: ${error}`);
  }
}
```

### Example 3: Create and Start a Container

This example shows how to create and start a Docker container.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function createAndStartContainer(
  mcpClient: McpClient,
  name: string,
  image: string,
  ports: Record<string, string> = {},
  volumes: Record<string, string> = {},
  env: string[] = []
) {
  try {
    // Create the container
    const createResponse = await mcpClient.invokeTool('docker', 'createContainer', {
      name,
      image,
      HostConfig: {
        PortBindings: Object.entries(ports).reduce((acc, [containerPort, hostPort]) => {
          acc[`${containerPort}/tcp`] = [{ HostPort: hostPort }];
          return acc;
        }, {} as Record<string, any>),
        Binds: Object.entries(volumes).map(([hostPath, containerPath]) => `${hostPath}:${containerPath}`)
      },
      Env: env
    });

    if (createResponse.status === 'error') {
      throw new Error(createResponse.error);
    }

    const containerId = createResponse.result.Id;
    console.log(`Created container with ID: ${containerId}`);

    // Start the container
    const startResponse = await mcpClient.invokeTool('docker', 'startContainer', {
      id: containerId
    });

    if (startResponse.status === 'error') {
      throw new Error(startResponse.error);
    }

    console.log(`Started container: ${name}`);
    vscode.window.showInformationMessage(`Started container: ${name}`);

    return containerId;
  } catch (error) {
    console.error('Error creating and starting container:', error);
    vscode.window.showErrorMessage(`Error creating and starting container: ${error}`);
    return null;
  }
}
```

### Example 4: Stop and Remove a Container

This example shows how to stop and remove a Docker container.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function stopAndRemoveContainer(mcpClient: McpClient, containerId: string) {
  try {
    // Stop the container
    const stopResponse = await mcpClient.invokeTool('docker', 'stopContainer', {
      id: containerId
    });

    if (stopResponse.status === 'error') {
      throw new Error(stopResponse.error);
    }

    console.log(`Stopped container: ${containerId}`);

    // Remove the container
    const removeResponse = await mcpClient.invokeTool('docker', 'removeContainer', {
      id: containerId
    });

    if (removeResponse.status === 'error') {
      throw new Error(removeResponse.error);
    }

    console.log(`Removed container: ${containerId}`);
    vscode.window.showInformationMessage(`Container ${containerId} stopped and removed`);

    return true;
  } catch (error) {
    console.error('Error stopping and removing container:', error);
    vscode.window.showErrorMessage(`Error stopping and removing container: ${error}`);
    return false;
  }
}
```

### Example 5: Get Container Logs

This example shows how to get logs from a Docker container.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function getContainerLogs(
  mcpClient: McpClient,
  containerId: string,
  tail: number = 100,
  timestamps: boolean = true
) {
  try {
    // Invoke the getContainerLogs tool
    const response = await mcpClient.invokeTool('docker', 'getContainerLogs', {
      id: containerId,
      tail: `${tail}`,
      timestamps
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const logs = response.result;
    console.log(`Logs for container ${containerId}:`);
    console.log(logs);

    // Show logs in a new editor
    const document = await vscode.workspace.openTextDocument({
      content: logs,
      language: 'log'
    });
    await vscode.window.showTextDocument(document);

    return logs;
  } catch (error) {
    console.error('Error getting container logs:', error);
    vscode.window.showErrorMessage(`Error getting container logs: ${error}`);
    return null;
  }
}
```

### Example 6: List Images

This example shows how to list Docker images.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function listImages(mcpClient: McpClient, showAll: boolean = false) {
  try {
    // Invoke the listImages tool
    const response = await mcpClient.invokeTool('docker', 'listImages', {
      all: showAll
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the results
    const images = response.result;
    console.log(`Found ${images.length} images:`);
    
    for (const image of images) {
      const tags = image.RepoTags || ['<none>:<none>'];
      const size = (image.Size / (1024 * 1024)).toFixed(2) + ' MB';
      console.log(`- ${tags.join(', ')} (${size})`);
    }

    return images;
  } catch (error) {
    console.error('Error listing images:', error);
    vscode.window.showErrorMessage(`Error listing images: ${error}`);
    return [];
  }
}
```

### Example 7: Build an Image

This example shows how to build a Docker image from a Dockerfile.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function buildImage(
  mcpClient: McpClient,
  contextPath: string,
  tag: string,
  dockerfile: string = 'Dockerfile'
) {
  try {
    // Show a progress notification
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: `Building image ${tag}...`,
      cancellable: false
    }, async () => {
      // Invoke the buildImage tool
      const response = await mcpClient.invokeTool('docker', 'buildImage', {
        context: contextPath,
        tag,
        dockerfile
      });

      if (response.status === 'error') {
        throw new Error(response.error);
      }

      // Process the result
      console.log(`Successfully built image: ${tag}`);
      vscode.window.showInformationMessage(`Successfully built image: ${tag}`);
    });
  } catch (error) {
    console.error('Error building image:', error);
    vscode.window.showErrorMessage(`Error building image: ${error}`);
  }
}
```

### Example 8: Inspect a Container

This example shows how to inspect a Docker container to get detailed information.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function inspectContainer(mcpClient: McpClient, containerId: string) {
  try {
    // Invoke the inspectContainer tool
    const response = await mcpClient.invokeTool('docker', 'inspectContainer', {
      id: containerId
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const containerInfo = response.result[0];
    console.log(`Container information for ${containerId}:`);
    console.log(`- Name: ${containerInfo.Name.replace(/^\//, '')}`);
    console.log(`- Image: ${containerInfo.Config.Image}`);
    console.log(`- Status: ${containerInfo.State.Status}`);
    console.log(`- Created: ${new Date(containerInfo.Created).toLocaleString()}`);
    console.log(`- Ports: ${JSON.stringify(containerInfo.NetworkSettings.Ports)}`);
    console.log(`- Volumes: ${JSON.stringify(containerInfo.Mounts)}`);

    return containerInfo;
  } catch (error) {
    console.error('Error inspecting container:', error);
    vscode.window.showErrorMessage(`Error inspecting container: ${error}`);
    return null;
  }
}
```

## Integration with Qwen

You can use the Docker MCP server with Qwen to perform Docker operations based on natural language instructions. Here's an example of how to integrate the Docker MCP server with Qwen:

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { QwenApiClient } from './qwenApi';
import { McpClient } from './mcp-client/mcpClient';
import { McpQwenBridge } from './mcp/mcpQwenBridge';

// Assume qwenClient, mcpClient, and mcpQwenBridge are already initialized
async function processDockerRequest(
  qwenClient: QwenApiClient,
  mcpClient: McpClient,
  mcpQwenBridge: McpQwenBridge,
  request: string
) {
  try {
    // Process the request using the MCP-Qwen bridge
    const response = await mcpQwenBridge.processRequest(request);

    // Show the response
    vscode.window.showInformationMessage('Docker operation completed successfully');
    
    return response;
  } catch (error) {
    console.error('Error processing Docker request:', error);
    vscode.window.showErrorMessage(`Error processing Docker request: ${error}`);
    return null;
  }
}

// Example usage
// processDockerRequest(qwenClient, mcpClient, mcpQwenBridge, 'Pull the latest nginx image and create a container named "web-server" that maps port 80 to port 8080 on the host');
```

## Docker Compose Examples

The Docker MCP server also supports Docker Compose operations. Here are some examples:

### Example 9: Docker Compose Up

This example shows how to start services defined in a Docker Compose file.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function dockerComposeUp(
  mcpClient: McpClient,
  composeFilePath: string,
  projectName: string,
  detach: boolean = true
) {
  try {
    // Show a progress notification
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: `Starting Docker Compose services...`,
      cancellable: false
    }, async () => {
      // Invoke the composeUp tool
      const response = await mcpClient.invokeTool('docker', 'composeUp', {
        file: composeFilePath,
        projectName,
        detach
      });

      if (response.status === 'error') {
        throw new Error(response.error);
      }

      // Process the result
      console.log(`Successfully started Docker Compose services for project: ${projectName}`);
      vscode.window.showInformationMessage(`Successfully started Docker Compose services for project: ${projectName}`);
    });
  } catch (error) {
    console.error('Error starting Docker Compose services:', error);
    vscode.window.showErrorMessage(`Error starting Docker Compose services: ${error}`);
  }
}
```

### Example 10: Docker Compose Down

This example shows how to stop and remove services defined in a Docker Compose file.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function dockerComposeDown(
  mcpClient: McpClient,
  composeFilePath: string,
  projectName: string,
  removeVolumes: boolean = false
) {
  try {
    // Show a progress notification
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: `Stopping Docker Compose services...`,
      cancellable: false
    }, async () => {
      // Invoke the composeDown tool
      const response = await mcpClient.invokeTool('docker', 'composeDown', {
        file: composeFilePath,
        projectName,
        removeVolumes
      });

      if (response.status === 'error') {
        throw new Error(response.error);
      }

      // Process the result
      console.log(`Successfully stopped Docker Compose services for project: ${projectName}`);
      vscode.window.showInformationMessage(`Successfully stopped Docker Compose services for project: ${projectName}`);
    });
  } catch (error) {
    console.error('Error stopping Docker Compose services:', error);
    vscode.window.showErrorMessage(`Error stopping Docker Compose services: ${error}`);
  }
}
```

## Troubleshooting

### Docker Daemon Connection Issues

If you encounter issues connecting to the Docker daemon:

1. Verify that Docker is running on your system
2. Check that the `DOCKER_HOST` setting is correct
3. Ensure that your user has permission to access the Docker socket
4. On Linux, add your user to the `docker` group: `sudo usermod -aG docker $USER`

### API Version Mismatch

If you see API version mismatch errors:

1. Check your Docker version with `docker version`
2. Update the `DOCKER_API_VERSION` setting to match your Docker API version
3. Consider updating Docker to the latest version

### Permission Issues

If you encounter permission issues:

1. Check that your user has permission to access the Docker socket
2. On Linux, verify that the Docker socket has the correct permissions
3. Consider running Docker in rootless mode if security is a concern

### Resource Limits

If containers fail to start due to resource limits:

1. Check available disk space with `df -h`
2. Verify available memory with `free -m`
3. Adjust Docker's resource limits in Docker Desktop settings
4. Clean up unused containers and images with `docker system prune`

## Additional Resources

- [Docker API Documentation](https://docs.docker.com/engine/api/)
- [Docker CLI Documentation](https://docs.docker.com/engine/reference/commandline/cli/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker MCP Server Repository](https://github.com/modelcontextprotocol/mcp-server-docker)
