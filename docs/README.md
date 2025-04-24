# Augment Adam Documentation

This directory contains documentation for the Augment Adam project.

## Directory Structure

- **api/**: API documentation
  - **ai_agent/**: Documentation for the AI agent API
  - **core/**: Documentation for the core API
  - **memory/**: Documentation for the memory API

- **architecture/**: Architecture documentation
  - `ARCHITECTURE.md`: Overview of the system architecture
  - `AGENT_CORE.md`: Documentation for the agent core
  - `CONTEXT_ENGINE.md`: Documentation for the context engine
  - `MCP_CONTEXT_ENGINE.md`: Documentation for the MCP context engine
  - `memory_system.md`: Documentation for the memory system
  - `plugin_system.md`: Documentation for the plugin system

- **development/**: Development documentation
  - `CONTRIBUTING.md`: Guidelines for contributing to the project
  - `GUIDELINES.md`: Development guidelines
  - `ONBOARDING.md`: Onboarding guide for new developers
  - `PLANNING.md`: Planning process
  - `PROGRESS.md`: Progress tracking
  - `TASKS.md`: Task management
  - `TESTING.md`: Testing guidelines
  - `DIRECTORY_STRUCTURE.md`: Directory structure documentation
  - `RELEASE.md`: Release process
  - `SECURITY.md`: Security guidelines
  - `SUPPORT.md`: Support information
  - `CODE_OF_CONDUCT.md`: Code of conduct
  - `CODEOWNERS.md`: Code ownership information
  - `MAINTAINERS.md`: Maintainer information

- **guides/**: User guides
  - `agent_coordination.md`: Guide for agent coordination
  - `building_agents.md`: Guide for building agents
  - `hardware_optimization.md`: Guide for hardware optimization
  - `parallel_monte_carlo.md`: Guide for parallel Monte Carlo techniques
  - `small_models_large_context.md`: Guide for using small models with large context

- **migration/**: Migration documentation
  - `MIGRATION_GUIDE.md`: Guide for migrating from dukat to augment_adam
  - `MIGRATION_COMPLETED.md`: Documentation of the completed migration

- **research/**: Research papers and notes
  - **ai-digest/**: AI research digest
  - `agentic-memory.md`: Research on agentic memory
  - `ai-agent-dev.md`: Research on AI agent development
  - `dspy.md`: Research on DSPy
  - `Sequential-monte-carlo`: Research on Sequential Monte Carlo methods

- **user_guide/**: User documentation
  - `getting_started.md`: Getting started guide
  - `quickstart.md`: Quickstart guide

## Other Documentation Files

- `container_optimization.md`: Guide for container optimization
- `docker-mcp-tools.md`: Documentation for Docker MCP tools
- `error_handling.md`: Guide for error handling
- `gpu_test_generation.md`: Guide for GPU test generation
- `index.md`: Main documentation index
- `local_model_setup.md`: Guide for local model setup
- `mcp-ecosystem-tracker.md`: MCP ecosystem tracker
- `mcp-integration.md`: Guide for MCP integration
- `mcp-server-template.md`: MCP server template
- `model-context-protocol.md`: Documentation for the Model Context Protocol
- `settings_management.md`: Guide for settings management
- `test_generation.md`: Guide for test generation
- `web_interface.md`: Documentation for the web interface

## Building the Documentation

We use MkDocs to build the documentation. To build the documentation locally:

```bash
# Install MkDocs and required plugins
pip install mkdocs mkdocs-material mkdocstrings mkdocs-jupyter

# Build the documentation
mkdocs build

# Serve the documentation locally
mkdocs serve
```

## Contributing to the Documentation

If you find any issues or have suggestions for improving the documentation, please open an issue or submit a pull request.
