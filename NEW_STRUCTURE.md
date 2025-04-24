# New Directory Structure for Augment Adam

This document explains the new directory structure for the Augment Adam project.

## Overview

The project has been reorganized to follow Python packaging best practices and established standards. The main changes are:

1. Consolidated all code under the `augment_adam` package
2. Organized documentation, tests, Docker files, and configuration files into dedicated directories
3. Updated package configuration to use Poetry
4. Standardized module organization and imports

## Directory Structure

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

## Main Package Structure

The `augment_adam` package is organized into the following modules:

- `ai_agent`: AI agent implementation
- `cli`: Command-line interface
- `context_engine`: Context engine
- `core`: Core functionality
- `memory`: Memory systems
- `models`: Model implementations
- `plugins`: Plugin system
- `server`: Server implementation
- `utils`: Utility functions
- `web`: Web interface

## Migration Status

The migration is still in progress. The following tasks have been completed:

1. ✅ Created the new directory structure
2. ✅ Moved Docker files to the `docker` directory
3. ✅ Moved configuration files to the `config` directory
4. ✅ Consolidated documentation in the `docs` directory
5. ✅ Consolidated examples in the `examples` directory
6. ✅ Consolidated scripts in the `scripts` directory
7. ✅ Consolidated tests in the `tests` directory
8. ✅ Copied core files from `augment-adam` to the new structure
9. ✅ Copied core files from `dukat` to the new structure
10. ✅ Updated imports in key files
11. ✅ Updated package configuration

The following tasks still need to be completed:

1. ❌ Update imports in all files
2. ❌ Update tests to use the new structure
3. ❌ Update documentation to reflect the new structure
4. ❌ Create a proper CI/CD pipeline

## Next Steps

1. Run the test script to verify the new structure: `./test_structure.py`
2. Fix any import errors that are found
3. Update the remaining files to use the new structure
4. Create a proper CI/CD pipeline
5. Update documentation to reflect the new structure
