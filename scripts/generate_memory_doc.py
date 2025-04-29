#!/usr/bin/env python3
"""
Simple script to generate memory system architecture documentation.

This script uses a template string directly instead of relying on the template engine,
which allows us to generate documentation without installing the full package.
"""

import os
import json
import sys
from pathlib import Path

# Load the memory system architecture data
data_path = Path("docs/data/memory_system_arch.json")
if not data_path.exists():
    print(f"Error: Data file {data_path} not found.")
    sys.exit(1)

with open(data_path, 'r') as f:
    data = json.load(f)

# Simple template for architecture documentation
TEMPLATE = """# {title}

## Overview

{description}

{architecture_diagram_section}

## Components

{components_section}

## Interfaces

{interfaces_section}

## Workflows

{workflows_section}

## Examples

{examples_section}

## Integration with Other Components

{integration_section}

## Future Enhancements

{future_enhancements_section}
"""

# Process architecture diagram
if "architecture_diagram" in data:
    architecture_diagram_section = f"""## Architecture Diagram

{data['architecture_diagram']['description']}

```
{data['architecture_diagram']['diagram']}
```"""
else:
    architecture_diagram_section = ""

# Process components
components_section = ""
if "components" in data:
    for component in data["components"]:
        components_section += f"### {component['name']}\n\n{component['description']}\n\n"
        
        if "responsibilities" in component:
            components_section += "#### Responsibilities\n\n"
            for responsibility in component["responsibilities"]:
                components_section += f"- {responsibility}\n"
            components_section += "\n"
            
        if "interfaces" in component:
            components_section += "#### Interfaces\n\n"
            for interface in component["interfaces"]:
                components_section += f"- `{interface['name']}`: {interface['description']}\n"
            components_section += "\n"
            
        if "implementation" in component:
            components_section += f"#### Implementation\n\n{component['implementation']}\n\n"
            if "code" in component:
                components_section += f"```python\n{component['code']}\n```\n\n"

# Process interfaces
interfaces_section = ""
if "interfaces" in data:
    for interface in data["interfaces"]:
        interfaces_section += f"### {interface['name']}\n\n{interface['description']}\n\n"
        if "code" in interface:
            interfaces_section += f"```python\n{interface['code']}\n```\n\n"

# Process workflows
workflows_section = ""
if "workflows" in data:
    for workflow in data["workflows"]:
        workflows_section += f"### {workflow['name']}\n\n{workflow['description']}\n\n"
        
        if "steps" in workflow:
            workflows_section += "#### Steps\n\n"
            for i, step in enumerate(workflow["steps"], 1):
                workflows_section += f"{i}. {step}\n"
            workflows_section += "\n"
            
        if "diagram" in workflow:
            workflows_section += f"#### Diagram\n\n```\n{workflow['diagram']}\n```\n\n"

# Process examples
examples_section = ""
if "examples" in data:
    for example in data["examples"]:
        examples_section += f"### {example['title']}\n\n{example['description']}\n\n"
        if "code" in example:
            examples_section += f"```python\n{example['code']}\n```\n\n"

# Process integration
integration_section = ""
if "integration" in data:
    for integration_item in data["integration"]:
        integration_section += f"### {integration_item['component']}\n\n{integration_item['description']}\n\n"
        if "code" in integration_item:
            integration_section += f"```python\n{integration_item['code']}\n```\n\n"

# Process future enhancements
future_enhancements_section = ""
if "future_enhancements" in data:
    for enhancement in data["future_enhancements"]:
        future_enhancements_section += f"- **{enhancement['title']}**: {enhancement['description']}\n"

# Render the template
output = TEMPLATE.format(
    title=data["title"],
    description=data["description"],
    architecture_diagram_section=architecture_diagram_section,
    components_section=components_section,
    interfaces_section=interfaces_section,
    workflows_section=workflows_section,
    examples_section=examples_section,
    integration_section=integration_section,
    future_enhancements_section=future_enhancements_section
)

# Save the output
output_path = Path("docs/architecture/MEMORY_SYSTEM.md")
os.makedirs(output_path.parent, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(output)

print(f"Generated documentation at {output_path}")
