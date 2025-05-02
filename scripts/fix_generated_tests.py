#!/usr/bin/env python3
"""
Fix Generated Tests.

This script fixes common issues in the generated test files.
"""

import os
import sys
import re
import glob
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fix_generated_tests")

def fix_abstract_class_instantiation(file_path: str) -> bool:
    """
    Fix abstract class instantiation in test files.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        True if the file was modified, False otherwise
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if the file contains abstract class instantiation
    if "self.instance = Memory(" in content:
        # Replace with a concrete implementation
        modified_content = content.replace(
            "self.instance = Memory(",
            "# Create a concrete implementation of Memory for testing\n        class TestMemoryImpl(Memory):\n            def __init__(self, name=\"test_memory\", memory_type=MemoryType.VECTOR):\n                super().__init__(name=name, memory_type=memory_type)\n                \n            def search(self, query, limit=10):\n                # Simple implementation for testing\n                return list(self.items.values())[:limit]\n        \n        self.instance = TestMemoryImpl("
        )
        
        # Write the modified content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        return True
    
    return False

def fix_missing_imports(file_path: str) -> bool:
    """
    Fix missing imports in test files.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        True if the file was modified, False otherwise
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = False
    
    # Add missing imports
    if "MemoryType" in content and "from augment_adam.memory.core.base import MemoryType" not in content:
        import_line = "from augment_adam.memory.core.base import *"
        new_import_line = "from augment_adam.memory.core.base import *, MemoryType"
        content = content.replace(import_line, new_import_line)
        modified = True
    
    # Fix undefined variables in mock calls
    content = re.sub(r'result = self\.instance\.(\w+)\((.*?)content(.*?)\)', r'result = self.instance.\1(\2"test_content"\3)', content)
    content = re.sub(r'result = self\.instance\.(\w+)\((.*?)metadata(.*?)\)', r'result = self.instance.\1(\2{}\3)', content)
    content = re.sub(r'result = self\.instance\.(\w+)\((.*?)limit(.*?)\)', r'result = self.instance.\1(\210\3)', content)
    
    # Write the modified content back to the file
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return modified

def fix_test_file(file_path: str) -> bool:
    """
    Fix issues in a test file.
    
    Args:
        file_path: Path to the test file
        
    Returns:
        True if the file was modified, False otherwise
    """
    modified = False
    
    # Fix abstract class instantiation
    if fix_abstract_class_instantiation(file_path):
        modified = True
    
    # Fix missing imports
    if fix_missing_imports(file_path):
        modified = True
    
    return modified

def main():
    """Run the test fixer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix issues in generated test files")
    parser.add_argument("--directory", default="tests/unit", help="Directory containing test files to fix")
    parser.add_argument("--file", help="Fix a specific test file")
    args = parser.parse_args()
    
    # Fix a specific file or all files in the directory
    if args.file:
        if not os.path.exists(args.file):
            logger.error(f"File not found: {args.file}")
            return
        
        logger.info(f"Fixing test file: {args.file}")
        if fix_test_file(args.file):
            logger.info(f"Fixed issues in {args.file}")
        else:
            logger.info(f"No issues found in {args.file}")
    
    else:
        # Find all test files in the directory
        test_files = glob.glob(os.path.join(args.directory, "**", "test_*.py"), recursive=True)
        logger.info(f"Found {len(test_files)} test files in {args.directory}")
        
        # Fix issues in each file
        fixed_files = 0
        for file_path in test_files:
            logger.info(f"Fixing test file: {file_path}")
            if fix_test_file(file_path):
                logger.info(f"Fixed issues in {file_path}")
                fixed_files += 1
            else:
                logger.info(f"No issues found in {file_path}")
        
        logger.info(f"Fixed issues in {fixed_files} test files")

if __name__ == "__main__":
    main()
