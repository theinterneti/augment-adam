#!/usr/bin/env python3
"""
Script to archive old code into the archive directory.

This script moves old code to the archive directory, preserving the directory structure.
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import tarfile


def archive_directory(source_dir: str, archive_dir: str, timestamp: str) -> None:
    """
    Archive a directory.
    
    Args:
        source_dir: Path to the directory to archive
        archive_dir: Path to the archive directory
        timestamp: Timestamp to use in the archive name
    """
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Source directory {source_dir} does not exist")
        return
    
    # Create archive directory if it doesn't exist
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    
    # Create archive name
    archive_name = f"{source_path.name}_{timestamp}.tar.gz"
    archive_file = archive_path / archive_name
    
    # Create the archive
    with tarfile.open(archive_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    
    print(f"Archived {source_dir} to {archive_file}")


def update_gitignore(archive_patterns: list) -> None:
    """
    Update .gitignore to ignore the archive files.
    
    Args:
        archive_patterns: Patterns to add to .gitignore
    """
    gitignore_path = Path(".gitignore")
    
    # Create .gitignore if it doesn't exist
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("# Archived code\n")
            for pattern in archive_patterns:
                f.write(f"{pattern}\n")
        return
    
    # Read existing .gitignore
    with open(gitignore_path, "r") as f:
        content = f.read()
    
    # Check if archive section already exists
    if "# Archived code" in content:
        # Update existing section
        lines = content.split("\n")
        archive_section_start = lines.index("# Archived code")
        archive_section_end = archive_section_start + 1
        while archive_section_end < len(lines) and lines[archive_section_end].startswith("#") is False and lines[archive_section_end].strip() != "":
            archive_section_end += 1
        
        # Replace archive section
        new_lines = lines[:archive_section_start + 1]
        for pattern in archive_patterns:
            new_lines.append(pattern)
        new_lines.extend(lines[archive_section_end:])
        
        # Write updated .gitignore
        with open(gitignore_path, "w") as f:
            f.write("\n".join(new_lines))
    else:
        # Add archive section
        with open(gitignore_path, "a") as f:
            f.write("\n\n# Archived code\n")
            for pattern in archive_patterns:
                f.write(f"{pattern}\n")
    
    print(f"Updated .gitignore to ignore archive files")


def main() -> None:
    """Main function to archive old code."""
    parser = argparse.ArgumentParser(description="Archive old code")
    parser.add_argument("--code-dir", default="augment_adam", help="Directory containing code to archive")
    parser.add_argument("--docs-dir", default="docs", help="Directory containing docs to archive")
    parser.add_argument("--tests-dir", default="tests", help="Directory containing tests to archive")
    parser.add_argument("--archive-dir", default="archive", help="Directory to store archives")
    parser.add_argument("--no-gitignore", action="store_true", help="Don't update .gitignore")
    
    args = parser.parse_args()
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Archive directories
    archive_directory(args.code_dir, f"{args.archive_dir}/code", timestamp)
    archive_directory(args.docs_dir, f"{args.archive_dir}/docs", timestamp)
    archive_directory(args.tests_dir, f"{args.archive_dir}/tests", timestamp)
    
    # Update .gitignore
    if not args.no_gitignore:
        update_gitignore([
            f"{args.archive_dir}/code/*.tar.gz",
            f"{args.archive_dir}/docs/*.tar.gz",
            f"{args.archive_dir}/tests/*.tar.gz"
        ])


if __name__ == "__main__":
    main()
