#!/usr/bin/env python3
"""
Simple script to generate getting started guide.

This script uses a template string directly instead of relying on the template engine,
which allows us to generate documentation without installing the full package.
"""

import os
import json
import sys
from pathlib import Path

# Load the getting started data
data_path = Path("docs/data/getting_started.json")
if not data_path.exists():
    print(f"Error: Data file {data_path} not found.")
    sys.exit(1)

with open(data_path, 'r') as f:
    data = json.load(f)

# Simple template for user guide
TEMPLATE = """# {title}

{description}

{sections_content}

{examples_content}

{troubleshooting_content}

{next_steps_content}
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

# Process examples
examples_content = ""
if "examples" in data:
    examples_content += "## Examples\n\n"
    for example in data["examples"]:
        examples_content += f"### {example['title']}\n\n{example['description']}\n\n"
        if "code" in example:
            examples_content += f"```python\n{example['code']}\n```\n\n"
        if "output" in example:
            examples_content += f"Output:\n```\n{example['output']}\n```\n\n"

# Process troubleshooting
troubleshooting_content = ""
if "troubleshooting" in data:
    troubleshooting_content += "## Troubleshooting\n\n"
    for issue in data["troubleshooting"]:
        troubleshooting_content += f"### {issue['problem']}\n\n{issue['solution']}\n\n"

# Process next steps
next_steps_content = ""
if "next_steps" in data:
    next_steps_content += "## Next Steps\n\n"
    for step in data["next_steps"]:
        description = f": {step['description']}" if "description" in step else ""
        next_steps_content += f"- [{step['title']}]({step['link']}){description}\n"

# Render the template
output = TEMPLATE.format(
    title=data["title"],
    description=data["description"],
    sections_content=sections_content,
    examples_content=examples_content,
    troubleshooting_content=troubleshooting_content,
    next_steps_content=next_steps_content
)

# Save the output
output_path = Path("docs/user_guide/getting_started.md")
os.makedirs(output_path.parent, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(output)

print(f"Generated documentation at {output_path}")
