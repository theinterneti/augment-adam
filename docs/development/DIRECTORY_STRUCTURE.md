# Directory Structure

This document outlines the directory structure of the Augment Adam project.

## Overview

The Augment Adam project is organized into the following main directories:

- `augment_adam/`: Main package directory containing all the code
- `docs/`: Documentation files
- `scripts/`: Utility scripts for development and maintenance
- `tests/`: Test files organized by test type

## Main Package Structure

The `augment_adam/` directory is organized as follows:

```
augment_adam/
├── __init__.py           # Package initialization
├── ai_agent/             # AI agent implementation
│   ├── __init__.py
│   ├── cli.py            # Command-line interface for AI agents
│   ├── coordination/     # Agent coordination functionality
│   ├── memory/           # Agent-specific memory implementations
│   ├── models/           # Model management for AI agents
│   ├── reasoning/        # Reasoning capabilities for agents
│   ├── smc/              # Sequential Monte Carlo implementation
│   └── types/            # Type definitions for AI agents
├── cli/                  # Command-line interface
│   ├── __init__.py
│   ├── commands/         # CLI command implementations
│   └── progress_bar.py   # Progress bar utilities
├── config.py             # Configuration management
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── agent.py          # Base agent implementation
│   ├── assistant.py      # Assistant implementation
│   ├── async_assistant.py # Asynchronous assistant
│   ├── circuit_breaker.py # Circuit breaker pattern
│   ├── errors.py         # Error handling
│   ├── memory_manager.py # Memory management
│   ├── model_manager.py  # Model management
│   ├── parallel_executor.py # Parallel execution
│   ├── progress.py       # Progress tracking
│   ├── prompt_manager.py # Prompt management
│   ├── settings.py       # Settings management
│   ├── task_persistence.py # Task persistence
│   ├── task_queue.py     # Task queue
│   └── task_scheduler.py # Task scheduling
├── memory/               # Memory implementations
│   ├── __init__.py
│   ├── base.py           # Base memory interface
│   ├── episodic.py       # Episodic memory
│   ├── faiss_episodic.py # FAISS-based episodic memory
│   ├── faiss_memory.py   # FAISS-based memory
│   ├── faiss_semantic.py # FAISS-based semantic memory
│   ├── semantic.py       # Semantic memory
│   └── working.py        # Working memory
├── models/               # Model implementations
│   ├── __init__.py
│   ├── interface.py      # Model interface
│   └── manager.py        # Model manager
├── plugins/              # Plugin system
│   ├── __init__.py
│   ├── base.py           # Base plugin interface
│   ├── file_manager.py   # File manager plugin
│   ├── system_info.py    # System information plugin
│   └── web_search.py     # Web search plugin
└── web/                  # Web interface
    ├── __init__.py
    ├── conversation_viz.py # Conversation visualization
    ├── interface.py      # Web interface
    ├── plugin_manager.py # Plugin management UI
    ├── settings_manager.py # Settings management UI
    └── task_manager.py   # Task management UI
```

## Test Structure

The `tests/` directory is organized by test type:

```
tests/
├── __init__.py
├── compatibility/        # Compatibility tests
├── conftest.py           # Pytest configuration
├── e2e/                  # End-to-end tests
├── integration/          # Integration tests
├── performance/          # Performance tests
├── stress/               # Stress tests
└── unit/                 # Unit tests
    ├── __init__.py
    ├── ai_agent/         # Tests for AI agent functionality
    ├── core/             # Tests for core functionality
    ├── examples/         # Example tests
    └── ...               # Other unit tests
```

## Documentation Structure

The `docs/` directory contains all documentation:

```
docs/
├── api/                  # API documentation
│   ├── ai_agent/         # AI agent API docs
│   ├── core/             # Core API docs
│   └── memory/           # Memory API docs
├── development/          # Development guides
├── guides/               # User guides
├── research/             # Research notes
│   └── ai-digest/        # AI research digest
└── user_guide/           # User guides
```

## Scripts

The `scripts/` directory contains utility scripts:

```
scripts/
├── generate_tests.py     # Test generation script
├── update_docs.py        # Documentation update script
└── update_imports.py     # Import update script
```
