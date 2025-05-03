# Containerizing MCP Tools for VSCode Extension

## Introduction

This document outlines the approach for containerizing Model-Control-Protocol (MCP) tools to be used with our VSCode extension. By containerizing these tools, we can provide a consistent, isolated environment for each tool while enabling dynamic instantiation and efficient resource management.

## What is MCP?

Model-Control-Protocol (MCP) is a standardized protocol for AI models to interact with external tools. It allows models to:

1. Discover available tools
2. Understand tool capabilities and parameters
3. Invoke tools with appropriate arguments
4. Process tool results in a structured format

Qwen-Agent provides native support for MCP, making it an ideal framework for our hierarchical agent system.

## Benefits of Containerization

Containerizing MCP tools offers several advantages:

1. **Isolation**: Each tool runs in its own environment, preventing conflicts
2. **Consistency**: Tools behave the same way regardless of the host system
3. **Portability**: Containers can run on any system with Docker support
4. **Scalability**: Multiple instances can be created as needed
5. **Resource Management**: Container resources can be limited and monitored
6. **Security**: Containers provide an additional security boundary

## Container Architecture

Our containerized MCP tools will follow this architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                Docker Container                              │
│                                                             │
│  ┌───────────────────────┐      ┌───────────────────────┐   │
│  │  MCP Server           │      │  Tool Implementation  │   │
│  │                       │      │                       │   │
│  │ - API Endpoint        │◄────►│ - Core Functionality  │   │
│  │ - Schema Definition   │      │ - Resource Management │   │
│  │ - Request Handling    │      │ - Error Handling      │   │
│  └───────────────┬───────┘      └───────────────────────┘   │
│                  │                                          │
│                  ▼                                          │
│  ┌───────────────────────┐                                  │
│  │  Container Interface  │                                  │
│  │                       │                                  │
│  │ - Health Endpoint     │                                  │
│  │ - Metrics Endpoint    │                                  │
│  │ - Lifecycle Hooks     │                                  │
│  └───────────────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core MCP Tools for DevOps

We will containerize the following core MCP tools for our DevOps workflow:

### 1. GitHub MCP Tool

This tool provides GitHub integration capabilities:

- Repository management (clone, fork, create)
- Branch operations (create, merge, delete)
- Pull request management (create, review, merge)
- Issue tracking (create, update, close)
- Commit operations (commit, push, pull)
- Code review assistance

### 2. Docker MCP Tool

This tool provides Docker management capabilities:

- Image management (build, pull, push)
- Container lifecycle (create, start, stop, remove)
- Volume management
- Network configuration
- Docker Compose operations
- Registry interactions

### 3. Testing MCP Tool

This tool provides testing capabilities:

- Test discovery and execution
- Test result analysis
- Coverage reporting
- Test generation
- Mocking and stubbing
- Performance testing

### 4. CI/CD MCP Tool

This tool provides CI/CD pipeline capabilities:

- Pipeline definition and execution
- Build automation
- Deployment management
- Release coordination
- Environment configuration
- Monitoring and reporting

## Implementation Details

### Dockerfile Template

Here's a template Dockerfile for creating MCP tool containers:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server and tool implementation
COPY mcp_server.py .
COPY tool_implementation.py .

# Expose MCP server port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start MCP server
CMD ["python", "mcp_server.py"]
```

### MCP Server Implementation

Here's a simplified implementation of an MCP server in Python:

```python
from flask import Flask, request, jsonify
import json
import tool_implementation

app = Flask(__name__)

# Tool schema definition
TOOL_SCHEMA = {
    "name": "github_tool",
    "description": "GitHub integration for repository management, PR handling, and more",
    "functions": [
        {
            "name": "create_branch",
            "description": "Create a new branch in a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name (owner/repo)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Name of the branch to create"
                    },
                    "base": {
                        "type": "string",
                        "description": "Base branch to create from"
                    }
                },
                "required": ["repo", "branch", "base"]
            }
        },
        # Additional function definitions...
    ]
}

@app.route("/schema", methods=["GET"])
def get_schema():
    """Return the tool schema"""
    return jsonify(TOOL_SCHEMA)

@app.route("/invoke", methods=["POST"])
def invoke_tool():
    """Invoke a tool function"""
    data = request.json
    function_name = data.get("function")
    parameters = data.get("parameters", {})

    # Call the appropriate function in the tool implementation
    if hasattr(tool_implementation, function_name):
        try:
            result = getattr(tool_implementation, function_name)(**parameters)
            return jsonify({"status": "success", "result": result})
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 400
    else:
        return jsonify({"status": "error", "error": f"Function {function_name} not found"}), 404

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### Tool Implementation Example

Here's a simplified implementation of the GitHub tool:

```python
import os
import requests
from github import Github

# Initialize GitHub client
github_token = os.environ.get("GITHUB_TOKEN")
g = Github(github_token)

def create_branch(repo, branch, base):
    """Create a new branch in a repository"""
    try:
        # Get the repository
        repository = g.get_repo(repo)

        # Get the base branch
        base_branch = repository.get_branch(base)

        # Create the new branch
        repository.create_git_ref(
            ref=f"refs/heads/{branch}",
            sha=base_branch.commit.sha
        )

        return {
            "success": True,
            "message": f"Branch '{branch}' created successfully from '{base}'",
            "repo": repo,
            "branch": branch
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_pull_request(repo, title, body, head, base):
    """Create a pull request"""
    try:
        # Get the repository
        repository = g.get_repo(repo)

        # Create the pull request
        pr = repository.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )

        return {
            "success": True,
            "message": f"Pull request created successfully",
            "pr_number": pr.number,
            "pr_url": pr.html_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Additional functions...
```

## Container Management in VSCode Extension

To manage containerized MCP tools from our VSCode extension, we'll implement a Container Manager class:

```typescript
// container-manager.ts
import * as vscode from 'vscode';
import * as Docker from 'dockerode';
import * as path from 'path';

export class ContainerManager {
    private docker: Docker;
    private activeContainers: Map<string, string> = new Map(); // tool name -> container ID

    constructor() {
        // Initialize Docker client
        this.docker = new Docker();
    }

    /**
     * Start a containerized MCP tool
     */
    async startTool(toolName: string): Promise<string> {
        // Check if container is already running
        if (this.activeContainers.has(toolName)) {
            return this.getToolUrl(toolName);
        }

        try {
            // Pull the image if needed
            await this.pullImage(toolName);

            // Create and start the container
            const container = await this.docker.createContainer({
                Image: `qwen-mcp-${toolName}:latest`,
                ExposedPorts: { '8080/tcp': {} },
                HostConfig: {
                    PortBindings: { '8080/tcp': [{ HostPort: '0' }] }, // Assign random port
                    RestartPolicy: { Name: 'unless-stopped' }
                },
                Env: this.getToolEnvironment(toolName)
            });

            await container.start();

            // Get container info
            const containerInfo = await container.inspect();
            const containerId = containerInfo.Id;
            const port = containerInfo.NetworkSettings.Ports['8080/tcp'][0].HostPort;

            // Store container info
            this.activeContainers.set(toolName, containerId);

            // Return the tool URL
            return `http://localhost:${port}`;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start ${toolName} tool: ${error.message}`);
            throw error;
        }
    }

    /**
     * Stop a containerized MCP tool
     */
    async stopTool(toolName: string): Promise<void> {
        const containerId = this.activeContainers.get(toolName);
        if (!containerId) {
            return;
        }

        try {
            const container = this.docker.getContainer(containerId);
            await container.stop();
            await container.remove();
            this.activeContainers.delete(toolName);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to stop ${toolName} tool: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get the URL for a running tool
     */
    async getToolUrl(toolName: string): Promise<string> {
        const containerId = this.activeContainers.get(toolName);
        if (!containerId) {
            throw new Error(`Tool ${toolName} is not running`);
        }

        try {
            const container = this.docker.getContainer(containerId);
            const containerInfo = await container.inspect();
            const port = containerInfo.NetworkSettings.Ports['8080/tcp'][0].HostPort;
            return `http://localhost:${port}`;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get URL for ${toolName} tool: ${error.message}`);
            throw error;
        }
    }

    /**
     * Pull the Docker image for a tool
     */
    private async pullImage(toolName: string): Promise<void> {
        const imageName = `qwen-mcp-${toolName}:latest`;

        try {
            // Check if image exists locally
            const images = await this.docker.listImages();
            const imageExists = images.some(image =>
                image.RepoTags && image.RepoTags.includes(imageName)
            );

            if (!imageExists) {
                vscode.window.showInformationMessage(`Downloading ${toolName} tool...`);

                // Pull the image
                await new Promise<void>((resolve, reject) => {
                    this.docker.pull(imageName, {}, (err, stream) => {
                        if (err) {
                            reject(err);
                            return;
                        }

                        this.docker.modem.followProgress(stream, (err) => {
                            if (err) {
                                reject(err);
                                return;
                            }
                            resolve();
                        });
                    });
                });

                vscode.window.showInformationMessage(`${toolName} tool downloaded successfully`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to download ${toolName} tool: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get environment variables for a tool
     */
    private getToolEnvironment(toolName: string): string[] {
        const env: string[] = [];

        // Add tool-specific environment variables
        switch (toolName) {
            case 'github':
                const githubToken = vscode.workspace.getConfiguration('devopsExtension').get('githubToken');
                if (githubToken) {
                    env.push(`GITHUB_TOKEN=${githubToken}`);
                }
                break;

            case 'docker':
                // Docker tool might need access to the Docker socket
                env.push('DOCKER_HOST=unix:///var/run/docker.sock');
                break;

            // Add other tool-specific environment variables
        }

        return env;
    }

    /**
     * Stop all running containers
     */
    async stopAllTools(): Promise<void> {
        for (const toolName of this.activeContainers.keys()) {
            await this.stopTool(toolName);
        }
    }
}
```

## Integration with Qwen-Agent

To integrate our containerized MCP tools with Qwen-Agent, we'll use the MCP configuration feature:

```python
from qwen_agent.agents import Assistant

# Define LLM configuration
llm_cfg = {
    'model': 'Qwen3-30B-A3B',
    'model_server': 'http://localhost:8000/v1',
    'api_key': 'EMPTY',
}

# Define MCP tools configuration
mcp_tools = {
    'mcpServers': {
        'github': {
            'url': 'http://localhost:8081',  # Will be dynamically assigned
        },
        'docker': {
            'url': 'http://localhost:8082',  # Will be dynamically assigned
        },
        'testing': {
            'url': 'http://localhost:8083',  # Will be dynamically assigned
        },
        'ci_cd': {
            'url': 'http://localhost:8084',  # Will be dynamically assigned
        }
    }
}

# Create agent with MCP tools
agent = Assistant(llm=llm_cfg, function_list=[mcp_tools])

# Example usage
messages = [
    {'role': 'user', 'content': 'Create a new branch called "feature/new-feature" from "main" in the repository "username/repo"'}
]

for response in agent.run(messages=messages):
    print(response)
```

## Conclusion

Containerizing MCP tools for our VSCode extension provides a flexible, scalable approach to integrating various DevOps tools with our hierarchical agent system. By leveraging Docker containers and the MCP protocol, we can create a consistent, isolated environment for each tool while enabling dynamic instantiation and efficient resource management.

The integration with Qwen-Agent allows our hierarchical agent system to seamlessly interact with these containerized tools, providing a comprehensive DevOps guidance system that can adapt to various user needs and workflows.

## Next Steps

1. Implement the core MCP tools (GitHub, Docker, Testing, CI/CD)
2. Create Docker images for each tool
3. Implement the Container Manager in the VSCode extension
4. Integrate with the hierarchical agent system
5. Test the system with various DevOps scenarios

## References

1. [Qwen-Agent Documentation](https://qwen.readthedocs.io/en/latest/framework/qwen_agent.html)
2. [Docker SDK for Node.js](https://github.com/apocas/dockerode)
3. [Flask Documentation](https://flask.palletsprojects.com/)
4. [GitHub API Documentation](https://docs.github.com/en/rest)
5. [VS Code Extension API](https://code.visualstudio.com/api)
