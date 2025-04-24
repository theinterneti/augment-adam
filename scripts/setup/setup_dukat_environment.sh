#!/bin/bash
# setup_dukat_environment.sh - Script to set up the Dukat development and testing environment

set -e  # Exit on error

echo "Setting up Dukat development and testing environment..."

# Create necessary directories
mkdir -p monitoring/dashboards monitoring/datasources test_templates test_results

# Create optimized Dockerfile.test-gen
cat > Dockerfile.test-gen << 'EOF'
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04 as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Configure apt caching for faster builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    curl \
    wget \
    jq \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/python3.10 /usr/bin/python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base as builder

# Install Python dependencies
COPY requirements-test-gen.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements-test-gen.txt \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    && pip install --no-cache-dir pytest pytest-cov pytest-xdist hypothesis pynguin \
       mutmut pytest-benchmark pytest-mock pytest-timeout

FROM base

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Create directories for test results and reports
RUN mkdir -p /app/test_results /app/reports /app/models /app/templates/project /app/config

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set the entrypoint
ENTRYPOINT ["python", "-m", "scripts.auto_test_generator"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Main development container
  dukat-dev:
    build:
      context: .
      dockerfile: .devcontainer/Dockerfile
      args:
        BUILDKIT_INLINE_CACHE: 1
    container_name: dukat-dev
    volumes:
      - .:/workspace:cached
      - /var/run/docker.sock:/var/run/docker.sock
      - ollama-models:/root/.ollama:cached
      - model-cache:/workspace/.cache/models:cached
      - huggingface-cache:/workspace/.cache/huggingface:cached
      - pip-cache:/root/.cache/pip:cached
      - apt-cache:/var/cache/apt:cached
      - torch-cache:/root/.cache/torch:cached
    ports:
      - "8888:8888"  # Jupyter
    environment:
      - PYTHONPATH=/workspace
      - HF_HOME=/workspace/.cache/huggingface
      - OLLAMA_HOST=http://dukat-ollama:11434
      - CHROMA_HOST=http://dukat-chroma:8000
      - NEO4J_URI=bolt://dukat-neo4j:7687
      - REDIS_HOST=dukat-redis
    depends_on:
      - dukat-ollama
      - dukat-chroma
      - dukat-neo4j
      - dukat-redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Ollama for local LLM inference
  dukat-ollama:
    image: ollama/ollama:latest
    container_name: dukat-ollama
    volumes:
      - ollama-models:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ChromaDB for vector storage
  dukat-chroma:
    image: chromadb/chroma:latest
    container_name: dukat-chroma
    volumes:
      - chroma-data:/chroma/chroma
    ports:
      - "8000:8000"
    environment:
      - ALLOW_RESET=true
      - ANONYMIZED_TELEMETRY=false

  # Neo4j for graph relationships
  dukat-neo4j:
    image: neo4j:5.13.0
    container_name: dukat-neo4j
    environment:
      - NEO4J_AUTH=neo4j/dukatpassword
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j-data:/data
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt

  # Redis for caching
  dukat-redis:
    image: redis:latest
    container_name: dukat-redis
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

volumes:
  ollama-models:
    external: true  # Use existing Ollama models volume
  model-cache:
  huggingface-cache:
  pip-cache:
    name: dukat-pip-cache
  apt-cache:
    name: dukat-apt-cache
  torch-cache:
    name: dukat-torch-cache
  chroma-data:
  neo4j-data:
  redis-data:
EOF

# Create docker-compose.test-gen.yml
cat > docker-compose.test-gen.yml << 'EOF'
version: '3.8'

services:
  ai-test-ollama:
    image: ollama/ollama:latest
    container_name: ai-test-ollama
    ports:
      - "11435:11434"
    volumes:
      - ollama-models:/root/.ollama
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  dukat-test-generator:
    build:
      context: .
      dockerfile: Dockerfile.test-gen
    container_name: dukat-test-generator
    volumes:
      - ./:/project  # Mount the current project
      - ./test_config.yml:/app/config/project_config.yml  # Project-specific config
      - ./test_templates:/app/templates/project  # Project-specific templates
      - test-results:/app/test_results
      - pip-cache:/root/.cache/pip:cached
      - apt-cache:/var/cache/apt:cached
      - torch-cache:/root/.cache/torch:cached
    depends_on:
      ai-test-ollama:
        condition: service_healthy
    environment:
      - OLLAMA_HOST=http://ai-test-ollama:11434
      - PYTHONUNBUFFERED=1
      - CUDA_VISIBLE_DEVICES=0
      - PROJECT_PATH=/project
      - CONFIG_PATH=/app/config/project_config.yml
      - TEMPLATE_PATH=/app/templates/project
      - RESULTS_PATH=/app/test_results
      - PROJECT_NAME=dukat
    command: >
      bash -c "cd /app &&
      python -m scripts.auto_test_generator --project-path /project --config /app/config/project_config.yml --project dukat"

volumes:
  ollama-models:
    external: true
  test-results:
  pip-cache:
    name: dukat-pip-cache
    external: true
  apt-cache:
    name: dukat-apt-cache
    external: true
  torch-cache:
    name: dukat-torch-cache
    external: true
EOF

# Create test_config.yml
cat > test_config.yml << 'EOF'
# Dukat-specific test configuration
project:
  name: "dukat"
  language: "python"
  test_framework: "pytest"
  
code_paths:
  - src/
  - dukat/
  
exclude_paths:
  - tests/
  - examples/
  
test_settings:
  coverage_threshold: 80
  parallel_tests: 4
  timeout: 60
  
model_settings:
  model: "codellama:7b"
  temperature: 0.2
  max_tokens: 2000
  
output_settings:
  output_dir: "generated_tests"
  report_format: "html"
EOF

# Create a script to pull models
cat > pull_models.sh << 'EOF'
#!/bin/bash
# Pull required models for Ollama

echo "Pulling models for Ollama..."
docker exec -it dukat-ollama ollama pull codellama:7b
docker exec -it ai-test-ollama ollama pull codellama:7b

echo "Verifying models..."
docker exec -it dukat-ollama ollama list
EOF
chmod +x pull_models.sh

# Create a script to set up the environment
cat > setup_environment.sh << 'EOF'
#!/bin/bash
# Set up the Dukat environment

set -e  # Exit on error

echo "Setting up Dukat environment..."

# Pull required Docker images
echo "Pulling Docker images..."
docker pull nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
docker pull ollama/ollama:latest
docker pull chromadb/chroma:latest
docker pull neo4j:5.13.0
docker pull redis:latest

# Build and start the main development environment
echo "Building and starting development environment..."
DOCKER_BUILDKIT=1 docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
docker-compose up -d dukat-ollama dukat-chroma dukat-neo4j dukat-redis
docker-compose up -d dukat-dev

# Build and start the test environment
echo "Building and starting test environment..."
DOCKER_BUILDKIT=1 docker-compose -f docker-compose.test-gen.yml build --build-arg BUILDKIT_INLINE_CACHE=1
docker-compose -f docker-compose.test-gen.yml up -d ai-test-ollama
docker-compose -f docker-compose.test-gen.yml up -d dukat-test-generator

# Verify the containers are running
echo "Verifying containers..."
docker-compose ps
docker-compose -f docker-compose.test-gen.yml ps

echo "Environment setup complete!"
echo "Run ./pull_models.sh to pull required models for Ollama."
EOF
chmod +x setup_environment.sh

# Create a script to configure services
cat > configure_services.sh << 'EOF'
#!/bin/bash
# Configure services for Dukat

set -e  # Exit on error

echo "Configuring services..."

# Configure Neo4j
echo "Configuring Neo4j..."
docker exec -it dukat-neo4j cypher-shell -u neo4j -p dukatpassword \
  "CREATE CONSTRAINT unique_file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE"

# Configure ChromaDB
echo "Configuring ChromaDB..."
cat > create_collection.py << 'PYEOF'
import chromadb

client = chromadb.HttpClient(host="dukat-chroma", port=8000)
collection = client.create_collection(
    name="dukat_code",
    metadata={"description": "Dukat code embeddings"}
)
print(f"Created collection: {collection.name}")
PYEOF

docker cp create_collection.py dukat-dev:/tmp/
docker exec -it dukat-dev python /tmp/create_collection.py

echo "Service configuration complete!"
EOF
chmod +x configure_services.sh

# Create a script to run tests
cat > run_tests.sh << 'EOF'
#!/bin/bash
# Run tests using the test generator

set -e  # Exit on error

echo "Running tests..."

# Run tests using the test generator
docker-compose -f docker-compose.test-gen.yml run dukat-test-generator \
  python -m scripts.auto_test_generator \
  --project-path /project \
  --config /app/config/project_config.yml \
  --project dukat \
  --output-dir /app/test_results

echo "Tests complete!"
EOF
chmod +x run_tests.sh

# Create a script to clean up
cat > cleanup.sh << 'EOF'
#!/bin/bash
# Clean up the Dukat environment

echo "Cleaning up Dukat environment..."

# Stop and remove containers
docker-compose down
docker-compose -f docker-compose.test-gen.yml down

echo "Cleanup complete!"
EOF
chmod +x cleanup.sh

echo "Setup scripts created!"
echo "To set up the environment, run: ./setup_environment.sh"
echo "To pull models, run: ./pull_models.sh"
echo "To configure services, run: ./configure_services.sh"
echo "To run tests, run: ./run_tests.sh"
echo "To clean up, run: ./cleanup.sh"