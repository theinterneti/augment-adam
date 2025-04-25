#!/usr/bin/env python3
"""
Script to archive old code into compressed files.

This script compresses directories into tar.gz files and moves them to the archive directory.
The compressed files are gitignored to save space in the repository.
"""

import os
import sys
import tarfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def create_archive(source_dir: str, archive_dir: str, name: Optional[str] = None) -> str:
    """
    Create a compressed archive of a directory.
    
    Args:
        source_dir: Path to the directory to archive
        archive_dir: Path to the directory where the archive will be stored
        name: Optional name for the archive (default: basename of source_dir)
        
    Returns:
        Path to the created archive file
    
    Raises:
        FileNotFoundError: If the source directory doesn't exist
        OSError: If there's an error creating the archive
    """
    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")
    
    # Create archive directory if it doesn't exist
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    # Generate archive name if not provided
    if name is None:
        name = source_path.name
    
    # Add timestamp to archive name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{name}_{timestamp}.tar.gz"
    archive_file = archive_path / archive_name
    
    # Create the archive
    with tarfile.open(archive_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    
    return str(archive_file)


def update_gitignore(archive_pattern: str) -> None:
    """
    Update .gitignore to ignore the archive files.
    
    Args:
        archive_pattern: Pattern to add to .gitignore
        
    Raises:
        OSError: If there's an error updating .gitignore
    """
    gitignore_path = Path(".gitignore")
    
    # Create .gitignore if it doesn't exist
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write(f"# Archived code\n{archive_pattern}\n")
        return
    
    # Check if pattern already exists in .gitignore
    with open(gitignore_path, "r") as f:
        content = f.read()
    
    if archive_pattern in content:
        return
    
    # Add pattern to .gitignore
    with open(gitignore_path, "a") as f:
        f.write(f"\n# Archived code\n{archive_pattern}\n")


def main() -> None:
    """Main function to archive code."""
    parser = argparse.ArgumentParser(description="Archive code into compressed files")
    parser.add_argument("source_dirs", nargs="+", help="Directories to archive")
    parser.add_argument("--archive-dir", default="archive/code", help="Directory where archives will be stored")
    parser.add_argument("--no-gitignore", action="store_true", help="Don't update .gitignore")
    
    args = parser.parse_args()
    
    for source_dir in args.source_dirs:
        try:
            archive_file = create_archive(source_dir, args.archive_dir)
            print(f"Created archive: {archive_file}")
        except Exception as e:
            print(f"Error archiving {source_dir}: {e}", file=sys.stderr)
    
    if not args.no_gitignore:
        try:
            update_gitignore(f"{args.archive_dir}/*.tar.gz")
            print(f"Updated .gitignore to ignore {args.archive_dir}/*.tar.gz")
        except Exception as e:
            print(f"Error updating .gitignore: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
