#!/usr/bin/env python3
"""
Example script to generate Memory Service code using templates.

This script demonstrates how to use the template engine to generate
Memory Service code using different MCP integration approaches.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.augment_adam.utils.templates import render_code_template

# Define the service
service_definition = {
    "service_name": "Memory Service",
    "service_description": "A service for managing memory storage and retrieval",
    "endpoints": [
        {
            "name": "add_memory",
            "path": "/memories",
            "method": "POST",
            "description": "Add a new memory",
            "parameters": [
                {"name": "text", "type": "str", "description": "The text content of the memory"},
                {"name": "metadata", "type": "dict", "description": "Additional metadata for the memory"}
            ],
            "returns": {"type": "dict", "description": "The created memory with ID"}
        },
        {
            "name": "get_memory",
            "path": "/memories/{memory_id}",
            "method": "GET",
            "description": "Get a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to retrieve"}
            ],
            "returns": {"type": "dict", "description": "The memory with the specified ID"}
        },
        {
            "name": "list_memories",
            "path": "/memories",
            "method": "GET",
            "description": "List all memories",
            "parameters": [],
            "returns": {"type": "dict", "description": "List of all memories"}
        },
        {
            "name": "delete_memory",
            "path": "/memories/{memory_id}",
            "method": "DELETE",
            "description": "Delete a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to delete"}
            ],
            "returns": {"type": "dict", "description": "Success message"}
        }
    ],
    "models": [
        {
            "name": "Memory",
            "description": "A memory item",
            "fields": [
                {"name": "id", "type": "str", "required": True, "description": "Unique identifier"},
                {"name": "text", "type": "str", "required": True, "description": "Text content"},
                {"name": "metadata", "type": "dict", "required": False, "description": "Additional metadata"}
            ]
        },
        {
            "name": "MemoryCreate",
            "description": "Request to create a memory",
            "fields": [
                {"name": "text", "type": "str", "required": True, "description": "Text content"},
                {"name": "metadata", "type": "dict", "required": False, "description": "Additional metadata"}
            ]
        }
    ],
    "mcp_tools": [
        {
            "name": "add_memory",
            "description": "Add a new memory",
            "parameters": [
                {"name": "text", "type": "str", "description": "The text content of the memory"},
                {"name": "metadata", "type": "dict", "description": "Additional metadata for the memory"}
            ],
            "returns": {"type": "dict", "description": "The created memory with ID"}
        },
        {
            "name": "get_memory",
            "description": "Get a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to retrieve"}
            ],
            "returns": {"type": "dict", "description": "The memory with the specified ID"}
        },
        {
            "name": "list_memories",
            "description": "List all memories",
            "parameters": [],
            "returns": {"type": "dict", "description": "List of all memories"}
        },
        {
            "name": "delete_memory",
            "description": "Delete a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to delete"}
            ],
            "returns": {"type": "dict", "description": "Success message"}
        }
    ],
    "tools": [
        {
            "name": "add_memory",
            "description": "Add a new memory",
            "parameters": [
                {"name": "text", "type": "str", "description": "The text content of the memory"},
                {"name": "metadata", "type": "dict", "description": "Additional metadata for the memory"}
            ],
            "returns": {"type": "dict", "description": "The created memory with ID"}
        },
        {
            "name": "get_memory",
            "description": "Get a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to retrieve"}
            ],
            "returns": {"type": "dict", "description": "The memory with the specified ID"}
        },
        {
            "name": "list_memories",
            "description": "List all memories",
            "parameters": [],
            "returns": {"type": "dict", "description": "List of all memories"}
        },
        {
            "name": "delete_memory",
            "description": "Delete a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to delete"}
            ],
            "returns": {"type": "dict", "description": "Success message"}
        }
    ],
    "resources": [
        {
            "name": "get_memory",
            "uri": "memory://{memory_id}",
            "description": "Get a memory by ID",
            "parameters": [
                {"name": "memory_id", "type": "str", "description": "The ID of the memory to retrieve"}
            ],
            "returns": {"type": "dict", "description": "The memory with the specified ID"}
        }
    ],
    "version": "0.1.0"
}

def generate_service(template_name, output_path):
    """Generate service code using the specified template.
    
    Args:
        template_name: Name of the template to use
        output_path: Path to save the generated code
    """
    # Render the template
    code = render_code_template(template_name, service_definition)
    
    # Save the generated code
    with open(output_path, "w") as f:
        f.write(code)
    
    print(f"Generated {output_path}")

def main():
    """Generate Memory Service code using different templates."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "generated")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate code using different templates
    generate_service(
        "fastapi_mcp_service.py.j2",
        os.path.join(output_dir, "memory_service_fastapi_mcp.py")
    )
    
    generate_service(
        "openwebui_mcp_service.py.j2",
        os.path.join(output_dir, "memory_service_openwebui_mcp.py")
    )
    
    generate_service(
        "fastmcp_service.py.j2",
        os.path.join(output_dir, "memory_service_fastmcp.py")
    )

if __name__ == "__main__":
    main()
