# MCP Ecosystem Tracker

This document tracks the latest developments in the Model Context Protocol (MCP) ecosystem, with a focus on open-source and free/freemium services that can be integrated into our project.

**Last Updated: 2025-04-29**

## Open Source MCP Servers

| Server Name | Description | GitHub Repository | License |
|-------------|-------------|-------------------|---------|
| GitHub | Repository management, file operations, and GitHub API integration | [modelcontextprotocol/server-github](https://github.com/modelcontextprotocol/servers/tree/main/src/github) | MIT |
| Filesystem | Secure file operations with configurable access controls | [modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | MIT |
| Memory | Knowledge graph-based persistent memory system | [modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) | MIT |
| PostgreSQL | Read-only database access with schema inspection | [modelcontextprotocol/server-postgres](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) | MIT |
| SQLite | Database interaction and business intelligence capabilities | [modelcontextprotocol/server-sqlite](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) | MIT |
| Git | Tools to read, search, and manipulate Git repositories | [modelcontextprotocol/server-git](https://github.com/modelcontextprotocol/servers/tree/main/src/git) | MIT |
| Fetch | Web content fetching and conversion for efficient LLM usage | [modelcontextprotocol/server-fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) | MIT |
| Brave Search | Web and local search using Brave's Search API | [modelcontextprotocol/server-brave-search](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search) | MIT |
| Google Drive | File access and search capabilities for Google Drive | [modelcontextprotocol/server-gdrive](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive) | MIT |
| Redis | Interact with Redis key-value stores | [modelcontextprotocol/server-redis](https://github.com/modelcontextprotocol/servers/tree/main/src/redis) | MIT |

## Free/Freemium MCP Servers

| Server Name | Description | Free Tier Limitations | Provider |
|-------------|-------------|------------------------|----------|
| Supabase | Database, authentication, storage, and serverless functions | 500MB database, 1GB storage, 2GB bandwidth/month | [Supabase](https://supabase.com/docs/guides/getting-started/mcp) |
| Chroma | Vector database for AI applications | 1GB storage, limited API calls | [Chroma](https://github.com/chroma-core/chroma-mcp) |
| Cloudflare | Deploy, configure & interrogate resources on Cloudflare | Limited to free Cloudflare services | [Cloudflare](https://github.com/cloudflare/mcp-server-cloudflare) |
| Replicate | Search, run and manage machine learning models | Limited free credits for new users | [Replicate](https://github.com/deepfates/mcp-replicate) |
| Apify | Web scraping and automation tools | Limited free compute units | [Apify](https://github.com/apify/actors-mcp-server) |

## MCP Client Integrations

| Client | Description | Status |
|--------|-------------|--------|
| Claude Desktop | Official Anthropic desktop application | Fully supported |
| VS Code | GitHub Copilot integration in VS Code | Preview support |
| JetBrains IDEs | Plugin for IntelliJ, PyCharm, etc. | Beta support |
| Cursor | AI-powered code editor | Full support |
| Custom Web Apps | Web applications using MCP client libraries | Supported via SDKs |

## Recent Developments

### 2025-04-29
- Supabase released official MCP server documentation
- VS Code added preview support for MCP servers in GitHub Copilot

### 2025-04-25
- New Chroma MCP server released for vector database integration
- Improved documentation for containerizing MCP servers with Docker

### 2025-04-20
- Apify released MCP server for web scraping and automation
- New TypeScript SDK version with improved error handling

## Upcoming MCP Servers

| Server Name | Description | Expected Release |
|-------------|-------------|------------------|
| MongoDB | Database integration for MongoDB | May 2025 |
| Azure | Integration with Azure services | June 2025 |
| Pinecone | Vector database for AI applications | May 2025 |
| Hugging Face | Access to Hugging Face models and datasets | July 2025 |

## Monitoring Sources

To stay current with MCP developments, we monitor the following sources:

1. [Model Context Protocol GitHub Organization](https://github.com/modelcontextprotocol)
2. [Docker MCP Servers Repository](https://github.com/docker/mcp-servers)
3. [MCP Discord Community](https://discord.gg/mcp-community)
4. [Reddit r/mcp](https://www.reddit.com/r/mcp/)
5. [Awesome MCP Servers](https://github.com/wong2/awesome-mcp-servers)
6. [MCP.run Registry](https://mcp.run)

## Integration Priorities

Based on our project needs, we prioritize the following MCP integrations:

1. **Knowledge Management**: Memory, Filesystem, Git
2. **Database Access**: PostgreSQL, Supabase, SQLite
3. **External Services**: GitHub, Google Drive
4. **Search Capabilities**: Brave Search, Fetch
5. **Caching**: Redis

## Automation

We've implemented an automated daily check for new MCP developments:

```python
# Daily MCP ecosystem check script
import requests
import json
from datetime import datetime

def check_mcp_ecosystem():
    """Check for new MCP servers and developments."""
    sources = [
        "https://api.github.com/orgs/modelcontextprotocol/repos?sort=updated",
        "https://api.github.com/repos/docker/mcp-servers/commits",
        "https://mcp.run/api/servers?sort=newest"
    ]
    
    updates = []
    
    for source in sources:
        response = requests.get(source)
        if response.status_code == 200:
            data = response.json()
            # Process data and extract updates
            # ...
            updates.extend(processed_updates)
    
    # Save updates to file
    with open(f"mcp-updates-{datetime.now().strftime('%Y-%m-%d')}.json", "w") as f:
        json.dump(updates, f, indent=2)
    
    return updates

if __name__ == "__main__":
    updates = check_mcp_ecosystem()
    print(f"Found {len(updates)} new MCP developments")
```
