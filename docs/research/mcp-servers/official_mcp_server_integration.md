# Official MCP Server Integration Guide

## Overview

This document provides comprehensive guidance on integrating official Model Context Protocol (MCP) servers with the VS Code extension. It covers setup, configuration, authentication, usage patterns, and troubleshooting for the five key official MCP servers:

1. GitHub MCP Server
2. Docker MCP Server
3. Git MCP Server
4. Memory MCP Server
5. Filesystem MCP Server

## General Integration Process

The integration process for all official MCP servers follows these general steps:

1. **Installation**: Add the server from its GitHub repository
2. **Configuration**: Configure server-specific settings
3. **Authentication**: Set up required authentication credentials
4. **Starting**: Start the server and verify it's running
5. **Usage**: Use the server's tools through Qwen

### Prerequisites

Before integrating any MCP server, ensure you have:

- Docker installed and running (for containerized servers)
- Appropriate API keys or credentials for services (GitHub token, etc.)
- Sufficient disk space for server containers and data
- Network access to required services

## GitHub MCP Server

The GitHub MCP server provides tools for interacting with GitHub repositories, issues, pull requests, and other GitHub features.

### Installation

```
Repository URL: https://github.com/modelcontextprotocol/mcp-server-github
```

1. In the VS Code extension, open the MCP Servers view
2. Click the "Add Server from GitHub" button
3. Enter the repository URL
4. Wait for the server to be added

### Configuration

The GitHub MCP server requires the following configuration:

| Setting | Description | Default |
|---------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | None |
| `CACHE_TTL` | Cache time-to-live in seconds | 300 |
| `MAX_CONCURRENT_REQUESTS` | Maximum concurrent GitHub API requests | 5 |

To configure these settings:

1. Right-click the GitHub server in the MCP Servers view
2. Select "Configure Server"
3. Enter the required settings
4. Click "Save"

### Authentication

The GitHub MCP server requires a GitHub Personal Access Token (PAT) with the following scopes:

- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows
- `read:org` - Read organization membership
- `user` - Read all user profile data

To create a GitHub PAT:

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Select the required scopes
4. Copy the token and add it to the server configuration

### Usage Examples

#### List Repositories

```typescript
const response = await mcpClient.invokeTool('github', 'listRepositories', {
  visibility: 'all',
  affiliation: 'owner',
  sort: 'updated',
  direction: 'desc',
  per_page: 10
});

console.log('Repositories:', response.result);
```

#### Create Issue

```typescript
const response = await mcpClient.invokeTool('github', 'createIssue', {
  owner: 'username',
  repo: 'repository',
  title: 'Issue title',
  body: 'Issue description',
  labels: ['bug', 'high-priority']
});

console.log('Created issue:', response.result);
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication errors | Verify your GitHub token has the correct scopes and hasn't expired |
| Rate limiting | Increase the `CACHE_TTL` setting to reduce API calls |
| Timeout errors | Check your network connection and GitHub service status |
| Permission errors | Ensure your token has access to the requested repositories |

## Docker MCP Server

The Docker MCP server provides tools for managing Docker containers, images, volumes, and networks.

### Installation

```
Repository URL: https://github.com/modelcontextprotocol/mcp-server-docker
```

1. In the VS Code extension, open the MCP Servers view
2. Click the "Add Server from GitHub" button
3. Enter the repository URL
4. Wait for the server to be added

### Configuration

The Docker MCP server requires the following configuration:

| Setting | Description | Default |
|---------|-------------|---------|
| `DOCKER_HOST` | Docker daemon socket | unix:///var/run/docker.sock |
| `DOCKER_API_VERSION` | Docker API version | 1.41 |
| `MAX_CONTAINER_LOGS` | Maximum number of log lines to return | 100 |

To configure these settings:

1. Right-click the Docker server in the MCP Servers view
2. Select "Configure Server"
3. Enter the required settings
4. Click "Save"

### Authentication

The Docker MCP server requires access to the Docker daemon socket. On Linux, this typically requires the user to be in the `docker` group. On Windows and macOS, Docker Desktop typically handles this automatically.

For remote Docker daemons, you may need to configure TLS certificates:

1. Generate client and server certificates
2. Configure the Docker daemon to use TLS
3. Set the `DOCKER_HOST` to `tcp://hostname:port`
4. Set the `DOCKER_CERT_PATH` to the directory containing your certificates
5. Set `DOCKER_TLS_VERIFY` to `1`

### Usage Examples

#### List Containers

```typescript
const response = await mcpClient.invokeTool('docker', 'listContainers', {
  all: true,
  filters: JSON.stringify({
    status: ['running']
  })
});

console.log('Running containers:', response.result);
```

#### Pull Image

```typescript
const response = await mcpClient.invokeTool('docker', 'pullImage', {
  image: 'nginx:latest'
});

console.log('Pull result:', response.result);
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Socket permission errors | Ensure your user is in the `docker` group |
| Connection refused | Verify Docker daemon is running |
| API version mismatch | Update the `DOCKER_API_VERSION` setting |
| Resource limits | Check available disk space and memory |

## Git MCP Server

The Git MCP server provides tools for interacting with local Git repositories.

### Installation

```
Repository URL: https://github.com/modelcontextprotocol/mcp-server-git
```

1. In the VS Code extension, open the MCP Servers view
2. Click the "Add Server from GitHub" button
3. Enter the repository URL
4. Wait for the server to be added

### Configuration

The Git MCP server requires the following configuration:

| Setting | Description | Default |
|---------|-------------|---------|
| `WORKSPACE_DIR` | Directory containing Git repositories | /workspace |
| `GIT_BINARY_PATH` | Path to Git executable | git |
| `MAX_DIFF_SIZE` | Maximum diff size in bytes | 1048576 |

To configure these settings:

1. Right-click the Git server in the MCP Servers view
2. Select "Configure Server"
3. Enter the required settings
4. Click "Save"

### Authentication

The Git MCP server uses the Git credentials configured on the host system. For HTTPS repositories, this typically means:

1. Configure Git credential helper: `git config --global credential.helper store`
2. Set your Git username: `git config --global user.name "Your Name"`
3. Set your Git email: `git config --global user.email "your.email@example.com"`

For SSH repositories:

1. Generate SSH keys: `ssh-keygen -t ed25519 -C "your.email@example.com"`
2. Add your public key to GitHub/GitLab/etc.
3. Ensure the SSH agent is running: `eval "$(ssh-agent -s)"`
4. Add your private key to the agent: `ssh-add ~/.ssh/id_ed25519`

### Usage Examples

#### Clone Repository

```typescript
const response = await mcpClient.invokeTool('git', 'clone', {
  url: 'https://github.com/username/repository.git',
  directory: 'repository'
});

console.log('Clone result:', response.result);
```

#### Get Repository Status

```typescript
const response = await mcpClient.invokeTool('git', 'status', {
  repository: 'repository'
});

console.log('Repository status:', response.result);
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failures | Verify Git credentials are configured correctly |
| Repository not found | Check the `WORKSPACE_DIR` setting and repository path |
| Git command not found | Verify the `GIT_BINARY_PATH` setting |
| Large diff errors | Increase the `MAX_DIFF_SIZE` setting |

## Memory MCP Server

The Memory MCP server provides a knowledge graph-based persistent memory system for LLMs.

### Installation

```
Repository URL: https://github.com/modelcontextprotocol/mcp-server-memory
```

1. In the VS Code extension, open the MCP Servers view
2. Click the "Add Server from GitHub" button
3. Enter the repository URL
4. Wait for the server to be added

### Configuration

The Memory MCP server requires the following configuration:

| Setting | Description | Default |
|---------|-------------|---------|
| `STORAGE_DIR` | Directory for storing memory data | /data |
| `MEMORY_TYPE` | Type of memory storage (graph, vector, hybrid) | hybrid |
| `VECTOR_DIMENSIONS` | Dimensions for vector embeddings | 1536 |
| `EMBEDDING_MODEL` | Model to use for embeddings | all-MiniLM-L6-v2 |

To configure these settings:

1. Right-click the Memory server in the MCP Servers view
2. Select "Configure Server"
3. Enter the required settings
4. Click "Save"

### Authentication

The Memory MCP server typically doesn't require authentication as it's designed to be used locally. However, if you're using a remote embedding service, you may need to configure API keys:

1. Right-click the Memory server in the MCP Servers view
2. Select "Configure Server"
3. Set the `EMBEDDING_API_KEY` setting
4. Click "Save"

### Usage Examples

#### Store Memory

```typescript
const response = await mcpClient.invokeTool('memory', 'store', {
  content: 'The user prefers dark mode in their IDE.',
  metadata: {
    source: 'conversation',
    timestamp: Date.now()
  }
});

console.log('Memory stored:', response.result);
```

#### Retrieve Memories

```typescript
const response = await mcpClient.invokeTool('memory', 'retrieve', {
  query: 'user preferences',
  limit: 5
});

console.log('Retrieved memories:', response.result);
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Storage errors | Check disk space and permissions for the `STORAGE_DIR` |
| Embedding failures | Verify the embedding model is available or API key is valid |
| Slow retrieval | Consider changing the `MEMORY_TYPE` or optimizing vector dimensions |
| Memory corruption | Backup and reset the memory storage |

## Filesystem MCP Server

The Filesystem MCP server provides secure file operations with configurable access controls.

### Installation

```
Repository URL: https://github.com/modelcontextprotocol/mcp-server-filesystem
```

1. In the VS Code extension, open the MCP Servers view
2. Click the "Add Server from GitHub" button
3. Enter the repository URL
4. Wait for the server to be added

### Configuration

The Filesystem MCP server requires the following configuration:

| Setting | Description | Default |
|---------|-------------|---------|
| `ROOT_DIR` | Root directory for file operations | /workspace |
| `ALLOW_WRITE` | Allow write operations | true |
| `ALLOW_DELETE` | Allow delete operations | false |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 10485760 |
| `ALLOWED_EXTENSIONS` | Comma-separated list of allowed file extensions | * |

To configure these settings:

1. Right-click the Filesystem server in the MCP Servers view
2. Select "Configure Server"
3. Enter the required settings
4. Click "Save"

### Authentication

The Filesystem MCP server typically doesn't require authentication as it's designed to be used locally with access controls configured through settings.

### Usage Examples

#### List Directory

```typescript
const response = await mcpClient.invokeTool('filesystem', 'listDirectory', {
  path: '/'
});

console.log('Directory contents:', response.result);
```

#### Read File

```typescript
const response = await mcpClient.invokeTool('filesystem', 'readFile', {
  path: '/path/to/file.txt'
});

console.log('File contents:', response.result);
```

#### Write File

```typescript
const response = await mcpClient.invokeTool('filesystem', 'writeFile', {
  path: '/path/to/file.txt',
  content: 'Hello, world!',
  overwrite: true
});

console.log('Write result:', response.result);
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Check the server's access control settings |
| File not found | Verify the file path is correct and within the `ROOT_DIR` |
| File too large | Increase the `MAX_FILE_SIZE` setting |
| Extension not allowed | Add the file extension to the `ALLOWED_EXTENSIONS` setting |

## Integration Best Practices

### Server Management

1. **Automatic Startup**: Configure important servers to start automatically with the extension
2. **Resource Allocation**: Allocate appropriate resources (memory, CPU) to each server
3. **Health Monitoring**: Enable health checks to detect and recover from server failures
4. **Version Control**: Keep servers updated to the latest versions

### Authentication

1. **Credential Security**: Store credentials securely using VS Code's secret storage
2. **Scope Limitation**: Use the minimum required permissions for each service
3. **Token Rotation**: Regularly rotate API keys and tokens
4. **Audit Logging**: Enable logging for authentication events

### Performance Optimization

1. **Caching**: Configure appropriate cache settings for each server
2. **Parallel Requests**: Use concurrent requests where appropriate
3. **Resource Limits**: Set reasonable limits for memory, CPU, and disk usage
4. **Idle Shutdown**: Configure servers to shut down when idle to conserve resources

### Error Handling

1. **Graceful Degradation**: Handle server failures gracefully
2. **Retry Logic**: Implement exponential backoff for transient errors
3. **User Feedback**: Provide clear error messages to users
4. **Logging**: Log detailed error information for troubleshooting

## Conclusion

Integrating official MCP servers with the VS Code extension provides powerful capabilities for AI-assisted coding. By following the guidelines in this document, you can ensure a smooth integration process and optimal performance.

For more detailed information on each server, refer to the official documentation:

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [Model Context Protocol Servers Repository](https://github.com/modelcontextprotocol/servers)
- [TypeScript MCP SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
