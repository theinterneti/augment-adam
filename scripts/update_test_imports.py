#!/usr/bin/env python3
"""Script to update imports in test files from dukat to augment_adam.

This script finds all Python test files in the tests directory
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
    
    # Replace patch paths
    updated_content = re.sub(
        r"patch\(['\"]dukat\.", 
        "patch('augment_adam.", 
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
    
    # Replace logger names
    updated_content = re.sub(
        r'logger = logging\.getLogger\("dukat', 
        'logger = logging.getLogger("augment_adam', 
        updated_content
    )
    updated_content = re.sub(
        r'logging\.getLogger\("dukat', 
        'logging.getLogger("augment_adam', 
        updated_content
    )
    
    # Replace temp dir names
    updated_content = re.sub(
        r'tempfile\.mkdtemp\(prefix="dukat_', 
        'tempfile.mkdtemp(prefix="augment_adam_', 
        updated_content
    )
    updated_content = re.sub(
        r'tempfile\.mktemp\(prefix="dukat_', 
        'tempfile.mktemp(prefix="augment_adam_', 
        updated_content
    )
    
    # Replace test names
    updated_content = re.sub(
        r'def test_dukat_', 
        'def test_augment_adam_', 
        updated_content
    )
    
    # Replace module imports
    updated_content = re.sub(
        r'spec_from_file_location\("dukat\.', 
        'spec_from_file_location("augment_adam.', 
        updated_content
    )
    updated_content = re.sub(
        r'sys\.modules\["dukat\.', 
        'sys.modules["augment_adam.', 
        updated_content
    )
    updated_content = re.sub(
        r"'../../dukat/", 
        "'../../augment_adam/", 
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
        root_dir = os.path.join(os.getcwd(), "tests")
    
    print(f"Updating imports in {root_dir}...")
    
    updated_files = 0
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    print(f"Updated {file_path}")
                    updated_files += 1
    
    print(f"Updated {updated_files} files.")


if __name__ == "__main__":
    main()
