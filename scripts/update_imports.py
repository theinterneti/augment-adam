#!/usr/bin/env python3
"""Script to update imports from dukat to augment_adam.

This script finds all Python files in the augment_adam directory
and replaces imports from dukat to augment_adam.
"""

import os
import re
import sys
from pathlib import Path


def update_file(file_path):
    """Update imports in a file.

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
    
    # Replace logger names
    updated_content = re.sub(
        r'logger = logging\.getLogger\("dukat', 
        'logger = logging.getLogger("augment_adam', 
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

    # Write the updated content back to the file if it changed
    if content != updated_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        return True
    
    return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.path.join(os.getcwd(), "augment_adam")
    
    print(f"Updating imports in {root_dir}...")
    
    updated_files = 0
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    print(f"Updated {file_path}")
                    updated_files += 1
    
    print(f"Updated {updated_files} files.")


if __name__ == "__main__":
    main()
