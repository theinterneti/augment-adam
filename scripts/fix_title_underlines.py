#!/usr/bin/env python3
"""
Script to fix title underline warnings in Sphinx documentation.
"""

import os
import re
from pathlib import Path

def fix_title_underlines():
    """Fix title underlines that are too short."""
    print("Fixing title underlines...")
    
    # Get all .rst files
    rst_files = []
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if file.endswith(".rst"):
                rst_files.append(os.path.join(root, file))
    
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

def main():
    """Main function."""
    print("Fixing title underline warnings in Sphinx documentation...")
    
    # Fix title underlines
    fix_title_underlines()
    
    print("Done!")

if __name__ == "__main__":
    main()
