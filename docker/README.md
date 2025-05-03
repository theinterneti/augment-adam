# Docker Configuration for Augment Adam

This directory contains all Docker-related configuration files and scripts for the Augment Adam project.

## Directory Structure

```
docker/
├── devcontainer/           # All devcontainer-specific files
│   ├── Dockerfile          # Main devcontainer Dockerfile
│   ├── docker-compose.yml  # Main devcontainer compose file
│   ├── scripts/            # Scripts specific to devcontainer
│   │   ├── entrypoint.sh   # Container entrypoint script
│   │   ├── post-start.sh   # Post-start initialization script
│   │   └── verify_docker_access.sh # Docker access verification
│   └── config/             # Configuration files for devcontainer
│       └── .dockerignore   # Files to ignore in Docker build
│
├── services/               # Service-specific Docker files
│   ├── api/                # API service
│   │   ├── Dockerfile      # API service Dockerfile
│   │   └── docker-compose.yml # API service compose file
│   ├── mcp-context-engine/ # MCP Context Engine service
│   │   ├── Dockerfile      # MCP Context Engine Dockerfile
│   │   ├── docker-compose.yml # MCP Context Engine compose file
│   │   └── scripts/        # Service-specific scripts
│   │       └── setup_integration.sh # MCP integration script
│   └── ollama/             # Ollama service
│       ├── Dockerfile      # Ollama service Dockerfile
│       └── docker-compose.yml # Ollama service compose file
│
└── scripts/                # Docker management scripts
    ├── manage_services.sh  # Generic service management script
    ├── manage_mcp.sh       # MCP-specific management script
    └── create_volumes.sh   # Script to create required volumes
```

## Usage

### Managing Services

The `manage_services.sh` script provides a unified interface for managing all Docker services:

```bash
# Create required Docker volumes
./docker/scripts/manage_services.sh create-volumes

# Start all services
./docker/scripts/manage_services.sh all start

# Start a specific service
./docker/scripts/manage_services.sh mcp-context-engine start

# Check service status
./docker/scripts/manage_services.sh mcp-context-engine status

# View logs
./docker/scripts/manage_services.sh mcp-context-engine logs

# Stop services
./docker/scripts/manage_services.sh all stop
```

### MCP Context Engine

For convenience, there's a dedicated script for managing the MCP Context Engine:

```bash
# Start MCP Context Engine
./docker/scripts/manage_mcp.sh start

# Check status
./docker/scripts/manage_mcp.sh status

# View logs
./docker/scripts/manage_mcp.sh logs
```

### DevContainer

The devcontainer configuration is used by VS Code's Remote Containers extension to provide a consistent development environment. The configuration is in `.devcontainer/devcontainer.json` and references the Docker files in `docker/devcontainer/`.

## Volumes

The project uses named Docker volumes to persist data and cache dependencies. These volumes are created with the `create_volumes.sh` script:

- `augment-adam-ollama-models`: Ollama models
- `augment-adam-model-cache`: General model cache
- `augment-adam-huggingface-cache`: HuggingFace models
- `augment-adam-pip-cache`: Cache pip packages
- `augment-adam-apt-cache`: Cache apt packages
- `augment-adam-torch-cache`: Cache PyTorch models and weights
- `augment-adam-chroma-data`: ChromaDB data
- `augment-adam-neo4j-data`: Neo4j data
- `augment-adam-redis-data`: Redis data
- `augment-adam-redis-vector-data`: Redis Vector data

## Architecture

The project follows a microservices architecture with the following components:

1. **DevContainer**: The main development environment with all tools and dependencies.
2. **MCP Context Engine**: A service for context retrieval and management.
3. **API Service**: (Future) REST API for interacting with the system.
4. **Supporting Services**:
   - Ollama: Local LLM inference
   - ChromaDB: Vector database
   - Neo4j: Graph database
   - Redis: Caching and message broker
   - Redis Vector: Vector search

## Network Architecture

The services are organized in a way that:
1. Only the main container talks to the host
2. Supporting services talk to the main container
3. The host doesn't need direct access to supplemental services

This is achieved through Docker's networking features and careful port exposure configuration.
