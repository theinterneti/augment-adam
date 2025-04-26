#!/usr/bin/env python3
"""
Script to fix common Sphinx documentation warnings.

This script analyzes the Sphinx build output and fixes common warnings.
"""

import os
import re
import glob
from pathlib import Path

def fix_title_underlines():
    """Fix title underlines that are too short."""
    print("Fixing title underlines...")
    
    # Get all .rst files
    rst_files = glob.glob("docs/**/*.rst", recursive=True)
    
    for file_path in rst_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find title lines and their underlines
        title_pattern = re.compile(r'^([^\n]+)\n([=\-~]+)$', re.MULTILINE)
        
        def replace_underline(match):
            title = match.group(1)
            underline = match.group(2)
            char = underline[0]
            # Make the underline at least as long as the title
            new_underline = char * max(len(title), len(underline))
            return f"{title}\n{new_underline}"
        
        # Replace underlines
        new_content = title_pattern.sub(replace_underline, content)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  Fixed underlines in {file_path}")

def fix_include_paths():
    """Fix include directive paths."""
    print("Fixing include directive paths...")
    
    # Get all .rst files
    rst_files = glob.glob("docs/**/*.rst", recursive=True)
    
    for file_path in rst_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find include directives with incorrect paths
        include_pattern = re.compile(r'.. include:: ([^\n]+)')
        
        def fix_path(match):
            path = match.group(1)
            # Remove 'architecture/' or 'developer_guide/' prefix if present
            if path.startswith('architecture/') or path.startswith('developer_guide/'):
                new_path = path.split('/', 1)[1]
                # Check if the file exists in the docs directory
                if os.path.exists(os.path.join('docs', new_path)):
                    return f".. include:: ../../{new_path}"
            return match.group(0)
        
        # Replace paths
        new_content = include_pattern.sub(fix_path, content)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  Fixed include paths in {file_path}")

def create_missing_files():
    """Create placeholder files for missing includes."""
    print("Creating placeholder files for missing includes...")
    
    # Common missing files
    missing_files = [
        "docs/architecture/AGENT_COORDINATION.md",
        "docs/architecture/CONTEXT_ENGINE.md",
        "docs/architecture/TEMPLATE_ENGINE.md",
        "docs/developer_guide/TESTING_FRAMEWORK.md"
    ]
    
    for file_path in missing_files:
        if not os.path.exists(file_path):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create a placeholder file
            with open(file_path, 'w') as f:
                title = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
                f.write(f"# {title}\n\n")
                f.write(f"This is a placeholder for the {title} documentation.\n")
                f.write("This file will be replaced with actual content.\n")
            
            print(f"  Created placeholder file: {file_path}")

def fix_toctree():
    """Fix toctree references."""
    print("Fixing toctree references...")
    
    # Update the index.rst file
    index_path = "docs/index.rst"
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Remove 'docs/' prefix from toctree entries
        toctree_pattern = re.compile(r'(\s+docs/)([^\n]+)')
        new_content = toctree_pattern.sub(r'\1\2', content)
        
        if new_content != content:
            with open(index_path, 'w') as f:
                f.write(new_content)
            print(f"  Fixed toctree references in {index_path}")

def main():
    """Main function."""
    print("Fixing Sphinx documentation warnings...")
    
    # Fix title underlines
    fix_title_underlines()
    
    # Fix include paths
    fix_include_paths()
    
    # Create missing files
    create_missing_files()
    
    # Fix toctree references
    fix_toctree()
    
    print("Done!")

if __name__ == "__main__":
    main()
