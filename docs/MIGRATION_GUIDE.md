# Migration Guide: dukat to augment_adam

This guide helps users migrate from the old `dukat` package to the new `augment_adam` package.

## Overview

The project has been renamed from `dukat` to `augment_adam` and the directory structure has been reorganized to follow a more standard Python package layout. This guide will help you update your code to work with the new package.

## Installation

If you were previously installing the package from PyPI:

```bash
# Old
pip install dukat

# New
pip install augment-adam
```

If you were installing from source:

```bash
# Old
git clone https://github.com/yourusername/dukat.git
cd dukat
pip install -e .

# New
git clone https://github.com/augment-adam/augment-adam.git
cd augment-adam
pip install -e .
```

## Import Changes

All imports need to be updated from `dukat` to `augment_adam`:

```python
# Old
from dukat.core import Assistant
from dukat.memory import FAISSMemory
from dukat.plugins import get_plugin_registry

# New
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory
from augment_adam.plugins import get_plugin_manager  # Note: registry renamed to manager
```

## Configuration Files

Configuration files are now stored in `~/.augment_adam/` instead of `~/.dukat/`:

```python
# Old
config_path = "~/.dukat/config.yaml"
memory_path = "~/.dukat/memory"

# New
config_path = "~/.augment_adam/config.yaml"
memory_path = "~/.augment_adam/memory"
```

## Class and Function Renames

Some classes and functions have been renamed for clarity:

1. `DukatError` → `AugmentAdamError`
2. `ParallelTaskExecutor` → `ParallelExecutor`
3. `PluginRegistry` → `PluginManager`
4. `get_plugin_registry()` → `get_plugin_manager()`

## Collection Names

If you were directly accessing memory collections, the collection names have changed:

```python
# Old
collection_name = "dukat_memory"
collection_name = "dukat_concepts"
collection_name = "dukat_episodes"

# New
collection_name = "augment_adam_memory"
collection_name = "augment_adam_concepts"
collection_name = "augment_adam_episodes"
```

## Command-Line Interface

The command-line interface has been updated:

```bash
# Old
dukat
dukat web

# New
augment-adam
augment-adam web
```

## Docker Images

Docker image names have been updated:

```bash
# Old
docker pull yourusername/dukat:latest
docker run -it yourusername/dukat:latest

# New
docker pull augment-adam/augment-adam:latest
docker run -it augment-adam/augment-adam:latest
```

## Automatic Migration Script

We've provided a script to help you automatically update your code. Save this as `migrate.py` and run it on your codebase:

```python
#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def update_file(file_path):
    """Update imports and references in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace imports
    updated_content = re.sub(
        r"from dukat\.", 
        "from augment_adam.", 
        content
    )
    updated_content = re.sub(
        r"import dukat\.", 
        "import augment_adam.", 
        updated_content
    )
    
    # Replace paths
    updated_content = re.sub(
        r"~\/\.dukat\/", 
        "~/.augment_adam/", 
        updated_content
    )
    
    # Replace collection names
    updated_content = re.sub(
        r'"dukat_', 
        '"augment_adam_', 
        updated_content
    )
    updated_content = re.sub(
        r"'dukat_", 
        "'augment_adam_", 
        updated_content
    )
    
    # Replace class names
    updated_content = re.sub(
        r"DukatError", 
        "AugmentAdamError", 
        updated_content
    )
    
    # Replace ParallelTaskExecutor
    updated_content = re.sub(
        r"ParallelTaskExecutor", 
        "ParallelExecutor", 
        updated_content
    )
    
    # Replace PluginRegistry
    updated_content = re.sub(
        r"PluginRegistry", 
        "PluginManager", 
        updated_content
    )
    
    # Replace get_plugin_registry
    updated_content = re.sub(
        r"get_plugin_registry", 
        "get_plugin_manager", 
        updated_content
    )
    
    # Replace CLI commands
    updated_content = re.sub(
        r"\bdukat\b", 
        "augment-adam", 
        updated_content
    )

    # Write the updated content back to the file if it changed
    if content != updated_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        return True
    
    return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <directory>")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    print(f"Updating references in {root_dir}...")
    
    updated_files = 0
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".py", ".md", ".yaml", ".yml", ".json")):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    print(f"Updated {file_path}")
                    updated_files += 1
    
    print(f"Updated {updated_files} files.")

if __name__ == "__main__":
    main()
```

Run the script on your codebase:

```bash
python migrate.py /path/to/your/code
```

## Need Help?

If you encounter any issues during migration, please [open an issue](https://github.com/augment-adam/augment-adam/issues) on our GitHub repository.
