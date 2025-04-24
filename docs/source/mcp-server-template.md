# Custom MCP Server Development Template

This document provides a template and guidelines for building and containerizing custom Model Context Protocol (MCP) servers for our project.

## Project Structure

```
my-custom-mcp-server/
├── src/
│   ├── index.ts              # Main entry point
│   ├── tools/                # Tool implementations
│   │   ├── index.ts          # Tool exports
│   │   └── myTool.ts         # Custom tool implementation
│   ├── resources/            # Resource implementations
│   │   ├── index.ts          # Resource exports
│   │   └── myResource.ts     # Custom resource implementation
│   └── prompts/              # Prompt implementations
│       ├── index.ts          # Prompt exports
│       └── myPrompt.ts       # Custom prompt implementation
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Docker Compose configuration
├── package.json              # Node.js package configuration
├── tsconfig.json             # TypeScript configuration
└── README.md                 # Documentation
```

## Getting Started

### 1. Create a New MCP Server Project

```bash
# Create a new directory for your project
mkdir my-custom-mcp-server
cd my-custom-mcp-server

# Initialize a new Node.js project
npm init -y

# Install MCP SDK and other dependencies
npm install @modelcontextprotocol/typescript-sdk typescript ts-node @types/node

# Create source directory
mkdir -p src/tools src/resources src/prompts
```

### 2. Configure TypeScript

Create a `tsconfig.json` file:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "outDir": "./dist",
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 3. Implement a Basic MCP Server

Create `src/index.ts`:

```typescript
import { createServer, StdioTransport } from '@modelcontextprotocol/typescript-sdk';
import { tools } from './tools';
import { resources } from './resources';
import { prompts } from './prompts';

// Create an MCP server
const server = createServer({
  tools,
  resources,
  prompts,
  serverInfo: {
    name: 'my-custom-mcp-server',
    version: '1.0.0'
  }
});

// Use stdio transport for communication
const transport = new StdioTransport();

// Start the server
server.listen(transport);

console.log('MCP server started');
```

### 4. Implement a Custom Tool

Create `src/tools/myTool.ts`:

```typescript
import { Tool } from '@modelcontextprotocol/typescript-sdk';

export const myTool: Tool = {
  name: 'myTool',
  description: 'A custom tool that performs a specific function',
  inputSchema: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        description: 'First parameter'
      },
      param2: {
        type: 'number',
        description: 'Second parameter'
      }
    },
    required: ['param1']
  },
  execute: async (params) => {
    const { param1, param2 = 0 } = params;
    
    // Implement your tool logic here
    const result = `Processed ${param1} with value ${param2}`;
    
    return { result };
  }
};
```

Create `src/tools/index.ts`:

```typescript
import { myTool } from './myTool';

export const tools = [myTool];
```

### 5. Implement Resources and Prompts (Optional)

Create empty exports for now:

```typescript
// src/resources/index.ts
export const resources = [];

// src/prompts/index.ts
export const prompts = [];
```

### 6. Update package.json

Add scripts to your `package.json`:

```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  }
}
```

## Containerization

### 1. Create a Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build TypeScript code
RUN npm run build

# Expose MCP port (if using TCP transport)
EXPOSE 8811

# Start the server
CMD ["npm", "start"]
```

### 2. Create a docker-compose.yml File

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: my-custom-mcp-server
    ports:
      - "8811:8811"  # Only needed if using TCP transport
    volumes:
      - ./config:/app/config  # For configuration files
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=info
```

### 3. Build and Run the Container

```bash
# Build the container
docker build -t my-custom-mcp-server .

# Run with Docker
docker run -it my-custom-mcp-server

# Or run with Docker Compose
docker-compose up -d
```

## Integration with MCP Clients

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "docker",
      "args": ["run", "-i", "my-custom-mcp-server"]
    }
  }
}
```

### VS Code Configuration

```json
{
  "github.copilot.chat.mcpServers": {
    "my-custom-server": {
      "command": "docker",
      "args": ["run", "-i", "my-custom-mcp-server"]
    }
  }
}
```

## Best Practices

1. **Security First**: Carefully validate all inputs and limit access to sensitive resources
2. **Error Handling**: Implement robust error handling and provide clear error messages
3. **Logging**: Add comprehensive logging for debugging and monitoring
4. **Configuration**: Use environment variables or configuration files for customization
5. **Testing**: Write unit and integration tests for your MCP server
6. **Documentation**: Document your server's tools, resources, and prompts
7. **Versioning**: Follow semantic versioning for your MCP server

## Example: Database MCP Server

Here's an example of a custom MCP server that provides access to a database:

```typescript
// src/tools/queryDatabase.ts
import { Tool } from '@modelcontextprotocol/typescript-sdk';
import { Pool } from 'pg';

// Create a connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

export const queryDatabase: Tool = {
  name: 'queryDatabase',
  description: 'Execute a SQL query against the database',
  inputSchema: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'SQL query to execute'
      }
    },
    required: ['query']
  },
  execute: async (params) => {
    const { query } = params;
    
    try {
      // Execute the query
      const result = await pool.query(query);
      
      return {
        rows: result.rows,
        rowCount: result.rowCount
      };
    } catch (error) {
      throw new Error(`Database query failed: ${error.message}`);
    }
  }
};
```

## Deployment Options

1. **Local Development**: Run the server directly with `npm run dev`
2. **Docker Container**: Build and run as a Docker container
3. **Kubernetes**: Deploy to a Kubernetes cluster using the provided Dockerfile
4. **Cloud Services**: Deploy to cloud services like AWS ECS, Google Cloud Run, or Azure Container Instances
5. **Serverless**: Package as a serverless function (requires TCP transport)

## Troubleshooting

1. **Connection Issues**: Ensure the MCP client can reach the server
2. **Permission Problems**: Check file and network permissions
3. **Environment Variables**: Verify all required environment variables are set
4. **Logs**: Check server logs for error messages
5. **Version Compatibility**: Ensure MCP SDK versions are compatible
