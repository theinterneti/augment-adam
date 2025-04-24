# Utility Scripts

This directory contains utility scripts for development, maintenance, and migration.

## Scripts

### `generate_tests.py`

Generates test files for Python modules using various strategies including LLM-based generation and property-based testing.

Usage:
```bash
python scripts/generate_tests.py --source-file augment_adam/core/async_assistant.py --output-dir tests/unit/
```

### `update_imports.py`

Updates imports from `dukat` to `augment_adam` in Python files.

Usage:
```bash
python scripts/update_imports.py [directory]
```

### `update_docs.py`

Updates references in documentation files from `dukat` to `augment_adam`.

Usage:
```bash
python scripts/update_docs.py [directory]
```

### `update_test_imports.py`

Updates imports in test files from `dukat` to `augment_adam`.

Usage:
```bash
python scripts/update_test_imports.py [directory]
```

### `migrate.py`

Helps users migrate their code from the old `dukat` package to the new `augment_adam` package.

Usage:
```bash
python scripts/migrate.py /path/to/your/code
```

## Adding New Scripts

When adding new scripts to this directory:

1. Make sure the script has a clear purpose and is well-documented
2. Add a shebang line at the top: `#!/usr/bin/env python3`
3. Add a docstring explaining what the script does
4. Make the script executable: `chmod +x scripts/your_script.py`
5. Update this README.md file with information about your script
