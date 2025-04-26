#!/usr/bin/env python3
"""
Simple script to generate testing framework documentation.

This script uses a template string directly instead of relying on the template engine,
which allows us to generate documentation without installing the full package.
"""

import os
import json
import sys
from pathlib import Path

# Load the testing framework data
data_path = Path("docs/data/testing_framework.json")
if not data_path.exists():
    print(f"Error: Data file {data_path} not found.")
    sys.exit(1)

with open(data_path, 'r') as f:
    data = json.load(f)

# Simple template for user guide
TEMPLATE = """# {title}

{description}

{sections_content}
"""

# Process sections
sections_content = ""
if "sections" in data:
    for section in data["sections"]:
        sections_content += f"## {section['title']}\n\n{section['content']}\n\n"
        if "code" in section:
            sections_content += f"```python\n{section['code']}\n```\n\n"

        if "subsections" in section:
            for subsection in section["subsections"]:
                sections_content += f"### {subsection['title']}\n\n{subsection['content']}\n\n"
                if "code" in subsection:
                    sections_content += f"```python\n{subsection['code']}\n```\n\n"

# Render the template
output = TEMPLATE.format(
    title=data["title"],
    description=data["description"],
    sections_content=sections_content
)

# Save the output
output_path = Path("docs/developer_guide/TESTING_FRAMEWORK.md")
os.makedirs(output_path.parent, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(output)

print(f"Generated documentation at {output_path}")
