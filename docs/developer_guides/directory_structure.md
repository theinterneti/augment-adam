# Directory Structure

This document explains the directory structure of the Augment Adam project.

## Overview

The Augment Adam project follows a modular structure organized by functionality. The main directories are:

- `src/augment_adam`: Main source code
- `tests`: Test code
- `docs`: Documentation
- `examples`: Example code
- `scripts`: Utility scripts
- `templates`: Template files

## Source Code Structure

The `src/augment_adam` directory contains the main source code for the project:

```
src/augment_adam/
├── __init__.py
├── ai_agent/              # Agent-related code
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── mcp/               # Monte Carlo Planning agents
│   ├── worker/            # Worker agents
│   └── coordination/      # Agent coordination
├── context_engine/        # Context engine
│   ├── __init__.py
│   ├── chunking/          # Text chunking
│   ├── composition/       # Context composition
│   └── retrieval/         # Context retrieval
├── memory/                # Memory systems
│   ├── __init__.py
│   ├── base.py            # Base memory class
│   ├── vector/            # Vector memory
│   ├── graph/             # Graph memory
│   ├── episodic/          # Episodic memory
│   └── semantic/          # Semantic memory
├── models/                # Model interfaces
│   ├── __init__.py
│   ├── interface.py       # Model interface
│   ├── openai.py          # OpenAI model
│   ├── anthropic.py       # Anthropic model
│   └── ollama.py          # Ollama model
├── plugins/               # Plugin system
│   ├── __init__.py
│   ├── base.py            # Base plugin class
│   ├── file_manager.py    # File manager plugin
│   ├── web_search.py      # Web search plugin
│   └── system_info.py     # System info plugin
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── tagging/           # Tagging system
│   ├── templates/         # Template engine
│   ├── async_utils.py     # Async utilities
│   ├── parallel.py        # Parallel processing
│   └── hardware.py        # Hardware utilities
└── core/                  # Core functionality
    ├── __init__.py
    ├── assistant.py       # Main assistant class
    ├── settings.py        # Settings management
    └── errors.py          # Error handling
```

## Test Structure

The `tests` directory contains the test code for the project:

```
tests/
├── __init__.py
├── unit/                  # Unit tests
│   ├── __init__.py
│   ├── test_ai_agent/     # Tests for ai_agent module
│   ├── test_context_engine/ # Tests for context_engine module
│   ├── test_memory/       # Tests for memory module
│   ├── test_models/       # Tests for models module
│   ├── test_plugins/      # Tests for plugins module
│   ├── test_utils/        # Tests for utils module
│   └── test_core/         # Tests for core module
├── integration/           # Integration tests
│   ├── __init__.py
│   ├── test_ai_agent_memory/ # Tests for ai_agent and memory integration
│   ├── test_context_engine_memory/ # Tests for context_engine and memory integration
│   └── test_models_memory/ # Tests for models and memory integration
└── e2e/                   # End-to-end tests
    ├── __init__.py
    ├── test_assistant.py  # Tests for the assistant
    └── test_workflows.py  # Tests for workflows
```

## Documentation Structure

The `docs` directory contains the documentation for the project:

```
docs/
├── architecture/          # Architecture documentation
│   ├── MCP_CONTEXT_ENGINE.md # Monte Carlo Planning context engine
│   ├── TAGGING_SYSTEM.md  # Tagging system
│   ├── TEMPLATE_ENGINE.md # Template engine
│   ├── MEMORY_SYSTEM.md   # Memory system
│   ├── AGENT_COORDINATION.md # Agent coordination
│   ├── DOCUMENTATION_SYSTEM.md # Documentation system
│   ├── TESTING_FRAMEWORK.md # Testing framework
│   ├── CONTEXT_ENGINE.md  # Context engine
│   └── PLUGIN_SYSTEM.md   # Plugin system
├── user_guide/            # User guides
│   ├── getting_started.md # Getting started guide
│   ├── installation.md    # Installation guide
│   ├── configuration.md   # Configuration guide
│   ├── hardware_optimization.md # Hardware optimization guide
│   ├── parallel_monte_carlo.md # Parallel Monte Carlo guide
│   ├── building_agents.md # Building agents guide
│   └── agent_coordination.md # Agent coordination guide
├── developer_guides/      # Developer guides
│   ├── contributing.md    # Contributing guide
│   ├── extending.md       # Extending guide
│   ├── plugins.md         # Plugins guide
│   ├── directory_structure.md # Directory structure guide
│   ├── testing.md         # Testing guide
│   ├── documentation.md   # Documentation guide
│   └── release.md         # Release guide
├── api/                   # API documentation
│   ├── memory.md          # Memory API
│   ├── models.md          # Models API
│   ├── agents.md          # Agents API
│   ├── context.md         # Context API
│   ├── utils.md           # Utils API
│   ├── templates.md       # Templates API
│   ├── tagging.md         # Tagging API
│   ├── monte_carlo.md     # Monte Carlo API
│   └── parallel.md        # Parallel API
└── research/              # Research documentation
    ├── monte_carlo.md     # Monte Carlo research
    └── context_engine.md  # Context engine research
```

## Examples Structure

The `examples` directory contains example code for the project:

```
examples/
├── ai_agent/              # Agent examples
│   ├── mcp_agent.py       # Monte Carlo Planning agent example
│   ├── worker_agent.py    # Worker agent example
│   └── coordination.py    # Agent coordination example
├── context_engine/        # Context engine examples
│   ├── chunking.py        # Text chunking example
│   ├── composition.py     # Context composition example
│   └── retrieval.py       # Context retrieval example
├── memory/                # Memory examples
│   ├── vector_memory.py   # Vector memory example
│   ├── graph_memory.py    # Graph memory example
│   ├── episodic_memory.py # Episodic memory example
│   └── semantic_memory.py # Semantic memory example
├── models/                # Model examples
│   ├── openai_model.py    # OpenAI model example
│   ├── anthropic_model.py # Anthropic model example
│   └── ollama_model.py    # Ollama model example
├── plugins/               # Plugin examples
│   ├── file_manager.py    # File manager plugin example
│   ├── web_search.py      # Web search plugin example
│   └── system_info.py     # System info plugin example
└── utils/                 # Utility examples
    ├── tagging.py         # Tagging system example
    ├── templates.py       # Template engine example
    ├── async_utils.py     # Async utilities example
    ├── parallel.py        # Parallel processing example
    └── hardware.py        # Hardware utilities example
```

## Scripts Structure

The `scripts` directory contains utility scripts for the project:

```
scripts/
├── setup.sh               # Setup script
├── build.sh               # Build script
├── test.sh                # Test script
├── docs.sh                # Documentation script
├── release.sh             # Release script
└── utils/                 # Utility scripts
    ├── generate_docs.py   # Generate documentation
    ├── check_code.py      # Check code quality
    └── benchmark.py       # Benchmark performance
```

## Templates Structure

The `templates` directory contains template files for the project:

```
templates/
├── code/                  # Code templates
│   ├── python/            # Python templates
│   │   ├── class_template.j2 # Class template
│   │   ├── module_template.j2 # Module template
│   │   ├── function_template.j2 # Function template
│   │   ├── dataclass_template.j2 # Dataclass template
│   │   ├── enum_template.j2 # Enum template
│   │   ├── protocol_template.j2 # Protocol template
│   │   └── type_template.j2 # Type template
│   ├── javascript/        # JavaScript templates
│   │   ├── class_template.js.j2 # Class template
│   │   ├── module_template.js.j2 # Module template
│   │   ├── function_template.js.j2 # Function template
│   │   └── react_component.js.j2 # React component template
│   ├── sql/               # SQL templates
│   │   ├── table_template.sql.j2 # Table template
│   │   ├── query_template.sql.j2 # Query template
│   │   ├── index_template.sql.j2 # Index template
│   │   └── view_template.sql.j2 # View template
│   └── yaml_json/         # YAML/JSON templates
│       ├── config_template.yaml.j2 # Config template
│       ├── schema_template.json.j2 # Schema template
│       └── api_spec_template.yaml.j2 # API spec template
├── test/                  # Test templates
│   ├── python/            # Python test templates
│   │   ├── unit_test_template.j2 # Unit test template
│   │   ├── integration_test_template.j2 # Integration test template
│   │   ├── e2e_test_template.j2 # End-to-end test template
│   │   ├── pytest_fixture_template.j2 # Pytest fixture template
│   │   ├── pytest_parametrize_template.j2 # Pytest parametrize template
│   │   └── mock_template.j2 # Mock template
│   └── javascript/        # JavaScript test templates
│       ├── jest_test_template.js.j2 # Jest test template
│       └── mocha_test_template.js.j2 # Mocha test template
├── doc/                   # Documentation templates
│   ├── markdown/          # Markdown templates
│   │   ├── module_doc_template.md.j2 # Module documentation template
│   │   ├── api_doc_template.md.j2 # API documentation template
│   │   ├── guide_template.md.j2 # Guide template
│   │   ├── readme_template.md.j2 # README template
│   │   └── changelog_template.md.j2 # Changelog template
│   ├── rst/               # reStructuredText templates
│   │   ├── sphinx_doc_template.rst.j2 # Sphinx documentation template
│   │   └── api_doc_template.rst.j2 # API documentation template
│   └── html/              # HTML templates
│       ├── api_doc_template.html.j2 # API documentation template
│       └── guide_template.html.j2 # Guide template
└── memory/                # Memory templates
    ├── vector_query_template.j2 # Vector query template
    ├── cypher_query_template.j2 # Cypher query template
    ├── graph_visualization_template.j2 # Graph visualization template
    ├── memory_schema_template.j2 # Memory schema template
    └── embedding_template.j2 # Embedding template
```

## Configuration Files

The project includes several configuration files:

```
/
├── .augment-guidelines.yaml # Project guidelines
├── pyproject.toml        # Python project configuration
├── setup.py              # Package setup
├── setup.cfg             # Package setup configuration
├── requirements.txt      # Package dependencies
├── requirements-dev.txt  # Development dependencies
├── .gitignore            # Git ignore file
├── .github/              # GitHub configuration
│   └── workflows/        # GitHub Actions workflows
└── docker/               # Docker configuration
    ├── Dockerfile        # Dockerfile
    └── docker-compose.yml # Docker Compose configuration
```

## Best Practices

When working with the Augment Adam codebase, follow these best practices:

1. **Follow the Directory Structure**: Place new files in the appropriate directories
2. **Use Consistent Naming**: Follow the naming conventions used in the project
3. **Add Documentation**: Document new code with docstrings and update the documentation
4. **Add Tests**: Write tests for new code
5. **Use Type Hints**: Add type hints to new code
6. **Follow the Style Guide**: Follow the Google Python Style Guide
7. **Use the Tagging System**: Tag new code with appropriate tags
8. **Use the Template Engine**: Use templates for generating code, tests, and documentation
9. **Keep the Directory Structure Updated**: Update this document when adding new directories

## Next Steps

After understanding the directory structure, check out the [Contributing Guide](contributing.md) to learn how to contribute to the project.
