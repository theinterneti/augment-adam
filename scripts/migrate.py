#!/usr/bin/env python3
"""Migration script for dukat to augment_adam.

This script helps users migrate their code from the old dukat package
to the new augment_adam package by automatically updating imports,
references, and paths.
"""

import os
import re
import sys
from pathlib import Path


def update_file(file_path):
    """Update imports and references in a file.

    Args:
        file_path: Path to the file to update.

    Returns:
        True if the file was updated, False otherwise.
    """
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
