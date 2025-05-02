#!/usr/bin/env python3
"""
Example script to generate an Integrated Memory Service using templates.

This script demonstrates how to use the template engine to generate
an Integrated Memory Service that combines all three MCP integration approaches.
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

def main():
    """Generate an Integrated Memory Service using the template."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "generated")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate code using the integrated template
    code = render_code_template("integrated_mcp_service.py.j2", service_definition)
    
    # Save the generated code
    output_path = os.path.join(output_dir, "memory_service_integrated.py")
    with open(output_path, "w") as f:
        f.write(code)
    
    print(f"Generated {output_path}")
    print("\nThis integrated service combines all three MCP approaches:")
    print("1. FastAPI with FastAPI-MCP (Direct API-to-MCP)")
    print("2. FastAPI with open-webui-mcp (Proxied API-to-MCP)")
    print("3. FastMCP with FastAPI Generation (Native MCP-to-API)")
    print("\nTo run the service:")
    print(f"python {output_path}")
    print("\nThis will start the following servers:")
    print("- Main API server on port 8000")
    print("- Direct MCP server on port 8001")
    print("- Native MCP server on port 8002")
    print("- Proxied MCP server on port 8003")

if __name__ == "__main__":
    main()
