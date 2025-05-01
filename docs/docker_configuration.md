# Docker Configuration

This document provides detailed information about the Docker configuration used in the Augment Adam project.

## Development Environment

The project uses a Docker-based development environment with VS Code's Dev Containers extension. This provides a consistent development experience across different machines and operating systems.

### Services

The development environment includes the following services:

1. **Main Development Container**
   - Python 3.10 environment with all required dependencies
   - GPU support for NVIDIA GPUs
   - Access to all other services

2. **Ollama**
   - Local LLM inference
   - GPU acceleration for model inference
   - Accessible at `http://ollama:11434` within the container network

3. **ChromaDB**
   - Vector database for embeddings storage
   - Accessible at `http://chroma:8000` within the container network

4. **Neo4j**
   - Graph database for knowledge representation
   - Accessible via Bolt protocol at `bolt://neo4j:7687` within the container network
   - Default credentials: `neo4j/augmentpassword`

5. **Redis**
   - In-memory data store for caching
   - Accessible at `redis:6379` within the container network

6. **Redis Vector**
   - Redis with vector search capabilities for efficient similarity search
   - Accessible at `redis-vector:6379` within the container network
   - Default password: `redispassword`

### Persistent Volumes

The environment uses named volumes to persist data across container restarts:

- **Model Volumes**
  - `ollama-models`: Stores Ollama models
  - `model-cache`: General model cache
  - `huggingface-cache`: HuggingFace models and cache

- **Cache Volumes**
  - `pip-cache`: Cache for pip packages
  - `apt-cache`: Cache for apt packages
  - `torch-cache`: Cache for PyTorch models and weights

- **Service Data Volumes**
  - `chroma-data`: ChromaDB data
  - `neo4j-data`: Neo4j database files
  - `redis-data`: Redis data
  - `redis-vector-data`: Redis Vector data

All volumes are configured as external volumes, which means they persist even if the containers are removed.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- VS Code with the Dev Containers extension
- NVIDIA GPU with CUDA support (optional, for GPU acceleration)
- NVIDIA Container Toolkit (for GPU support)

### Opening the Development Environment

1. Clone the repository
2. Open the repository in VS Code
3. When prompted, click "Reopen in Container"
4. Alternatively, use the Command Palette (Ctrl+Shift+P) and select "Dev Containers: Reopen in Container"

### Testing Services

The repository includes a test script to verify connectivity to all services:

```bash
python test_services.py
```

This script checks connectivity to all services and reports their status.

## GPU Support

The development environment is configured to use NVIDIA GPUs if available. The main container and Ollama service are configured with GPU support.

To use GPU acceleration:

1. Ensure you have NVIDIA drivers installed
2. Install the NVIDIA Container Toolkit (nvidia-docker2)
3. Restart Docker after installation
4. The containers will automatically detect and use available GPUs

## Customization

### Environment Variables

The main development container is configured with the following environment variables:

- `PYTHONPATH=/workspace`: Sets the Python path to include the workspace directory
- `HF_HOME=/workspace/.cache/huggingface`: Sets the HuggingFace cache directory
- `OLLAMA_HOST=http://ollama:11434`: Sets the Ollama host
- `CHROMA_HOST=http://chroma:8000`: Sets the ChromaDB host
- `NEO4J_URI=bolt://neo4j:7687`: Sets the Neo4j URI
- `NEO4J_USER=neo4j`: Sets the Neo4j username
- `NEO4J_PASSWORD=augmentpassword`: Sets the Neo4j password
- `REDIS_HOST=redis`: Sets the Redis host
- `REDIS_VECTOR_HOST=redis-vector`: Sets the Redis Vector host
- `REDIS_VECTOR_PASSWORD=redispassword`: Sets the Redis Vector password

### VS Code Extensions

The development environment comes with a set of pre-installed VS Code extensions for:

- Python development
- AI assistance
- Jupyter and data science
- Docker and containers
- Database tools
- Git and collaboration
- Web development
- Markdown and documentation
- Productivity and UI
- Testing
- REST API development

## Troubleshooting

### Service Connectivity Issues

If you encounter connectivity issues with any of the services, you can use the `test_services.py` script to diagnose the problem:

```bash
python test_services.py
```

### Container Startup Issues

If the container fails to start:

1. Check Docker logs: `docker logs <container_id>`
2. Verify that all required ports are available
3. Ensure you have sufficient disk space for the volumes
4. Check that the NVIDIA Container Toolkit is properly installed (for GPU support)

### Volume Persistence Issues

If data is not persisting across container restarts:

1. Check that the volumes are properly created: `docker volume ls`
2. Verify that the volumes are properly mounted in the container
3. Ensure that the services are properly configured to use the mounted volumes
