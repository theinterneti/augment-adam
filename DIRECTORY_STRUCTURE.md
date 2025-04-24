# Augment Adam Directory Structure

This document outlines the standard directory structure for the Augment Adam project.

## Root Directory

```
/workspace/
├── augment_adam/        # Main package code
├── config/              # Configuration files
├── docker/              # Docker-related files
├── docs/                # Documentation
├── examples/            # Example code and notebooks
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── .env                 # Environment variables (not in version control)
├── .gitignore           # Git ignore file
├── LICENSE              # License file
├── pyproject.toml       # Project configuration
├── README.md            # Project readme
└── CHANGELOG.md         # Version history
```

## Main Package (`augment_adam/`)

```
augment_adam/
├── __init__.py          # Package initialization
├── ai_agent/            # AI agent implementation
│   ├── coordination/    # Agent coordination
│   ├── memory_integration/ # Memory integration
│   ├── reasoning/       # Reasoning capabilities
│   ├── smc/             # Sequential Monte Carlo
│   ├── tools/           # Agent tools
│   └── types/           # Type definitions
├── cli/                 # Command-line interface
├── context_engine/      # Context engine
│   ├── chunking/        # Text chunking
│   ├── composition/     # Context composition
│   ├── prompt/          # Prompt management
│   └── retrieval/       # Retrieval mechanisms
├── core/                # Core functionality
├── memory/              # Memory systems
├── models/              # Model implementations
├── plugins/             # Plugin system
├── server/              # Server implementation
├── utils/               # Utility functions
└── web/                 # Web interface
```

## Documentation (`docs/`)

```
docs/
├── api/                 # API reference
├── development/         # Development guides
├── research/            # Research papers and notes
│   └── ai-digest/       # AI research digests
└── user_guide/          # User guides
```

## Tests (`tests/`)

```
tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
├── e2e/                 # End-to-end tests
├── performance/         # Performance tests
├── stress/              # Stress tests
└── conftest.py          # Test configuration
```

## Docker (`docker/`)

```
docker/
├── Dockerfile.api       # API server Dockerfile
├── Dockerfile.worker    # Worker Dockerfile
├── docker-compose.yml   # Main docker-compose file
└── docker-compose.test.yml # Testing docker-compose file
```

## Configuration (`config/`)

```
config/
├── neo4j/               # Neo4j configuration
├── redis/               # Redis configuration
└── default_settings.yml # Default application settings
```

## Examples (`examples/`)

```
examples/
├── agent_coordination/  # Agent coordination examples
├── memory_systems/      # Memory system examples
├── mcp_server/          # MCP server examples
└── README.md            # Examples documentation
```

## Scripts (`scripts/`)

```
scripts/
├── monitoring/          # Monitoring scripts
├── setup/               # Setup scripts
└── test_utils/          # Test utilities
```

## Best Practices

1. **Package Organization**:
   - Keep related code together in modules
   - Use clear, descriptive names for modules and packages
   - Follow Python naming conventions (snake_case for modules and functions)

2. **Documentation**:
   - Document all public APIs
   - Keep documentation up-to-date with code changes
   - Use docstrings for all classes and functions

3. **Testing**:
   - Write tests for all new functionality
   - Organize tests to mirror the package structure
   - Use fixtures for common test setup

4. **Configuration**:
   - Use environment variables for sensitive information
   - Store default configuration in version control
   - Override configuration with environment-specific settings

5. **Docker**:
   - Keep Dockerfiles simple and focused
   - Use multi-stage builds for smaller images
   - Use docker-compose for local development

6. **Scripts**:
   - Make scripts executable and add shebang lines
   - Document script usage with comments or help text
   - Use argparse for command-line arguments
