# GitHub MCP Server Examples

This document provides examples of how to use the GitHub MCP server with the VS Code extension.

## Setup

Before using the GitHub MCP server, you need to add it to your MCP server list and configure it with your GitHub token.

### Adding the GitHub MCP Server

1. Open the MCP Servers view in VS Code
2. Click the "Add Official MCP Server" button
3. Select "GitHub MCP Server" from the list
4. Wait for the server to be added

### Configuring Authentication

1. Right-click the GitHub server in the MCP Servers view
2. Select "Configure Server"
3. Enter your GitHub Personal Access Token (PAT)
4. Click "Save"

Your GitHub PAT should have the following scopes:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows
- `read:org` - Read organization membership
- `user` - Read all user profile data

## Examples

### Example 1: List User Repositories

This example shows how to list the repositories owned by the authenticated user.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function listUserRepositories(mcpClient: McpClient) {
  try {
    // Invoke the listRepositories tool
    const response = await mcpClient.invokeTool('github', 'listRepositories', {
      visibility: 'all',
      affiliation: 'owner',
      sort: 'updated',
      direction: 'desc',
      per_page: 10
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the results
    const repositories = response.result;
    console.log(`Found ${repositories.length} repositories:`);
    
    for (const repo of repositories) {
      console.log(`- ${repo.name}: ${repo.description || 'No description'}`);
    }

    return repositories;
  } catch (error) {
    console.error('Error listing repositories:', error);
    vscode.window.showErrorMessage(`Error listing repositories: ${error}`);
    return [];
  }
}
```

### Example 2: Create an Issue

This example shows how to create an issue in a repository.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function createIssue(
  mcpClient: McpClient,
  owner: string,
  repo: string,
  title: string,
  body: string,
  labels: string[] = []
) {
  try {
    // Invoke the createIssue tool
    const response = await mcpClient.invokeTool('github', 'createIssue', {
      owner,
      repo,
      title,
      body,
      labels
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const issue = response.result;
    console.log(`Created issue #${issue.number}: ${issue.title}`);
    console.log(`URL: ${issue.html_url}`);

    // Show a success message
    vscode.window.showInformationMessage(`Created issue #${issue.number}: ${issue.title}`);

    return issue;
  } catch (error) {
    console.error('Error creating issue:', error);
    vscode.window.showErrorMessage(`Error creating issue: ${error}`);
    return null;
  }
}
```

### Example 3: Get Pull Requests

This example shows how to get pull requests for a repository.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function getPullRequests(
  mcpClient: McpClient,
  owner: string,
  repo: string,
  state: 'open' | 'closed' | 'all' = 'open'
) {
  try {
    // Invoke the listPullRequests tool
    const response = await mcpClient.invokeTool('github', 'listPullRequests', {
      owner,
      repo,
      state,
      sort: 'updated',
      direction: 'desc',
      per_page: 10
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the results
    const pullRequests = response.result;
    console.log(`Found ${pullRequests.length} pull requests:`);
    
    for (const pr of pullRequests) {
      console.log(`- #${pr.number}: ${pr.title} (${pr.state})`);
      console.log(`  Created by: ${pr.user.login}`);
      console.log(`  URL: ${pr.html_url}`);
    }

    return pullRequests;
  } catch (error) {
    console.error('Error getting pull requests:', error);
    vscode.window.showErrorMessage(`Error getting pull requests: ${error}`);
    return [];
  }
}
```

### Example 4: Create a Pull Request

This example shows how to create a pull request.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function createPullRequest(
  mcpClient: McpClient,
  owner: string,
  repo: string,
  title: string,
  body: string,
  head: string,
  base: string = 'main'
) {
  try {
    // Invoke the createPullRequest tool
    const response = await mcpClient.invokeTool('github', 'createPullRequest', {
      owner,
      repo,
      title,
      body,
      head,
      base
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const pullRequest = response.result;
    console.log(`Created pull request #${pullRequest.number}: ${pullRequest.title}`);
    console.log(`URL: ${pullRequest.html_url}`);

    // Show a success message
    vscode.window.showInformationMessage(`Created pull request #${pullRequest.number}: ${pullRequest.title}`);

    return pullRequest;
  } catch (error) {
    console.error('Error creating pull request:', error);
    vscode.window.showErrorMessage(`Error creating pull request: ${error}`);
    return null;
  }
}
```

### Example 5: Get Repository Contents

This example shows how to get the contents of a file in a repository.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function getFileContents(
  mcpClient: McpClient,
  owner: string,
  repo: string,
  path: string,
  ref: string = 'main'
) {
  try {
    // Invoke the getContent tool
    const response = await mcpClient.invokeTool('github', 'getContent', {
      owner,
      repo,
      path,
      ref
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const content = response.result;
    
    // If the content is a file, decode the content
    if (content.type === 'file') {
      // GitHub API returns content as base64-encoded
      const decodedContent = Buffer.from(content.content, 'base64').toString('utf8');
      console.log(`File contents of ${path}:`);
      console.log(decodedContent);
      return decodedContent;
    } else {
      // If it's a directory, list the items
      console.log(`Contents of directory ${path}:`);
      for (const item of content) {
        console.log(`- ${item.name} (${item.type})`);
      }
      return content;
    }
  } catch (error) {
    console.error('Error getting file contents:', error);
    vscode.window.showErrorMessage(`Error getting file contents: ${error}`);
    return null;
  }
}
```

### Example 6: Create a Repository

This example shows how to create a new repository.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function createRepository(
  mcpClient: McpClient,
  name: string,
  description: string = '',
  isPrivate: boolean = false
) {
  try {
    // Invoke the createRepository tool
    const response = await mcpClient.invokeTool('github', 'createRepository', {
      name,
      description,
      private: isPrivate,
      auto_init: true
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const repository = response.result;
    console.log(`Created repository: ${repository.full_name}`);
    console.log(`URL: ${repository.html_url}`);

    // Show a success message
    vscode.window.showInformationMessage(`Created repository: ${repository.full_name}`);

    return repository;
  } catch (error) {
    console.error('Error creating repository:', error);
    vscode.window.showErrorMessage(`Error creating repository: ${error}`);
    return null;
  }
}
```

### Example 7: Search Repositories

This example shows how to search for repositories on GitHub.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function searchRepositories(
  mcpClient: McpClient,
  query: string,
  sort: 'stars' | 'forks' | 'updated' = 'stars',
  order: 'asc' | 'desc' = 'desc'
) {
  try {
    // Invoke the searchRepositories tool
    const response = await mcpClient.invokeTool('github', 'searchRepositories', {
      q: query,
      sort,
      order,
      per_page: 10
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the results
    const searchResults = response.result;
    console.log(`Found ${searchResults.total_count} repositories matching "${query}":`);
    
    for (const repo of searchResults.items) {
      console.log(`- ${repo.full_name}: ${repo.description || 'No description'}`);
      console.log(`  Stars: ${repo.stargazers_count}, Forks: ${repo.forks_count}`);
      console.log(`  URL: ${repo.html_url}`);
    }

    return searchResults.items;
  } catch (error) {
    console.error('Error searching repositories:', error);
    vscode.window.showErrorMessage(`Error searching repositories: ${error}`);
    return [];
  }
}
```

### Example 8: Get User Information

This example shows how to get information about a GitHub user.

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { McpClient } from './mcp-client/mcpClient';

// Assume mcpClient is already initialized
async function getUserInfo(
  mcpClient: McpClient,
  username: string
) {
  try {
    // Invoke the getUser tool
    const response = await mcpClient.invokeTool('github', 'getUser', {
      username
    });

    if (response.status === 'error') {
      throw new Error(response.error);
    }

    // Process the result
    const user = response.result;
    console.log(`User information for ${user.login}:`);
    console.log(`- Name: ${user.name || 'Not specified'}`);
    console.log(`- Bio: ${user.bio || 'Not specified'}`);
    console.log(`- Location: ${user.location || 'Not specified'}`);
    console.log(`- Public repositories: ${user.public_repos}`);
    console.log(`- Followers: ${user.followers}`);
    console.log(`- Following: ${user.following}`);
    console.log(`- URL: ${user.html_url}`);

    return user;
  } catch (error) {
    console.error('Error getting user information:', error);
    vscode.window.showErrorMessage(`Error getting user information: ${error}`);
    return null;
  }
}
```

## Integration with Qwen

You can use the GitHub MCP server with Qwen to perform GitHub operations based on natural language instructions. Here's an example of how to integrate the GitHub MCP server with Qwen:

```typescript
// Import the required modules
import * as vscode from 'vscode';
import { QwenApiClient } from './qwenApi';
import { McpClient } from './mcp-client/mcpClient';
import { McpQwenBridge } from './mcp/mcpQwenBridge';

// Assume qwenClient, mcpClient, and mcpQwenBridge are already initialized
async function processGitHubRequest(
  qwenClient: QwenApiClient,
  mcpClient: McpClient,
  mcpQwenBridge: McpQwenBridge,
  request: string
) {
  try {
    // Process the request using the MCP-Qwen bridge
    const response = await mcpQwenBridge.processRequest(request);

    // Show the response
    vscode.window.showInformationMessage('GitHub operation completed successfully');
    
    return response;
  } catch (error) {
    console.error('Error processing GitHub request:', error);
    vscode.window.showErrorMessage(`Error processing GitHub request: ${error}`);
    return null;
  }
}

// Example usage
// processGitHubRequest(qwenClient, mcpClient, mcpQwenBridge, 'Create a new issue in my repository called "example-repo" with the title "Fix bug in login form" and description "The login form doesn\'t validate email addresses correctly."');
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Check that your GitHub PAT has the correct scopes
2. Verify that the token is still valid (not expired)
3. Try regenerating the token in your GitHub settings
4. Check the server logs for detailed error messages

### Rate Limiting

GitHub API has rate limits. If you encounter rate limiting issues:

1. Use conditional requests with ETags to reduce API usage
2. Implement caching for frequently accessed data
3. Increase the `CACHE_TTL` setting in the server configuration
4. Consider using a GitHub App instead of a PAT for higher rate limits

### Connection Issues

If you have trouble connecting to the GitHub API:

1. Check your internet connection
2. Verify that GitHub services are operational
3. Check if your network has any firewall rules blocking GitHub
4. Try restarting the MCP server

## Additional Resources

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub API Rate Limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Creating a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub MCP Server Repository](https://github.com/modelcontextprotocol/mcp-server-github)
