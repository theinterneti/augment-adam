#!/usr/bin/env python3
"""
Script to generate an index file for the documentation.
"""

import os
from pathlib import Path

# Define the documentation directories
doc_dirs = [
    "docs/architecture",
    "docs/developer_guide",
    "docs/user_guide",
    "docs/api"
]

# Define the template for the index file
TEMPLATE = """# Augment Adam Documentation

Welcome to the Augment Adam documentation. This documentation provides information about the architecture, usage, and development of the Augment Adam system.

## Architecture

{architecture_links}

## Developer Guide

{developer_guide_links}

## User Guide

{user_guide_links}

## API Reference

{api_links}
"""

# Function to get links for a directory
def get_links(directory):
    links = []
    if os.path.exists(directory):
        for file in sorted(os.listdir(directory)):
            if file.endswith(".md"):
                # Get the file path
                file_path = os.path.join(directory, file)
                
                # Read the first line of the file to get the title
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    title = first_line.lstrip("# ")
                
                # Create a link to the file
                link = f"- [{title}]({file_path})"
                links.append(link)
    return "\n".join(links) if links else "No documentation available yet."

# Generate the links for each section
architecture_links = get_links("docs/architecture")
developer_guide_links = get_links("docs/developer_guide")
user_guide_links = get_links("docs/user_guide")
api_links = get_links("docs/api")

# Render the template
output = TEMPLATE.format(
    architecture_links=architecture_links,
    developer_guide_links=developer_guide_links,
    user_guide_links=user_guide_links,
    api_links=api_links
)

# Save the output
output_path = Path("docs/README.md")
with open(output_path, 'w') as f:
    f.write(output)

print(f"Generated documentation index at {output_path}")
