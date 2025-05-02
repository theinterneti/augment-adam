#!/usr/bin/env python3
"""
Rename Test Files.

This script renames test files to avoid import file mismatch errors.
"""

import os
import sys
import glob
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rename_test_files")

def rename_test_files(directory: str) -> None:
    """
    Rename test files to avoid import file mismatch errors.
    
    Args:
        directory: The directory containing test files
    """
    # Find all test files
    test_files = glob.glob(os.path.join(directory, "**", "test_*.py"), recursive=True)
    logger.info(f"Found {len(test_files)} test files in {directory}")
    
    # Group test files by name
    test_files_by_name = {}
    for file_path in test_files:
        file_name = os.path.basename(file_path)
        if file_name not in test_files_by_name:
            test_files_by_name[file_name] = []
        test_files_by_name[file_name].append(file_path)
    
    # Rename test files with the same name
    renamed_files = 0
    for file_name, file_paths in test_files_by_name.items():
        if len(file_paths) > 1:
            logger.info(f"Found {len(file_paths)} test files with the same name: {file_name}")
            
            for file_path in file_paths[1:]:
                # Get the parent directory name
                parent_dir = os.path.basename(os.path.dirname(file_path))
                
                # Create a new file name
                new_file_name = f"test_{parent_dir}_{file_name[5:]}"
                new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
                
                # Rename the file
                os.rename(file_path, new_file_path)
                logger.info(f"Renamed {file_path} to {new_file_path}")
                renamed_files += 1
    
    logger.info(f"Renamed {renamed_files} test files")

def main():
    """Run the test file renamer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rename test files to avoid import file mismatch errors")
    parser.add_argument("--directory", default="tests/unit", help="Directory containing test files to rename")
    args = parser.parse_args()
    
    rename_test_files(args.directory)

if __name__ == "__main__":
    main()
