# Docker MCP Tools

This document provides detailed information about the tools available through the Docker Model Context Protocol (MCP) server.

## Knowledge Graph Tools

### create_entities

Create multiple new entities in the knowledge graph.

**Input Schema:**
```json
{
  "entities": [
    {
      "name": "string",
      "entityType": "string",
      "observations": ["string"]
    }
  ]
}
```

### create_relations

Create multiple new relations between entities in the knowledge graph. Relations should be in active voice.

**Input Schema:**
```json
{
  "relations": [
    {
      "from": "string",
      "to": "string",
      "relationType": "string"
    }
  ]
}
```

### add_observations

Add new observations to existing entities in the knowledge graph.

**Input Schema:**
```json
{
  "observations": [
    {
      "entityName": "string",
      "contents": ["string"]
    }
  ]
}
```

### delete_entities

Delete multiple entities and their associated relations from the knowledge graph.

**Input Schema:**
```json
{
  "entityNames": ["string"]
}
```

### delete_observations

Delete specific observations from entities in the knowledge graph.

**Input Schema:**
```json
{
  "deletions": [
    {
      "entityName": "string",
      "observations": ["string"]
    }
  ]
}
```

### delete_relations

Delete multiple relations from the knowledge graph.

**Input Schema:**
```json
{
  "relations": [
    {
      "from": "string",
      "to": "string",
      "relationType": "string"
    }
  ]
}
```

### read_graph

Read the entire knowledge graph.

**Input Schema:**
```json
{}
```

### search_nodes

Search for nodes in the knowledge graph based on a query.

**Input Schema:**
```json
{
  "query": "string"
}
```

### open_nodes

Open specific nodes in the knowledge graph by their names.

**Input Schema:**
```json
{
  "names": ["string"]
}
```

## GitHub Integration Tools

### create_or_update_file

Create or update a single file in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "path": "string",
  "content": "string",
  "message": "string",
  "branch": "string",
  "sha": "string" // Required when updating existing files
}
```

### search_repositories

Search for GitHub repositories.

**Input Schema:**
```json
{
  "query": "string",
  "page": "number", // Optional
  "perPage": "number" // Optional
}
```

### create_repository

Create a new GitHub repository in your account.

**Input Schema:**
```json
{
  "name": "string",
  "description": "string", // Optional
  "private": "boolean", // Optional
  "autoInit": "boolean" // Optional
}
```

### get_file_contents

Get the contents of a file or directory from a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "path": "string",
  "branch": "string" // Optional
}
```

### push_files

Push multiple files to a GitHub repository in a single commit.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "branch": "string",
  "files": [
    {
      "path": "string",
      "content": "string"
    }
  ],
  "message": "string"
}
```

### create_issue

Create a new issue in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "title": "string",
  "body": "string", // Optional
  "assignees": ["string"], // Optional
  "labels": ["string"], // Optional
  "milestone": "number" // Optional
}
```

### create_pull_request

Create a new pull request in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "title": "string",
  "body": "string", // Optional
  "head": "string",
  "base": "string",
  "draft": "boolean", // Optional
  "maintainerCanModify": "boolean" // Optional
}
```

### fork_repository

Fork a GitHub repository to your account or specified organization.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "organization": "string" // Optional
}
```

### create_branch

Create a new branch in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "branch": "string",
  "fromBranch": "string" // Optional
}
```

### list_commits

Get list of commits of a branch in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "page": "number", // Optional
  "perPage": "number", // Optional
  "sha": "string" // Optional
}
```

### list_issues

List issues in a GitHub repository with filtering options.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "state": "string", // Optional: "open", "closed", "all"
  "sort": "string", // Optional: "created", "updated", "comments"
  "direction": "string", // Optional: "asc", "desc"
  "since": "string", // Optional
  "labels": ["string"], // Optional
  "page": "number", // Optional
  "perPage": "number" // Optional
}
```

### update_issue

Update an existing issue in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "issueNumber": "number",
  "title": "string", // Optional
  "body": "string", // Optional
  "state": "string", // Optional: "open", "closed"
  "assignees": ["string"], // Optional
  "labels": ["string"], // Optional
  "milestone": "number" // Optional
}
```

### add_issue_comment

Add a comment to an existing issue.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "issueNumber": "number",
  "body": "string"
}
```

### search_code

Search for code across GitHub repositories.

**Input Schema:**
```json
{
  "q": "string",
  "order": "string", // Optional: "asc", "desc"
  "perPage": "number", // Optional
  "page": "number" // Optional
}
```

### search_issues

Search for issues and pull requests across GitHub repositories.

**Input Schema:**
```json
{
  "q": "string",
  "sort": "string", // Optional
  "order": "string", // Optional: "asc", "desc"
  "perPage": "number", // Optional
  "page": "number" // Optional
}
```

### search_users

Search for users on GitHub.

**Input Schema:**
```json
{
  "q": "string",
  "sort": "string", // Optional: "followers", "repositories", "joined"
  "order": "string", // Optional: "asc", "desc"
  "perPage": "number", // Optional
  "page": "number" // Optional
}
```

### get_issue

Get details of a specific issue in a GitHub repository.

**Input Schema:**
```json
{
  "owner": "string",
  "repo": "string",
  "issueNumber": "number"
}
```

## Docker CLI Tool

### docker

Use the Docker CLI through the MCP server.

**Input Schema:**
```json
{
  "args": ["string"] // Arguments to pass to the Docker command
}
```

## Tool Registration

### tool-registration

Bootstrap a tool definition in the current session.

**Input Schema:**
```json
{
  "name": "string",
  "content": "string"
}
```

## Using These Tools

To use these tools in your project, you need to:

1. Set up the Docker MCP server
2. Configure your MCP client to connect to the server
3. Call the tools using the appropriate input schema

### Example: Creating a Knowledge Graph Entity

```json
{
  "entities": [
    {
      "name": "Project Documentation",
      "entityType": "Document",
      "observations": [
        "Contains information about the project architecture",
        "Updated on 2025-01-15"
      ]
    }
  ]
}
```

### Example: Using Docker CLI

```json
{
  "args": ["ps", "-a"]
}
```
